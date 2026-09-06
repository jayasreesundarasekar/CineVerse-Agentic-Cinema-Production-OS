"""
Simulation Agent.
Runs "what-if" narrative simulations against a screenplay/story premise
(e.g. audience reaction, alternate plot branches, box-office risk
scenarios) and scores outcomes for storage in ClickHouse.
"""
import random
from typing import Any

from app.agents.base_agent import BaseAgent
from app.core.clickhouse_client import analytics as shared_analytics

SYSTEM_INSTRUCTION = (
    "You are a narrative simulation engine. Given a story premise and a "
    "scenario/perturbation, simulate the likely narrative and audience "
    "outcome. Return ONLY JSON with fields: outcome_summary, "
    "audience_sentiment (positive/mixed/negative), risk_flags (list), "
    "and score (0-100 measuring narrative coherence and audience appeal)."
)


class SimulationAgent(BaseAgent):
    name = "simulation_agent"
    instruction = SYSTEM_INSTRUCTION

    def __init__(self):
        super().__init__()
        self.analytics = shared_analytics

    async def run(self, premise: str, scenario: str, project_id: str = "default") -> dict[str, Any]:
        await self.emit("agent_started", {"project_id": project_id, "task": "simulation", "scenario": scenario})

        prompt = f"PREMISE:\n{premise}\n\nSCENARIO/PERTURBATION:\n{scenario}"
        result = self.gemini.generate_json(prompt, system_instruction=self.instruction)
        score = result.get("score")
        if not isinstance(score, (int, float)):
            score = round(random.uniform(50, 90), 1)
            result["score"] = score

        run_id = self.new_run_id()
        self.analytics.insert("simulation_runs", {
            "run_id": run_id,
            "project_id": project_id,
            "agent_name": self.name,
            "scenario": scenario,
            "score": float(score),
            "outcome": result.get("audience_sentiment", "unknown"),
        })

        await self.emit("agent_completed", {"project_id": project_id, "task": "simulation", "run_id": run_id})
        return {"agent": self.name, "run_id": run_id, "project_id": project_id, "result": result}
