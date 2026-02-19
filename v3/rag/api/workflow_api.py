from rag.workflow.orchestrator import handle_user_message
from rag.workflow.schemas import SearchMemory


def run_workflow(user_message: str, memory: SearchMemory):

    ALLOWED_ATTRS = {"color", "material", "size", "shape"}

    memory.attributes = {
        k: v for k, v in (memory.attributes or {}).items()
        if k in ALLOWED_ATTRS
    }

   

    return handle_user_message(user_message, memory)
