# rag/workflow_v4_1/intent_v4_1.py

from enum import Enum
from rag.workflow.signals import (
    extract_product_signals,
    has_search_signal,
    is_question,
)


class IntentV41(Enum):
    SMALL_TALK = "small_talk"
    PRODUCT_SEARCH = "product_search"
    MATERIAL_KNOWLEDGE = "material_knowledge"
    OTHER = "other"


def detect_intent_v4_1(user_message: str) -> IntentV41:
    text = user_message.lower()
    signals = extract_product_signals(text)

    # -------------------------
    # 1️⃣ Informational material question
    # Example: "è meglio plastica o vetro?"
    # -------------------------
    if "materials" in signals and is_question(text):
        return IntentV41.MATERIAL_KNOWLEDGE

    # -------------------------
    # 2️⃣ Any product signal → search
    # -------------------------
    if has_search_signal(text):
        return IntentV41.PRODUCT_SEARCH

    # -------------------------
    # 3️⃣ Fallback
    # -------------------------
    return IntentV41.SMALL_TALK
