# rag/workflow/orchestrator.py

from rag.workflow.intent import Intent, detect_intent
from rag.workflow.memory import update_memory, memory_ready
from rag.workflow.search_step import build_rag_query, call_rag
from rag.workflow.explanation import generate_explanation
from rag.workflow.extraction import extract_memory


def handle_user_message(user_message, memory):


    # 1️⃣ Detect intent (initial guess)
    intent = detect_intent(user_message)

    # 2️⃣ Extract & update memory
    updates = extract_memory(user_message, memory)
    memory = update_memory(memory, updates)

    # 3️⃣ Memory-first override
    if memory_ready(memory):
        intent = Intent.PRODUCT_SEARCH

    # 4️⃣ Non-search intents
    if intent != Intent.PRODUCT_SEARCH:
        return (
            "Hi! How can I help you?",
            memory,
            {
                "intent": intent.value,
                "rag_called": False,
            }
        )

    # 5️⃣ RAG flow
    rag_query = build_rag_query(memory, user_message)
    results = call_rag(rag_query)

    reply = generate_explanation(results)

    return (
        reply,
        memory,
        {
            "intent": intent.value,
            "rag_called": True,
            "num_results": len(results),
            "results": results[:5],
        }
    )
