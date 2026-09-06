"""
Self-Critique / Red Team Agent (ANALYZE module).
A deliberately adversarial agent whose job is to try to kill the
project before it's greenlit: plot holes, character inconsistencies,
unrealistic decisions, excessive costs, weak audience appeal,
dependency risks, unresolved threads.
"""
from typing import Any

from app.agents.base_agent import BaseAgent
from app.core.clickhouse_client import analytics as shared_analytics

SYSTEM_INSTRUCTION = (
    "You are the RED TEAM — a deliberately adversarial critic whose job is "
    "to try to kill this film project before it is greenlit. Look for: "
    "plot holes, character inconsistencies, unrealistic decisions, "
    "excessive production costs, weak audience appeal, dependency risks, "
    "and unresolved story threads. Return ONLY JSON with a 'findings' list "
    "(each: severity [critical/moderate/minor], issue, recommendation) and "
    "a top-level 'verdict' (greenlight/fix_required/kill)."
)


class RedTeamAgent(BaseAgent):
    name = "red_team_agent"
    instruction = SYSTEM_INSTRUCTION

    def __init__(self):
        super().__init__()
        self.analytics = shared_analytics

    async def run(self, context_bundle: str, project_id: str = "default",
                   universe_id: str = "") -> dict[str, Any]:
        await self.emit("agent_started", {"project_id": project_id, "task": "red_team"})

        prompt = f"PROJECT CONTEXT (screenplay/simulation/budget/audience notes):\n{context_bundle[:12000]}"
        result = self.gemini.generate_json(prompt, system_instruction=self.instruction)

        for finding in result.get("findings", []):
            self.analytics.insert("red_team_findings", {
                "finding_id": self.new_run_id(),
                "project_id": project_id,
                "universe_id": universe_id,
                "severity": str(finding.get("severity", "minor")),
                "issue": str(finding.get("issue", "")),
                "recommendation": str(finding.get("recommendation", "")),
            })

        await self.emit("agent_completed", {"project_id": project_id, "task": "red_team", "verdict": result.get("verdict")})
        return {"agent": self.name, "project_id": project_id, "result": result}
