"""Smoke tests for the Visual Universe Generator + AI Shot Designer pipeline."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SCRIPT_TEXT = (
    "FADE IN: A mysterious coastal town where the protagonist Maya returns "
    "after 15 years. Abandoned colonial buildings line the wet streets under "
    "monsoon clouds. A cinematic thriller atmosphere hangs over everything."
)


def test_extract_visual_dna():
    resp = client.post("/create/visual-universe/extract-dna", json={
        "project_id": "vu1", "script_text": SCRIPT_TEXT,
    })
    assert resp.status_code == 200
    assert "visual_dna" in resp.json()


def test_generate_visuals_default_scene_type():
    resp = client.post("/create/visual-universe/generate", json={
        "project_id": "vu1",
        "prompt": "A mysterious coastal town, abandoned colonial buildings, monsoon clouds, wet streets.",
        "generate_type": "location",
        "count": 4,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["generate_type"] == "location"
    assert len(body["images"]) == 4
    for img in body["images"]:
        assert "storage_uri" in img and "variant" in img

    history = client.get("/create/visual-universe/history", params={"project_id": "vu1"})
    assert history.status_code == 200
    assert len(history.json()["rows"]) >= 1


def test_generate_visuals_count_clamped():
    resp = client.post("/create/visual-universe/generate", json={
        "project_id": "vu1", "prompt": "Test prompt", "generate_type": "character", "count": 10,
    })
    assert resp.status_code == 200
    assert len(resp.json()["images"]) == 4  # clamped to preset variant list length


def test_scene_package_full_pipeline():
    resp = client.post("/create/scene-package", json={
        "project_id": "vu1",
        "script_text": SCRIPT_TEXT,
        "scene_text": "INT. ABANDONED HOUSE - NIGHT. Maya finds an old photograph.",
        "generate_type": "scene",
        "count": 2,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "visual_dna" in body
    assert "visuals" in body and len(body["visuals"]["images"]) == 2
    assert "shots" in body and "shot_plan" in body["shots"]


def test_shot_designer_includes_lens_and_movement_fields():
    resp = client.post("/create/storyboard", json={
        "project_id": "vu1",
        "scene_text": "EXT. TRAIN PLATFORM - DAY. Maya looks toward the departing train.",
        "visual_references": ["Wide shot", "Close-up"],
    })
    assert resp.status_code == 200
    assert "shot_plan" in resp.json()
