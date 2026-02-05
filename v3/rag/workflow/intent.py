# rag/workflow/intent.py

from enum import Enum
from typing import Dict, List
from rag.workflow.vocab import PRODUCT_SIGNAL_GROUPS



# ==========================
# Intent enum
# ==========================

class Intent(Enum):
    SMALL_TALK = "small_talk"
    STORE_INFO = "store_info"
    PROMOTION = "promotion"
    PRODUCT_SEARCH = "product_search"


# ==========================
# Signal extraction
# ==========================

def extract_product_signals(text: str) -> Dict[str, List[str]]:
    """
    Extract product-related signals grouped by semantic category.
    """
    text = text.lower()
    found: Dict[str, List[str]] = {}

    for group, keywords in PRODUCT_SIGNAL_GROUPS.items():
        matches = [kw for kw in keywords if kw in text]
        if matches:
            found[group] = matches

    return found


def has_product_signal(text: str, min_groups: int = 1) -> bool:
    """
    Decide whether the text contains enough product-related signals.
    """
    signals = extract_product_signals(text)
    return len(signals) >= min_groups


# ==========================
# Intent detection
# ==========================

def detect_intent(user_message: str) -> Intent:
    """
    Domain-aware, signal-based intent detection.
    """
    if has_product_signal(user_message, min_groups=1):
        return Intent.PRODUCT_SEARCH

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
