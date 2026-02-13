from pydantic import BaseModel, Field
from typing import Optional, Dict


class MemoryPayload(BaseModel):
    category: Optional[str] = None
    product_type: Optional[str] = None
    use_case: Optional[str] = None
    attributes: Dict = Field(default_factory=dict)





class WorkflowRequest(BaseModel):
    user_message: str
    memory: MemoryPayload

class WorkflowResponse(BaseModel):
    reply: str
    memory: MemoryPayload
    debug: dict
