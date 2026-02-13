from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rag.workflow_v4.api.workflow_api_v4 import build_engine
from rag.api.schemas import WorkflowRequest, WorkflowResponse
from rag.workflow.schemas import SearchMemory
from rag.workflow_v4.api.schemas_v4 import WorkflowResponseV4

app = FastAPI(title="Conversational Recommender v4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 singleton engine
engine = build_engine()

@app.post("/chat", response_model=WorkflowResponseV4)
def chat_v4(req: WorkflowRequest):

    memory = SearchMemory(
        category=req.memory.category,
        product_type=req.memory.product_type,
        use_case=req.memory.use_case,
        attributes=req.memory.attributes,
    )

    reply, updated_memory, debug = engine.run(
        req.user_message,
        memory
    )

    final_memory = updated_memory or memory

    return WorkflowResponseV4(
        reply=reply,
        memory=final_memory,   # ⬅ مستقیم مدل رو بده
        debug=debug or {}
    )


