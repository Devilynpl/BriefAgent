from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class ToolExecution(BaseModel):
    tool_name: str
    tool_input: dict
    tool_output: Optional[str] = None
    error: Optional[str] = None
    duration_ms: float
    retry_count: int = 0


class AccountBrief(BaseModel):
    company_name: str
    value_proposition: str
    headquarters: Optional[str] = None
    estimated_size: str
    leadership: List[str] = Field(default_factory=list)
    products_and_services: List[str] = Field(default_factory=list)
    target_markets: List[str] = Field(default_factory=list)
    key_competitors: List[str] = Field(default_factory=list)
    tech_stack_detected: List[str] = Field(default_factory=list)
    sales_triggers: List[str] = Field(default_factory=list)
    ai_and_digital_opportunities: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    verified_sources: List[str] = Field(default_factory=list)
    icebreaker_emails: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


class AgentState(BaseModel):
    company_name: str
    company_domain: str
    step_count: int = 0
    max_steps: int = 12
    cost_spent_usd: float = 0.0
    cost_budget_usd: float = 0.15
    collected_evidence: Dict[str, str] = Field(default_factory=dict)  # URL -> extracted text
    trace_log: List[ToolExecution] = Field(default_factory=list)
    status: Literal[
        "PLANNING",
        "RESEARCHING",
        "VERIFYING",
        "SYNTHESIS",
        "COMPLETED",
        "FAILED",
        "UNVERIFIABLE_COMPANY",
    ] = "PLANNING"
    final_brief: Optional[AccountBrief] = None
