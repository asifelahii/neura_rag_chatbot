import time
import uuid
from typing import Dict, List

from app.conversations.base import BaseConversationStore
from app.core.config import settings


class MemoryConversationStore(BaseConversationStore):

    def __init__(self):
        self._conversations: Dict[str, dict] = {}

    async def create(self) -> str:
        conversation_id = str(uuid.uuid4())

        self._conversations[conversation_id] = {
            "messages": [],
            "last_activity": time.time(),
        }

        return conversation_id

    async def exists(self, conversation_id: str) -> bool:
        conversation = self._conversations.get(
            conversation_id
        )

        if not conversation:
            return False

        ttl_seconds = (
            settings.conversation_ttl_minutes * 60
        )

        if (
            time.time()
            - conversation["last_activity"]
            > ttl_seconds
        ):
            del self._conversations[conversation_id]
            return False

        return True

    async def get_messages(
        self,
        conversation_id: str,
    ) -> List[dict]:

        if not await self.exists(conversation_id):
            return []

        conversation = self._conversations[
            conversation_id
        ]

        conversation["last_activity"] = time.time()

        return conversation["messages"].copy()

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> None:

        conversation = self._conversations[
            conversation_id
        ]

        conversation["messages"].append(
            {
                "role": role,
                "content": content,
            }
        )

        conversation["messages"] = (
            conversation["messages"][
                -settings.max_history_messages:
            ]
        )

        conversation["last_activity"] = time.time()

    async def ping(self) -> bool:
        return True

    async def close(self) -> None:
        pass
