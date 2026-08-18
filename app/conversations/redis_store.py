import json
import uuid
from typing import List

import redis.asyncio as redis

from app.conversations.base import BaseConversationStore
from app.core.config import settings


class RedisConversationStore(BaseConversationStore):

    def __init__(self):
        self.client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

    def _meta_key(
        self,
        conversation_id: str,
    ) -> str:
        return (
            f"{settings.redis_key_prefix}"
            f"{conversation_id}:meta"
        )

    def _messages_key(
        self,
        conversation_id: str,
    ) -> str:
        return (
            f"{settings.redis_key_prefix}"
            f"{conversation_id}:messages"
        )

    def _ttl_seconds(self) -> int:
        return settings.conversation_ttl_minutes * 60

    async def create(self) -> str:
        conversation_id = str(uuid.uuid4())

        await self.client.set(
            self._meta_key(conversation_id),
            "1",
            ex=self._ttl_seconds(),
        )

        return conversation_id

    async def exists(
        self,
        conversation_id: str,
    ) -> bool:

        exists = await self.client.exists(
            self._meta_key(conversation_id)
        )

        return bool(exists)

    async def get_messages(
        self,
        conversation_id: str,
    ) -> List[dict]:

        if not await self.exists(conversation_id):
            return []

        meta_key = self._meta_key(conversation_id)
        messages_key = self._messages_key(
            conversation_id
        )

        raw_messages = await self.client.lrange(
            messages_key,
            0,
            -1,
        )

        ttl = self._ttl_seconds()

        await self.client.expire(
            meta_key,
            ttl,
        )

        if raw_messages:
            await self.client.expire(
                messages_key,
                ttl,
            )

        return [
            json.loads(message)
            for message in raw_messages
        ]

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> None:

        meta_key = self._meta_key(conversation_id)
        messages_key = self._messages_key(
            conversation_id
        )

        if not await self.exists(conversation_id):
            raise KeyError(
                "Conversation does not exist."
            )

        message = json.dumps(
            {
                "role": role,
                "content": content,
            }
        )

        ttl = self._ttl_seconds()

        async with self.client.pipeline(
            transaction=True
        ) as pipe:
            pipe.rpush(
                messages_key,
                message,
            )

            pipe.ltrim(
                messages_key,
                -settings.max_history_messages,
                -1,
            )

            pipe.expire(
                messages_key,
                ttl,
            )

            pipe.expire(
                meta_key,
                ttl,
            )

            await pipe.execute()

    async def ping(self) -> bool:
        return bool(
            await self.client.ping()
        )
    async def close(self) -> None:
        await self.client.aclose()
