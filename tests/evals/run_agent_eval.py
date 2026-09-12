import asyncio
import json
import os
import time
from typing import Dict, List
from pydantic import BaseModel

from briefagent.graph.engine import StateGraphEngine
from briefagent.state.models import AgentState
from briefagent.state.rubric import RubricResult, evaluate_brief_rubric
from briefagent.tools.manager import ToolManager
from briefagent.trace.collector import ExecutionTraceCollector
from briefagent.trace.visualizer import ExecutionTraceVisualizer
from tests.evals.dataset import BenchmarkCompany, load_benchmark_25


class EvalRunResult(BaseModel):
    company_name: str
    domain: str
    tier: str
    is_adversarial: bool
    status: str
    step_count: int
    cost_spent_usd: float
    rubric_result: RubricResult
    trace_jsonl: str
    trace_html: str


async def evaluate_single_company(
    comp: BenchmarkCompany,
    tools: ToolManager,
    semaphore: asyncio.Semaphore,
    artifacts_dir: str = "artifacts",
) -> EvalRunResult:
    async with semaphore:
        run_id = f"{comp.name.lower().replace(' ', '_')}_{int(time.time() * 1000)}"
        collector = ExecutionTraceCollector(run_id=run_id, company_name=comp.name, output_dir=artifacts_dir)
        engine = StateGraphEngine(tools=tools)

        # Record start in collector
        collector.record_step(
            step=0,
            thought=f"Initiating research protocol for {comp.name} ({comp.domain}). Tier: {comp.tier}",
            action_plan="Planner hypothesis formulation and DNS pre-flight verification",
            cost_spent_usd=0.0,
        )

        state = await engine.run(comp.name, comp.domain)

        # Transfer trace log from state into collector
        for idx, log in enumerate(state.trace_log, start=1):
            collector.record_step(
                step=idx,
                thought=f"Executing resilient tool action for hypothesis validation",
                action_plan=f"Tool call: {log.tool_name}",
                tool_call={"tool": log.tool_name, "input": log.tool_input},
                tool_result=log.tool_output or log.error,
                cost_spent_usd=0.003,
            )

        collector.record_step(
            step=len(state.trace_log) + 1,
            thought=f"Dossier completed with status {state.status}",
            action_plan="Synthesize structured AccountBrief",
            cost_spent_usd=state.cost_spent_usd,
        )

        # Generate HTML and MD reports
        html_content = ExecutionTraceVisualizer.render_html(state, collector.get_all_records())
        html_path = os.path.join(artifacts_dir, f"trace_{run_id}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        md_content = ExecutionTraceVisualizer.render_markdown(state, collector.get_all_records())
        md_path = os.path.join(artifacts_dir, f"trace_{run_id}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Independent rubric evaluation (0/1)
        rubric_res = evaluate_brief_rubric(
            brief=state.final_brief,
            is_adversarial_or_stealth=comp.is_adversarial,
            agent_status=state.status,
        )

        return EvalRunResult(
            company_name=comp.name,
            domain=comp.domain,
            tier=comp.tier,
            is_adversarial=comp.is_adversarial,
            status=state.status,
            step_count=state.step_count,
            cost_spent_usd=state.cost_spent_usd,
            rubric_result=rubric_res,
            trace_jsonl=collector.jsonl_path,
            trace_html=html_path,
        )


async def run_benchmark():
    dataset = load_benchmark_25()
    print(f"\n[RUNNING] Launching BriefAgent Benchmark Runner for {len(dataset)} companies (Concurrency: 5)...")
    
    semaphore = asyncio.Semaphore(5)
    tools = ToolManager(use_mock_fallback=True, force_mock=True)

    tasks = [
        evaluate_single_company(comp, tools, semaphore, artifacts_dir="artifacts")
        for comp in dataset
    ]
    results: List[EvalRunResult] = await asyncio.gather(*tasks)

    # Calculate final metrics
    total_cases = len(results)
    success_count = sum(1 for r in results if r.rubric_result.is_success)
    task_success_rate = (success_count / total_cases) * 100.0

    avg_steps = sum(r.step_count for r in results) / total_cases
    avg_cost = sum(r.cost_spent_usd for r in results) / total_cases

    adversarial_cases = [r for r in results if r.is_adversarial]
    zero_hallucination_success = sum(
        1 for r in adversarial_cases if r.status == "UNVERIFIABLE_COMPANY" and r.rubric_result.is_success
    )
    zero_hallucination_rate = (zero_hallucination_success / len(adversarial_cases)) * 100.0

    tool_recovery_rate = tools.recovery_rate * 100.0

    print("\n" + "=" * 60)
    print("BRIEFAGENT BENCHMARK EVALUATION RESULTS (25 CASES)")
    print("=" * 60)
    print(f"Total Companies Evaluated:      {total_cases}")
    print(f"Task Success Rate (min 5/6):    {task_success_rate:.1f}% ({success_count}/{total_cases})")
    print(f"Avg Steps to Completion:        {avg_steps:.1f} steps (Target: < 8)")
    print(f"Tool Error Recovery Rate:       {tool_recovery_rate:.1f}% (Target: > 75%)")
    print(f"Avg Cost per Brief:             ${avg_cost:.4f} (Target: < $0.10)")
    print(f"Zero-Hallucination Rate:        {zero_hallucination_rate:.1f}% ({zero_hallucination_success}/{len(adversarial_cases)})")
    print("=" * 60)

    # Detailed breakdown per company
    print("\nDetailed Per-Company Outcomes:")
    for r in results:
        status_icon = "[PASS]" if r.rubric_result.is_success else "[FAIL]"
        adv_tag = " [ADVERSARIAL]" if r.is_adversarial else ""
        print(f"{status_icon} | {r.company_name:<30} | Tier: {r.tier:<20} | Steps: {r.step_count:2d} | Cost: ${r.cost_spent_usd:.4f}{adv_tag}")

    # Export summary report to artifacts/benchmark_summary.json
    summary = {
        "total_cases": total_cases,
        "task_success_rate_percent": task_success_rate,
        "avg_steps": avg_steps,
        "avg_cost_usd": avg_cost,
        "tool_recovery_rate_percent": tool_recovery_rate,
        "zero_hallucination_rate_percent": zero_hallucination_rate,
        "results": [r.model_dump() for r in results],
    }
    with open("artifacts/benchmark_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nArtifacts and trace reports stored in 'artifacts/'. Summary written to 'artifacts/benchmark_summary.json'.")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
