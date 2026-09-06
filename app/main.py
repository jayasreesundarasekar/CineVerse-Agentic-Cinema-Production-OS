"""
Cineverse — Multi-Agent Screenplay & Production Intelligence Platform
FastAPI entrypoint: mounts all routers and configures CORS/logging.

Run with:
    uvicorn app.main:app --reload --port 8000
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    routes_agents,
    routes_analytics,
    routes_lumia,
    routes_mission_control,
    routes_studio,
    routes_upload,
)
from app.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

settings = get_settings()

app = FastAPI(
    title="Cineverse API",
    description=(
        "Multi-agent screenplay reasoning, simulation, research, and "
        "forensics platform. Backed by Gemini, Agent Builder/Agent Engine, "
        "GCS, and ClickHouse; monitored via Grafana Mission Control."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_upload.router)
app.include_router(routes_agents.router)
app.include_router(routes_studio.router)
app.include_router(routes_lumia.router)
app.include_router(routes_analytics.router)
app.include_router(routes_mission_control.router)


@app.get("/", tags=["health"])
async def root():
    return {
        "service": "Cineverse API",
        "status": "ok",
        "mock_mode": settings.mock_mode,
    }


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy"}
