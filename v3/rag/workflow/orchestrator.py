# rag/workflow/orchestrator.py

from rag.workflow.intent import Intent, detect_intent
from rag.workflow.memory import update_memory, memory_ready
from rag.workflow.search_step import build_rag_query, call_rag
from rag.workflow.explanation import generate_explanation
from rag.workflow.extraction import extract_memory
from rag.workflow.ask_back import decide_ask_back
from rag.workflow.ask_back_questions import (
    ASK_BACK_QUESTIONS_IT, build_refinement_question_it,
)
from rag.workflow.refinement import suggest_refinements


def handle_user_message(user_message, memory):

    # 1️⃣ Detect intent
    intent = detect_intent(user_message)

    # 2️⃣ Extract & update memory
    updates = extract_memory(user_message, memory)
    memory = update_memory(memory, updates)

    # 2.5️⃣ Blocking Ask-Back (pre-RAG)
    ask_back = decide_ask_back(memory)
    if ask_back.should_ask:
        question = ASK_BACK_QUESTIONS_IT.get(
            ask_back.slot,
            "Puoi darmi qualche dettaglio in più?"
        )
        return (
            question,
            memory,
            {
                "intent": intent.value,
                "ask_back": True,
                "slot": ask_back.slot,
                "reason": ask_back.reason,
            }
        )

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

    # 6️⃣ 🔹 Refinement suggestion (non-blocking, post-RAG)
    refinements = suggest_refinements(memory)
    refinement_question = build_refinement_question_it(refinements)

    if refinement_question:
        reply = reply + "\n\n" + refinement_question

    return (
        reply,
        memory,
        {
            "intent": intent.value,
            "rag_called": True,
            "num_results": len(results),
            "results": results[:5],
            "refinement_suggested": bool(refinement_question),
        }
    )


'''بعداً می‌تونی:

question = llm_generate_question(
    slot=ask_back.slot,
    memory=memory,
    locale="it"
)'''