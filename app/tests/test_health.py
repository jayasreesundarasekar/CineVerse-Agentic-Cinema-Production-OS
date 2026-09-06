"""Smoke tests for the Cineverse API — run with: pytest"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200


def test_list_agents():
    resp = client.get("/agents/")
    assert resp.status_code == 200
    agents = resp.json()["available_agents"]
    assert "screenplay" in agents
    assert "simulation" in agents


def test_screenplay_analysis_mock():
    resp = client.post("/agents/screenplay/analyze", json={
        "project_id": "test-project",
        "script_text": "FADE IN: A hero begins their journey...",
    })
    assert resp.status_code == 200
    assert resp.json()["agent"] == "screenplay_agent"


def test_simulation_mock():
    resp = client.post("/agents/simulation/run", json={
        "project_id": "test-project",
        "premise": "A detective investigates a mysterious disappearance.",
        "scenario": "Alternate ending where the detective fails.",
    })
    assert resp.status_code == 200
    assert "run_id" in resp.json()


def test_analytics_backend_status():
    resp = client.get("/analytics/backend-status")
    assert resp.status_code == 200
