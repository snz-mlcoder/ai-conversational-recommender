# Conversational RAG – Current Architecture

## Purpose

This system implements a **deterministic, stateful backbone** for a conversational product search experience.
It is intentionally simple and explainable, designed to be extended later with an LLM.

---

## What the System Does

* Maintains a **SearchMemory** object across turns
* Extracts high‑confidence signals from user messages (item, color, size, shape, etc.)
* Updates memory incrementally (merge, not replace)
* Builds a search query from memory
* Calls a retrieval engine (RAG) and returns ranked results

---

## What the System Does *Not* Do (by Design)

* No semantic reasoning
* No complex negotiation or conflict resolution
* No natural language understanding beyond keyword signals
* No multi‑attribute disambiguation in a single turn

These responsibilities are **explicitly deferred to an LLM**.

---

## Core Components

* **Intent Detection**: Rule‑based, conservative
* **Extraction**: Keyword‑based signal extraction
* **Memory Update**: Deterministic state reducer
* **Search Step**: Text‑based query construction
* **Orchestrator**: Controls the workflow

---

## Design Principles

* Deterministic over clever
* Stateful over stateless
* Explainable over opaque
* Backbone first, intelligence later

---

## Future Extensions (Planned)

* Conversation ID & persistence
* LLM‑based extraction and negotiation
* Semantic re‑ranking and clustering
* Natural language response generation

---

## Summary

This codebase is a **stable foundation**, not a finished conversational agent.
Its primary goal is to make future LLM integration safe, testable, and controlled.
