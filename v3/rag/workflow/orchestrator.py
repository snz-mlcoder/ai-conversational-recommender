# rag/workflow/orchestrator.py

from rag.workflow.intent import Intent , detect_intent
from rag.workflow.memory import update_memory, memory_ready
from rag.workflow.search_step import build_rag_query, call_rag
from rag.workflow.explanation import generate_explanation
from rag.workflow.extraction import extract_memory_updates


def handle_user_message(user_message, memory):
    intent = detect_intent(user_message)

    # 🧠 Extract → Update
    updates = extract_memory_updates(user_message, memory)
    memory = update_memory(memory, updates)

    # 🔥 Memory-first override
    if memory_ready(memory):
        intent = Intent.PRODUCT_SEARCH

    if intent != Intent.PRODUCT_SEARCH:
        return (
            "Hi! How can I help you?",
            memory,
            {
                "intent": intent.value,
                "rag_called": False
            }
        )

    rag_query = build_rag_query(memory)
    results = call_rag(rag_query)
    reply = generate_explanation(results)

    return reply, memory, {
        "intent": intent.value,
        "rag_called": True
    }


    '''بعداً (v2) چی می‌شه؟

بعداً این لایه میاد وسط:

updates = extract_memory_updates(user_message, memory)
memory = update_memory(memory, updates)


ولی الان عمداً نداریمش و این کاملاً درسته.'''



    memory = update_memory(memory, {})

    if not memory_ready(memory):
        return (
            "Can you tell me more?",
            memory,
            {
                "intent": intent.value,
                "rag_called": False
            }
        )

    rag_query = build_rag_query(memory)
    results = call_rag(rag_query)

    reply = generate_explanation(results)

    return (
        reply,
        memory,
        {
            "intent": intent.value,
            "rag_called": True
        }
    )