import pytest

import app.conversations.memory as memory_module
from app.conversations.memory import MemoryConversationStore
from app.core.config import settings


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_history_is_trimmed(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "max_history_messages",
        12,
    )

    store = MemoryConversationStore()

    conversation_id = await store.create()

    for i in range(20):
        await store.add_message(
            conversation_id,
            "user",
            f"Message {i + 1}",
        )

    messages = await store.get_messages(
        conversation_id
    )

    assert len(messages) == 12

    assert (
        messages[0]["content"]
        == "Message 9"
    )

    assert (
        messages[-1]["content"]
        == "Message 20"
    )


@pytest.mark.anyio
async def test_conversation_expires(
    monkeypatch,
):
    current_time = [1000.0]

    monkeypatch.setattr(
        memory_module.time,
        "time",
        lambda: current_time[0],
    )

    monkeypatch.setattr(
        settings,
        "conversation_ttl_minutes",
        1,
    )

    store = MemoryConversationStore()

    conversation_id = await store.create()

    assert (
        await store.exists(conversation_id)
        is True
    )

    current_time[0] = 1061.0

    assert (
        await store.exists(conversation_id)
        is False
    )
