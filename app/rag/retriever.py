from abc import ABC, abstractmethod
from typing import Optional

from app.core.config import settings


class KnowledgeRetriever(ABC):
    @abstractmethod
    async def retrieve(self, query: str) -> Optional[str]:
        pass


class NullKnowledgeRetriever(KnowledgeRetriever):
    async def retrieve(self, query: str) -> Optional[str]:
        return None


class UnconfiguredKnowledgeRetriever(KnowledgeRetriever):
    async def retrieve(self, query: str) -> Optional[str]:
        raise RuntimeError(
            "RAG is enabled but no knowledge retriever is configured."
        )


def get_knowledge_retriever() -> KnowledgeRetriever:
    if settings.rag_enabled:
        return UnconfiguredKnowledgeRetriever()

    return NullKnowledgeRetriever()
