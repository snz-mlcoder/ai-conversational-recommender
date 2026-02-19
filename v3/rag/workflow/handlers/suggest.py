from rag.workflow.search_step import build_rag_query, call_rag
from rag.workflow.explanation import generate_explanation


def handle_suggest(user_message: str, memory):
    """
    Suggest mode = guided broad retrieval.
    Not pure LLM imagination.
    """

    # Broad query based on occasion
    rag_query = build_rag_query(memory, user_message)

    results = call_rag(rag_query, memory)

    if not results:
        return (
            "Posso suggerirti piatti, bicchieri o accessori per la tavola. "
            "Dimmi per quale occasione ti serve."
        )

    return generate_explanation(results, memory)
