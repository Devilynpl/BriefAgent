import pytest
from briefagent.graph.engine import StateGraphEngine
from briefagent.state.rubric import evaluate_brief_rubric
from briefagent.tools.manager import ToolManager


@pytest.mark.asyncio
async def test_graph_execution_enterprise_company():
    tools = ToolManager(force_mock=True)
    engine = StateGraphEngine(tools=tools)

    state = await engine.run(company_name="Snowflake", company_domain="snowflake.com")
    assert state.status == "COMPLETED"
    assert state.step_count <= state.max_steps
    assert state.cost_spent_usd <= state.cost_budget_usd
    assert state.final_brief is not None
    assert "Snowflake" in state.final_brief.company_name
    assert len(state.final_brief.verified_sources) >= 1
    assert len(state.final_brief.sales_triggers) >= 2

    # Rubric check
    rubric = evaluate_brief_rubric(state.final_brief, is_adversarial_or_stealth=False)
    assert rubric.is_success is True
    assert rubric.passed_count >= 5


@pytest.mark.asyncio
async def test_graph_adversarial_graceful_degradation():
    tools = ToolManager(force_mock=True)
    engine = StateGraphEngine(tools=tools)

    state = await engine.run(
        company_name="OmniVortex HyperTech Dynamics",
        company_domain="omnivortexhypertech.nonexistent",
    )
    assert state.status == "UNVERIFIABLE_COMPANY"
    assert state.step_count <= 4  # Short-circuits quickly
    assert state.final_brief is not None
    assert "UNVERIFIABLE" in state.final_brief.value_proposition
    assert state.final_brief.confidence_score == 0.0

    rubric = evaluate_brief_rubric(
        state.final_brief,
        is_adversarial_or_stealth=True,
        agent_status=state.status,
    )
    assert rubric.is_success is True


@pytest.mark.asyncio
async def test_hard_step_budget_enforcement():
    tools = ToolManager(force_mock=True)
    engine = StateGraphEngine(tools=tools)

    # Force step_count close to limit and verify it never exceeds 12
    state = await engine.run(company_name="Datadog", company_domain="datadoghq.com")
    assert state.step_count <= 12
    assert state.cost_spent_usd < 0.15
