from rag.workflow.orchestrator import handle_user_message
from rag.workflow.schemas import SearchMemory

def run_workflow(user_message, memory_payload):
    # 🔁 ADAPTER: API → Workflow
    memory = SearchMemory(
        category=memory_payload.category,
        product_type=memory_payload.product_type,
        use_case=memory_payload.use_case,
        attributes=memory_payload.attributes or {},
    )

    return handle_user_message(user_message, memory)