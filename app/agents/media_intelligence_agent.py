"""
Media Intelligence Agent — pulls demo/media metadata from YouTube
(trailers, reactions, comparable content) to support movie research
and marketing-angle analysis via Gemini.
"""
from typing import Any

from app.agents.base_agent import BaseAgent
from app.integrations.youtube_client import YouTubeClient

SYSTEM_INSTRUCTION = (
    "You are a media intelligence analyst. Given YouTube search results "
    "about a movie/show topic, return ONLY JSON with fields: "
    "audience_buzz_summary, notable_videos (list of titles), and "
    "marketing_angles (list)."
)


class MediaIntelligenceAgent(BaseAgent):
    name = "media_intelligence_agent"
    instruction = SYSTEM_INSTRUCTION

    def __init__(self):
        super().__init__()
        self.youtube = YouTubeClient()

    async def run(self, query: str, project_id: str = "default") -> dict[str, Any]:
        await self.emit("agent_started", {"project_id": project_id, "task": "media_intelligence", "query": query})

        videos = await self.youtube.search_videos(query)
        prompt = f"TOPIC:\n{query}\n\nYOUTUBE RESULTS:\n{videos}"
        analysis = self.gemini.generate_json(prompt, system_instruction=self.instruction)

        await self.emit("agent_completed", {"project_id": project_id, "task": "media_intelligence"})
        return {"agent": self.name, "project_id": project_id, "videos": videos, "analysis": analysis}
