"""
Lumia — the AI Co-Director. A conversational front for the whole agent
roster: free-form chat (plain text, not JSON) so it reads like a
production partner rather than a form. Quick actions in the dashboard
call the specialized agents directly; this agent handles the
open-ended "ask Lumia anything" conversation on the Home dashboard.
"""
from typing import Any

from app.agents.base_agent import BaseAgent

SYSTEM_INSTRUCTION = (
    "You are Lumia, the AI Co-Director inside Cineverse — a calm, sharp "
    "production partner for a filmmaker. Answer conversationally in 2-4 "
    "sentences, plain text (no JSON, no markdown headers). If the question "
    "needs a specific agent (screenplay analysis, budget, visuals, red "
    "team, greenlight), say which one you'd run and what it would tell "
    "them, but keep the tone like a trusted collaborator, not a menu."
)


class LumiaAgent(BaseAgent):
    name = "lumia_agent"
    instruction = SYSTEM_INSTRUCTION

    async def run(self, message: str, project_id: str = "default",
                   history: list[dict[str, str]] | None = None) -> dict[str, Any]:
        await self.emit("agent_started", {"project_id": project_id, "task": "lumia_chat"})

        history_block = ""
        if history:
            history_block = "\n".join(f"{h.get('role', 'user')}: {h.get('content', '')}" for h in history[-6:])
            history_block = f"RECENT CONVERSATION:\n{history_block}\n\n"

        prompt = f"{history_block}FILMMAKER'S MESSAGE:\n{message}"
        reply = self.gemini.generate(prompt, system_instruction=SYSTEM_INSTRUCTION)

        await self.emit("agent_completed", {"project_id": project_id, "task": "lumia_chat"})
        return {"agent": self.name, "project_id": project_id, "reply": reply.strip()}
