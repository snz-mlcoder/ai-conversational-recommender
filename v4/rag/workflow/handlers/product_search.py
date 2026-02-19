from rag.workflow.search_step import build_rag_query, call_rag
from rag.workflow.explanation import generate_explanation
from rag.workflow.result_validator import validate_results_against_memory
from rag.workflow.smart_intro_builder import build_smart_mismatch_intro


def handle_product_search(user_message: str, memory):
    """
    Product search handler with Smart Seller validation layer.
    Production-ready.
    """

    rag_query = build_rag_query(memory, user_message)
    results = call_rag(rag_query, memory)

    if not results:
        return (
            "Non ho trovato risultati corrispondenti. "
            "Vuoi specificare meglio cosa stai cercando?"
        )

    # 🔥 SMART VALIDATION LAYER
    mismatches = validate_results_against_memory(results, memory)

    if mismatches:
        intro = build_smart_mismatch_intro(memory, mismatches)

        # IMPORTANT: remove misleading attribute phrase
        explanation = generate_explanation(results, memory=None)

        return intro + "\n\n" + explanation

    return generate_explanation(results, memory)
