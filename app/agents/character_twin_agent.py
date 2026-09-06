"""
Character Digital Twin Agent (CREATE module).
Maintains a persistent profile (goals, fears, values, relationships,
secrets, knowledge, personality, arc) for each major character, and
answers continuity questions like "Would Maya realistically do this?"
against that stored profile — feeding the Continuity/Red Team checks.
"""
from typing import Any

from app.agents.base_agent import BaseAgent
from app.core.clickhouse_client import analytics as shared_analytics

PROFILE_INSTRUCTION = (
    "You build a character 'digital twin' profile from screenplay context. "
    "Return ONLY JSON with fields: goals, fears, values, relationships, "
    "secrets, knowledge, personality, character_arc — each a short list "
    "or string as appropriate."
)

CONSISTENCY_INSTRUCTION = (
    "You are a continuity guardian. Given a character's stored profile and "
    "a proposed decision/scene, judge whether the character would "
    "realistically act this way. Return ONLY JSON with fields: "
    "is_consistent (bool), confidence (0-100), explanation."
)


class CharacterTwinAgent(BaseAgent):
    name = "character_twin_agent"
    instruction = PROFILE_INSTRUCTION

    def __init__(self):
        super().__init__()
        self.analytics = shared_analytics

    async def run(self, name: str, context_text: str, project_id: str = "default") -> dict[str, Any]:
        """Create/update a character's digital twin profile from script context."""
        await self.emit("agent_started", {"project_id": project_id, "task": "character_twin", "character": name})

        prompt = f"CHARACTER NAME: {name}\n\nSCRIPT CONTEXT:\n{context_text[:8000]}"
        profile = self.gemini.generate_json(prompt, system_instruction=PROFILE_INSTRUCTION)

        character_id = self.new_run_id()
        self.analytics.insert("characters", {
            "character_id": character_id,
            "project_id": project_id,
            "name": name,
            "profile_json": str(profile),
        })

        await self.emit("agent_completed", {"project_id": project_id, "task": "character_twin", "character": name})
        return {"agent": self.name, "character_id": character_id, "project_id": project_id, "profile": profile}

    async def check_decision(self, name: str, decision_context: str, project_id: str = "default") -> dict[str, Any]:
        """Ask whether a proposed decision is consistent with a stored profile."""
        rows = self.analytics.query("characters", project_id=project_id, limit=200)
        matches = [r for r in rows if r.get("name", "").lower() == name.lower()]
        profile_json = matches[0]["profile_json"] if matches else "{}"

        prompt = f"CHARACTER PROFILE:\n{profile_json}\n\nPROPOSED DECISION/SCENE:\n{decision_context}"
        result = self.gemini.generate_json(prompt, system_instruction=CONSISTENCY_INSTRUCTION)
        return {"agent": self.name, "character": name, "project_id": project_id, "result": result}
