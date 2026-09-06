"""TMDB API client — movie metadata, genres, cast, release info (used by Movie Forensics agent)."""
import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger("cineverse.tmdb")
_settings = get_settings()
BASE_URL = "https://api.themoviedb.org/3"


class TMDBClient:
    def __init__(self):
        self.enabled = bool(_settings.tmdb_api_key)

    async def search_movie(self, title: str) -> dict[str, Any]:
        if not self.enabled:
            return self._mock(title)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{BASE_URL}/search/movie",
                    params={"api_key": _settings.tmdb_api_key, "query": title},
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("TMDB request failed, using mock: %s", exc)
            return self._mock(title)

    @staticmethod
    def _mock(title: str) -> dict[str, Any]:
        return {
            "mock": True,
            "results": [{
                "title": title,
                "genre_ids": [18, 878],
                "release_date": "2024-01-01",
                "overview": f"Simulated TMDB metadata for '{title}' (TMDB_API_KEY not set).",
            }],
        }
