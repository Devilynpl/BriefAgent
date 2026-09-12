import os
from typing import List, Optional
from briefagent.state.models import AccountBrief, AgentState
from .collector import ExecutionTraceCollector, StepTraceRecord


class ExecutionTraceVisualizer:
    """
    Generates rich visual execution reports in HTML and Markdown:
    - Decision tree flow
    - Tool calls with parameters and latency
    - Cost & step counters
    - Final AccountBrief dossier
    """

    @staticmethod
    def render_markdown(state: AgentState, records: List[StepTraceRecord]) -> str:
        md = []
        md.append(f"# Execution Trace: {state.company_name} (`{state.company_domain}`)")
        md.append(f"\n- **Final Status:** `{state.status}`")
        md.append(f"- **Total Steps:** `{state.step_count}/{state.max_steps}`")
        md.append(f"- **Total Cost:** `${state.cost_spent_usd:.4f} / ${state.cost_budget_usd:.2f}`")
        md.append(f"- **Evidence Sources:** `{len(state.collected_evidence)} URLs`\n")

        md.append("## 🌳 Decision Tree & Step Log\n")
        md.append("| Step | Node / Action | Tool Call | Tool Summary | Cost (USD) |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")

        for r in records:
            tool_name = r.tool_call.get("tool") if r.tool_call else "-"
            summary = (r.tool_result_summary or "-")[:60].replace("|", "/")
            md.append(f"| **{r.step}** | {r.action_plan} | `{tool_name}` | {summary} | `${r.cost_spent_usd:.4f}` |")

        if state.final_brief:
            md.append("\n## 📄 Final Account Brief\n")
            md.append(f"```json\n{state.final_brief.model_dump_json(indent=2)}\n```\n")

        return "\n".join(md)

    @staticmethod
    def render_html(state: AgentState, records: List[StepTraceRecord]) -> str:
        status_color = "#10b981" if state.status == "COMPLETED" else ("#f59e0b" if state.status == "UNVERIFIABLE_COMPANY" else "#ef4444")
        
        step_items_html = []
        for r in records:
            tool_badge = ""
            if r.tool_call:
                tool_badge = f"""<span class="badge tool-badge">{r.tool_call.get('tool', 'tool')}</span>"""
            summary_html = f"""<div class="result-summary">{r.tool_result_summary or 'None'}</div>""" if r.tool_result_summary else ""

            step_items_html.append(f"""
            <div class="step-card">
              <div class="step-header">
                <span class="step-badge">Step {r.step}</span>
                {tool_badge}
                <span class="step-cost">${r.cost_spent_usd:.4f}</span>
              </div>
              <div class="step-plan"><strong>Action:</strong> {r.action_plan}</div>
              <div class="step-thought"><strong>Chain-of-Thought:</strong> {r.thought}</div>
              {summary_html}
            </div>
            """)

        brief_json_pretty = state.final_brief.model_dump_json(indent=2) if state.final_brief else "No brief produced"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>BriefAgent Execution Trace - {state.company_name}</title>
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: #111827;
      --card-border: #1f2937;
      --accent: #3b82f6;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --status-color: {status_color};
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      padding: 2rem;
      margin: 0;
    }}
    .container {{
      max-width: 1000px;
      margin: 0 auto;
    }}
    .header {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .status-badge {{
      background: var(--status-color);
      color: #000;
      font-weight: 700;
      padding: 0.35rem 0.8rem;
      border-radius: 9999px;
      font-size: 0.85rem;
    }}
    .metrics-bar {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
      margin-bottom: 2rem;
    }}
    .metric-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 1rem;
      text-align: center;
    }}
    .metric-value {{
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--accent);
    }}
    .metric-label {{
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
      margin-top: 0.3rem;
    }}
    .timeline {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-bottom: 2rem;
    }}
    .step-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-left: 4px solid var(--accent);
      border-radius: 8px;
      padding: 1rem;
    }}
    .step-header {{
      display: flex;
      justify-content: space-between;
      margin-bottom: 0.5rem;
    }}
    .step-badge {{
      font-weight: 700;
      color: var(--accent);
    }}
    .tool-badge {{
      background: #1e3a8a;
      color: #93c5fd;
      padding: 0.2rem 0.6rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-family: monospace;
    }}
    .step-plan {{
      font-weight: 600;
      margin-bottom: 0.3rem;
    }}
    .step-thought {{
      font-size: 0.85rem;
      color: var(--text-muted);
      font-style: italic;
      margin-bottom: 0.5rem;
    }}
    .result-summary {{
      background: #0f172a;
      border: 1px solid #1e293b;
      padding: 0.6rem;
      border-radius: 6px;
      font-family: monospace;
      font-size: 0.75rem;
      color: #cbd5e1;
    }}
    pre {{
      background: #0b1120;
      border: 1px solid var(--card-border);
      padding: 1rem;
      border-radius: 8px;
      overflow-x: auto;
      font-size: 0.85rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1 style="margin:0 0 0.2rem 0;">BriefAgent Trace: {state.company_name}</h1>
        <small style="color: var(--text-muted);">{state.company_domain}</small>
      </div>
      <span class="status-badge">{state.status}</span>
    </div>

    <div class="metrics-bar">
      <div class="metric-card">
        <div class="metric-value">{state.step_count} / {state.max_steps}</div>
        <div class="metric-label">Execution Steps</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">${state.cost_spent_usd:.4f}</div>
        <div class="metric-label">Total Cost (Budget: ${state.cost_budget_usd:.2f})</div>
      </div>
      <div class="metric-card">
        <div class="metric-value">{len(state.collected_evidence)}</div>
        <div class="metric-label">Verified Sources</div>
      </div>
    </div>

    <h2>Drzewo Decyzji i Kroków (Trace Log)</h2>
    <div class="timeline">
      {"".join(step_items_html)}
    </div>

    <h2>Finalne Dossier (AccountBrief JSON)</h2>
    <pre><code>{brief_json_pretty}</code></pre>
  </div>
</body>
</html>
"""
        return html
