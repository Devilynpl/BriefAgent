import os
import pytest
from briefagent.state.models import AccountBrief, AgentState
from briefagent.trace.collector import ExecutionTraceCollector
from briefagent.trace.visualizer import ExecutionTraceVisualizer


def test_trace_collector_and_jsonl(tmp_path):
    collector = ExecutionTraceCollector(
        run_id="test-run-123",
        company_name="Snowflake",
        output_dir=str(tmp_path),
    )

    r1 = collector.record_step(
        step=1,
        thought="Need to verify domain existence first",
        action_plan="Perform DNS lookup on snowflake.com",
        tool_call={"tool": "domain_dns_lookup", "domain": "snowflake.com"},
        tool_result="Live domain with MX and A records",
        tokens_used=120,
        cost_spent_usd=0.0005,
    )

    r2 = collector.record_step(
        step=2,
        thought="Domain confirmed. Now search for value prop and headcount",
        action_plan="Web search for snowflake core business and scale",
        tool_call={"tool": "web_search", "query": "snowflake platform revenue"},
        tool_result="Snowflake provides cloud data platform with consumption pricing",
        tokens_used=350,
        cost_spent_usd=0.005,
    )

    assert len(collector.get_all_records()) == 2
    assert os.path.exists(collector.jsonl_path)

    with open(collector.jsonl_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 2
        assert "snowflake.com" in lines[0]


def test_trace_visualizer_renders_md_and_html(tmp_path):
    collector = ExecutionTraceCollector(
        run_id="render-test",
        company_name="Snowflake",
        output_dir=str(tmp_path),
    )
    collector.record_step(
        step=1,
        thought="Checking DNS",
        action_plan="DNS query",
        tool_call={"tool": "domain_dns_lookup"},
        tool_result="OK",
    )

    state = AgentState(company_name="Snowflake", company_domain="snowflake.com")
    state.status = "COMPLETED"
    state.final_brief = AccountBrief(
        company_name="Snowflake",
        value_proposition="Data cloud platform with consumption credits.",
        estimated_size="7,000+ employees",
        verified_sources=["https://snowflake.com"],
        tech_stack_detected=["Python", "Go"],
        sales_triggers=["Cortex AI launch"],
    )

    md = ExecutionTraceVisualizer.render_markdown(state, collector.get_all_records())
    assert "**Final Status:** `COMPLETED`" in md

    html = ExecutionTraceVisualizer.render_html(state, collector.get_all_records())
    assert "<!DOCTYPE html>" in html
    assert "BriefAgent Trace: Snowflake" in html
    assert "Finalne Dossier" in html
