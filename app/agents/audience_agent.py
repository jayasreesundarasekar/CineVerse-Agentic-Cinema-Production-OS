"""
Audience Simulator Agent (ANALYZE module).
Evaluates a story/universe against simulated audience segments
(age bands, genre fans, casual viewers, international audience) and
labels results clearly as AI projections, not real audience research.
"""
from typing import Any

from app.agents.base_agent import BaseAgent
from app.core.clickhouse_client import analytics as shared_analytics

DEFAULT_SEGMENTS = [
    "18-24", "25-34", "35-44", "Genre Fans", "Casual Viewers", "International Audience",
]

SYSTEM_INSTRUCTION = (
    "You are an AI audience-projection analyst (NOT real market research). "
    "Given a story/universe summary and a list of audience segments, "
    "return ONLY JSON with a 'projections' list, each item having: "
    "segment, appeal_score (0-100), rationale. Add a top-level "
    "'disclaimer' field noting these are simulated projections."
)


class AudienceAgent(BaseAgent):
    name = "audience_agent"
    instruction = SYSTEM_INSTRUCTION

    def __init__(self):
        super().__init__()
        self.analytics = shared_analytics

    async def run(self, story_summary: str, segments: list[str] | None = None,
                   project_id: str = "default", universe_id: str = "") -> dict[str, Any]:
        segments = segments or DEFAULT_SEGMENTS
        await self.emit("agent_started", {"project_id": project_id, "task": "audience_simulation"})

        prompt = f"STORY/UNIVERSE SUMMARY:\n{story_summary}\n\nSEGMENTS:\n{segments}"
        result = self.gemini.generate_json(prompt, system_instruction=self.instruction)

        for item in result.get("projections", []):
            self.analytics.insert("audience_projections", {
                "projection_id": self.new_run_id(),
                "project_id": project_id,
                "universe_id": universe_id,
                "segment": str(item.get("segment", "unknown")),
                "appeal_score": float(item.get("appeal_score", 0) or 0),
                "rationale": str(item.get("rationale", "")),
            })

        await self.emit("agent_completed", {"project_id": project_id, "task": "audience_simulation"})
        return {"agent": self.name, "project_id": project_id, "result": result}
