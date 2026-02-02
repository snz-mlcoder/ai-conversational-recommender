from pydantic import BaseModel 
from typing import Optional, Dict 

class MemoryPayload(BaseModel):
    category: Optional[str] = None
    product_type: Optional[str] = None
    use_case: Optional[str] = None
    attributes: Dict = {}



class WorkflowRequest(BaseModel):
    user_message: str
    memory: MemoryPayload

class WorkflowResponse(BaseModel):
    reply: str
    memory: MemoryPayload
    debug: dict
