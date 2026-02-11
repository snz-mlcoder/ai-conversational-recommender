# rag/workflow/orchestrator.py

from uuid import uuid4
import os

from rag.workflow.intent import Intent, detect_intent
from rag.workflow.memory import update_memory
from rag.workflow.search_step import build_rag_query, call_rag
from rag.workflow.explanation import generate_explanation
from rag.workflow.extraction import extract_memory
from rag.workflow.ask_back import decide_ask_back
from rag.workflow.ask_back_questions import (
    build_refinement_question_it,
    build_ask_back_question_it,
    build_item_ambiguity_question_it,
)
from rag.workflow.refinement import suggest_refinements
from rag.workflow.handlers.material_knowledge import handle_material_knowledge
from rag.workflow.handlers.store_info import handle_store_info
from rag.workflow.handlers.promotion import handle_promotion
from rag.workflow.logging import log_event
from rag.workflow.normalization import normalize_text
from rag.workflow.llm_extraction import llm_extract
from rag.workflow.merge_extraction import merge_extractions
from rag.workflow.signals import (
    extract_product_signals,
    detect_item_mode,
    ItemMode,
    detect_attribute_mode,
    AttributeMode,
    has_search_signal_from_updates,
)
from rag.workflow.goal import decide_goal, GoalDecision

# ---------------------------
# Debug / Logging helpers
# ---------------------------

DEBUG = os.getenv("DEBUG", "false").lower() == "true"


def debug_print(stage: str, payload):
    if DEBUG:
        print(f"[DEBUG:{stage}]", payload)


def log_system(trace_id, reply, **meta):
    log_event(
        "system_response",
        {
            "trace_id": trace_id,
            "reply": reply,
            **meta,
        },
    )


# ---------------------------
# Helpers
# ---------------------------

def needs_llm(rule_updates: dict) -> bool:
    return not rule_updates.get("product_type")


def resolve_attribute_intent(user_message: str) -> Intent | None:
    """
    Decide if attribute usage implies KNOWLEDGE or SEARCH.
    Returns Intent override or None.
    """
    signals = extract_product_signals(user_message)

    for group in ("colors", "materials", "sizes", "shapes"):
        values = signals.get(group)
        if not values or len(values) < 2:
            continue

        mode = detect_attribute_mode(user_message, values)

        if mode == AttributeMode.COMPARISON:
            return Intent.MATERIAL_KNOWLEDGE

        if mode == AttributeMode.AMBIGUOUS:
            return None

    return None


# ===========================
# Pipeline stages
# ===========================

def normalize_stage(user_message: str) -> str:
    return normalize_text(user_message)


def intent_stage(normalized: str) -> Intent:
    return detect_intent(normalized)


def rule_extraction_stage(normalized: str, memory):
    return extract_memory(normalized, memory)


def llm_fallback_stage(normalized: str, rule_updates: dict) -> dict:
    if needs_llm(rule_updates):
        return llm_extract(normalized)
    return {}


def item_conflict_stage(normalized: str, intent: Intent):
    signals = extract_product_signals(normalized)
    items = signals.get("items", [])

    if len(items) < 2:
        return intent, None

    item_mode = detect_item_mode(normalized, items)

    if item_mode == ItemMode.COMPARISON:
        question = build_item_ambiguity_question_it(items)
        return Intent.SMALL_TALK, {
            "type": "ask_back",
            "question": question,
            "reason": "item_comparison",
            "items": items,
        }

    if item_mode == ItemMode.MULTI_SEARCH:
        return Intent.PRODUCT_SEARCH, None

    return intent, None


def memory_update_stage(intent: Intent, memory, merged_updates: dict):
    if intent == Intent.PRODUCT_SEARCH:
        return update_memory(memory, merged_updates)
    return memory


def ask_back_stage(intent: Intent, memory):
    if intent != Intent.PRODUCT_SEARCH:
        return None

    ask_back = decide_ask_back(memory)
    if ask_back.should_ask:
        return build_ask_back_question_it(ask_back.slot, memory)

    return None


def execution_stage(intent: Intent, normalized: str, memory):
    if intent == Intent.MATERIAL_KNOWLEDGE:
        return handle_material_knowledge(normalized)

    if intent == Intent.STORE_INFO:
        return handle_store_info(normalized)

    if intent == Intent.PROMOTION:
        return handle_promotion(normalized)

    return None


# ===========================
# Main orchestrator
# ===========================

def handle_user_message(user_message, memory):
    trace_id = str(uuid4())

    # 1. Normalize
    normalized = normalize_stage(user_message)
    debug_print("NORMALIZED", normalized)

    # 2. Intent detection
    initial_intent = intent_stage(normalized)
    intent = initial_intent
    debug_print("INTENT_INITIAL", intent.value)

    # 3. Rule extraction
    rule_updates = rule_extraction_stage(normalized, memory)
    debug_print("RULE_UPDATES", rule_updates)

    # 4. Item conflict
    intent, interrupt = item_conflict_stage(normalized, intent)
    if interrupt:
        log_system(
            trace_id,
            interrupt["question"],
            intent="ask_back",
            reason=interrupt["reason"],
            items=interrupt["items"],
        )
        return interrupt["question"], memory, interrupt

    # 5. Attribute intent override
    attr_intent = resolve_attribute_intent(normalized)
    if attr_intent:
        intent = attr_intent
        debug_print("INTENT_OVERRIDE", intent.value)

    # 6. LLM fallback + merge
    llm_updates = llm_fallback_stage(normalized, rule_updates)
    debug_print("LLM_UPDATES", llm_updates)

    merged_updates = merge_extractions(rule_updates, llm_updates)
    debug_print("MERGED_UPDATES", merged_updates)

    # 6.1 Intent stabilization (IMPORTANT)
    if intent == Intent.SMALL_TALK:
        if merged_updates.get("product_type"):
            intent = Intent.PRODUCT_SEARCH
            debug_print("INTENT_STABILIZED", intent.value)

    # USER log (after stabilization)
    log_event(
        "user_message",
        {
            "trace_id": trace_id,
            "message": normalized,
            "initial_intent": initial_intent.value,
            "final_intent": intent.value,
        },
    )


    # 7. Memory update
    memory = memory_update_stage(intent, memory, merged_updates)
    debug_print("MEMORY", memory.dict())

    # ===============================
    # 7.1 GOAL / ANSWERABILITY LAYER
    # ===============================
    goal = decide_goal(intent, memory, normalized)
    debug_print("GOAL_DECISION", goal.value)

    # 🚫 HARD GATES — NOTHING PASSES BELOW
    if goal == GoalDecision.SUGGEST:
        reply = (
            "Posso aiutarti con qualche idea. "
            "Ad esempio: piatti, bicchieri o accessori "
            f"per {memory.occasion or 'la tua occasione'}?"
        )
        log_system(trace_id, reply, intent="suggest", goal="suggest")
        return reply, memory, {"intent": "suggest", "goal": "suggest"}

    if goal == GoalDecision.ASK_BACK:
        question = build_ask_back_question_it("product_type", memory)
        log_system(
            trace_id,
            question,
            intent="ask_back",
            goal="ask_back",
            reason="goal_ambiguity",
        )
        return question, memory, {"intent": "ask_back", "goal": "ask_back"}

    # ===============================
    # 8. Ask-back (slot-based, ONLY if ANSWER)
    # ===============================
    ask_back_question = ask_back_stage(intent, memory)
    if ask_back_question:
        log_system(trace_id, ask_back_question, intent=intent.value)
        return ask_back_question, memory, {
            "intent": intent.value,
            "ask_back": True,
        }

    # ===============================
    # 9. Early execution (NON SEARCH)
    # ===============================
    early_reply = execution_stage(intent, normalized, memory)
    if early_reply:
        log_system(trace_id, early_reply, intent=intent.value)
        return early_reply, memory, {"intent": intent.value}

    # ===============================
    # 10. 🔒 RAG FLOW (ONLY PATH)
    # ===============================
    if intent != Intent.PRODUCT_SEARCH:
        fallback = "Come posso aiutarti?"
        log_system(trace_id, fallback, intent=intent.value)
        return fallback, memory, {"intent": intent.value}

    rag_query = build_rag_query(memory, normalized)
    results = call_rag(rag_query)

    reply = generate_explanation(results)

    refinements = suggest_refinements(memory)
    refinement_question = build_refinement_question_it(refinements)
    if refinement_question:
        reply += "\n\n" + refinement_question

    log_system(
        trace_id,
        reply,
        intent=intent.value,
        rag_called=True,
        results=results[5:],  # log only top 5 for debugging
        num_results=len(results),
    )

    return reply, memory, {
        "intent": intent.value,
        "rag_called": True,
        "num_results": len(results),
    }
