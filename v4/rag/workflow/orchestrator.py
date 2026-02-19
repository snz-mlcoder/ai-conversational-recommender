# rag/workflow/orchestrator.py
# LEGACY ORCHESTRATOR
# Will be replaced by WorkflowEngine after full parity.

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
from rag.workflow.result_validation import validate_results_with_llm
from rag.workflow.constraint_engine import enforce_constraints
from rag.workflow.relaxation_engine import relax_constraints
from rag.workflow.non_search_reply import generate_non_search_reply
from rag.workflow.handlers.suggest import handle_suggest
from rag.workflow.llm_signal_extractor import extract_semantic_signals

from rag.workflow.handlers.product_search import handle_product_search


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
def log_trace(trace_id: str, stage: str, payload: dict):
    log_event(
        "trace",
        {
            "trace_id": trace_id,
            "stage": stage,
            **payload,
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


def intent_stage(normalized: str, memory) -> Intent:
    return detect_intent(normalized,memory)


def rule_extraction_stage(normalized: str, memory):
    return extract_memory(normalized, memory)

USE_LLM_FALLBACK = True  # toggle for testing LLM fallback impact on logs and performance

def llm_fallback_stage(normalized: str, rule_updates: dict, intent):

    if intent != "product_search":
        return {}

    if not USE_LLM_FALLBACK:
        return {}

    return llm_extract(normalized)



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

    # اگر update داریم، همیشه memory را update کن
    if merged_updates:
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
    
    return None



def should_call_llm_for_signals(rule_updates: dict) -> bool:
    # اگر product_type نداریم یا occasion نداریم
    if not rule_updates.get("product_type"):
        return True
    
    if not rule_updates.get("occasion"):
        return True
    
    return False



# ===========================
# Main orchestrator
# ===========================

def handle_user_message(user_message, memory):
    trace_id = str(uuid4())

    log_trace(trace_id, "00_start", {
        "memory_initial": memory.dict()
    })


    # 1. Normalize
    normalized = normalize_stage(user_message)
    debug_print("NORMALIZED", normalized)
    log_trace(trace_id, "01_normalize", {
        "user_message": user_message,
        "normalized": normalized
    })


    # 2. Intent detection
    initial_intent = intent_stage(normalized, memory)
    intent = initial_intent
    debug_print("INTENT_INITIAL", intent.value)
    log_trace(trace_id, "02_intent_detection", {
        "initial_intent": initial_intent.value,
        "memory_before": memory.dict()
    })

    # --------------------------------------------------
    # 🔥 Domain Semantic Rescue (LLM fallback)
    # --------------------------------------------------
    from rag.workflow.signals import has_search_signal

    if intent == Intent.SMALL_TALK and not has_search_signal(normalized):

        try:
            from rag.llm.openai_client import openai_client

            domain_prompt = f"""
            Is this message related to kitchen or tableware products?

            Message: {normalized}

            Answer only yes or no.
            """

            domain_answer = openai_client.generate(
                domain_prompt,
                temperature=0.0,
            ).strip().lower()

            if "yes" in domain_answer:
                intent = Intent.PRODUCT_SEARCH
                debug_print("INTENT_DOMAIN_RESCUE", intent.value)

                log_trace(trace_id, "02.1_domain_rescue", {
                    "rescued_intent": intent.value,
                    "domain_answer": domain_answer
                })

        except Exception as e:
            debug_print("DOMAIN_RESCUE_ERROR", str(e))

    # 3. Rule extraction
    # 3️⃣ Rule extraction (deterministic backbone)
    rule_updates = rule_extraction_stage(normalized, memory)

    # 3.1️⃣ LLM semantic signal rescue (only if needed)
    llm_updates = {}

    if should_call_llm_for_signals(rule_updates):
        llm_updates = extract_semantic_signals(normalized)

    # 3.2️⃣ Merge signals
    merged_updates = merge_extractions(rule_updates, llm_updates)
    debug_print("RULE_UPDATES", rule_updates)
    
    log_trace(trace_id, "03_rule_extraction", {
        "rule_updates": rule_updates,
        "llm_updates": llm_updates,
        "merged_updates": merged_updates,
        "memory_before": memory.dict()
    })

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
    
    log_trace(trace_id, "04_item_conflict", {
        "intent_after_item_conflict": intent.value,
        "interrupt": interrupt
        })

    # 5. Attribute intent override
    attr_intent = resolve_attribute_intent(normalized)
    if attr_intent:
        intent = attr_intent
        debug_print("INTENT_OVERRIDE", intent.value)
    log_trace(trace_id, "05_attribute_intent_override", {
        "intent_after_attribute_override": intent.value,
        "attr_intent": attr_intent.value if attr_intent else None
    })  

    # 6. LLM fallback + merge
    llm_updates = llm_fallback_stage(normalized, rule_updates, intent.value)
    debug_print("LLM_UPDATES", llm_updates)
    log_trace(trace_id, "06_llm_fallback", {
        "llm_updates": llm_updates,
        "rule_updates": rule_updates
    })  

    merged_updates = merge_extractions(rule_updates, llm_updates)
    debug_print("MERGED_UPDATES", merged_updates)
    log_trace(trace_id, "07_merge_extractions", {
        "merged_updates": merged_updates
    })  

    print("INTENT FINAL:", intent)
    print("MERGED_UPDATES:", merged_updates)

 

    # 6.1 Intent stabilization (IMPORTANT)
    if intent == Intent.SMALL_TALK:
        if merged_updates.get("product_type"):
            intent = Intent.PRODUCT_SEARCH
            debug_print("INTENT_STABILIZED", intent.value)
        log_trace(trace_id, "06.1_intent_stabilization", {
            "intent_after_stabilization": intent.value,
            "updates_for_stabilization": merged_updates
        })

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

    print("MERGED_UPDATES:", merged_updates)
    # 6.2 Intent correction for attribute continuation
    if (
        memory.product_type
        and not merged_updates.get("product_type")
        and merged_updates.get("attributes")
    ):
        intent = Intent.PRODUCT_SEARCH
        debug_print("INTENT_CORRECTED_TO_SEARCH", intent.value)
        log_trace(trace_id, "06.2_intent_correction", {
            "intent_after_correction": intent.value,
            "reason": "attribute_continuation",
            "memory_product_type": memory.product_type,
            "merged_attributes": merged_updates.get("attributes")
        })
    # 7. Memory update
    memory = memory_update_stage(intent, memory, merged_updates)
    debug_print("MEMORY", memory.dict())

    print("MEMORY AFTER UPDATE:", memory.dict())
    log_trace(trace_id, "07_memory_update", {
        "memory_after_update": memory.dict()
    })


    # ===============================
    # 7.1 GOAL / ANSWERABILITY LAYER
    # ===============================
    goal = decide_goal(intent, memory, normalized)
    debug_print("GOAL_DECISION", goal.value)
    log_trace(trace_id, "07.1_goal_decision", {
        "goal_decision": goal.value,
        "intent": intent.value,
        "memory": memory.dict()
    })

    # 🚫 HARD GATES — NOTHING PASSES BELOW 
    
    if goal == GoalDecision.SUGGEST:
        reply = handle_suggest(normalized, memory)

        log_system(
            trace_id,
            reply,
            intent=intent.value,
            goal="suggest",
            rag_called=False
        )

        return reply, memory, {
            "intent": intent.value,
            "goal": "suggest",
            "rag_called": False
        }


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
    
    log_trace(trace_id, "07.1.2_goal_ask_back", {
        "goal_ask_back": goal == GoalDecision.ASK_BACK
    })  

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
    log_trace(trace_id, "08_ask_back", {
        "ask_back_question": ask_back_question,
        "intent": intent.value
    })

    # ===============================
    # 9. Early execution (NON SEARCH)
    # ===============================
    early_reply = execution_stage(intent, normalized, memory)
    if early_reply:
        log_system(trace_id, early_reply, intent=intent.value)
        return early_reply, memory, {"intent": intent.value}
    log_trace(trace_id, "09_execution", {
        "early_reply": early_reply,
        "intent": intent.value
    })


    # ==========================================
    # HARD GUARD — ONLY PRODUCT_SEARCH CAN RAG
    # ==========================================
    if intent != Intent.PRODUCT_SEARCH:
        reply = generate_non_search_reply(intent, memory, normalized)

        log_system(
            trace_id,
            reply,
            intent=intent.value,
            rag_called=False
        )

        return reply, memory, {
            "intent": intent.value,
            "rag_called": False
        }

    # ===============================
    # 10. RAG FLOW
    # ===============================

    if intent == Intent.PRODUCT_SEARCH:
        from rag.workflow.handlers.product_search import handle_product_search
        reply = handle_product_search(user_message, memory)
        return reply, memory, {
            "intent": intent.value,
            "rag_called": True,
        }

    if intent == Intent.SUGGEST:
        from rag.workflow.handlers.suggest import handle_suggest
        reply = handle_suggest(user_message, memory)
        return reply, memory, {
            "intent": intent.value,       
            "rag_called": True,
        }

    # -------------------------------
    # Soft constraint handling (Demo mode)
    # -------------------------------

    if memory.product_type:
        # Only enforce product type in demo mode
        results = raw_results  # DEMO MODE: no strict filtering

    # -------------------------------
    # No results → Smart Seller Fallback
    # -------------------------------
    if not results:

        # 1️⃣ Try relaxation (attribute drop)
        from rag.workflow.relaxation_engine import relax_constraints

        relaxed_results, dropped_attr = relax_constraints(raw_results, memory)

        if relaxed_results:
            reply = (
                f"Non ho trovato risultati con il criterio '{dropped_attr}', "
                "ma ecco alcune alternative simili che potrebbero interessarti:\n\n"
            )
            reply += generate_explanation(relaxed_results, memory)

            log_system(
                trace_id,
                reply,
                intent=intent.value,
                rag_called=True,
                num_results=len(relaxed_results),
                relaxed=True,
            )

            return reply, memory, {
                "intent": intent.value,
                "rag_called": True,
                "num_results": len(relaxed_results),
                "relaxed": True,
            }

        # 2️⃣ LLM Suggest Similar Product Type
        try:
            from rag.llm.openai_client import openai_client

            fallback_prompt = f"""
            The requested product was not found.

            Requested product type: {memory.product_type}
            Occasion: {memory.occasion}
            Style: {memory.constraints.get("style")}

            Suggest a similar tableware product type in Italian.
            Return only a short phrase (no explanation).
            """

            suggestion = openai_client.generate(
                fallback_prompt,
                temperature=0.2,
            ).strip()

            reply = (
                f"Non ho trovato esattamente quello che cerchi. "
                f"Forse potrebbe interessarti: {suggestion}"
            )

        except Exception:
            reply = (
                f"Non ho trovato {memory.product_type or 'prodotti'} compatibili. "
                "Vuoi provare con un altro criterio?"
            )

        log_system(
            trace_id,
            reply,
            intent=intent.value,
            rag_called=True,
            num_results=0,
        )

        return reply, memory, {
            "intent": intent.value,
            "rag_called": True,
            "num_results": 0,
        }


    # -------------------------------
    # NORMAL FLOW (No validation)
    # -------------------------------

    reply = generate_explanation(results, memory)

    refinements = suggest_refinements(memory)
    refinement_question = build_refinement_question_it(refinements)

    if refinement_question:
        reply += "\n\n" + refinement_question

    log_system(
        trace_id,
        reply,
        intent=intent.value,
        rag_called=True,
        num_results=len(results),
    )

    return reply, memory, {
        "intent": intent.value,
        "rag_called": True,
        "num_results": len(results),
        "results": results[:5],
    }
