from rag.workflow.search_step import build_rag_query, call_rag
from rag.workflow.explanation import generate_explanation

# 🔥 NEW
from rag.workflow.result_validator import validate_results_against_memory
from rag.workflow.smart_intro_builder import build_smart_mismatch_intro
from rag.workflow.attribute_reflection import generate_attribute_reflection
def handle_suggest(user_message: str, memory):
    """
    Suggest mode = guided broad retrieval.
    Now with Smart Seller validation layer (demo-ready).
    """

    rag_query = build_rag_query(memory, user_message)
    results = call_rag(rag_query, memory)

    if not results:
        return (
            "Posso suggerirti piatti, bicchieri o accessori per la tavola. "
            "Dimmi per quale occasione ti serve."
        )

    # ==========================================
    # 🔥 SMART SELLER LAYER
    # ==========================================
    mismatches = validate_results_against_memory(results, memory)

    if mismatches:
        # 🔥 LLM reflection
        llm_intro = generate_attribute_reflection(memory, results)

        explanation = generate_explanation(results, memory=None)

        if llm_intro:
            return llm_intro + explanation

        # fallback
        intro = build_smart_mismatch_intro(memory, mismatches)
        return intro + explanation

    return generate_explanation(results, memory)
