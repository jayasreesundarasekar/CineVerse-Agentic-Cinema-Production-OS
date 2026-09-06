"""
WebSocket connection manager for real-time Mission Control updates.
Broadcasts agent activity, simulation progress, and analytics events
to all connected dashboard clients.
"""
import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("cineverse.ws")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket connected. Total: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("WebSocket disconnected. Total: %d", len(self.active_connections))

    async def broadcast(self, event_type: str, payload: dict[str, Any]):
        message = json.dumps({"type": event_type, "payload": payload})
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:  # noqa: BLE001
                dead.append(connection)
        for connection in dead:
            self.disconnect(connection)


manager = ConnectionManager()
