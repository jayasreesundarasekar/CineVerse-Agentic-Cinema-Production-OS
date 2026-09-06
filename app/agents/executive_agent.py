"""
Executive Agent — Greenlight Engine + Decision Provenance (DECIDE module).
Synthesizes screenplay, simulation, forensics/originality, audience,
budget, and red-team results into a single greenlight/no-greenlight
verdict, with an explicit reasoning trace citing the source run IDs
so the decision is explainable rather than a black box.
"""
from typing import Any

from app.agents.base_agent import BaseAgent
from app.core.clickhouse_client import analytics as shared_analytics

SYSTEM_INSTRUCTION = (
    "You are the Executive / Studio Board agent making the final "
    "greenlight decision. Given a bundle of scores and findings from "
    "other agents (story, audience, continuity/red-team, budget), weigh "
    "them and return ONLY JSON with fields: verdict "
    "(greenlight/hold/pass), overall_confidence (0-100), reasoning "
    "(short paragraph), and key_factors (list of short strings, each "
    "citing which input score/finding drove the decision)."
)


class ExecutiveAgent(BaseAgent):
    name = "executive_agent"
    instruction = SYSTEM_INSTRUCTION

    def __init__(self):
        super().__init__()
        self.analytics = shared_analytics

    async def run(self, project_id: str = "default", universe_id: str = "",
                   source_run_ids: list[str] | None = None,
                   score_bundle: dict[str, Any] | None = None) -> dict[str, Any]:
        await self.emit("agent_started", {"project_id": project_id, "task": "greenlight_decision"})

        score_bundle = score_bundle or {}
        source_run_ids = source_run_ids or []

        prompt = f"SCORE / FINDINGS BUNDLE:\n{score_bundle}\n\nSOURCE RUN IDS:\n{source_run_ids}"
        result = self.gemini.generate_json(prompt, system_instruction=self.instruction)

        decision_id = self.new_run_id()
        self.analytics.insert("decisions", {
            "decision_id": decision_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "verdict": str(result.get("verdict", "hold")),
            "reasoning": str(result.get("reasoning", "")),
            "source_run_ids": str(source_run_ids),
        })

        await self.emit("agent_completed", {
            "project_id": project_id, "task": "greenlight_decision",
            "decision_id": decision_id, "verdict": result.get("verdict"),
        })
        return {"agent": self.name, "decision_id": decision_id, "project_id": project_id, "result": result}
