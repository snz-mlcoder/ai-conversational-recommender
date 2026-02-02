# rag/workflow/memory.py

from rag.workflow.schemas import SearchMemory


def update_memory(memory, updates: dict):
    if not updates:
        return memory

    for key, value in updates.items():
        setattr(memory, key, value)

    return memory




def memory_ready(memory) -> bool:
    """
    MVP readiness check.
    We only require high-signal fields.
    """

    required_fields = [
        memory.category,
        memory.product_type,
        memory.use_case,
    ]

    filled = [f for f in required_fields if f and f.strip()]

    return len(filled) >= 2

"""علتی که اینجوری چک می‌کنیم چیه؟

اگر حداقل ۲ تا از اینا باشه → OK

attributes اصلاً مهم نیست

بعداً راحت می‌تونی rule رو تغییر بدی"""


def memory_to_text(memory: SearchMemory) -> str:
    """
    Deterministic conversion to search query.
    """
    parts = []

    if memory.product_type:
        parts.append(memory.product_type)

    if memory.use_case:
        parts.append(f"for {memory.use_case}")

    for k, v in memory.attributes.items():
        parts.append(f"{v} {k}")

    return " ".join(parts)
