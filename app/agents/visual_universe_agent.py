"""
Visual Universe Generator Agent (CREATE module).

Two jobs:
 1. extract_visual_dna() — reads a screenplay and pulls out the visual
    grammar of the world: locations, time period, weather, architecture,
    mood, color/lighting direction, genre, visual motifs, important
    props, and environmental details.
 2. generate_visuals() — turns a prompt (often built from the visual DNA)
    into 1-4 generated images for a chosen category (location, character,
    scene, moodboard, world, shot), each saved to GCS as an artifact.

Both steps run through Gemini only (generate_json for extraction,
GeminiImageClient — Gemini's image-output mode — for generation), so no
extra external API is introduced.
"""
from typing import Any

from app.agents.base_agent import BaseAgent
from app.core.clickhouse_client import analytics as shared_analytics
from app.core.gcs_storage import GCSStorage
from app.core.gemini_image_client import GeminiImageClient

DNA_INSTRUCTION = (
    "You are a production designer extracting the 'visual DNA' of a "
    "screenplay. Return ONLY JSON with fields: locations (list), "
    "time_period, weather, architecture, mood, color_lighting_direction, "
    "genre, visual_motifs (list), important_props (list), "
    "environmental_details (list). Also include a 'suggested_prompt' "
    "field: a single vivid cinematic image-generation prompt (1-2 "
    "sentences) synthesizing all of the above."
)

VARIANT_PRESETS: dict[str, list[str]] = {
    "location": ["Establishing shot", "Alternate location design", "Night version", "Interior version"],
    "character": ["Front portrait", "Action pose", "Costume detail", "Expression study"],
    "scene": ["Wide shot", "Medium shot", "Close-up", "Alternate angle"],
    "moodboard": ["Color palette", "Texture and lighting study", "Reference collage", "Atmosphere frame"],
    "world": ["Aerial view", "Street level", "Landmark", "Skyline / environment"],
    "shot": ["Shot composition A", "Shot composition B", "Shot composition C", "Shot composition D"],
}


class VisualUniverseAgent(BaseAgent):
    name = "visual_universe_agent"
    instruction = DNA_INSTRUCTION

    def __init__(self):
        super().__init__()
        self.storage = GCSStorage()
        self.image_client = GeminiImageClient()
        self.analytics = shared_analytics

    async def run(self, **kwargs) -> dict[str, Any]:
        """Default entry point: extract visual DNA. Use generate_visuals()
        directly for the image-generation step."""
        return await self.extract_visual_dna(**kwargs)

    async def extract_visual_dna(self, script_text: str, project_id: str = "default") -> dict[str, Any]:
        await self.emit("agent_started", {"project_id": project_id, "task": "visual_dna_extraction"})

        prompt = f"SCRIPT TEXT:\n{script_text[:12000]}"
        visual_dna = self.gemini.generate_json(prompt, system_instruction=DNA_INSTRUCTION)

        await self.emit("agent_completed", {"project_id": project_id, "task": "visual_dna_extraction"})
        return {"agent": self.name, "project_id": project_id, "visual_dna": visual_dna}

    async def generate_visuals(self, prompt: str, generate_type: str = "scene",
                                count: int = 4, project_id: str = "default") -> dict[str, Any]:
        generate_type = generate_type.lower()
        variants = VARIANT_PRESETS.get(generate_type, VARIANT_PRESETS["scene"])
        count = max(1, min(count, 4, len(variants)))
        chosen_variants = variants[:count]

        await self.emit("agent_started", {
            "project_id": project_id, "task": "visual_generation",
            "generate_type": generate_type, "count": count,
        })

        images = self.image_client.generate_images(prompt, chosen_variants)

        storage_uris = []
        any_mock = False
        for image in images:
            ext = "svg" if image.mime_type == "image/svg+xml" else "png"
            uri = self.storage.upload_bytes(
                image.data,
                filename=f"{generate_type}_{image.variant.replace(' ', '_')}.{ext}",
                folder=f"artifacts/visuals/{project_id}",
            )
            storage_uris.append({"variant": image.variant, "storage_uri": uri, "mock": image.mock})
            any_mock = any_mock or image.mock

        visual_id = self.new_run_id()
        self.analytics.insert("visual_generations", {
            "visual_id": visual_id,
            "project_id": project_id,
            "generate_type": generate_type,
            "prompt": prompt[:2000],
            "variant_count": count,
            "storage_uris_json": str(storage_uris),
            "mock": 1 if any_mock else 0,
        })

        await self.emit("agent_completed", {"project_id": project_id, "task": "visual_generation", "visual_id": visual_id})
        return {
            "agent": self.name,
            "visual_id": visual_id,
            "project_id": project_id,
            "generate_type": generate_type,
            "prompt": prompt,
            "images": storage_uris,
        }
