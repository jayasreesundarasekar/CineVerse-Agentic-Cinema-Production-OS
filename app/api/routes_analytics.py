"""Multiverse analytics routes — query ClickHouse-backed simulation runs,
screenplay scores, and Mission Control events."""
from fastapi import APIRouter

from app.core.clickhouse_client import analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/simulation-runs")
async def get_simulation_runs(project_id: str | None = None, limit: int = 100):
    return {"rows": analytics.query("simulation_runs", project_id=project_id, limit=limit)}


@router.get("/screenplay-scores")
async def get_screenplay_scores(project_id: str | None = None, limit: int = 100):
    return {"rows": analytics.query("screenplay_scores", project_id=project_id, limit=limit)}


@router.get("/mission-control-events")
async def get_mission_control_events(project_id: str | None = None, limit: int = 100):
    return {"rows": analytics.query("mission_control_events", project_id=project_id, limit=limit)}


@router.get("/backend-status")
async def backend_status():
    return {"clickhouse_connected": analytics.enabled}
