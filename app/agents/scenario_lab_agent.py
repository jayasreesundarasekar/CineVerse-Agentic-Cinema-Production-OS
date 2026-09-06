"""
Scenario Lab Agent (SIMULATE module).
Generalized "WHAT IF...?" production-decision simulator: budget cuts,
actor unavailability, ending changes, genre shifts, runtime changes,
release delays, etc. Can optionally register the result as a new node
in the Cinema Multiverse tree (see app/core/multiverse.py).
"""
from typing import Any

from app.agents.base_agent import BaseAgent
from app.core.clickhouse_client import analytics as shared_analytics

SYSTEM_INSTRUCTION = (
    "You are a production 'what-if' scenario engine. Given a baseline "
    "story/production summary and a WHAT IF perturbation, simulate the "
    "consequences across story, budget, schedule, and audience appeal. "
    "Return ONLY JSON with fields: consequence_summary, story_score (0-100), "
    "audience_score (0-100), continuity_score (0-100), budget_score (0-100), "
    "risk_flags (list), and recommendation."
)


class ScenarioLabAgent(BaseAgent):
    name = "scenario_lab_agent"
    instruction = SYSTEM_INSTRUCTION

    def __init__(self):
        super().__init__()
        self.analytics = shared_analytics

    async def run(self, baseline_summary: str, what_if: str,
                   project_id: str = "default", parent_universe_id: str = "",
                   register_as_universe: bool = True, title: str = "") -> dict[str, Any]:
        await self.emit("agent_started", {"project_id": project_id, "task": "scenario_lab", "what_if": what_if})

        prompt = f"BASELINE:\n{baseline_summary}\n\nWHAT IF:\n{what_if}"
        result = self.gemini.generate_json(prompt, system_instruction=self.instruction)

        universe_id = ""
        if register_as_universe:
            universe_id = self.new_run_id()
            self.analytics.insert("universes", {
                "universe_id": universe_id,
                "project_id": project_id,
                "parent_id": parent_universe_id,
                "title": title or what_if[:80],
                "summary": str(result.get("consequence_summary", ""))[:2000],
                "story_score": float(result.get("story_score", 0) or 0),
                "audience_score": float(result.get("audience_score", 0) or 0),
                "continuity_score": float(result.get("continuity_score", 0) or 0),
                "budget_score": float(result.get("budget_score", 0) or 0),
                "status": "simulated",
            })

        await self.emit("agent_completed", {"project_id": project_id, "task": "scenario_lab", "universe_id": universe_id})
        return {"agent": self.name, "project_id": project_id, "universe_id": universe_id, "result": result}
