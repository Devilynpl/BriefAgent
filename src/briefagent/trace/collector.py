import json
import os
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StepTraceRecord(BaseModel):
    step: int
    thought: str
    action_plan: str
    tool_call: Optional[Dict[str, Any]] = None
    tool_result_summary: Optional[str] = None
    tokens_used: int = 0
    cost_spent_usd: float = 0.0
    timestamp: float = Field(default_factory=time.time)


class ExecutionTraceCollector:
    """
    Records detailed chain-of-thought, action plans, tool executions, tokens and costs to JSONL.
    """

    def __init__(self, run_id: str, company_name: str, output_dir: str = "artifacts"):
        self.run_id = run_id
        self.company_name = company_name
        self.output_dir = output_dir
        self.records: List[StepTraceRecord] = []
        os.makedirs(output_dir, exist_ok=True)
        self.jsonl_path = os.path.join(output_dir, f"trace_{self.run_id}.jsonl")

    def record_step(
        self,
        step: int,
        thought: str,
        action_plan: str,
        tool_call: Optional[Dict[str, Any]] = None,
        tool_result: Optional[str] = None,
        tokens_used: int = 0,
        cost_spent_usd: float = 0.0,
    ) -> StepTraceRecord:
        summary = None
        if tool_result:
            summary = tool_result[:200].replace("\n", " ").strip()

        rec = StepTraceRecord(
            step=step,
            thought=thought,
            action_plan=action_plan,
            tool_call=tool_call,
            tool_result_summary=summary,
            tokens_used=tokens_used,
            cost_spent_usd=cost_spent_usd,
        )
        self.records.append(rec)
        self._append_jsonl(rec)
        return rec

    def _append_jsonl(self, record: StepTraceRecord):
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.model_dump(), ensure_ascii=False) + "\n")

    def get_all_records(self) -> List[StepTraceRecord]:
        return self.records
