"""Pydantic request/response schemas shared across API routes."""
from typing import Any, Optional

from pydantic import BaseModel


class ScreenplayAnalysisRequest(BaseModel):
    project_id: str = "default"
    script_text: str


class SimulationRequest(BaseModel):
    project_id: str = "default"
    premise: str
    scenario: str


class ResearchRequest(BaseModel):
    project_id: str = "default"
    query: str


class ForensicsRequest(BaseModel):
    project_id: str = "default"
    comparable_title: str
    script_summary: str


class MediaIntelligenceRequest(BaseModel):
    project_id: str = "default"
    query: str


class FullPipelineRequest(BaseModel):
    project_id: str = "default"
    script_title: str
    script_text: str


class AgentResponse(BaseModel):
    agent: str
    project_id: str
    data: dict[str, Any]


class UploadResponse(BaseModel):
    filename: str
    storage_uri: str
    size_bytes: int


class AnalyticsQuery(BaseModel):
    table: str
    project_id: Optional[str] = None
    limit: int = 100


# ---- CREATE module ----

class StoryboardRequest(BaseModel):
    project_id: str = "default"
    scene_text: str
    visual_references: Optional[list[str]] = None


class VisualDNARequest(BaseModel):
    project_id: str = "default"
    script_text: str


class VisualGenerateRequest(BaseModel):
    project_id: str = "default"
    prompt: str
    generate_type: str = "scene"  # location | character | scene | moodboard | world | shot
    count: int = 4


class ScenePackageRequest(BaseModel):
    project_id: str = "default"
    script_text: str
    scene_text: str
    generate_type: str = "scene"
    count: int = 4
    prompt_override: str = ""


class CharacterTwinRequest(BaseModel):
    project_id: str = "default"
    name: str
    context_text: str


class CharacterConsistencyRequest(BaseModel):
    project_id: str = "default"
    name: str
    decision_context: str


# ---- SIMULATE module ----

class ScenarioLabRequest(BaseModel):
    project_id: str = "default"
    baseline_summary: str
    what_if: str
    parent_universe_id: str = ""
    register_as_universe: bool = True
    title: str = ""


# ---- ANALYZE module ----

class AudienceRequest(BaseModel):
    project_id: str = "default"
    universe_id: str = ""
    story_summary: str
    segments: Optional[list[str]] = None


class RedTeamRequest(BaseModel):
    project_id: str = "default"
    universe_id: str = ""
    context_bundle: str


# ---- PRODUCE module ----

class BudgetRequest(BaseModel):
    project_id: str = "default"
    universe_id: str = ""
    line_items: dict[str, float]
    change_request: str


# ---- DECIDE module ----

class GreenlightPipelineRequest(BaseModel):
    project_id: str = "default"
    universe_id: str = ""
    title: str
    universe_summary: str
    line_items: Optional[dict[str, float]] = None


class ExecutiveDecisionRequest(BaseModel):
    project_id: str = "default"
    universe_id: str = ""
    source_run_ids: list[str] = []
    score_bundle: dict[str, Any] = {}


class LumiaChatRequest(BaseModel):
    project_id: str = "default"
    message: str
    history: Optional[list[dict[str, str]]] = None
