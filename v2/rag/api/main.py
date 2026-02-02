from fastapi import FastAPI
from rag.api.schemas import WorkflowRequest, WorkflowResponse
from rag.api.workflow_api import run_workflow

app = FastAPI()

@app.post("/chat", response_model=WorkflowResponse)
def chat(req: WorkflowRequest):
    reply, updated_memory, debug = run_workflow(
        req.user_message,
        req.memory
    )

    return {
        "reply": reply,
        "memory": updated_memory,
        "debug": debug
    }
