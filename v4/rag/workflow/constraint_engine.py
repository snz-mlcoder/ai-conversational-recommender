# rag/workflow/constraint_engine.py

from typing import List, Dict


def enforce_constraints(results: List[Dict], memory) -> List[Dict]:
    """
    Enforce hard constraints from memory on semantic results.

    This ensures semantic retrieval does not violate structured intent.
    """

    if not results:
        return []

    filtered = []

    for r in results:
        if not _match_product_type(r, memory):
            continue

        if not _match_attributes(r, memory):
            continue

        if not _match_constraints(r, memory):
            continue

        filtered.append(r)

    return filtered


# -------------------------
# Constraint blocks
# -------------------------

def _match_product_type(result: Dict, memory) -> bool:
    if not memory.product_type:
        return True

    product_type = memory.product_type.lower()

    # 1️⃣ Try category first
    category = (result.get("category") or "").lower()
    if product_type in category:
        return True

    # 2️⃣ Fallback: try URL matching
    # TEMPORARY SOLUTION FOR DEMO:
    # Ideally product_type should be stored as structured metadata.
    url = (result.get("url") or "").lower()
    if product_type in url:
        return True

    return False


def _match_attributes(result: Dict, memory) -> bool:
    """
    Generic attribute matcher.
    Works for color, material, size, shape...

    If structured metadata exists, use it.
    Otherwise fallback to URL parsing (temporary demo solution).
   

    if not memory.attributes:
        return True

    url = (result.get("url") or "").lower()

    for key, value in memory.attributes.items():
        value = value.lower()

        # 1️⃣ Try structured metadata first
        result_value = (result.get(key) or "").lower()
        if result_value:
            if value not in result_value:
                return False
            continue

        # 2️⃣ Fallback to URL parsing
        # TEMPORARY SOLUTION FOR DEMO:
        # Attributes should be stored in metadata instead of relying on URL text.
        if value not in url:
            return False """

    return True


def _match_constraints(result: Dict, memory) -> bool:
    """
    Future-proof for numeric constraints (price, volume, etc.)


    if not memory.constraints:
        return True

    for key, value in memory.constraints.items():
        result_value = result.get(key)

        if result_value is None:
            continue

        # Simple equality constraint (can be extended later)
        if result_value != value:
            return False
"""
    return True
