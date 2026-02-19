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
    Production-safe version with scoped reset logic.
    """

    new_memory = sanitize_memory(memory)

    if not updates:
        return new_memory

    previous_product = new_memory.product_type
    previous_use_case = new_memory.use_case
    previous_occasion = new_memory.occasion

    for key, value in updates.items():

        # =====================================================
        # 1️⃣ NEGATIONS
        # =====================================================
        if key == "negations" and isinstance(value, dict):

            for attr, neg_value in value.items():

                if attr == "product_type":
                    if neg_value == NEGATION_ANY:
                        new_memory.product_type = None
                    elif new_memory.product_type == neg_value:
                        new_memory.product_type = None
                    continue

                if neg_value == NEGATION_ANY:
                    new_attrs = dict(new_memory.attributes)
                    new_attrs.pop(attr, None)
                    new_memory.attributes = new_attrs

                elif neg_value and new_memory.attributes.get(attr) == neg_value:
                    new_attrs = dict(new_memory.attributes)
                    new_attrs.pop(attr, None)
                    new_memory.attributes = new_attrs

            continue

        # =====================================================
        # 2️⃣ CONSTRAINTS
        # =====================================================
        if key == "constraints" and isinstance(value, dict):

            if value:
                new_constraints = dict(new_memory.constraints)
                new_constraints.update(value)
                new_memory.constraints = new_constraints

            continue

        # =====================================================
        # 3️⃣ EXCLUSIONS
        # =====================================================
        if key == "exclusions" and isinstance(value, dict):

            if value:
                new_exclusions = dict(new_memory.exclusions)
                new_exclusions.update(value)
                new_memory.exclusions = new_exclusions

            continue

        # =====================================================
        # 4️⃣ ATTRIBUTES
        # =====================================================
        if key == "attributes" and isinstance(value, dict):

            cleaned = {
                attr: normalize_value(val)
                for attr, val in value.items()
                if normalize_value(val) is not None
            }

            if cleaned:
                new_attrs = dict(new_memory.attributes)
                new_attrs.update(cleaned)
                new_memory.attributes = new_attrs

            continue

        # =====================================================
        # 5️⃣ SCALAR FIELDS
        # =====================================================
        if key in {"category", "product_type", "use_case", "occasion"}:

            norm_value = normalize_value(value) if isinstance(value, str) else value

            if norm_value is None:
                continue

            # 🔥 اگر product_type عوض شد → search context reset
            if key == "product_type":
                if previous_product and previous_product != norm_value:
                    new_memory.use_case = None
                    new_memory.occasion = None
                    new_memory.attributes = {}
                    new_memory.constraints = {}

                setattr(new_memory, key, norm_value)
                continue

            # 🔥 اگر use_case عوض شد ولی product ثابت است
            if key == "use_case":
                if previous_use_case and previous_use_case != norm_value:
                    new_memory.attributes = {}
                    new_memory.constraints = {}

                setattr(new_memory, key, norm_value)
                continue

            # 🔥 occasion فقط context hint است → reset نکن
            setattr(new_memory, key, norm_value)
            continue

        # =====================================================
        # 6️⃣ SEMANTIC SOFT SIGNALS (LLM)
        # =====================================================
        if key in {"style", "target", "mood"} and isinstance(value, str):
            norm_value = normalize_value(value)
            if norm_value:
                new_constraints = dict(new_memory.constraints)
                new_constraints[key] = norm_value
                new_memory.constraints = new_constraints
            continue

        # -----------------------------------------------------
        # Unknown keys → ignore safely
        # -----------------------------------------------------

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
