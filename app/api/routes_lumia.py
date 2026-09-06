"""Lumia — the AI Co-Director chat endpoint used by the Home dashboard."""
from fastapi import APIRouter

from app.agents.orchestrator import orchestrator
from app.models.schemas import LumiaChatRequest

router = APIRouter(prefix="/lumia", tags=["lumia"])


@router.post("/chat")
async def lumia_chat(req: LumiaChatRequest):
    return await orchestrator.route(
        "lumia", message=req.message, project_id=req.project_id, history=req.history
    )
