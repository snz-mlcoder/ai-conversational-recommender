# rag/workflow/extraction.py

from typing import Dict
from rag.workflow.schemas import SearchMemory
from rag.workflow.signals import extract_product_signals
from rag.workflow.vocab import (
    PRODUCT_SIGNAL_GROUPS,
    NEGATION_WORDS,
)
from rag.workflow.intent_vocab import PROMOTION_TERMS


NEGATION_ANY = "__ANY__"


# =====================================================
# Utilities
# =====================================================

def contains_any(text: str, terms: set[str]) -> bool:
    return bool(terms) and any(term in text for term in terms)


# =====================================================
# Negation Extraction
# =====================================================

def extract_negations(text: str) -> dict:
    text = text.lower()
    negations: dict = {}

    if not any(n in text for n in NEGATION_WORDS):
        return negations

    for group_name, vocab in PRODUCT_SIGNAL_GROUPS.items():

        if group_name not in {"colors", "materials", "sizes", "shapes", "items"}:
            continue

        found = [term for term in vocab if term in text]

        if not found:
            continue

        # 🔥 items → product_type negation
        if group_name == "items":
            if len(found) >= 2:
                negations["product_type"] = NEGATION_ANY
            else:
                negations["product_type"] = found[0]
            continue

        # attributes
        if len(found) >= 2:
            negations[group_name[:-1]] = NEGATION_ANY
        else:
            negations[group_name[:-1]] = found[0]

    return negations


# =====================================================
# Main Extraction
# =====================================================

def extract_memory(
    user_message: str,
    memory: SearchMemory
) -> Dict:

    user_message = user_message.lower()

    signals = extract_product_signals(user_message)
    updates: Dict = {}

    # --------------------
    # product_type
    # --------------------
    if "items" in signals:
        updates["product_type"] = signals["items"][0]

        if not memory.category:
            updates["category"] = "tableware"

    # --------------------
    # use_case
    # --------------------
    if "use_cases" in signals:
        updates["use_case"] = signals["use_cases"][0]

    # --------------------
    # occasion
    # --------------------
    if "occasions" in signals:
        updates["occasion"] = signals["occasions"][0]

    # --------------------
    # negations only (structure)
    # --------------------
    negations = extract_negations(user_message)
    if negations:
        updates["negations"] = negations

    return updates
