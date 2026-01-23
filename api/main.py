from fastapi import FastAPI
from api.routers import ingest, prepare, embed, search, chat

app = FastAPI(
    title="RAG Pipeline API",
    version="0.1.0"
)

app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(prepare.router, prefix="/prepare", tags=["prepare"])
app.include_router(embed.router, prefix="/embed", tags=["embed"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])


@app.get("/")
def health():
    return {"status": "ok"}
