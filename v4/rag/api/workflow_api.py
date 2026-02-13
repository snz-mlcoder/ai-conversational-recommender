from rag.workflow.orchestrator import handle_user_message
from rag.workflow.schemas import SearchMemory

def run_workflow(user_message, memory_payload):

    # 🔥 sanitize attributes (remove swagger placeholders)
    raw_attrs = memory_payload.attributes or {}

    ALLOWED_ATTRS = {"color", "material", "size", "shape"}

    clean_attrs = {
        k: v for k, v in raw_attrs.items()
        if k in ALLOWED_ATTRS
}

    memory = SearchMemory(
        category=memory_payload.category,
        product_type=memory_payload.product_type,
        use_case=memory_payload.use_case,
        attributes=clean_attrs,
    )

    return handle_user_message(user_message, memory)
