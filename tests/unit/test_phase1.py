import pytest
from briefagent.state.models import AccountBrief, AgentState, ToolExecution
from briefagent.state.rubric import evaluate_brief_rubric
from tests.evals.dataset import load_benchmark_25


def test_agent_state_initialization():
    state = AgentState(company_name="Snowflake", company_domain="snowflake.com")
    assert state.step_count == 0
    assert state.max_steps == 12
    assert state.cost_spent_usd == 0.0
    assert state.cost_budget_usd == 0.15
    assert state.status == "PLANNING"
    assert len(state.collected_evidence) == 0
    assert len(state.trace_log) == 0
    assert state.final_brief is None


def test_tool_execution_model():
    exec_record = ToolExecution(
        tool_name="web_search",
        tool_input={"query": "Snowflake pricing"},
        tool_output="Snowflake offers consumption-based pricing...",
        duration_ms=234.5,
        retry_count=1,
    )
    assert exec_record.tool_name == "web_search"
    assert exec_record.duration_ms == 234.5
    assert exec_record.retry_count == 1
    assert exec_record.error is None


def test_rubric_pass_perfect_brief():
    brief = AccountBrief(
        company_name="Datadog",
        value_proposition="Datadog provides an observability and security platform for cloud applications with SaaS subscription revenue model.",
        estimated_size="5,000+ employees globally",
        verified_sources=["https://datadoghq.com/about", "https://datadoghq.com/press"],
        tech_stack_detected=["Go", "Python", "Kubernetes", "Kafka"],
        sales_triggers=[
            "Announced new LLM Observability module in Q2",
            "Expanding enterprise sales team across EMEA region",
        ],
        confidence_score=0.95,
        missing_information=[],
    )
    result = evaluate_brief_rubric(brief=brief, is_adversarial_or_stealth=False)
    assert result.is_success is True
    assert result.passed_count >= 5


def test_rubric_fail_vague_brief():
    brief = AccountBrief(
        company_name="VagueCorp",
        value_proposition="Leading provider of innovative solutions",  # Vague
        estimated_size="Unknown",  # Missing headcount number
        verified_sources=[],  # Missing sources
        tech_stack_detected=[],  # Missing tech
        sales_triggers=["Expanding"],  # Only 1 trigger
        confidence_score=0.4,
        missing_information=[],
    )
    result = evaluate_brief_rubric(brief=brief, is_adversarial_or_stealth=False)
    assert result.is_success is False
    assert result.passed_count < 5
    assert len(result.rejection_reasons) > 0


def test_rubric_adversarial_graceful_degradation():
    result = evaluate_brief_rubric(
        brief=None,
        is_adversarial_or_stealth=True,
        agent_status="UNVERIFIABLE_COMPANY",
    )
    assert result.is_success is True
    assert result.passed_count == 6


def test_benchmark_dataset_distribution():
    dataset = load_benchmark_25()
    assert len(dataset) == 25
    tiers = [d.tier for d in dataset]
    assert tiers.count("ENTERPRISE") == 10
    assert tiers.count("MID_MARKET_SAAS") == 8
    assert tiers.count("SMALL_SMB") == 4
    assert tiers.count("ADVERSARIAL_STEALTH") == 3
