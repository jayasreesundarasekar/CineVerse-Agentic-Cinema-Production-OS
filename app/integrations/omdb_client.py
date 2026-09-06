"""OMDb API client — movie metadata/ratings lookup (used by the Forensics agent)."""
import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger("cineverse.omdb")
_settings = get_settings()
BASE_URL = "https://www.omdbapi.com/"


class OMDbClient:
    def __init__(self):
        self.enabled = bool(_settings.omdb_api_key)

    async def lookup(self, title: str) -> dict[str, Any]:
        if not self.enabled:
            return self._mock(title)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(BASE_URL, params={"apikey": _settings.omdb_api_key, "t": title})
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("OMDb request failed, using mock: %s", exc)
            return self._mock(title)

    @staticmethod
    def _mock(title: str) -> dict[str, Any]:
        return {
            "mock": True,
            "Title": title,
            "imdbRating": "7.4",
            "Ratings": [{"Source": "Simulated", "Value": "N/A"}],
            "Note": "OMDB_API_KEY not set — simulated response.",
        }
