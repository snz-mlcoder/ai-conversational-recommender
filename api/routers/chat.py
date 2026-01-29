from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from rag.intent.detect import detect_intent
from rag.llm.ollama_client import ollama_client

from rag.retrieval.search import search
from rag.reasoning.cluster_results import cluster_results
from rag.reasoning.rank_clusters import rank_clusters
from rag.reasoning.rank_items import rank_items

router = APIRouter()

# 🔥 SIMPLE IN-MEMORY CONTEXT (per session-less demo)
LAST_PRODUCT_QUERY = None


class ChatRequest(BaseModel):
    query: str
    top_k: int = 20
    language: Optional[str] = "it"


@router.post("/")
def chat(req: ChatRequest):
    global LAST_PRODUCT_QUERY

    query = req.query.strip()
    query_lower = query.lower()

    # 1️⃣ Detect intent
    intent = detect_intent(
        llm_client=ollama_client,
        message=query
    )

    # 2️⃣ GREETING
    if intent == "GREETING":
        LAST_PRODUCT_QUERY = None
        return {
            "message": (
                "Ciao! 😊 Dimmi che prodotto stai cercando."
                if req.language == "it"
                else "Hello! 😊 Tell me what product you are looking for."
            ),
            "products": [],
            "intent": intent
        }

    # 3️⃣ SAVE PRODUCT QUERY
    if intent == "SEARCH_PRODUCT" and "per " not in query_lower:
        LAST_PRODUCT_QUERY = query

    # 4️⃣ READY CHECK
    READY_KEYWORDS = ["ristorante", "bar", "hotel", "casa", "professionale"]

    is_context_only = any(k in query_lower for k in READY_KEYWORDS) and LAST_PRODUCT_QUERY

    # 5️⃣ ASK FOLLOW-UP (no RAG yet)
    if intent == "SEARCH_PRODUCT" and not is_context_only and LAST_PRODUCT_QUERY is None:
        return {
            "message": (
                "Perfetto 👍 per che uso lo stai cercando? "
                "(ristorante, casa, bar…)"
                if req.language == "it"
                else
                "Great 👍 what is the use case? "
                "(restaurant, home, bar…)"
            ),
            "products": [],
            "intent": intent
        }

    # 6️⃣ BUILD FINAL QUERY (🔥 THIS IS THE FIX)
    if is_context_only:
        final_query = f"{LAST_PRODUCT_QUERY} {query}"
    else:
        final_query = query

    # 7️⃣ RUN RAG
    results = search(final_query, req.top_k)

    clusters = cluster_results(results)
    ranked_clusters = rank_clusters(clusters, final_query)

    if not ranked_clusters:
        return {
            "message": (
                "Non ho trovato prodotti adatti."
                if req.language == "it"
                else "I couldn't find suitable products."
            ),
            "products": [],
            "intent": "READY_FOR_SEARCH"
        }

    top_cluster = ranked_clusters[0]
    products = rank_items(top_cluster["items"], top_k=5)

    return {
        "message": (
            "Ecco alcune opzioni adatte a questo utilizzo:"
            if req.language == "it"
            else
            "Here are some options suitable for this use case:"
        ),
        "products": products,
        "intent": "READY_FOR_SEARCH"
    }
