# [PHASE-2]: optional LLM-assisted intent disambiguation

# rag/workflow/intent.py

from enum import Enum
from typing import Tuple, Optional

from rag.workflow.signals import (
    extract_product_signals,
    has_search_signal,
    is_question,
)
from rag.workflow.intent_vocab import (
    STORE_INFO_TERMS,
)
from rag.workflow.intent_types import Intent


# =====================================================
# Utilities
# =====================================================

def contains_any(text: str, terms: set[str]) -> bool:
    return bool(terms) and any(term in text for term in terms)


# =====================================================
# Rule-based Intent Stage
# =====================================================

def rule_intent_stage(text: str, signals: dict) -> Tuple[Intent, float]:

    # 1️⃣ Store info (high priority, explicit)
    if contains_any(text, STORE_INFO_TERMS):
        return Intent.STORE_INFO, 0.95

    # 2️⃣ Material knowledge (question about materials)
    if (
        "materials" in signals
        and is_question(text)
    ):
        return Intent.MATERIAL_KNOWLEDGE, 0.9

    # 3️⃣ Explicit item → product search
    if "items" in signals:
        return Intent.PRODUCT_SEARCH, 0.9

    # 4️⃣ Attribute-only refinement (no question)
    if has_search_signal(text) and not is_question(text):
        return Intent.PRODUCT_SEARCH, 0.85

    return Intent.SMALL_TALK, 0.4

# =====================================================
# Hybrid Detect Intent (Rule + Optional LLM)
# =====================================================

LLM_CONFIDENCE_THRESHOLD = 0.6


def detect_intent(user_message: str) -> Intent:

    from rag.workflow.llm_intent import llm_intent_disambiguation

    text = user_message.lower()
    signals = extract_product_signals(text)

    rule_intent, confidence = rule_intent_stage(text, signals)

    # 🔥 LLM disambiguation layer
    if confidence < 0.85:
        llm_intent = llm_intent_disambiguation(text)
        if llm_intent:
            return llm_intent

    return rule_intent





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