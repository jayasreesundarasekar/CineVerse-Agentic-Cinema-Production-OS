"""
Movie Forensics Agent — cross-references a title against TMDB and OMDb
metadata/ratings, then has Gemini reason about similarities, tropes,
or continuity/plagiarism-risk flags relative to the uploaded script.
"""
from typing import Any

from app.agents.base_agent import BaseAgent
from app.integrations.omdb_client import OMDbClient
from app.integrations.tmdb_client import TMDBClient

SYSTEM_INSTRUCTION = (
    "You are a movie forensics analyst. Given TMDB/OMDb metadata for "
    "comparable titles and a description of a new script, return ONLY "
    "JSON with fields: comparable_titles (list), shared_tropes (list), "
    "originality_score (0-100), and notes."
)


class ForensicsAgent(BaseAgent):
    name = "forensics_agent"
    instruction = SYSTEM_INSTRUCTION

    def __init__(self):
        super().__init__()
        self.tmdb = TMDBClient()
        self.omdb = OMDbClient()

    async def run(self, comparable_title: str, script_summary: str, project_id: str = "default") -> dict[str, Any]:
        await self.emit("agent_started", {"project_id": project_id, "task": "forensics", "title": comparable_title})

        tmdb_data = await self.tmdb.search_movie(comparable_title)
        omdb_data = await self.omdb.lookup(comparable_title)

        prompt = (
            f"SCRIPT SUMMARY:\n{script_summary}\n\n"
            f"TMDB METADATA:\n{tmdb_data}\n\nOMDB METADATA:\n{omdb_data}"
        )
        analysis = self.gemini.generate_json(prompt, system_instruction=self.instruction)

        await self.emit("agent_completed", {"project_id": project_id, "task": "forensics"})
        return {
            "agent": self.name,
            "project_id": project_id,
            "tmdb": tmdb_data,
            "omdb": omdb_data,
            "analysis": analysis,
        }
