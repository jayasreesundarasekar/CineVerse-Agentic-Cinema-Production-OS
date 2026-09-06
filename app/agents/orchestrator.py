"""
Agent Orchestrator — the local stand-in for Google Cloud Agent Builder /
Agent Engine's orchestration layer.

In production, each specialized agent below can be deployed as its own
Agent Engine reasoning engine (or Agent Builder agent) and this class's
`route()`/`run_pipeline()` methods become calls to the deployed Agent
Engine endpoints (via the `agent_engine_id` in Settings) instead of the
in-process classes. Keeping the interface identical means swapping in
real Agent Engine calls later requires no changes to API routes.
"""
from typing import Any

from app.agents.audience_agent import AudienceAgent
from app.agents.budget_agent import BudgetAgent
from app.agents.character_twin_agent import CharacterTwinAgent
from app.agents.executive_agent import ExecutiveAgent
from app.agents.forensics_agent import ForensicsAgent
from app.agents.lumia_agent import LumiaAgent
from app.agents.media_intelligence_agent import MediaIntelligenceAgent
from app.agents.red_team_agent import RedTeamAgent
from app.agents.research_agent import ResearchAgent
from app.agents.scenario_lab_agent import ScenarioLabAgent
from app.agents.screenplay_agent import ScreenplayAgent
from app.agents.simulation_agent import SimulationAgent
from app.agents.storyboard_agent import StoryboardAgent
from app.agents.visual_universe_agent import VisualUniverseAgent
from app.config import get_settings

_settings = get_settings()


class AgentOrchestrator:
    """Routes work to specialized agents and can chain them into pipelines.

    Module map (matches the CREATE / SIMULATE / ANALYZE / PRODUCE / DECIDE /
    CONTROL product structure):
      CREATE   -> screenplay, storyboard, character_twin, visual_universe
      SIMULATE -> simulation, scenario_lab
      ANALYZE  -> research, forensics, audience, red_team
      PRODUCE  -> budget
      DECIDE   -> executive (greenlight + decision provenance)
      CONTROL  -> Mission Control (WebSocket, not an agent)
    """

    def __init__(self):
        self.agents = {
            "screenplay": ScreenplayAgent(),
            "simulation": SimulationAgent(),
            "research": ResearchAgent(),
            "forensics": ForensicsAgent(),
            "media_intelligence": MediaIntelligenceAgent(),
            "storyboard": StoryboardAgent(),
            "character_twin": CharacterTwinAgent(),
            "budget": BudgetAgent(),
            "audience": AudienceAgent(),
            "scenario_lab": ScenarioLabAgent(),
            "red_team": RedTeamAgent(),
            "executive": ExecutiveAgent(),
            "visual_universe": VisualUniverseAgent(),
            "lumia": LumiaAgent(),
        }
        # In production this points at a deployed Agent Engine resource.
        self.agent_engine_id = _settings.agent_engine_id or None

    def available_agents(self) -> list[str]:
        return list(self.agents.keys())

    async def route(self, agent_key: str, **kwargs) -> dict[str, Any]:
        if agent_key not in self.agents:
            raise ValueError(f"Unknown agent '{agent_key}'. Available: {self.available_agents()}")
        return await self.agents[agent_key].run(**kwargs)

    async def run_full_pipeline(self, script_text: str, script_title: str, project_id: str) -> dict[str, Any]:
        """
        End-to-end multi-agent pipeline used by the /pipeline/full endpoint:
        screenplay analysis -> research grounding -> forensics comparison
        -> a baseline audience-reaction simulation.
        """
        screenplay_result = await self.route("screenplay", script_text=script_text, project_id=project_id)

        research_result = await self.route(
            "research",
            query=f"Fact-check key claims and setting details in the screenplay '{script_title}'",
            project_id=project_id,
        )

        forensics_result = await self.route(
            "forensics",
            comparable_title=script_title,
            script_summary=script_text[:2000],
            project_id=project_id,
        )

        simulation_result = await self.route(
            "simulation",
            premise=script_text[:2000],
            scenario="Baseline theatrical release, general audience",
            project_id=project_id,
        )

        return {
            "project_id": project_id,
            "screenplay": screenplay_result,
            "research": research_result,
            "forensics": forensics_result,
            "simulation": simulation_result,
        }

    async def check_character_consistency(self, name: str, decision_context: str,
                                            project_id: str = "default") -> dict[str, Any]:
        """CharacterTwinAgent has a second method beyond run() — expose it explicitly."""
        agent: CharacterTwinAgent = self.agents["character_twin"]  # type: ignore[assignment]
        return await agent.check_decision(name, decision_context, project_id=project_id)

    async def generate_visuals(self, prompt: str, generate_type: str = "scene",
                                count: int = 4, project_id: str = "default") -> dict[str, Any]:
        """VisualUniverseAgent's image-generation entry point (run() only does DNA extraction)."""
        agent: VisualUniverseAgent = self.agents["visual_universe"]  # type: ignore[assignment]
        return await agent.generate_visuals(prompt, generate_type=generate_type, count=count, project_id=project_id)

    async def run_scene_to_shots_pipeline(self, script_text: str, scene_text: str,
                                           project_id: str = "default", generate_type: str = "scene",
                                           count: int = 4, prompt_override: str = "") -> dict[str, Any]:
        """
        Full CREATE-module pipeline: Story -> Scene -> Visuals -> Shots.
        1. Extract visual DNA from the full script (locations, mood, color/
           lighting direction, genre, motifs, props, environmental detail).
        2. Generate 1-4 reference visuals for the chosen category using the
           DNA's suggested prompt (or a user-supplied override).
        3. Feed the scene text + generated-visual variant labels into the
           AI Shot Designer to produce the cinematography shot list.
        """
        visual_universe: VisualUniverseAgent = self.agents["visual_universe"]  # type: ignore[assignment]
        dna_result = await visual_universe.extract_visual_dna(script_text=script_text, project_id=project_id)
        visual_dna = dna_result["visual_dna"]

        prompt = prompt_override or visual_dna.get("suggested_prompt") or scene_text[:300]
        visuals_result = await visual_universe.generate_visuals(
            prompt=prompt, generate_type=generate_type, count=count, project_id=project_id
        )
        visual_variant_labels = [img["variant"] for img in visuals_result["images"]]

        shots_result = await self.route(
            "storyboard", scene_text=scene_text, project_id=project_id,
            visual_references=visual_variant_labels,
        )

        return {
            "project_id": project_id,
            "visual_dna": dna_result,
            "visuals": visuals_result,
            "shots": shots_result,
        }

    async def run_greenlight_pipeline(self, universe_summary: str, title: str,
                                       project_id: str, universe_id: str = "",
                                       line_items: dict[str, float] | None = None) -> dict[str, Any]:
        """
        DECIDE-module convenience pipeline: runs Audience, Budget, and Red
        Team against a universe/story summary, then has the Executive agent
        weigh all of it into a greenlight verdict with decision provenance.
        """
        audience_result = await self.route(
            "audience", story_summary=universe_summary, project_id=project_id, universe_id=universe_id
        )
        budget_result = await self.route(
            "budget",
            line_items=line_items or {"actors": 2500000, "locations": 800000, "vfx": 1500000,
                                       "crew": 1200000, "shooting": 2000000, "marketing": 3000000},
            change_request="Baseline budget for greenlight review — no change requested.",
            project_id=project_id, universe_id=universe_id,
        )
        red_team_context = (
            f"TITLE: {title}\nSUMMARY: {universe_summary}\n"
            f"AUDIENCE FINDINGS: {audience_result['result']}\nBUDGET FINDINGS: {budget_result['result']}"
        )
        red_team_result = await self.route(
            "red_team", context_bundle=red_team_context, project_id=project_id, universe_id=universe_id
        )

        score_bundle = {
            "audience": audience_result["result"],
            "budget": budget_result["result"],
            "red_team": red_team_result["result"],
        }
        source_run_ids = [
            audience_result.get("agent", ""), budget_result.get("budget_id", ""),
            red_team_result.get("agent", ""),
        ]
        executive_result = await self.route(
            "executive", project_id=project_id, universe_id=universe_id,
            source_run_ids=source_run_ids, score_bundle=score_bundle,
        )

        return {
            "project_id": project_id,
            "universe_id": universe_id,
            "audience": audience_result,
            "budget": budget_result,
            "red_team": red_team_result,
            "executive_decision": executive_result,
        }


orchestrator = AgentOrchestrator()
