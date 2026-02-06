# rag/workflow/extraction.py

from typing import Dict
from rag.workflow.schemas import SearchMemory
from rag.workflow.signals import extract_product_signals
from rag.workflow.vocab import PRODUCT_SIGNAL_GROUPS, NEGATION_WORDS


NEGATION_ANY = "__ANY__"


def extract_negations(text: str) -> dict:
    text = text.lower()
    negations: dict = {}

    # اگر اصلاً negation word نداشت، سریع خارج شو
    if not any(n in text for n in NEGATION_WORDS):
        return negations

    # روی همه‌ی گروه‌ها loop بزن
    for group_name, vocab in PRODUCT_SIGNAL_GROUPS.items():

        # فقط attribute-like groups
        if group_name not in {"colors", "materials", "sizes", "shapes"}:
            continue

        found = [term for term in vocab if term in text]

        if not found:
            continue

        # چند مقدار → remove whole attribute
        if len(found) >= 2:
            negations[group_name[:-1]] = NEGATION_ANY
        else:
            # یک مقدار → remove specific value
            negations[group_name[:-1]] = found[0]

    return negations



def extract_memory(
    user_message: str,
    memory: SearchMemory
) -> Dict:
    """
    Domain-aware memory extractor.
    Reuses product signal extraction from intent layer.
    """

    signals = extract_product_signals(user_message)
    updates: Dict = {}
    negations = extract_negations(user_message)
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
    # occasion
    # --------------------

    if "occasions" in signals:
         updates["occasion"] = signals["occasions"][0]

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
    # negations
    # --------------------
    if negations:
        updates["negations"] = negations

    # --------------------
    # conservative category
    # --------------------
    if not memory.category and "items" in signals:
        updates["category"] = "tableware"

    return updates