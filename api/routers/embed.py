from fastapi import APIRouter

from rag.pipeline.embed_documents import run as embed_documents

router = APIRouter()


@router.post("/faiss")
def embed_faiss():
    embed_documents()
    return {"status": "ok", "index": "faiss"}
