"""
Parallel API / MCP client — web research and factual information retrieval,
used by the Research Agent to ground screenplay/production claims in
real-world facts (locations, historical accuracy, factual continuity).
"""
import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger("cineverse.parallel")
_settings = get_settings()
BASE_URL = "https://api.parallel.ai/v1"


class ParallelClient:
    def __init__(self):
        self.enabled = bool(_settings.parallel_api_key)

    async def research(self, query: str) -> dict[str, Any]:
        """Run a web research task via the Parallel Task API (or MCP endpoint)."""
        if not self.enabled:
            return self._mock(query)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{BASE_URL}/tasks/runs",
                    headers={"x-api-key": _settings.parallel_api_key},
                    json={"input": query, "processor": "base"},
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Parallel API request failed, using mock: %s", exc)
            return self._mock(query)

    @staticmethod
    def _mock(query: str) -> dict[str, Any]:
        return {
            "mock": True,
            "query": query,
            "findings": [
                f"Simulated research finding relevant to: '{query}'.",
                "PARALLEL_API_KEY not set — replace with live research results.",
            ],
            "sources": [],
        }
