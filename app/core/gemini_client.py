"""
Wrapper around the Google Gemini API using the current `google-genai`
SDK (the old `google-generativeai` package reached end-of-life and
receives no more fixes — see requirements.txt). This is the single
core-AI entry point used by every agent for:
 - story reasoning / screenplay analysis
 - simulation narration
 - structured (JSON) extraction

Falls back to a clearly-labeled mock response when no GEMINI_API_KEY
is configured, OR when a live call fails for any reason — but unlike
the previous version, the actual error is surfaced in the mock output
and logged at ERROR level, so a bad key, a retired model, or a rate
limit doesn't get silently mistaken for "no key configured."
"""
import json
import logging
from typing import Any, Optional

from app.config import get_settings

logger = logging.getLogger("cineverse.gemini")
_settings = get_settings()


class GeminiClient:
    def __init__(self, model: Optional[str] = None):
        self.model_name = model or _settings.gemini_model
        self.enabled = bool(_settings.gemini_api_key)

    def generate(self, prompt: str, system_instruction: Optional[str] = None,
                 json_mode: bool = False) -> str:
        """Generate free-form or JSON text from Gemini."""
        if not self.enabled:
            return self._mock(prompt, json_mode, reason="GEMINI_API_KEY not set")

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=_settings.gemini_api_key)
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json" if json_mode else None,
            )
            response = client.models.generate_content(
                model=self.model_name, contents=prompt, config=config,
            )
            if not response.text:
                raise RuntimeError(f"Empty response from {self.model_name} (check finish_reason/safety blocks)")
            return response.text
        except Exception as exc:  # noqa: BLE001
            # Surfaced (not just logged) so a real API failure — bad key,
            # retired model ID, 429, safety block — is visible in the
            # response itself instead of looking identical to mock mode.
            logger.error("Gemini call to model '%s' failed: %s", self.model_name, exc, exc_info=True)
            return self._mock(prompt, json_mode, reason=f"Gemini API error: {exc}")

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> dict[str, Any]:
        raw = self.generate(prompt, system_instruction=system_instruction, json_mode=True)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            start, end = raw.find("{"), raw.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(raw[start:end + 1])
                except json.JSONDecodeError:
                    pass
            return {"raw_text": raw}

    @staticmethod
    def _mock(prompt: str, json_mode: bool, reason: str) -> str:
        snippet = prompt.strip().replace("\n", " ")[:160]
        if json_mode:
            return json.dumps({
                "mock": True,
                "note": f"{reason} — returning simulated reasoning.",
                "prompt_preview": snippet,
                "analysis": "Simulated structural analysis: three-act balance, "
                             "protagonist agency steady, midpoint reversal detected.",
            })
        return f"[MOCK GEMINI RESPONSE] ({reason}) — reasoning over: '{snippet}...'"
