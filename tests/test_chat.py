import pytest
from fastapi.testclient import TestClient

from app.api.chat import gemini_service
from app.conversations.store import conversation_store
from app.security.rate_limiter import rate_limiter
from app.services.ai_exceptions import AIServiceUnavailableError
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_state():

    if hasattr(
        conversation_store,
        "_conversations",
    ):
        conversation_store._conversations.clear()

    rate_limiter.reset()

    yield

    if hasattr(
        conversation_store,
        "_conversations",
    ):
        conversation_store._conversations.clear()

    rate_limiter.reset()


def test_empty_message_returns_422():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "",
            "conversation_id": None,
        },
    )

    assert response.status_code == 422


def test_invalid_conversation_returns_404():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "conversation_id": "does-not-exist",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Conversation not found."
    }


def test_new_conversation_returns_response(monkeypatch):
    async def fake_generate_response(
        message,
        history,
        context=None,
    ):
        return "Mock Gemini response"

    monkeypatch.setattr(
        gemini_service,
        "generate_response",
        fake_generate_response,
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "What is ERP?",
            "conversation_id": None,
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["conversation_id"]
    assert data["message"] == "Mock Gemini response"
    assert data["mode"] == "general"


def test_conversation_history_is_used(monkeypatch):
    received_histories = []

    async def fake_generate_response(
        message,
        history,
        context=None,
    ):
        received_histories.append(history.copy())
        return f"Reply to: {message}"

    monkeypatch.setattr(
        gemini_service,
        "generate_response",
        fake_generate_response,
    )

    first_response = client.post(
        "/api/v1/chat",
        json={
            "message": "What is ERP?",
            "conversation_id": None,
        },
    )

    conversation_id = first_response.json()["conversation_id"]

    second_response = client.post(
        "/api/v1/chat",
        json={
            "message": "Does it include inventory?",
            "conversation_id": conversation_id,
        },
    )

    assert second_response.status_code == 200

    assert len(received_histories) == 2

    second_history = received_histories[1]

    assert len(second_history) == 2
    assert second_history[0]["role"] == "user"
    assert second_history[0]["content"] == "What is ERP?"
    assert second_history[1]["role"] == "assistant"
    assert second_history[1]["content"] == "Reply to: What is ERP?"


def test_gemini_failure_returns_safe_503(monkeypatch):
    async def fake_generate_response(
        message,
        history,
        context=None,
    ):
        raise RuntimeError("Simulated Gemini failure")

    monkeypatch.setattr(
        gemini_service,
        "generate_response",
        fake_generate_response,
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "conversation_id": None,
        },
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "The AI service is temporarily unavailable."
    }

def test_rate_limit_returns_429(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "rate_limit_requests",
        2,
    )

    monkeypatch.setattr(
        settings,
        "rate_limit_window_seconds",
        60,
    )

    async def fake_generate_response(
        message,
        history,
        context=None,
    ):
        return "Mock response"

    monkeypatch.setattr(
        gemini_service,
        "generate_response",
        fake_generate_response,
    )

    for _ in range(2):
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "Hello",
                "conversation_id": None,
            },
        )

        assert response.status_code == 200

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello again",
            "conversation_id": None,
        },
    )

    assert response.status_code == 429

    assert response.json() == {
        "detail": "Too many requests. Please try again shortly."
    }

    assert "Retry-After" in response.headers

def test_ai_provider_unavailable_returns_503(
    monkeypatch,
):
    async def fake_generate_response(
        message,
        history,
        context=None,
    ):
        raise AIServiceUnavailableError(
            "Simulated provider limit"
        )

    monkeypatch.setattr(
        gemini_service,
        "generate_response",
        fake_generate_response,
    )

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "conversation_id": None,
        },
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": (
            "The AI service is temporarily busy. "
            "Please try again shortly."
        )
    }