from enum import Enum
from rag.workflow.intent_vocab import (
    STORE_INFO_TERMS,
    PROMOTION_TERMS,
    MATERIAL_KNOWLEDGE_TERMS,
    
)
from rag.workflow.signals import has_product_signal, extract_product_signals, is_question



class Intent(Enum):
    SMALL_TALK = "small_talk"
    PRODUCT_SEARCH = "product_search"
    STORE_INFO = "store_info"
    PROMOTION = "promotion"
    MATERIAL_KNOWLEDGE = "material_knowledge"


def contains_any(text: str, terms: set[str]) -> bool:
    return bool(terms) and any(term in text for term in terms)


def detect_intent(user_message: str) -> Intent:
    text = user_message.lower()
    signals = extract_product_signals(text)

    # 1️⃣ Product search (item wins)
    if has_product_signal(text):
        return Intent.PRODUCT_SEARCH

    # 2️⃣ 🔥 Material knowledge disambiguation
    if (
        "materials" in signals
        and "items" not in signals
        and is_question(text)
    ):
        return Intent.MATERIAL_KNOWLEDGE

    # 3️⃣ Promotion
    if contains_any(text, PROMOTION_TERMS):
        return Intent.PROMOTION

    # 4️⃣ Store info
    if contains_any(text, STORE_INFO_TERMS):
        return Intent.STORE_INFO

    return Intent.SMALL_TALK


"""
نکات مهم معماری:

- vocab غنی و واقعی (بر اساس دیتای سایت)
- bilingual (IT + EN)
- rule-based و explainable
- قابل reuse برای extraction / memory / explanation
- threshold قابل تنظیم (min_groups)
- آماده برای جایگزینی با LLM در آینده
"""
