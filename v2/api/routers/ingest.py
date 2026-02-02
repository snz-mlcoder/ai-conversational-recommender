from fastapi import APIRouter
from scripts.file_to_json import run as ingest_file

router = APIRouter()

@router.post("/file")
def ingest_from_file():
    ingest_file()
    return {"status": "ok", "source": "file"}
