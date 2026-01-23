from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict

from rag.retrieval.search import search
from rag.reasoning.cluster_results import cluster_results
from rag.reasoning.rank_clusters import rank_clusters

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 20
    filters: Optional[Dict] = None


@router.post("/")
def simple_search(req: SearchRequest):
    results = search(
        query=req.query,
        top_k=req.top_k,
        filters=req.filters,
    )
    return {"results": results}


@router.post("/full")
def full_search(req: SearchRequest):
    results = search(req.query, req.top_k, req.filters)
    clusters = cluster_results(results)
    ranked = rank_clusters(clusters, req.query)

    return {
        "query": req.query,
        "clusters": ranked,
    }
