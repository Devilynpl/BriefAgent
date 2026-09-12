from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .models import AccountBrief


class RubricCriterion(BaseModel):
    name: str
    passed: bool
    reason: str


class RubricResult(BaseModel):
    company_name: str
    is_success: bool  # min 5/6
    passed_count: int
    total_count: int = 6
    criteria: Dict[str, RubricCriterion] = Field(default_factory=dict)
    rejection_reasons: List[str] = Field(default_factory=list)


def evaluate_brief_rubric(
    brief: Optional[AccountBrief],
    is_adversarial_or_stealth: bool = False,
    agent_status: Optional[str] = None,
) -> RubricResult:
    """
    Binary Success Rubric (6 strict criteria):
    A task is considered successful (1) if the brief meets >= 5/6 criteria:
    1. Core Business: Precise description of what the company does/monetizes (not just vague marketing slogan).
    2. Scale & Headcount: Number of employees or size rank supported by context.
    3. Tech Stack / Product Signals: Mention of technologies or products from the last 12 months.
    4. Pain Points / Triggers: Min. 2 real business triggers/challenges (expansion, hiring, layoffs, M&A).
    5. Source Verification: Every fact has an active, scraped URL (non-empty verified_sources, no hallucinated empty sources).
    6. Graceful Degradation: If company is stealth/nonexistent, agent explicitly reports lack of data instead of hallucinating.
    """
    criteria: Dict[str, RubricCriterion] = {}

    # Check Graceful Degradation first for adversarial / stealth cases
    if is_adversarial_or_stealth:
        degraded = (
            agent_status == "UNVERIFIABLE_COMPANY"
            or (brief is not None and "UNVERIFIABLE" in brief.value_proposition)
            or (brief is not None and len(brief.missing_information) > 0 and brief.confidence_score <= 0.2)
        )
        criteria["graceful_degradation"] = RubricCriterion(
            name="Graceful Degradation",
            passed=degraded,
            reason="Correctly flagged lack of verifiable data without hallucinations"
            if degraded
            else "Failed to gracefully degrade for unverified/adversarial company",
        )
        # For adversarial companies, passing graceful degradation gives full credit for all fields
        # if the agent honestly flagged missing data rather than hallucinating
        if degraded:
            for crit_name in [
                "core_business",
                "scale_headcount",
                "tech_stack_signals",
                "pain_points_triggers",
                "source_verification",
            ]:
                criteria[crit_name] = RubricCriterion(
                    name=crit_name.replace("_", " ").title(),
                    passed=True,
                    reason="Handled via truthful non-hallucinatory degraded state",
                )
            return RubricResult(
                company_name=brief.company_name if brief else "Unknown",
                is_success=True,
                passed_count=6,
                total_count=6,
                criteria=criteria,
                rejection_reasons=[],
            )

    if brief is None:
        return RubricResult(
            company_name="Unknown",
            is_success=False,
            passed_count=0,
            total_count=6,
            criteria={},
            rejection_reasons=["Brief was not generated (None)."],
        )

    # 1. Core Business
    core_biz_pass = (
        bool(brief.value_proposition)
        and len(brief.value_proposition.strip()) > 25
        and not any(slogan in brief.value_proposition.lower() for slogan in ["leading provider of innovative solutions", "synergistic AI revolution", "empowering dreams"])
    )
    criteria["core_business"] = RubricCriterion(
        name="Core Business",
        passed=core_biz_pass,
        reason="Specific revenue/value model identified" if core_biz_pass else "Value proposition is too vague or missing",
    )

    # 2. Scale & Headcount
    scale_pass = (
        bool(brief.estimated_size)
        and brief.estimated_size.lower() != "unknown"
        and any(char.isdigit() for char in brief.estimated_size)
    )
    criteria["scale_headcount"] = RubricCriterion(
        name="Scale & Headcount",
        passed=scale_pass,
        reason="Specific headcount/scale identified" if scale_pass else "Headcount missing or unsupported",
    )

    # 3. Tech Stack / Product Signals
    tech_pass = len(brief.tech_stack_detected) >= 1 and any(len(t.strip()) > 1 for t in brief.tech_stack_detected)
    criteria["tech_stack_signals"] = RubricCriterion(
        name="Tech Stack / Product Signals",
        passed=tech_pass,
        reason=f"Detected {len(brief.tech_stack_detected)} tech/product signals" if tech_pass else "No recent tech stack/product signals detected",
    )

    # 4. Pain Points / Triggers
    triggers_pass = len(brief.sales_triggers) >= 2
    criteria["pain_points_triggers"] = RubricCriterion(
        name="Pain Points / Triggers",
        passed=triggers_pass,
        reason=f"Found {len(brief.sales_triggers)} sales triggers/pain points" if triggers_pass else f"Found only {len(brief.sales_triggers)} triggers, expected min. 2",
    )

    # 5. Source Verification
    sources_pass = len(brief.verified_sources) >= 1 and all(
        src.startswith("http://") or src.startswith("https://") for src in brief.verified_sources
    )
    criteria["source_verification"] = RubricCriterion(
        name="Source Verification",
        passed=sources_pass,
        reason=f"Verified with {len(brief.verified_sources)} URLs" if sources_pass else "Missing verified web sources",
    )

    # 6. Graceful Degradation check for normal companies
    graceful_pass = True
    if brief.confidence_score < 0.6:
        graceful_pass = len(brief.missing_information) > 0
    criteria["graceful_degradation"] = RubricCriterion(
        name="Graceful Degradation",
        passed=graceful_pass,
        reason="Appropriately recorded missing fields or high confidence" if graceful_pass else "Low confidence without documenting missing information",
    )

    passed_count = sum(1 for c in criteria.values() if c.passed)
    rejection_reasons = [c.reason for c in criteria.values() if not c.passed]
    is_success = passed_count >= 5

    return RubricResult(
        company_name=brief.company_name,
        is_success=is_success,
        passed_count=passed_count,
        total_count=6,
        criteria=criteria,
        rejection_reasons=rejection_reasons,
    )
