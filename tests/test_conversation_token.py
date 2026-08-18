import pytest

from app.security.conversation_token import (
    ConversationTokenError,
    ConversationTokenService,
)


def test_conversation_token_round_trip():
    service = ConversationTokenService()

    conversation_id = (
        "7ce69416-e157-4cf6-a7ba-16f646a42d0f"
    )

    token = service.create(conversation_id)

    assert token != conversation_id

    result = service.verify(token)

    assert result == conversation_id


def test_tampered_conversation_token_is_rejected():
    service = ConversationTokenService()

    token = service.create(
        "7ce69416-e157-4cf6-a7ba-16f646a42d0f"
    )

    payload, signature = token.split(".", 1)

    tampered_token = (
        f"{payload}x.{signature}"
    )

    with pytest.raises(
        ConversationTokenError
    ):
        service.verify(tampered_token)


def test_malformed_conversation_token_is_rejected():
    service = ConversationTokenService()

    with pytest.raises(
        ConversationTokenError
    ):
        service.verify(
            "definitely-not-a-valid-token"
        )
