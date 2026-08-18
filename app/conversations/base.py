from abc import ABC, abstractmethod
from typing import List


class BaseConversationStore(ABC):

    @abstractmethod
    async def create(self) -> str:
        pass

    @abstractmethod
    async def exists(
        self,
        conversation_id: str,
    ) -> bool:
        pass

    @abstractmethod
    async def get_messages(
        self,
        conversation_id: str,
    ) -> List[dict]:
        pass

    @abstractmethod
    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> None:
        pass

    @abstractmethod
    async def ping(self) -> bool:
        pass

    async def close(self) -> None:
        pass
