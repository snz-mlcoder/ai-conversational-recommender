# rag/workflow/intent.py

from enum import Enum


class Intent(Enum):
    SMALL_TALK = "small_talk"
    STORE_INFO = "store_info"
    PROMOTION = "promotion"
    PRODUCT_SEARCH = "product_search"


def detect_intent(user_message: str) -> Intent:
    """
    MVP intent detection.
    Deliberately simple and deterministic.
    """

    text = user_message.lower()

    if any(word in text for word in ["buy", "need", "looking", "search", "find"]):
        return Intent.PRODUCT_SEARCH

    return Intent.SMALL_TALK


'''
نکات خیلی مهم:

deliberately ساده‌ست

explainable ـه

فقط برای اینکه workflow راه بیفته

بعداً خیلی راحت با LLM جایگزین می‌شه
'''