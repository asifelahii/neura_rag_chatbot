from app.conversations.base import BaseConversationStore
from app.conversations.memory import MemoryConversationStore
from app.conversations.redis_store import RedisConversationStore
from app.core.config import settings


def create_conversation_store() -> BaseConversationStore:
    store_type = settings.conversation_store.lower()

    if store_type == "memory":
        return MemoryConversationStore()

    if store_type == "redis":
        return RedisConversationStore()

    raise RuntimeError(
        f"Unsupported conversation store: {store_type}"
    )


conversation_store = create_conversation_store()
