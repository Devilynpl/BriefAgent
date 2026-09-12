import logging
from typing import Optional
from briefagent.state.models import AccountBrief, AgentState
from briefagent.tools.manager import ToolManager
from .nodes import EvaluatorNode, PlannerNode, SynthesizerNode, ToolCallerNode

logger = logging.getLogger("briefagent.engine")


class StateGraphEngine:
    """
    Deterministic State Graph Engine for BriefAgent.
    Orchestrates execution across Planner -> ToolCaller -> Evaluator -> Synthesizer.
    Guarantees hard budgets (max_steps=12, cost_budget_usd=$0.15) and prevents infinite loops.
    """

    def __init__(self, tools: Optional[ToolManager] = None):
        self.tools = tools or ToolManager()
        self.planner = PlannerNode()
        self.tool_caller = ToolCallerNode()
        self.evaluator = EvaluatorNode()
        self.synthesizer = SynthesizerNode()

    async def run(self, company_name: str, company_domain: str) -> AgentState:
        state = AgentState(
            company_name=company_name,
            company_domain=company_domain,
            max_steps=12,
            cost_budget_usd=0.15,
        )

        logger.info(f"Starting BriefAgent research on {company_name} ({company_domain})...")

        # Main deterministic FSM cycle
        while state.status not in ("COMPLETED", "FAILED"):
            # Check hard limits
            if state.step_count >= state.max_steps or state.cost_spent_usd >= state.cost_budget_usd:
                logger.warning(
                    f"Hard budget reached (steps: {state.step_count}/{state.max_steps}, "
                    f"cost: ${state.cost_spent_usd:.4f}/${state.cost_budget_usd:.2f}). Transitioning to synthesis."
                )
                state = await self.synthesizer.execute(state, self.tools)
                break

            if state.status == "PLANNING":
                state = await self.planner.execute(state, self.tools)
                if state.status == "SYNTHESIS":
                    state = await self.synthesizer.execute(state, self.tools)
                else:
                    state = await self.tool_caller.execute(state, self.tools)
                    if state.status == "RESEARCHING":
                        state = await self.evaluator.execute(state, self.tools)
                        if state.status == "SYNTHESIS":
                            state = await self.synthesizer.execute(state, self.tools)
                        elif state.status == "PLANNING":
                            pass  # Next loop

            elif state.status == "RESEARCHING":
                state = await self.evaluator.execute(state, self.tools)
                if state.status == "SYNTHESIS":
                    state = await self.synthesizer.execute(state, self.tools)

            elif state.status == "VERIFYING":
                if state.status == "SYNTHESIS":
                    state = await self.synthesizer.execute(state, self.tools)
                else:
                    state.status = "PLANNING"

            elif state.status == "UNVERIFIABLE_COMPANY":
                # Immediately synthesize the zero-hallucination degraded brief
                state = await self.synthesizer.execute(state, self.tools)
                break

            elif state.status == "SYNTHESIS":
                state = await self.synthesizer.execute(state, self.tools)
                break

            else:
                logger.error(f"Unknown status '{state.status}'. Aborting to partial synthesis.")
                state = await self.synthesizer.execute(state, self.tools)
                break

        return state
