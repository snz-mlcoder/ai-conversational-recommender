from enum import Enum
from rag.workflow.vocab import PRODUCT_SIGNAL_GROUPS


# =====================================================
# Item detection
# =====================================================

class ItemMode(Enum):
    SINGLE = "single"
    MULTI_SEARCH = "multi_search"
    COMPARISON = "comparison"
    AMBIGUOUS = "ambiguous"


ITEM_COMPARISON_CUES = {
    "meglio",
    " o ",
    "vs",
    "contro",
}


def detect_item_mode(text: str, items: list[str]) -> ItemMode:
    text = text.lower()

    if len(items) == 1:
        return ItemMode.SINGLE

    # comparison / choice
    if "?" in text or any(cue in text for cue in ITEM_COMPARISON_CUES):
        return ItemMode.COMPARISON

    # list / OR search
    if " e " in text or "," in text:
        return ItemMode.MULTI_SEARCH

    return ItemMode.AMBIGUOUS


# =====================================================
# Attribute detection
# =====================================================

class AttributeMode(Enum):
    SINGLE = "single"
    MULTI_FILTER = "multi_filter"
    COMPARISON = "comparison"
    AMBIGUOUS = "ambiguous"


ATTRIBUTE_COMPARISON_CUES = {
    "meglio",
    " o ",
    "vs",
    "contro",
    "differenza",
}


def detect_attribute_mode(text: str, values: list[str]) -> AttributeMode:
    text = text.lower()

    if len(values) == 1:
        return AttributeMode.SINGLE

    if "?" in text or any(cue in text for cue in ATTRIBUTE_COMPARISON_CUES):
        return AttributeMode.COMPARISON

    if " e " in text or "," in text:
        return AttributeMode.MULTI_FILTER

    return AttributeMode.AMBIGUOUS


# =====================================================
# Question & material helpers
# =====================================================

QUESTION_STARTERS = {
    "è", "è",
    "qual", "quale", "quali",
    "come",
    "quanto", "quanti", "quanta",
    "posso",
    "si può", "si puo",
    "meglio",
    "conviene",
    "perché", "perche",
}


MATERIAL_COMPARISON_CUES = {
    " o ",
    "meglio",
    "vs",
    "contro",
    "differenza",
}


def is_material_comparison_question(text: str, materials: set[str]) -> bool:
    text = text.lower()

    mentioned = [m for m in materials if m in text]
    if len(mentioned) >= 2:
        return True

    return any(cue in text for cue in MATERIAL_COMPARISON_CUES)


def is_question(text: str) -> bool:
    text = text.strip().lower()

    if "?" in text:
        return True

    return any(text.startswith(q) for q in QUESTION_STARTERS)


# =====================================================
# Product signal extraction
# =====================================================

def extract_product_signals(text: str) -> dict:
    text = text.lower()
    found = {}

    for group, terms in PRODUCT_SIGNAL_GROUPS.items():
        matches = [t for t in terms if t in text]
        if matches:
            found[group] = matches

    return found


def has_product_signal(text: str) -> bool:
    signals = extract_product_signals(text)
    return bool(signals.get("items"))


def has_search_signal(text: str) -> bool:
    signals = extract_product_signals(text)

    return bool(
        signals.get("items")
        or signals.get("use_cases")
        or signals.get("occasions")
        or signals.get("materials")
        or signals.get("colors")
        or signals.get("sizes")
        or signals.get("shapes")
    )


def has_search_signal_from_updates(updates: dict) -> bool:
    return bool(
        updates.get("product_type")
        or updates.get("occasion")
        or updates.get("use_case")
        or updates.get("attributes")
    )
