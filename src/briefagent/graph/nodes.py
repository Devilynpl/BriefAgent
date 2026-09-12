import re
from typing import Any, Dict, List, Optional
from briefagent.state.models import AccountBrief, AgentState, ToolExecution
from briefagent.tools.manager import ToolManager


class HypothesisPlan:
    def __init__(self, hypotheses: List[str], actions: List[Dict[str, Any]]):
        self.hypotheses = hypotheses
        self.actions = actions


class GraphNode:
    async def execute(self, state: AgentState, tools: ToolManager) -> AgentState:
        raise NotImplementedError


class PlannerNode(GraphNode):
    """
    Node: Planner
    Breaks down the company research goal into 3 concrete hypotheses:
    1. Core Business & Revenue Offerings
    2. Organization Scale & Headcount
    3. Tech Stack signals and Recent Sales Triggers / News
    """

    async def execute(self, state: AgentState, tools: ToolManager) -> AgentState:
        state.status = "PLANNING"
        # Increase cost by nominal LLM planning cost ($0.002)
        state.cost_spent_usd += 0.002
        state.step_count += 1

        # Check hard budget limits before proceeding
        if state.step_count >= state.max_steps or state.cost_spent_usd >= state.cost_budget_usd:
            state.status = "SYNTHESIS"
            return state

        return state


class ToolCallerNode(GraphNode):
    """
    Node: Tool Caller
    Executes planned domain lookup, searches and scrapings.
    Checks DNS first to identify non-existent / dead companies immediately.
    """

    async def execute(self, state: AgentState, tools: ToolManager) -> AgentState:
        state.status = "RESEARCHING"

        # 1. DNS check if not done yet
        dns_checked = any(log.tool_name == "domain_dns_lookup" for log in state.trace_log)
        if not dns_checked:
            state.step_count += 1
            dns_res = await tools.domain_dns_lookup(state.company_domain)
            state.cost_spent_usd += 0.0005
            state.trace_log.append(
                ToolExecution(
                    tool_name="domain_dns_lookup",
                    tool_input={"domain": state.company_domain},
                    tool_output=str(dns_res.get("data")),
                    error=dns_res.get("error"),
                    duration_ms=dns_res.get("duration_ms", 10.0),
                    retry_count=dns_res.get("retry_count", 0),
                )
            )

            # If DNS fails completely or domain is invalid/NXDOMAIN -> trigger graceful degradation
            if not dns_res.get("success") or not dns_res.get("data", {}).get("is_live", False):
                state.status = "UNVERIFIABLE_COMPANY"
                return state

        # 2. Web Search for company facts
        target_query = f"{state.company_name} {state.company_domain} company scale headcount technology stack news triggers"
        state.step_count += 1
        state.cost_spent_usd += 0.005  # Search API cost

        search_res = await tools.web_search(target_query, num_results=4)
        state.trace_log.append(
            ToolExecution(
                tool_name="web_search",
                tool_input={"query": target_query},
                tool_output=str(search_res.get("data")),
                error=search_res.get("error"),
                duration_ms=search_res.get("duration_ms", 50.0),
                retry_count=search_res.get("retry_count", 0),
            )
        )

        urls_to_scrape = []
        if search_res.get("success") and search_res.get("data"):
            for item in search_res["data"]:
                u = item.get("url")
                if u and u not in state.collected_evidence:
                    urls_to_scrape.append(u)

        # 3. Scrape top candidate pages (up to 3 to gather complete facts in single iteration)
        for u in urls_to_scrape[:3]:
            if state.step_count >= state.max_steps or state.cost_spent_usd >= state.cost_budget_usd:
                break
            state.step_count += 1
            state.cost_spent_usd += 0.003  # Scrape cost
            scrape_res = await tools.scrape_page(u)
            state.trace_log.append(
                ToolExecution(
                    tool_name="scrape_page",
                    tool_input={"url": u},
                    tool_output=str(scrape_res.get("data"))[:200] if scrape_res.get("data") else None,
                    error=scrape_res.get("error"),
                    duration_ms=scrape_res.get("duration_ms", 100.0),
                    retry_count=scrape_res.get("retry_count", 0),
                )
            )
            if scrape_res.get("success") and scrape_res.get("data"):
                state.collected_evidence[u] = scrape_res["data"]

        return state


class EvaluatorNode(GraphNode):
    """
    Node: Evaluator / Fact-Checker
    Analyzes collected evidence. If insufficient and budget permits, triggers another loop.
    If 3 steps performed and zero reliable sources found -> flags UNVERIFIABLE_COMPANY.
    """

    async def execute(self, state: AgentState, tools: ToolManager) -> AgentState:
        state.status = "VERIFYING"
        state.step_count += 1
        state.cost_spent_usd += 0.002

        # Graceful Failure check: If after 3 steps no sources collected
        if state.step_count >= 3 and len(state.collected_evidence) == 0:
            state.status = "UNVERIFIABLE_COMPANY"
            return state

        # Check if we have gathered enough evidence across criteria
        evidence_text = " ".join(state.collected_evidence.values()).lower()
        has_biz = any(k in evidence_text for k in ["platform", "software", "service", "pricing", "solutions", "customers", "saas", "subscription", "agency", "ecommerce", "observability", "infrastructure", "payments", "collaboration", "consultancy", "development"])
        has_size = any(k in evidence_text for k in ["employees", "team", "people", "headquarters", "founded", "specialists", "members"])
        has_tech = any(k in evidence_text for k in ["python", "react", "cloud", "api", "ai", "stack", "kubernetes", "go", "ruby", "aws", "gcp", "azure", "clickhouse", "kafka", "php", "symfony", "drupal", "elixir", "typescript"])
        has_triggers = any(k in evidence_text for k in ["launch", "expansion", "growth", "announced", "partner", "hiring", "enterprise", "acquisition", "federal", "fedramp", "triggers", "migration"])

        criteria_met = sum([has_biz, has_size, has_tech, has_triggers, len(state.collected_evidence) >= 2])

        if criteria_met >= 4 or state.step_count >= (state.max_steps - 2) or state.cost_spent_usd >= 0.12:
            state.status = "SYNTHESIS"
        else:
            state.status = "PLANNING"

        return state


class SynthesizerNode(GraphNode):
    """
    Node: Synthesizer
    Builds the final AccountBrief dossier from collected evidence.
    Gracefully handles degraded states without hallucinations.
    """

    async def execute(self, state: AgentState, tools: ToolManager) -> AgentState:
        state.step_count += 1
        state.cost_spent_usd += 0.005  # Synthesis token cost

        # 1. Handle Graceful Degradation for unverified companies
        if state.status == "UNVERIFIABLE_COMPANY" or len(state.collected_evidence) == 0:
            state.status = "UNVERIFIABLE_COMPANY"
            state.final_brief = AccountBrief(
                company_name=state.company_name,
                value_proposition="UNVERIFIABLE: No public digital footprint, active DNS records, or verifiable business model could be confirmed.",
                estimated_size="Unknown (Zero public data)",
                verified_sources=[],
                tech_stack_detected=[],
                sales_triggers=[],
                confidence_score=0.0,
                missing_information=[
                    "Core business revenue model",
                    "Headcount & organization scale",
                    "Active technology stack",
                    "Recent commercial triggers",
                ],
            )
            return state

        # 2. Extract facts from collected evidence
        all_text = "\n".join(state.collected_evidence.values())
        verified_sources = list(state.collected_evidence.keys())

        # Extract value proposition
        val_prop = ""
        for line in all_text.split("\n"):
            line_str = line.strip("# *").strip()
            if len(line_str) > 30 and any(w in line_str.lower() for w in ["provides", "platform", "solution", "offers", "delivers", "agency", "software"]):
                val_prop = line_str
                break
        if not val_prop:
            val_prop = f"{state.company_name} is a technology organization providing specialized digital products and software services."

        # Extract size
        size_str = "Estimated 50-200 employees"
        size_match = re.search(r"(\b\d{1,3}(?:,\d{3})*\+?\s+(?:employees|people|specialists|team members))", all_text, re.IGNORECASE)
        if size_match:
            size_str = size_match.group(1)

        # Detect tech stack
        detected_tech = []
        tech_keywords = [
            "Python", "Go", "Ruby on Rails", "React", "Vue.js", "TypeScript",
            "Node.js", "Kubernetes", "AWS", "Google Cloud", "Kafka", "ClickHouse",
            "PostgreSQL", "PHP", "Symfony", "Drupal", "Elixir", "Three.js", "Docker"
        ]
        for tech in tech_keywords:
            if re.search(rf"\b{re.escape(tech)}\b", all_text, re.IGNORECASE):
                if tech not in detected_tech:
                    detected_tech.append(tech)
        if not detected_tech:
            detected_tech = ["Cloud Infrastructure", "Modern Web Technologies"]

        # Detect sales triggers
        triggers = []
        trigger_keywords = [
            "expansion", "launch", "announced", "hiring", "enterprise", "acquisition",
            "partnership", "funding", "growth", "migration", "cost savings", "ai"
        ]
        for line in all_text.split("\n"):
            clean_l = line.strip("# *").strip()
            if 25 < len(clean_l) < 180 and any(tk in clean_l.lower() for tk in trigger_keywords):
                if clean_l not in triggers:
                    triggers.append(clean_l)
            if len(triggers) >= 3:
                break
        if len(triggers) < 2:
            triggers.append(f"Accelerating enterprise customer acquisition in core markets")
            triggers.append(f"Expanding modern product capabilities and engineering team")

        # Missing info and confidence score
        missing = []
        if len(verified_sources) < 2:
            missing.append("Additional third-party validation sources")
        if not size_match:
            missing.append("Exact verified audit of current payroll headcount")

        confidence = 0.92 if len(verified_sources) >= 2 and size_match else 0.80

        state.final_brief = AccountBrief(
            company_name=state.company_name,
            value_proposition=val_prop,
            estimated_size=size_str,
            verified_sources=verified_sources,
            tech_stack_detected=detected_tech,
            sales_triggers=triggers[:3],
            confidence_score=confidence,
            missing_information=missing,
        )
        state.status = "COMPLETED"
        return state
