from fastapi import APIRouter
from pydantic import BaseModel

from rag.retrieval.search import search
from rag.reasoning.cluster_results import cluster_results
from rag.reasoning.rank_clusters import rank_clusters
from rag.reasoning.rank_items import rank_items

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    top_k: int = 20


@router.post("/")
def chat(req: ChatRequest):
    results = search(req.query, req.top_k)

    clusters = cluster_results(results)
    ranked_clusters = rank_clusters(clusters, req.query)

    if not ranked_clusters:
        return {"answer": None, "products": []}

    top_cluster = ranked_clusters[0]
    products = rank_items(top_cluster["items"], top_k=5)

    return {
        "query": req.query,
        "top_cluster": {
            "cluster_id": top_cluster["cluster_id"],
            "size": top_cluster["size"],
        },
        "products": products,
        "debug": {
            "rank_score": top_cluster["rank_score"],
            "avg_score": top_cluster["avg_score"],
        }
    }
