from typing import List, Dict, Optional
from pydantic import BaseModel
from rag.workflow.schemas import SearchMemory as MemoryV4


class RecommendationItem(BaseModel):
    product_id: str
    score: float
    category: Optional[str] = None
    url: Optional[str] = None
    images: List[str] = []


class RecommendationGroup(BaseModel):
    group_id: str
    group_label: str
    group_score: Optional[float] = None
    items: List[RecommendationItem]


class DebugInfoV4(BaseModel):
    engine_version: str = "v4"
    intent: str

    rag_called: bool = False
    num_candidates: int = 0
    num_groups: int = 0

    recommendations: List[RecommendationGroup] = []


class WorkflowResponseV4(BaseModel):
    reply: str
    memory: MemoryV4
    debug: DebugInfoV4
