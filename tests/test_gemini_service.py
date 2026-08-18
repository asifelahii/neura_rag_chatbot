import asyncio
from types import SimpleNamespace

import pytest

from app.core.config import settings
from app.services.ai_exceptions import AIServiceUnavailableError
from app.services.gemini_service import GeminiService


def test_gemini_uses_max_output_tokens(monkeypatch):
    service = GeminiService()
    captured = {}

    async def fake_generate_content(**kwargs):
        captured.update(kwargs)

        return SimpleNamespace(
            text="Test response"
        )

    monkeypatch.setattr(
        service.client.aio.models,
        "generate_content",
        fake_generate_content,
    )

    result = asyncio.run(
        service.generate_response(
            message="Hello",
            history=[],
        )
    )

    assert result == "Test response"

    config = captured["config"]

    assert (
        config.max_output_tokens
        == settings.gemini_max_output_tokens
    )


def test_gemini_timeout_is_mapped_to_service_error(
    monkeypatch,
):
    service = GeminiService()

    monkeypatch.setattr(
        settings,
        "gemini_request_timeout_seconds",
        0.01,
    )

    async def slow_generate_content(**kwargs):
        await asyncio.sleep(0.05)

        return SimpleNamespace(
            text="Too late"
        )

    monkeypatch.setattr(
        service.client.aio.models,
        "generate_content",
        slow_generate_content,
    )

    with pytest.raises(
        AIServiceUnavailableError,
        match="timed out",
    ):
        asyncio.run(
            service.generate_response(
                message="Hello",
                history=[],
            )
        )
