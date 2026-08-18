import base64
import hashlib
import hmac

from app.core.config import settings


class ConversationTokenError(Exception):
    pass


class ConversationTokenService:

    def __init__(self):
        self._secret = settings.app_secret_key.encode(
            "utf-8"
        )

    def create(self, conversation_id: str) -> str:
        payload = base64.urlsafe_b64encode(
            conversation_id.encode("utf-8")
        ).decode("ascii").rstrip("=")

        signature = hmac.new(
            self._secret,
            payload.encode("ascii"),
            hashlib.sha256,
        ).digest()

        encoded_signature = (
            base64.urlsafe_b64encode(signature)
            .decode("ascii")
            .rstrip("=")
        )

        return f"{payload}.{encoded_signature}"

    def verify(self, token: str) -> str:
        try:
            payload, supplied_signature = token.split(
                ".",
                1,
            )

        except ValueError as exc:
            raise ConversationTokenError(
                "Invalid conversation token."
            ) from exc

        expected_signature = hmac.new(
            self._secret,
            payload.encode("ascii"),
            hashlib.sha256,
        ).digest()

        try:
            supplied_signature_bytes = (
                self._decode_base64(
                    supplied_signature
                )
            )

        except Exception as exc:
            raise ConversationTokenError(
                "Invalid conversation token."
            ) from exc

        if not hmac.compare_digest(
            expected_signature,
            supplied_signature_bytes,
        ):
            raise ConversationTokenError(
                "Invalid conversation token."
            )

        try:
            conversation_id = self._decode_base64(
                payload
            ).decode("utf-8")

        except Exception as exc:
            raise ConversationTokenError(
                "Invalid conversation token."
            ) from exc

        if not conversation_id:
            raise ConversationTokenError(
                "Invalid conversation token."
            )

        return conversation_id

    @staticmethod
    def _decode_base64(value: str) -> bytes:
        padding = "=" * (-len(value) % 4)

        return base64.urlsafe_b64decode(
            value + padding
        )


conversation_token_service = ConversationTokenService()
