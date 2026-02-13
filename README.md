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

Versions
_____________________________________________________________
🔹 v2 – Legacy Product-Level Chunking

Early RAG pipeline:

Product-level chunking

Embedding-based retrieval

Basic FAISS index

No structured conversational memory

Stable but not conversationally aware.
___________________________________________________________

🔹 v3 – Conversational Recommender (Deterministic Backbone)

Stable rule-based conversational engine.
Core features:
Rule-based intent detection
Structured memory tracking
Attribute extraction
Goal decision layer
Ask-back logic (slot filling)
RAG integration
Minimal demo UI

Focus:
Deterministic conversational control + predictable behavior.
No clustering. No semantic reasoning layer.
____________________________________________________________

🔹 v4 – Modular Workflow Engine + Semantic Reasoning

Major architectural refactor.
New in v4:
Fully modular WorkflowEngine
Pluggable search pipeline
Embedding-based semantic retrieval
Business-aware reranking
Embedding-driven clustering
Deterministic reasoning layer
Structured grouped recommendations
Improved explainability

v4 moves the system from:
Deterministic conversational RAG
to:
Modular semantic retrieval + recommendation engine

