"""
Gemini image-generation wrapper — used by the Visual Universe Generator.
Uses the current `google-genai` SDK's image-output mode (the
"Nano Banana" family, e.g. gemini-3.1-flash-image) rather than a
separate image API, so the "only use specified APIs" constraint holds:
this is still the Google Gemini API, just its image-output mode.

Falls back to a labeled placeholder SVG per variant — with the real
error message attached — when no GEMINI_API_KEY is configured or the
image call fails, so the Visual Universe pipeline (extract DNA ->
generate visuals -> shot design) still runs end-to-end in mock mode
and a real failure is never mistaken for "no key configured."
"""
import logging
from dataclasses import dataclass

from app.config import get_settings

logger = logging.getLogger("cineverse.gemini_image")
_settings = get_settings()


@dataclass
class GeneratedImage:
    variant: str
    mime_type: str
    data: bytes
    mock: bool


class GeminiImageClient:
    def __init__(self):
        self.enabled = bool(_settings.gemini_api_key)
        self.model_name = _settings.gemini_image_model

    def generate_images(self, base_prompt: str, variants: list[str]) -> list[GeneratedImage]:
        return [self._generate_one(f"{base_prompt} — {variant}.", variant) for variant in variants]

    def _generate_one(self, prompt: str, variant: str) -> GeneratedImage:
        if not self.enabled:
            return self._mock_placeholder(prompt, variant, reason="GEMINI_API_KEY not set")

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=_settings.gemini_api_key)
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
            )
            for part in response.parts:
                inline_data = getattr(part, "inline_data", None)
                if inline_data and getattr(inline_data, "data", None):
                    return GeneratedImage(
                        variant=variant,
                        mime_type=inline_data.mime_type or "image/png",
                        data=inline_data.data,
                        mock=False,
                    )
            raise RuntimeError(f"No inline image data in response (model may have refused/blocked the prompt)")
        except Exception as exc:  # noqa: BLE001
            logger.error("Gemini image generation ('%s', model '%s') failed: %s", variant, self.model_name, exc, exc_info=True)
            return self._mock_placeholder(prompt, variant, reason=f"Gemini image API error: {exc}")

    @staticmethod
    def _mock_placeholder(prompt: str, variant: str, reason: str) -> GeneratedImage:
        safe_prompt = (prompt[:140] + "...") if len(prompt) > 140 else prompt
        safe_reason = reason.replace("<", "&lt;").replace(">", "&gt;")[:200]
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="768" height="432">
  <rect width="100%" height="100%" fill="#1a1a2e"/>
  <text x="24" y="48" fill="#e94560" font-size="22" font-family="sans-serif">[MOCK VISUAL] {variant}</text>
  <text x="24" y="80" fill="#eeeeee" font-size="13" font-family="sans-serif">{safe_reason}</text>
  <text x="24" y="110" fill="#aaaaaa" font-size="13" font-family="sans-serif">
    <tspan x="24" dy="0">Prompt:</tspan>
    <tspan x="24" dy="20">{safe_prompt}</tspan>
  </text>
</svg>'''
        return GeneratedImage(variant=variant, mime_type="image/svg+xml", data=svg.encode("utf-8"), mock=True)
