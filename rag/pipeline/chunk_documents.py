import json
from pathlib import Path


# =======================
# CONFIG
# =======================
INPUT_PATH = Path("rag/data/documents.jsonl")
OUTPUT_PATH = Path("rag/data/chunks.jsonl")

CHUNK_SIZE = 500    # characters
CHUNK_OVERLAP = 50  # characters


# =======================
# HELPERS
# =======================
def chunk_text(text: str, size: int, overlap: int):
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += size - overlap

    return chunks


# =======================
# MAIN
# =======================
def run():
    if not INPUT_PATH.exists():
        print("❌ documents.jsonl not found.")
        return

    written = 0

    with INPUT_PATH.open("r", encoding="utf-8") as infile, \
         OUTPUT_PATH.open("w", encoding="utf-8") as outfile:

        for line in infile:
            doc = json.loads(line)

            text = doc.get("text", "")
            if not text.strip():
                continue

            chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

            for i, chunk in enumerate(chunks):
                chunk_doc = {
                    "id": doc.get("id"),
                    "url": doc.get("url"),
                    "source": doc.get("source"),
                    "category": doc.get("category"),
                    "chunk_index": i,
                    "text": chunk,
                    "images": doc.get("images", []),
                }

                outfile.write(
                    json.dumps(chunk_doc, ensure_ascii=False) + "\n"
                )
                written += 1

    print("🎉 DONE")
    print(f"🧩 Chunks written: {written}")
    print(f"💾 Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    run()