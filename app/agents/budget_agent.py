"""
Production Budget Simulator Agent (PRODUCE module).
Takes a baseline line-item budget plus a "what if" variable change
(e.g. cut shooting schedule by 5 days) and reasons about the resulting
cost, risk, quality, and audience-impact deltas.
"""
from typing import Any

from app.agents.base_agent import BaseAgent
from app.core.clickhouse_client import analytics as shared_analytics

SYSTEM_INSTRUCTION = (
    "You are a film production budget analyst. Given a baseline line-item "
    "budget (JSON) and a proposed change, return ONLY JSON with fields: "
    "new_line_items (object, same keys as baseline with adjusted values), "
    "total_cost (number), cost_delta_pct (number), risk_delta "
    "(increase/decrease/unchanged with a short reason), quality_delta "
    "(increase/decrease/unchanged with a short reason), and "
    "audience_impact (short string)."
)


class BudgetAgent(BaseAgent):
    name = "budget_agent"
    instruction = SYSTEM_INSTRUCTION

    def __init__(self):
        super().__init__()
        self.analytics = shared_analytics

    async def run(self, line_items: dict[str, float], change_request: str,
                   project_id: str = "default", universe_id: str = "") -> dict[str, Any]:
        await self.emit("agent_started", {"project_id": project_id, "task": "budget_simulation"})

        prompt = f"BASELINE LINE ITEMS (INR):\n{line_items}\n\nPROPOSED CHANGE:\n{change_request}"
        result = self.gemini.generate_json(prompt, system_instruction=self.instruction)

        total_cost = result.get("total_cost")
        if not isinstance(total_cost, (int, float)):
            total_cost = sum(v for v in line_items.values() if isinstance(v, (int, float)))
            result["total_cost"] = total_cost

        budget_id = self.new_run_id()
        self.analytics.insert("budgets", {
            "budget_id": budget_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "line_items_json": str(result.get("new_line_items", line_items)),
            "total_cost": float(total_cost),
            "risk_delta": str(result.get("risk_delta", "")),
            "quality_delta": str(result.get("quality_delta", "")),
            "notes": change_request,
        })

        await self.emit("agent_completed", {"project_id": project_id, "task": "budget_simulation", "budget_id": budget_id})
        return {"agent": self.name, "budget_id": budget_id, "project_id": project_id, "result": result}
