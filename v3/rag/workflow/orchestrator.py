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
from rag.workflow.handlers.material_knowledge import handle_material_knowledge
from rag.workflow.handlers.store_info import handle_store_info
from rag.workflow.handlers.promotion import handle_promotion
from rag.workflow.logging import log_event
from rag.workflow.normalization import normalize_text

from rag.workflow.llm_extraction import llm_extract
from rag.workflow.merge_extraction import merge_extractions
from rag.workflow.ask_back_questions import build_ask_back_question_it
from rag.workflow.signals import has_search_signal_from_updates

def needs_llm(rule_updates: dict) -> bool:
    """
    Decide whether LLM extraction is needed.
    LLM is a fallback, not default.
    """
    # If product_type is already known, rules are strong enough
    if rule_updates.get("product_type"):
        return False

    # Otherwise, LLM may help
    return True


def handle_user_message(user_message, memory):
    print("\n========== NEW MESSAGE ==========")
    print("RAW USER MESSAGE:", user_message)

    user_message = normalize_text(user_message)
    print("NORMALIZED MESSAGE:", user_message)

    # 1️⃣ Initial intent (hypothesis)
    initial_intent = detect_intent(user_message)
    intent = initial_intent
    print("INITIAL INTENT:", initial_intent)

    # 2️⃣ Always extract signals (rule + LLM)
    rule_updates = extract_memory(user_message, memory)
    print("RULE UPDATES:", rule_updates)

    llm_updates = {}

    if needs_llm(rule_updates):
        print("🤖 CALLING LLM EXTRACTION")
        llm_updates = llm_extract(user_message)
    else:
        print("⚡ SKIPPING LLM (rule extraction sufficient)")

    print("LLM UPDATES:", llm_updates)


    merged_updates = merge_extractions(rule_updates, llm_updates)
    print("MERGED UPDATES:", merged_updates)

    # 🚨 GUARD: merged_updates sanity
    if not isinstance(merged_updates, dict):
        print("⚠️ MERGED UPDATES IS NOT A DICT!")
        merged_updates = {}

        # 3️⃣ Intent stabilization
    # 3️⃣ Intent stabilization (FINAL, CORRECT)
    if intent == Intent.SMALL_TALK:
        if has_search_signal_from_updates(merged_updates):
            print("🔥 INTENT RESCUED BY SEARCH SIGNAL")
            intent = Intent.PRODUCT_SEARCH
        else:
            print("❌ NO SEARCH SIGNAL → intent stays SMALL_TALK")


    # 4️⃣ Update memory only if search
    if intent == Intent.PRODUCT_SEARCH:
        print("🧠 UPDATING MEMORY WITH:", merged_updates)
        memory = update_memory(memory, merged_updates)
    else:
        print("🧠 MEMORY NOT UPDATED (intent is not search)")

    print("MEMORY STATE:", memory)

    # 5️⃣ Ask-back decision
    ask_back = decide_ask_back(memory)
    print("ASK_BACK DECISION:", ask_back)

    # 6️⃣ Log AFTER everything is known
    log_event(
        event_type="user_message",
        payload={
            "message": user_message,
            "initial_intent": initial_intent.value,
            "final_intent": intent.value,
            "ask_back": ask_back.should_ask if intent == Intent.PRODUCT_SEARCH else False,
        },
    )

    # 7️⃣ Early exits (non-search handlers)
    if intent == Intent.MATERIAL_KNOWLEDGE:
        print("➡️ MATERIAL KNOWLEDGE HANDLER")
        return handle_material_knowledge(user_message), memory, {"intent": intent.value}

    if intent == Intent.STORE_INFO:
        print("➡️ STORE INFO HANDLER")
        return handle_store_info(user_message), memory, {"intent": intent.value}

    if intent == Intent.PROMOTION:
        print("➡️ PROMOTION HANDLER")
        return handle_promotion(user_message), memory, {"intent": intent.value}

    # 8️⃣ Blocking Ask-back ONLY if product_type missing
    if ask_back.should_ask:
            question = build_ask_back_question_it(
                ask_back.slot,
                memory,
            )
            return question, memory, {
                "intent": intent.value,
                "ask_back": True,
                "slot": ask_back.slot,
                "reason": ask_back.reason,
            }
    # 9️⃣ Final guard
    if intent != Intent.PRODUCT_SEARCH:
        print("🚪 FINAL GUARD HIT → returning small talk fallback")
        return "Hi! How can I help you?", memory, {"intent": intent.value}

    # 🔟 RAG flow
    print("🔎 ENTERING RAG FLOW")
    rag_query = build_rag_query(memory, user_message)
    print("RAG QUERY:", rag_query)

    results = call_rag(rag_query)
    print("RAG RESULTS COUNT:", len(results))

    reply = generate_explanation(results)

    refinements = suggest_refinements(memory)
    print("REFINEMENTS:", refinements)

    refinement_question = build_refinement_question_it(refinements)
    if refinement_question:
        reply += "\n\n" + refinement_question

    print("✅ RESPONSE READY")
    return reply, memory, {
        "intent": intent.value,
        "rag_called": True,
        "num_results": len(results),
        "results": results[:5],
        "refinement_suggested": bool(refinement_question),
    }


'''بعداً می‌تونی:

question = llm_generate_question(
    slot=ask_back.slot,
    memory=memory,
    locale="it"

    این یعنی:

به‌جای سوال‌های hardcode مثل:

"Che tipo di prodotto stai cercando?"


می‌خوای LLM:

با توجه به slot (مثلاً product_type)

و memory فعلی

یک سوال طبیعی و context-aware بسازه

📌 این LLM-based ask-back generation هست.
چرا عمداً هنوز LLM ask-back رو فعال نکردیم؟

چون ترتیب درست اینه:

1️⃣ اول: تصمیم ask-back (policy)

آیا باید سوال بپرسیم؟

کِی؟

blocking یا non-blocking؟

⬅️ اینو الان کاملاً درست کردیم.
)'''