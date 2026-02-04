# rag/workflow/extraction.py

from typing import Dict
from rag.workflow.schemas import SearchMemory


def extract_memory_updates(
    user_message: str,
    memory: SearchMemory
) -> Dict:
    """
    MVP extractor.
    Rule-based, conservative.
    Only extracts high-confidence signals.
    """

    text = user_message.lower()
    updates: Dict = {}

    # ---- product_type ----
    if "glass" in text:
        updates["product_type"] = "glass"

    if "wine glass" in text or "wine glasses" in text:
        updates["product_type"] = "wine glass"

    # ---- use_case ----
    if "dinner" in text:
        updates["use_case"] = "dinner"

    if "party" in text:
        updates["use_case"] = "party"

    # ---- category (only if missing) ----
    if not memory.category and "glass" in text:
        updates["category"] = "drinkware"

    # ---- attributes (future-ready) ----
    updates["attributes"] = {}

    return updates
