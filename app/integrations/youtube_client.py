"""YouTube Data API client — demo/media metadata and movie research (Media Intelligence agent)."""
import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger("cineverse.youtube")
_settings = get_settings()
BASE_URL = "https://www.googleapis.com/youtube/v3"


class YouTubeClient:
    def __init__(self):
        self.enabled = bool(_settings.youtube_api_key)

    async def search_videos(self, query: str, max_results: int = 5) -> dict[str, Any]:
        if not self.enabled:
            return self._mock(query)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{BASE_URL}/search",
                    params={
                        "key": _settings.youtube_api_key,
                        "q": query,
                        "part": "snippet",
                        "maxResults": max_results,
                        "type": "video",
                    },
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("YouTube request failed, using mock: %s", exc)
            return self._mock(query)

    @staticmethod
    def _mock(query: str) -> dict[str, Any]:
        return {
            "mock": True,
            "items": [{
                "id": {"videoId": "mock_video_id"},
                "snippet": {
                    "title": f"Simulated result for '{query}'",
                    "description": "YOUTUBE_API_KEY not set — simulated response.",
                },
            }],
        }
