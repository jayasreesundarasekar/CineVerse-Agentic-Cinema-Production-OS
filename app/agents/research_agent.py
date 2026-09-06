"""
Research Agent — grounds screenplay/production claims in real-world
facts using the Parallel API/MCP for web research, then has Gemini
synthesize the findings into a fact-check style report.
"""
from typing import Any

from app.agents.base_agent import BaseAgent
from app.integrations.parallel_client import ParallelClient

SYSTEM_INSTRUCTION = (
    "You are a factual research and fact-checking agent for film/TV "
    "production. Given research findings, synthesize ONLY JSON with "
    "fields: summary, verified_claims (list), unverified_claims (list), "
    "and recommended_revisions (list)."
)


class ResearchAgent(BaseAgent):
    name = "research_agent"
    instruction = SYSTEM_INSTRUCTION

    def __init__(self):
        super().__init__()
        self.parallel = ParallelClient()

    async def run(self, query: str, project_id: str = "default") -> dict[str, Any]:
        await self.emit("agent_started", {"project_id": project_id, "task": "research", "query": query})

        findings = await self.parallel.research(query)
        prompt = f"RESEARCH QUERY:\n{query}\n\nRAW FINDINGS:\n{findings}"
        synthesis = self.gemini.generate_json(prompt, system_instruction=self.instruction)

        await self.emit("agent_completed", {"project_id": project_id, "task": "research"})
        return {"agent": self.name, "project_id": project_id, "raw_findings": findings, "synthesis": synthesis}
