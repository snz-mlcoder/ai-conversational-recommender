from pydantic import BaseModel, Field
from typing import Optional, Dict
from rag.workflow.schemas import SearchMemory


class WorkflowRequest(BaseModel):
    user_message: str
    memory: SearchMemory

class WorkflowResponse(BaseModel):
    reply: str
    memory: SearchMemory
    debug: dict
