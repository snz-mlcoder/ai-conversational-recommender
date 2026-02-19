# rag/workflow/search_step.py

from rag.workflow.schemas import RAGQuery
from rag.workflow.memory import memory_to_text
from rag.retrieval.search_product import ProductSearchEngine
from rag.workflow.schemas import RAGQuery


# ---------------------------
# Lazy singleton (safe)
# ---------------------------

_search_engine: ProductSearchEngine | None = None


def get_search_engine() -> ProductSearchEngine:
    global _search_engine
    if _search_engine is None:
        _search_engine = ProductSearchEngine()
    return _search_engine


# ---------------------------
# RAG steps
# ---------------------------

from rag.workflow.query_rewriter import rewrite_query_with_llm


USE_LLM_QUERY_REWRITE = True  # feature flag


def build_rag_query(memory, user_message: str) -> RAGQuery:

    text_from_memory = memory_to_text(memory)

    if not text_from_memory.strip():
        base_text = user_message
    else:
        base_text = text_from_memory

    final_text = base_text

    # 🔥 LLM Query Rewriting Layer
    if USE_LLM_QUERY_REWRITE and memory.product_type:
        try:
            rewritten = rewrite_query_with_llm(memory, user_message)

            if rewritten and len(rewritten) > 3:
                final_text = rewritten

        except Exception as e:
            print("[RAG] LLM rewrite failed:", str(e))

    print("\n===== RAG QUERY BUILD =====")
    print("[RAG] user_message:", user_message)
    print("[RAG] memory_to_text:", text_from_memory)
    print("[RAG] base_text:", base_text)
    print("[RAG] final_text:", final_text)
    print("===========================\n")

    return RAGQuery(
        text=final_text,
        filters=None,
    )




def call_rag(rag_query, memory=None):
    engine = get_search_engine()

    print("\n===== CALL RAG =====")
    print("[RAG] query text:", rag_query.text)
    print("[RAG] memory:", memory.dict() if memory else None)
    print("=====================\n")

    return engine.search(
        rag_query.text,
        memory=memory,
        top_k=3,
    )

