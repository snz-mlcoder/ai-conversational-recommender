# AI Conversational Recommender (RAG MVP)

This project is a **simple Retrieval-Augmented Generation (RAG) pipeline**
built to recommend products based on a catalog (CSV / Excel).

The goal of this project is to:
- Load a product catalog
- Prepare data for semantic search
- Build a FAISS vector index
- Expose everything via a FastAPI backend
- Test search and recommendation logic before adding UI or LLMs

This is an **MVP / learning-oriented project**.

---

## 📦 Project Structure

```text
.
├── api/                # FastAPI application (API layer)
├── rag/                # RAG logic (prepare, search, reasoning)
├── scripts/            # Data ingestion scripts
├── data/               # Raw and processed data
├── requirements.txt
└── README.md

# AI Conversation Project

This repository contains multiple versions of the chatbot.

## Versions
- v2: Product-level chunking (legacy stable version)
- v3: Per-product chunking (experimental)
