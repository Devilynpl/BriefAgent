"""JudgeTargetAdapter for BriefAgent autonomous research system.

Implements BaseTargetAdapter protocol from JudgeKit.
Connects JudgeKit evaluation runner to BriefAgent's StateGraphEngine,
ToolManager, resilient circuit breakers, and 6-criteria rubric evaluator.
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure BriefAgent src is in path if not installed as package
CURRENT_DIR = Path(__file__).resolve().parent
BRIEFAGENT_SRC = CURRENT_DIR.parent.parent / "src"
if str(BRIEFAGENT_SRC) not in sys.path:
    sys.path.insert(0, str(BRIEFAGENT_SRC))

try:
    from judgekit.target_protocol import BaseTargetAdapter, TargetOutput
except ImportError:
    from pydantic import BaseModel, Field

    class TargetOutput(BaseModel):  # type: ignore
        answer: str
        contexts: List[str] = []
        input_tokens: int = 0
        output_tokens: int = 0
        latency_ms: float = 0.0
        cost_usd: float = 0.0
        step_count: Optional[int] = None
        status: Optional[str] = None
        tool_calls: List[Dict[str, Any]] = []
        tool_error_recovery_rate: Optional[float] = None
        metadata: Dict[str, Any] = {}

    class BaseTargetAdapter:  # type: ignore
        pass

from briefagent.graph.engine import StateGraphEngine
from briefagent.state.models import AgentState
from briefagent.state.rubric import evaluate_brief_rubric
from briefagent.tools.manager import ToolManager


class BriefAgentTargetAdapter(BaseTargetAdapter):
    """Adapter exposing BriefAgent autonomous research pipeline to JudgeKit."""

    def __init__(self, tools: Optional[ToolManager] = None):
        self.tools = tools or ToolManager(use_mock_fallback=True, force_mock=False)
        self.engine = StateGraphEngine(tools=self.tools)

    async def run_query(self, query: str, metadata: Optional[Dict[str, Any]] = None) -> TargetOutput:
        """Execute BriefAgent research on a company.

        Args:
            query: Company name (e.g. "Snowflake" or "OmniVortex HyperTech Dynamics")
            metadata: Optional dictionary with "domain", "tier", "is_adversarial"
        """
        metadata = metadata or {}
        company_name = query.strip()
        domain = metadata.get("domain") or f"{company_name.lower().replace(' ', '')}.com"
        is_adversarial = metadata.get("is_adversarial", False) or ("stealth" in metadata.get("category", "").lower())

        t0 = time.perf_counter()
        state: AgentState = await self.engine.run(company_name, domain)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        brief = state.final_brief

        # Extract answer / dossier representation
        if brief:
            answer_text = (
                f"Dossier: {brief.company_name}\n"
                f"Status: {state.status}\n"
                f"Value Proposition: {brief.value_proposition}\n"
                f"Estimated Size: {brief.estimated_size}\n"
                f"Tech Stack: {', '.join(brief.tech_stack_detected)}\n"
                f"Sales Triggers: {'; '.join(brief.sales_triggers)}\n"
                f"Confidence: {brief.confidence_score:.2f}"
            )
            contexts = list(brief.verified_sources)
        else:
            answer_text = f"Brak dossier. Status wykonania agenta: {state.status}"
            contexts = list(state.collected_evidence.keys())

        # Evaluate 6-criteria rubric
        rubric_res = evaluate_brief_rubric(
            brief=brief,
            is_adversarial_or_stealth=is_adversarial,
            agent_status=state.status,
        )
        rubric_score = rubric_res.passed_count / float(rubric_res.total_count)

        # Tool execution telemetry
        tool_records = [
            {
                "tool": log.tool_name,
                "input": log.tool_input,
                "duration_ms": log.duration_ms,
                "retries": log.retry_count,
                "error": log.error,
            }
            for log in state.trace_log
        ]

        # Estimated token metrics
        inp_tokens = state.step_count * 350
        out_tokens = len(answer_text.split()) * 2

        return TargetOutput(
            answer=answer_text,
            contexts=contexts,
            input_tokens=inp_tokens,
            output_tokens=out_tokens,
            latency_ms=round(latency_ms, 2),
            cost_usd=round(state.cost_spent_usd, 6),
            step_count=state.step_count,
            status=state.status,
            tool_calls=tool_records,
            tool_error_recovery_rate=self.tools.recovery_rate,
            metadata={
                "rubric_score": rubric_score,
                "rubric_passed_count": rubric_res.passed_count,
                "is_rubric_success": rubric_res.is_success,
                "is_adversarial": is_adversarial,
                "max_steps": state.max_steps,
                "max_cost_usd": state.cost_budget_usd,
            },
        )
