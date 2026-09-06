"""Smoke tests for the extended CREATE/SIMULATE/ANALYZE/PRODUCE/DECIDE modules."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_storyboard():
    resp = client.post("/create/storyboard", json={
        "project_id": "p1", "scene_text": "INT. WAREHOUSE - NIGHT. Maya confronts Daniel.",
    })
    assert resp.status_code == 200
    assert "shot_plan" in resp.json()


def test_character_twin_and_check():
    resp = client.post("/create/character-twin", json={
        "project_id": "p1", "name": "Maya", "context_text": "Maya is a detective seeking the truth about her sister.",
    })
    assert resp.status_code == 200
    assert resp.json()["character_id"]

    resp2 = client.post("/create/character-twin/check", json={
        "project_id": "p1", "name": "Maya", "decision_context": "Maya abandons the case without explanation.",
    })
    assert resp2.status_code == 200


def test_scenario_lab_and_multiverse():
    resp = client.post("/simulate/scenario-lab", json={
        "project_id": "p1",
        "baseline_summary": "A detective thriller set in Mumbai.",
        "what_if": "What if the ending changes to a twist reveal?",
        "title": "Universe B",
    })
    assert resp.status_code == 200
    assert resp.json()["universe_id"]

    tree_resp = client.get("/simulate/multiverse", params={"project_id": "p1"})
    assert tree_resp.status_code == 200
    assert tree_resp.json()["universe_count"] >= 1


def test_audience_and_red_team():
    resp = client.post("/analyze/audience", json={
        "project_id": "p1", "story_summary": "A detective thriller set in Mumbai.",
    })
    assert resp.status_code == 200

    resp2 = client.post("/analyze/red-team", json={
        "project_id": "p1", "context_bundle": "Screenplay + budget + audience notes here.",
    })
    assert resp2.status_code == 200


def test_budget_simulation():
    resp = client.post("/produce/budget", json={
        "project_id": "p1",
        "line_items": {"actors": 2500000, "vfx": 1500000},
        "change_request": "Cut shooting schedule by 5 days.",
    })
    assert resp.status_code == 200
    assert "budget_id" in resp.json()


def test_greenlight_pipeline():
    resp = client.post("/decide/greenlight", json={
        "project_id": "p1",
        "title": "Universe B",
        "universe_summary": "A detective thriller with a twist ending.",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "executive_decision" in body

    decisions_resp = client.get("/decide/decisions", params={"project_id": "p1"})
    assert decisions_resp.status_code == 200
    assert len(decisions_resp.json()["rows"]) >= 1
