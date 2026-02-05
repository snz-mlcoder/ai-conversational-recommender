from enum import Enum

from rag.workflow.intent_vocab import (
    STORE_INFO_TERMS,
    PROMOTION_TERMS,
    MATERIAL_KNOWLEDGE_TERMS,
)
from rag.workflow.signals import (
    extract_product_signals,
    is_question,
)


class Intent(Enum):
    SMALL_TALK = "small_talk"
    PRODUCT_SEARCH = "product_search"
    STORE_INFO = "store_info"
    PROMOTION = "promotion"
    MATERIAL_KNOWLEDGE = "material_knowledge"


def contains_any(text: str, terms: set[str]) -> bool:
    """
    Check if any keyword in `terms` is contained in the text.
    """
    return bool(terms) and any(term in text for term in terms)


def detect_intent(user_message: str) -> Intent:
    text = user_message.lower()
    signals = extract_product_signals(text)

    # 1️⃣ Store / service info
    if contains_any(text, STORE_INFO_TERMS):
        return Intent.STORE_INFO

    # 2️⃣ Promotion / commercial terms
    if contains_any(text, PROMOTION_TERMS):
        return Intent.PROMOTION

    # 3️⃣ Product search ALWAYS wins if item exists
    if "items" in signals:
        return Intent.PRODUCT_SEARCH

    # 4️⃣ Material knowledge (informational only)
    if "materials" in signals and is_question(text):
        return Intent.MATERIAL_KNOWLEDGE

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

'''نکات خیلی مهم (Architect-level)
✅ 1. Intentها mutually exclusive هستند

الان:

هر پیام دقیقاً یک intent دارد

کنترل ساده است

debug راحت است

Later:

می‌تونی multi-intent اضافه کنی

بدون شکستن این کد

✅ 2. detect_intent هیچ side-effect ندارد

memory را تغییر نمی‌دهد

ask_back ندارد

search نمی‌کند

📌 این یعنی testable و safe.

✅ 3. آماده‌ی LLM augmentation است

بعداً خیلی راحت می‌تونی:

# optional LLM disambiguation
if confidence_low:
    return llm_suggest_intent(...)


بدون دست زدن به این backbone.'''