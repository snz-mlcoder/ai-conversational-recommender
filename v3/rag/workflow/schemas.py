from pydantic import BaseModel , Field
from typing import Optional, Dict

class RAGQuery(BaseModel):
    text: str
    filters: Optional[Dict] = None

class SearchMemory(BaseModel):
    category: Optional[str] = None
    product_type: Optional[str] = None
    use_case: Optional[str] = None
    occasion: Optional[str] = None
    constraints: Dict = Field(default_factory=dict)
    attributes: Dict = {}
    exclusions: Dict = {}



class AskBackResult(BaseModel):
    should_ask: bool
    slot: Optional[str] = None   # 👈 WHAT is missing
    reason: Optional[str] = None # WHY