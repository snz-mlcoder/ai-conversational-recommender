from typing import List, Dict, Tuple
from copy import deepcopy
from rag.workflow.constraint_engine import enforce_constraints


def relax_constraints(results: List[Dict], memory) -> Tuple[List[Dict], str | None]:
    """
    Try dropping attributes one by one (priority order)
    to recover results instead of returning empty.
    """

    if not memory.attributes:
        return [], None

    attributes = list(memory.attributes.items())

    # اولویت ریلکس:
    # رنگ → سایز → متریال → ...
    priority_order = ["color", "size", "material"]

    sorted_attrs = sorted(
        attributes,
        key=lambda x: priority_order.index(x[0]) if x[0] in priority_order else 99
    )

    for key, value in sorted_attrs:

        temp_memory = deepcopy(memory)
        temp_memory.attributes.pop(key, None)

        relaxed = enforce_constraints(results, temp_memory)

        if relaxed:
            return relaxed, key

    return [], None
