"""
Verifies the two behaviors from the bug report:
1. No key configured -> mock reason says so explicitly.
2. A live call that raises -> the real error is surfaced in the mock
   output (not silently indistinguishable from "no key configured").
"""
import json
from unittest.mock import MagicMock, patch

from app.core.gemini_client import GeminiClient


def test_no_key_configured_reason():
    client = GeminiClient()
    client.enabled = False
    result = json.loads(client.generate("test prompt", json_mode=True))
    assert result["mock"] is True
    assert "GEMINI_API_KEY not set" in result["note"]


def test_live_call_failure_surfaces_real_error():
    client = GeminiClient()
    client.enabled = True  # pretend a key is configured

    with patch("google.genai.Client") as mock_client_cls:
        mock_client_cls.side_effect = RuntimeError("401 Unauthorized: bad API key")
        result = json.loads(client.generate("test prompt", json_mode=True))

    assert result["mock"] is True
    assert "Gemini API error" in result["note"]
    assert "401 Unauthorized" in result["note"]
    # Must NOT be confused with the "no key" case:
    assert "GEMINI_API_KEY not set" not in result["note"]
