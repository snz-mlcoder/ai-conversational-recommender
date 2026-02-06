
# Conversational RAG – Current Architecture (v3)

## Purpose

This system implements a **deterministic, stateful conversational backbone** for a B2B product discovery and assistance experience (HoReCamart-focused).

It is designed to:

* support **controlled product search**
* answer **store, promotion, and material knowledge questions**
* act as a **safe foundation for future LLM-driven intelligence**

---

## What the System Does

### 🧠 Conversation Backbone

* Maintains a **SearchMemory** object across turns
* Preserves user intent through incremental state updates
* Separates *what the user wants* from *how the system responds*

### 🎯 Intent Handling (Rule-Based)

* Detects **mutually exclusive intents**:

  * `PRODUCT_SEARCH`
  * `STORE_INFO`
  * `PROMOTION`
  * `MATERIAL_KNOWLEDGE`
  * `SMALL_TALK`
* Uses conservative, explainable keyword rules
* Ensures **search intent always wins** when product signals are present

### 🔍 Product Search (RAG)

* Extracts high-confidence signals:

  * item type
  * use case (home / restaurant / hotel)
  * attributes (color, material, size, shape)
* Updates memory deterministically (merge, never overwrite blindly)
* Builds a text query from memory
* Retrieves top-K products from a FAISS vector store
* Returns ranked results (flat list)

### 🏪 Store & Service Knowledge (Rule-Based)

* Answers questions about:

  * shipping & delivery
  * returns & refunds
  * payments
  * promotions & volume discounts
* Uses **structured knowledge data**, not LLM hallucinations
* Designed to be CMS / DB-backed in the future

### 🧪 Material Knowledge (LLM-Powered, Isolated)

* Handles **general material questions** (e.g. “Il vetro è sicuro?”)
* Stateless, no memory mutation
* Strict prompting rules:

  * no product claims
  * no medical or absolute guarantees
  * short, informative answers
* LLM is used **only where deterministic logic is insufficient**

### ❓ Ask-Back & Refinement

* Blocking ask-back only for **missing product type**
* Optional refinement suggestions (non-blocking):

  * color
  * material
  * shape
  * use case

---

## What the System Does *Not* Do (by Design)

* ❌ No deep semantic reasoning
* ❌ No fuzzy matching or typo correction (yet)
* ❌ No multi-intent resolution in a single turn
* ❌ No persuasive language generation in search results
* ❌ No automatic lead qualification

These are **explicitly deferred** to later LLM or orchestration layers.

---

## Core Components

* **Intent Detection** – rule-based, priority-driven
* **Signal Extraction** – keyword vocabularies (items, materials, etc.)
* **Memory Update** – deterministic state reducer
* **Search Step** – semantic retrieval via FAISS
* **Orchestrator** – single control flow for all intents
* **Handlers** – isolated logic per intent (search, store info, promotion, knowledge)

---

## Design Principles

* Deterministic over clever
* Stateful over stateless
* Explainable over opaque
* Business-safe over “AI magic”
* Backbone first, intelligence later

---

## Existing Advanced Capabilities (Currently Dormant)

* Semantic clustering of search results
* Cluster ranking and aggregation
* Group-level scoring for explainability

These are **intentionally not exposed yet**, and will be activated once:

* explanation generation is upgraded
* UI supports grouped recommendations
* sales-oriented reasoning is introduced

---

## Planned Next Phases

### Phase 2 — UX & Observability

* Conversation ID & persistence
* Full interaction logging
* Lead signals (frequency, interests, intent patterns)

### Phase 3 — Intelligence Augmentation

* LLM-assisted extraction (typos, plurals, synonyms)
* Cluster-based explanation generation
* Sales-style recommendation reasoning

### Phase 4 — Integration

* Botpress (UI, flows, multi-channel)
* n8n (automation, CRM, lead enrichment)
* CMS-backed store knowledge

---

## Summary

This codebase is **not a chatbot** — it is a **controlled conversational system**.

Its strength lies in:

* predictable behavior
* debuggable decisions
* safe extension paths

LLMs are treated as **optional intelligence modules**, not as the system core.

---
