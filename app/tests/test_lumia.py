"""Smoke test for the Lumia AI Co-Director chat endpoint."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_lumia_chat():
    resp = client.post("/lumia/chat", json={
        "project_id": "p1", "message": "What should I do next with my screenplay?",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["agent"] == "lumia_agent"
    assert isinstance(body["reply"], str) and len(body["reply"]) > 0
