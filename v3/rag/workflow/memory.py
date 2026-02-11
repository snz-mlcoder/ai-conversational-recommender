# rag/workflow/memory.py
# TODO [PHASE-2]: introduce probabilistic memory confidence
from copy import deepcopy
from rag.workflow.schemas import SearchMemory


NEGATION_ANY = "__ANY__"


def normalize_value(value: str | None) -> str | None:
    if value is None:
        return None

    v = value.strip().lower()
    if v in {"", "none", "null", "undefined", "string"}:
        return None

    return v

def sanitize_memory(memory: SearchMemory) -> SearchMemory:
    """
    Return a sanitized copy of memory.
    """
    m = deepcopy(memory)

    m.category = normalize_value(m.category)
    m.product_type = normalize_value(m.product_type)
    m.use_case = normalize_value(m.use_case)

    return m



def update_memory(memory: SearchMemory, updates: dict) -> SearchMemory:
    """
    Deterministic, immutable state reducer for conversational memory.
    """
    # always work on a copy
    new_memory = sanitize_memory(memory)

    if not updates:
        return new_memory

    for key, value in updates.items():

        # 1️⃣ NEGATIONS
        if key == "negations" and isinstance(value, dict):
            for attr, neg_value in value.items():
                if neg_value == NEGATION_ANY:
                    new_memory.attributes.pop(attr, None)
                elif (
                    neg_value
                    and new_memory.attributes.get(attr) == neg_value
                ):
                    new_memory.attributes.pop(attr, None)
            continue

        # 2️⃣ ATTRIBUTES
        if key == "attributes" and isinstance(value, dict):
            cleaned = {
                attr: normalize_value(val)
                for attr, val in value.items()
                if normalize_value(val) is not None
            }

            if cleaned:
                # copy-on-write
                new_attrs = dict(new_memory.attributes)
                new_attrs.update(cleaned)
                new_memory.attributes = new_attrs
            continue

        # 3️⃣ ONLY allow known scalar fields
        if key not in {"category", "product_type", "use_case", "occasion"}:
            continue

        norm_value = normalize_value(value) if isinstance(value, str) else value
        if norm_value is not None:
            setattr(new_memory, key, norm_value)

    return new_memory



# --------------------
# Memory readiness
# --------------------
def memory_ready(memory: SearchMemory) -> bool:
        return bool(memory.product_type)


# --------------------
# Memory → Query text
# --------------------
def memory_to_text(memory: SearchMemory) -> str:
    """
    Deterministic conversion to search query.
    Ordered attributes for reproducibility.
    """
    parts: list[str] = []

    # 1️⃣ product type
    if memory.product_type:
        parts.append(memory.product_type)

    # 2️⃣ occasion
    if getattr(memory, "occasion", None):
        parts.append(f"per {memory.occasion}")

    # 3️⃣ use case
    if memory.use_case:
        parts.append(memory.use_case)

    # 4️⃣ ordered attributes (FIXED ORDER)
    if memory.attributes.get("color"):
        parts.append(memory.attributes["color"])

    if memory.attributes.get("material"):
        parts.append(memory.attributes["material"])

    if memory.attributes.get("size"):
        parts.append(memory.attributes["size"])

    if memory.attributes.get("shape"):
        parts.append(memory.attributes["shape"])

    return " ".join(parts)


def memory_confidence(memory: SearchMemory) -> float:
    """
    Placeholder for future confidence scoring.
    Currently unused.
    """
    return 1.0 if memory.product_type else 0.0
# NOTE:
# memory_confidence will be introduced when
# ask-back / refinement become probabilistic
