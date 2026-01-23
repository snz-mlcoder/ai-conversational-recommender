from fastapi import APIRouter

from rag.pipeline.prepare_documents import run as prepare_documents
from rag.pipeline.chunk_documents import run as chunk_documents

router = APIRouter()


@router.post("/documents")
def prepare_docs():
    prepare_documents()
    return {"status": "ok", "step": "documents"}


@router.post("/chunks")
def prepare_chunks():
    chunk_documents()
    return {"status": "ok", "step": "chunks"}
