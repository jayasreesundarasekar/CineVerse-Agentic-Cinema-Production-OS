"""
Studio module routes — organizes the extended feature set into the
6 product modules: CREATE, SIMULATE, ANALYZE, PRODUCE, DECIDE, CONTROL
(CONTROL is Mission Control, already served by routes_mission_control.py).
"""
from fastapi import APIRouter

from app.agents.orchestrator import orchestrator
from app.core.clickhouse_client import analytics
from app.core.multiverse import build_tree
from app.models.schemas import (
    AudienceRequest,
    BudgetRequest,
    CharacterConsistencyRequest,
    CharacterTwinRequest,
    ExecutiveDecisionRequest,
    GreenlightPipelineRequest,
    RedTeamRequest,
    ScenarioLabRequest,
    ScenePackageRequest,
    StoryboardRequest,
    VisualDNARequest,
    VisualGenerateRequest,
)

router = APIRouter(tags=["studio"])

# ---------------- CREATE ----------------

@router.post("/create/storyboard")
async def create_storyboard(req: StoryboardRequest):
    return await orchestrator.route(
        "storyboard", scene_text=req.scene_text, project_id=req.project_id,
        visual_references=req.visual_references,
    )


@router.post("/create/visual-universe/extract-dna")
async def extract_visual_dna(req: VisualDNARequest):
    """Reads a screenplay and extracts its visual DNA: locations, time
    period, weather, architecture, mood, color/lighting direction,
    genre, visual motifs, important props, environmental details."""
    return await orchestrator.route("visual_universe", script_text=req.script_text, project_id=req.project_id)


@router.post("/create/visual-universe/generate")
async def generate_visuals(req: VisualGenerateRequest):
    """GENERATE VISUALS — produces 1-4 images for a category
    (location/character/scene/moodboard/world/shot), saved to GCS."""
    return await orchestrator.generate_visuals(
        prompt=req.prompt, generate_type=req.generate_type, count=req.count, project_id=req.project_id,
    )


@router.get("/create/visual-universe/history")
async def list_visual_generations(project_id: str | None = None, limit: int = 100):
    return {"rows": analytics.query("visual_generations", project_id=project_id, limit=limit)}


@router.post("/create/scene-package")
async def create_scene_package(req: ScenePackageRequest):
    """Full pipeline: Story -> Scene -> Visuals -> Shots. Extracts visual
    DNA from the script, generates reference visuals, then feeds both the
    scene and the visuals into the AI Shot Designer for a shot list."""
    return await orchestrator.run_scene_to_shots_pipeline(
        script_text=req.script_text, scene_text=req.scene_text, project_id=req.project_id,
        generate_type=req.generate_type, count=req.count, prompt_override=req.prompt_override,
    )


@router.post("/create/character-twin")
async def create_character_twin(req: CharacterTwinRequest):
    return await orchestrator.route(
        "character_twin", name=req.name, context_text=req.context_text, project_id=req.project_id
    )


@router.post("/create/character-twin/check")
async def check_character_twin(req: CharacterConsistencyRequest):
    return await orchestrator.check_character_consistency(
        name=req.name, decision_context=req.decision_context, project_id=req.project_id
    )


@router.get("/create/characters")
async def list_characters(project_id: str | None = None, limit: int = 100):
    return {"rows": analytics.query("characters", project_id=project_id, limit=limit)}


# ---------------- SIMULATE ----------------

@router.post("/simulate/scenario-lab")
async def run_scenario_lab(req: ScenarioLabRequest):
    return await orchestrator.route(
        "scenario_lab",
        baseline_summary=req.baseline_summary,
        what_if=req.what_if,
        project_id=req.project_id,
        parent_universe_id=req.parent_universe_id,
        register_as_universe=req.register_as_universe,
        title=req.title,
    )


@router.get("/simulate/multiverse")
async def get_multiverse_tree(project_id: str = "default"):
    """Returns the Cinema Multiverse branching tree for a project."""
    return build_tree(project_id, analytics=analytics)


@router.get("/simulate/universes")
async def list_universes(project_id: str | None = None, limit: int = 100):
    return {"rows": analytics.query("universes", project_id=project_id, limit=limit)}


# ---------------- ANALYZE ----------------

@router.post("/analyze/audience")
async def run_audience_simulation(req: AudienceRequest):
    return await orchestrator.route(
        "audience", story_summary=req.story_summary, segments=req.segments,
        project_id=req.project_id, universe_id=req.universe_id,
    )


@router.post("/analyze/red-team")
async def run_red_team(req: RedTeamRequest):
    return await orchestrator.route(
        "red_team", context_bundle=req.context_bundle,
        project_id=req.project_id, universe_id=req.universe_id,
    )


@router.get("/analyze/red-team/findings")
async def list_red_team_findings(project_id: str | None = None, limit: int = 100):
    return {"rows": analytics.query("red_team_findings", project_id=project_id, limit=limit)}


@router.get("/analyze/audience-projections")
async def list_audience_projections(project_id: str | None = None, limit: int = 100):
    return {"rows": analytics.query("audience_projections", project_id=project_id, limit=limit)}


# ---------------- PRODUCE ----------------

@router.post("/produce/budget")
async def run_budget_simulation(req: BudgetRequest):
    return await orchestrator.route(
        "budget", line_items=req.line_items, change_request=req.change_request,
        project_id=req.project_id, universe_id=req.universe_id,
    )


@router.get("/produce/budgets")
async def list_budgets(project_id: str | None = None, limit: int = 100):
    return {"rows": analytics.query("budgets", project_id=project_id, limit=limit)}


# ---------------- DECIDE ----------------

@router.post("/decide/greenlight")
async def run_greenlight_pipeline(req: GreenlightPipelineRequest):
    """Chains Audience + Budget + Red Team -> Executive verdict with provenance."""
    return await orchestrator.run_greenlight_pipeline(
        universe_summary=req.universe_summary, title=req.title, project_id=req.project_id,
        universe_id=req.universe_id, line_items=req.line_items,
    )


@router.post("/decide/executive")
async def run_executive_decision(req: ExecutiveDecisionRequest):
    """Direct call to the Executive agent if you already have your own score bundle."""
    return await orchestrator.route(
        "executive", project_id=req.project_id, universe_id=req.universe_id,
        source_run_ids=req.source_run_ids, score_bundle=req.score_bundle,
    )


@router.get("/decide/decisions")
async def list_decisions(project_id: str | None = None, limit: int = 100):
    """Decision Provenance log — every greenlight verdict with its reasoning trace."""
    return {"rows": analytics.query("decisions", project_id=project_id, limit=limit)}
