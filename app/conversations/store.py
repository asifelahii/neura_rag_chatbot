import uuid
from typing import Dict, List


class ConversationStore:
    def __init__(self):
        self._conversations: Dict[str, List[dict]] = {}

    def create(self) -> str:
        conversation_id = str(uuid.uuid4())

        self._conversations[conversation_id] = []

        return conversation_id

    def exists(self, conversation_id: str) -> bool:
        return conversation_id in self._conversations

    def get_messages(self, conversation_id: str) -> List[dict]:
        return self._conversations.get(conversation_id, [])

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> None:
        self._conversations[conversation_id].append(
            {
                "role": role,
                "content": content,
            }
        )


conversation_store = ConversationStore()
