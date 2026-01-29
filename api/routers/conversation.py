from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from rag.conversation.memory import conversation_memory
from rag.intent.detect import detect_intent
from rag.llm.ollama_client import ollama_client

router = APIRouter()


class ConversationRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    language: Optional[str] = "it"
    top_k: int = 5


@router.post("/")
def conversation(req: ConversationRequest):

    # conversation id
    if req.conversation_id:
        conversation_id = req.conversation_id
    else:
        conversation_id = conversation_memory.create(language=req.language)

    conversation_memory.add_message(conversation_id, "user", req.message)

    intent = detect_intent(
        llm_client=ollama_client,
        message=req.message
    )

    if intent == "GREETING":
        reply = "Ciao! Come posso aiutarti?"

    elif intent == "SEARCH_PRODUCT":
        reply = "Perfetto 👍 per che uso lo stai cercando?"

    else:
        reply = "Puoi spiegarmi meglio?"

    conversation_memory.add_message(conversation_id, "assistant", reply)

    return {
        "conversation_id": conversation_id,
        "intent": intent,
        "message": reply,
        "products": []   # 🔥 خیلی مهم
    }
