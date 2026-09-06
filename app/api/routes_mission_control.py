"""Mission Control — WebSocket endpoint for real-time agent activity,
plus a REST endpoint for manually publishing an event (used by
external monitors / Grafana webhook alerts)."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.clickhouse_client import analytics
from app.core.websocket_manager import manager

router = APIRouter(tags=["mission-control"])


@router.websocket("/ws/mission-control")
async def mission_control_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Client can send pings / filters; we just keep the socket alive.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/mission-control/publish")
async def publish_event(project_id: str, agent_name: str, event_type: str, payload: str = ""):
    event_id = analytics.insert("mission_control_events", {
        "project_id": project_id,
        "agent_name": agent_name,
        "event_type": event_type,
        "payload": payload,
    })
    await manager.broadcast(event_type, {"project_id": project_id, "agent": agent_name, "payload": payload})
    return {"event_id": event_id, "status": "published"}
