from pydantic import BaseModel, Field
from typing import Optional, Dict

class MemoryPayload(BaseModel):
    category: Optional[str] = Field(default=None, example=None)
    product_type: Optional[str] = Field(default=None, example=None)
    use_case: Optional[str] = Field(default=None, example=None)
    attributes: Dict = Field(default_factory=dict)




class WorkflowRequest(BaseModel):
    user_message: str
    memory: MemoryPayload

class WorkflowResponse(BaseModel):
    reply: str
    memory: MemoryPayload
    debug: dict
