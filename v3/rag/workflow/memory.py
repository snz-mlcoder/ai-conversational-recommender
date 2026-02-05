# rag/workflow/memory.py

from rag.workflow.schemas import SearchMemory


NEGATION_ANY = "__ANY__"


def normalize_value(value: str | None) -> str | None:
    if value is None:
        return None

    v = value.strip().lower()
    if v in {"", "none", "null", "undefined", "string"}:
        return None

    return v

def sanitize_memory(memory):
    memory.category = normalize_value(memory.category)
    memory.product_type = normalize_value(memory.product_type)
    memory.use_case = normalize_value(memory.use_case)
    return memory


def update_memory(memory: SearchMemory, updates: dict) -> SearchMemory:
    """
    Deterministic state reducer for conversational memory.
    """
    memory = sanitize_memory(memory)

    if not updates:
        return memory

    for key, value in updates.items():

        # 1️⃣ NEGATIONS
        if key == "negations" and isinstance(value, dict):
            for attr, neg_value in value.items():
                if neg_value == NEGATION_ANY:
                    memory.attributes.pop(attr, None)

                elif neg_value and memory.attributes.get(attr) == neg_value:
                    memory.attributes.pop(attr, None)

            continue

        # 2️⃣ ATTRIBUTES
        if key == "attributes" and isinstance(value, dict):
            cleaned = {
                attr: normalize_value(val)
                for attr, val in value.items()
                if normalize_value(val) is not None
            }

            if cleaned:
                memory.attributes.update(cleaned)

            continue

       # 3️⃣ ONLY allow known scalar fields
        if key not in {"category", "product_type", "use_case"}:
            continue  # 🚫 ignore unknown keys safely
        norm_value = normalize_value(value) if isinstance(value, str) else value
        if norm_value is not None:
            setattr(memory, key, norm_value)

    return memory



# --------------------
# Memory readiness
# --------------------
def memory_ready(memory: SearchMemory) -> bool:
    required_fields = [
        normalize_value(memory.category),
        normalize_value(memory.product_type),
        normalize_value(memory.use_case),
    ]

    filled = [f for f in required_fields if f]
    return len(filled) >= 2


# --------------------
# Memory → Query text
# --------------------
def memory_to_text(memory: SearchMemory) -> str:
    """
    Deterministic conversion to search query.
    No guessing. No noise.
    """
    parts: list[str] = []

    if memory.product_type:
        parts.append(memory.product_type)

    if memory.use_case:
        parts.append(memory.use_case)

    for v in memory.attributes.values():
        if isinstance(v, str) and v.strip():
            parts.append(v)

    return " ".join(parts)

