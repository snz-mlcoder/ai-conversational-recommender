from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import ingest, prepare, embed, search, chat
from api.routers import conversation

app = FastAPI(
    title="RAG Pipeline API",
    version="0.1.0"
)

# ✅ CORS frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(prepare.router, prefix="/prepare", tags=["prepare"])
app.include_router(embed.router, prefix="/embed", tags=["embed"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(conversation.router, prefix="/conversation", tags=["conversation"])


@app.get("/")
def health():
    return {"status": "ok"}
