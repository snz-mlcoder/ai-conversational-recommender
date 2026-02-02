from typing import Dict, List
from uuid import uuid4


class ConversationMemory:
    """
    In-memory conversation store.
    Can be replaced later with Redis / DB.
    """

    def __init__(self):
        self._store: Dict[str, Dict] = {}

    def create(self, language: str = "it") -> str:
        conversation_id = str(uuid4())
        self._store[conversation_id] = {
            "id": conversation_id,
            "language": language,
            "history": [],
            "constraints": {
                "category": None,
                "price_range": None,
                "use_case": None,
            }
        }
        return conversation_id

    def get(self, conversation_id: str) -> Dict:
        return self._store.get(conversation_id)

    def add_message(self, conversation_id: str, role: str, text: str):
        if conversation_id not in self._store:
            return
        self._store[conversation_id]["history"].append({
            "role": role,
            "text": text
        })

    def update_constraint(self, conversation_id: str, key: str, value):
        if conversation_id not in self._store:
            return
        self._store[conversation_id]["constraints"][key] = value
# singleton instance
conversation_memory = ConversationMemory()
