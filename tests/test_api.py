from fastapi.testclient import TestClient

from emotions_ai.api.app import create_app


def test_health():
    app = create_app()
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_chat_endpoint():
    app = create_app()
    client = TestClient(app)
    r = client.post("/chat", json={"user_id": "u", "message": "I finished my project!"})
    assert r.status_code == 200
    data = r.json()
    assert "text" in data
    assert "emotional_summary" in data