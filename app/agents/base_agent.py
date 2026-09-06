"""
Base class for all Cineverse specialized agents.

Designed to map cleanly onto Google Cloud Agent Builder / Agent Engine
concepts: each agent has a name, an instruction/persona, and a run()
method that can be registered as a remote Agent Engine reasoning
engine in production. Locally, run() calls Gemini directly through
GeminiClient so the whole pipeline works without deploying to Agent
Engine first.
"""
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any

from app.core.gemini_client import GeminiClient
from app.core.websocket_manager import manager


class BaseAgent(ABC):
    name: str = "base_agent"
    instruction: str = "You are a helpful agent."

    def __init__(self):
        self.gemini = GeminiClient()

    @abstractmethod
    async def run(self, **kwargs) -> dict[str, Any]:
        """Execute the agent's task and return a structured result."""

    async def emit(self, event_type: str, payload: dict[str, Any]):
        """Push a Mission Control event over the WebSocket for this agent."""
        await manager.broadcast(event_type, {
            "agent": self.name,
            "timestamp": time.time(),
            **payload,
        })

    @staticmethod
    def new_run_id() -> str:
        return uuid.uuid4().hex
