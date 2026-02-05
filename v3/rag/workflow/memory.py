# rag/workflow/memory.py

from rag.workflow.schemas import SearchMemory


def normalize_value(value: str | None) -> str | None:
    if value is None:
        return None

    v = value.strip().lower()

    if v in {"", "string", "none", "null", "undefined"}:
        return None

    return value


def update_memory(memory, updates: dict):
    if not updates:
        return memory

    for key, value in updates.items():

        # 🔥 attributes: merge only
        if key == "attributes" and isinstance(value, dict):
            for attr_key, attr_value in value.items():
                if isinstance(attr_value, str):
                    attr_value = normalize_value(attr_value)
                if attr_value is not None:
                    memory.attributes[attr_key] = attr_value
            continue

        # normal fields
        if isinstance(value, str):
            value = normalize_value(value)

        if value is not None:
            setattr(memory, key, value)

    return memory




def memory_ready(memory) -> bool:
    required_fields = [
        normalize_value(memory.category),
        normalize_value(memory.product_type),
        normalize_value(memory.use_case),
    ]

    filled = [f for f in required_fields if f]

    return len(filled) >= 2


def memory_to_text(memory: SearchMemory) -> str:
    """
    Deterministic conversion to search query.
    """
    parts: list[str] = []

    if memory.product_type:
        parts.append(str(memory.product_type))

    if memory.use_case:
        parts.append(str(memory.use_case))

    for v in memory.attributes.values():
        if isinstance(v, str):
            parts.append(v)

    return " ".join(parts)


