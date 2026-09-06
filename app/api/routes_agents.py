"""Routes exposing each specialized agent individually, plus the full
multi-agent pipeline via the orchestrator."""
from fastapi import APIRouter

from app.agents.orchestrator import orchestrator
from app.models.schemas import (
    ForensicsRequest,
    FullPipelineRequest,
    MediaIntelligenceRequest,
    ResearchRequest,
    ScreenplayAnalysisRequest,
    SimulationRequest,
)

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/")
async def list_agents():
    return {"available_agents": orchestrator.available_agents()}


@router.post("/screenplay/analyze")
async def analyze_screenplay(req: ScreenplayAnalysisRequest):
    return await orchestrator.route("screenplay", script_text=req.script_text, project_id=req.project_id)


@router.post("/simulation/run")
async def run_simulation(req: SimulationRequest):
    return await orchestrator.route(
        "simulation", premise=req.premise, scenario=req.scenario, project_id=req.project_id
    )


@router.post("/research/run")
async def run_research(req: ResearchRequest):
    return await orchestrator.route("research", query=req.query, project_id=req.project_id)


@router.post("/forensics/run")
async def run_forensics(req: ForensicsRequest):
    return await orchestrator.route(
        "forensics",
        comparable_title=req.comparable_title,
        script_summary=req.script_summary,
        project_id=req.project_id,
    )


@router.post("/media-intelligence/run")
async def run_media_intelligence(req: MediaIntelligenceRequest):
    return await orchestrator.route("media_intelligence", query=req.query, project_id=req.project_id)


@router.post("/pipeline/full")
async def run_full_pipeline(req: FullPipelineRequest):
    return await orchestrator.run_full_pipeline(
        script_text=req.script_text, script_title=req.script_title, project_id=req.project_id
    )
