"""
Screenplay Analysis Agent.
Uses Gemini to analyze structure, character arcs, pacing, dialogue
quality, and thematic consistency of an uploaded script.
"""
from typing import Any

from app.agents.base_agent import BaseAgent

SYSTEM_INSTRUCTION = (
    "You are a professional script analyst. Given screenplay text, "
    "return a structured JSON assessment covering: three_act_structure, "
    "character_arcs, pacing, dialogue_quality, thematic_consistency, "
    "and an overall_score from 0-100 with a one-paragraph rationale."
)


class ScreenplayAgent(BaseAgent):
    name = "screenplay_agent"
    instruction = SYSTEM_INSTRUCTION

    async def run(self, script_text: str, project_id: str = "default") -> dict[str, Any]:
        await self.emit("agent_started", {"project_id": project_id, "task": "screenplay_analysis"})

        prompt = (
            "Analyze the following screenplay excerpt and return ONLY JSON.\n\n"
            f"SCRIPT:\n{script_text[:12000]}"
        )
        analysis = self.gemini.generate_json(prompt, system_instruction=self.instruction)

        await self.emit("agent_completed", {"project_id": project_id, "task": "screenplay_analysis"})
        return {"agent": self.name, "project_id": project_id, "analysis": analysis}
