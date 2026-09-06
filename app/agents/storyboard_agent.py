"""
Storyboard / AI Shot Designer Agent (CREATE module).
Turns a greenlit scene or full script into a production-ready
cinematography plan: shot type, lens (mm), camera movement, camera
height/angle, duration, location, cast, props, VFX, lighting, and
estimated shooting time. The generated plan is also saved to GCS as a
JSON artifact.

Pipeline position: Story -> Scene -> Visuals (VisualUniverseAgent) ->
Shots (this agent). See AgentOrchestrator.run_scene_to_shots_pipeline().
"""
from typing import Any

from app.agents.base_agent import BaseAgent
from app.core.gcs_storage import GCSStorage

SYSTEM_INSTRUCTION = (
    "You are an AI Shot Designer — a professional 1st AD / cinematographer "
    "building a shot list. Given scene text (and optionally reference "
    "visual descriptions), produce ONLY JSON with a 'shots' list. Each "
    "shot has: scene_number, shot_id, description, shot_type (e.g. "
    "wide/medium/close-up/OTS/insert), lens_mm (e.g. 24, 35, 50, 85), "
    "camera_movement (e.g. static, slow push-in, handheld, dolly, pan), "
    "camera_height_angle (e.g. low angle, eye level, high angle, "
    "bird's-eye), duration_seconds, location, characters (list), "
    "props (list), vfx_requirements (list), lighting_notes, and "
    "estimated_setup_minutes. Also include a top-level "
    "'total_estimated_shoot_hours' field."
)


class StoryboardAgent(BaseAgent):
    name = "storyboard_agent"
    instruction = SYSTEM_INSTRUCTION

    def __init__(self):
        super().__init__()
        self.storage = GCSStorage()

    async def run(self, scene_text: str, project_id: str = "default",
                   visual_references: list[str] | None = None) -> dict[str, Any]:
        await self.emit("agent_started", {"project_id": project_id, "task": "shot_design"})

        ref_block = f"\n\nVISUAL REFERENCES (from Visual Universe Generator):\n{visual_references}" if visual_references else ""
        prompt = f"SCENE TEXT:\n{scene_text[:10000]}{ref_block}"
        shot_plan = self.gemini.generate_json(prompt, system_instruction=self.instruction)

        artifact_uri = self.storage.upload_bytes(
            str(shot_plan).encode("utf-8"),
            filename=f"shot_plan_{project_id}.json",
            folder="artifacts/storyboards",
        )

        await self.emit("agent_completed", {"project_id": project_id, "task": "shot_design"})
        return {"agent": self.name, "project_id": project_id, "shot_plan": shot_plan, "artifact_uri": artifact_uri}
