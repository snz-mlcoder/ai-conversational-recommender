# rag/workflow/extraction.py

from typing import Dict
from rag.workflow.schemas import SearchMemory
from rag.workflow.intent import extract_product_signals


def extract_memory_updates(
    user_message: str,
    memory: SearchMemory
) -> Dict:
    """
    Domain-aware memory extractor.
    Reuses product signal extraction from intent layer.
    """

    signals = extract_product_signals(user_message)
    updates: Dict = {}

    # --------------------
    # product_type (items)
    # --------------------
    if "items" in signals:
        # take the strongest / first item
        updates["product_type"] = signals["items"][0]

    # --------------------
    # use_case
    # --------------------
    if "use_cases" in signals:
        updates["use_case"] = signals["use_cases"][0]

    # --------------------
    # attributes (merge!)
    # --------------------
    attrs = {}

    if "colors" in signals:
        attrs["color"] = signals["colors"][0]

    if "materials" in signals:
        attrs["material"] = signals["materials"][0]

    if "sizes" in signals:
        attrs["size"] = signals["sizes"][0]

    if "shapes" in signals:
        attrs["shape"] = signals["shapes"][0]

    if attrs:
        updates["attributes"] = attrs



    # --------------------
    # category (optional, conservative)
    # --------------------
    if not memory.category and "items" in signals:
        updates["category"] = "tableware"

    return updates
