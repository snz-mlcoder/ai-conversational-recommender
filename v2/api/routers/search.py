from fastapi import APIRouter
from typing import Optional, Dict
from pydantic import BaseModel, Field


from rag.retrieval.search import search
from rag.reasoning.cluster_results import cluster_results
from rag.reasoning.rank_clusters import rank_clusters

router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., example="piatto bianco")
    top_k: int = Field(20, example=20)
    filters: Optional[Dict[str, str]] = Field(
        default=None,
        example=None
    )


@router.post("/")
def simple_search(req: SearchRequest):
    results = search(
        query=req.query,
        top_k=req.top_k,
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
