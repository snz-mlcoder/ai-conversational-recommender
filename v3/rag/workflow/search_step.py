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

def build_rag_query(memory, user_message: str) -> RAGQuery:
    text = memory_to_text(memory)

    # 🔥 fallback به پیام کاربر
    if not text.strip():
        text = user_message

    return RAGQuery(
        text=text,
        filters=None,
    )


def call_rag(rag_query):
    engine = get_search_engine()
    return engine.search(rag_query.text)


