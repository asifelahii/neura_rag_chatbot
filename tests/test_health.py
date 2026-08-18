from fastapi.testclient import TestClient

from app.conversations.store import conversation_store
from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "service": "Neura RAG Chatbot",
    }


def test_readiness_check_returns_200():
    response = client.get("/ready")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ready",
        "dependencies": {
            "conversation_store": "healthy",
        },
    }


def test_readiness_check_returns_503_when_store_fails(
    monkeypatch,
):
    async def fake_ping():
        raise ConnectionError(
            "Simulated conversation store failure"
        )

    monkeypatch.setattr(
        conversation_store,
        "ping",
        fake_ping,
    )

    response = client.get("/ready")

    assert response.status_code == 503

    assert response.json() == {
        "detail": "Service is not ready."
    }
