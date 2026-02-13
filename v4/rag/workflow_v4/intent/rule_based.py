from rag.workflow_v4.intent.base import IntentClassifier
from rag.workflow.intent import Intent
from rag.workflow.signals import (
    extract_product_signals,
    has_search_signal,
    is_question,
)

class RuleBasedIntentClassifier(IntentClassifier):

    def classify(self, text: str) -> Intent:

        text = text.lower()
        signals = extract_product_signals(text)

        # 1️⃣ Informational material question
        if signals.get("materials") and is_question(text):
            return Intent.MATERIAL_KNOWLEDGE

        # 2️⃣ Product search
        if has_search_signal(text):
            return Intent.PRODUCT_SEARCH

        # 3️⃣ Fallback
        return Intent.SMALL_TALK
