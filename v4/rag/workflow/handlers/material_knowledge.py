from rag.llm.openai_client import openai_client
from typing import Dict

from rag.workflow.prompts.material_knowledge_prompt import (
    build_material_knowledge_prompt
)
from rag.workflow.signals import (
    is_question,
    is_material_comparison_question,
)
from rag.workflow.vocab import MATERIAL_KNOWLEDGE_TERMS


# ---------------------------------------------------
# 1️⃣ Rule-based candidate detection
# ---------------------------------------------------

BUYING_CUES = {
    "comprare",
    "prezzo",
    "quanto costa",
    "disponibile",
    "ordinare",
    "acquistare",
}


def is_material_knowledge_candidate(text: str, signals: Dict) -> bool:
    """
    Decide if the message is likely a material knowledge question.
    Deterministic guard before LLM.
    """

    text = text.lower()

    has_material = "materials" in signals
    question = is_question(text)

    if not has_material or not question:
        return False

    # 🔥 Explicit material comparison → always knowledge
    if is_material_comparison_question(text, MATERIAL_KNOWLEDGE_TERMS):
        return True

    # If buying intent is present → likely product search
    if any(cue in text for cue in BUYING_CUES):
        return False

    return True


# ---------------------------------------------------
# 2️⃣ LLM fallback disambiguation (controlled)
# ---------------------------------------------------

ALLOWED_LABELS = {
    "material_knowledge",
    "product_search",
    "other",
}


def classify_material_intent_with_llm(text: str) -> bool:
    """
    Lightweight LLM classifier for ambiguous cases.
    Returns True only if confidently classified as material_knowledge.
    """

    prompt = f"""
Classify the user message.

Return ONLY one label:
- material_knowledge
- product_search
- other

No explanation.
Lowercase only.

Message:
{text}
""".strip()

    try:
        result = (
            openai_client.generate(prompt=prompt, temperature=0.0)
            .strip()
            .lower()
        )

        if result not in ALLOWED_LABELS:
            return False

        return result == "material_knowledge"

    except Exception:
        return False


# ---------------------------------------------------
# 3️⃣ Main handler (stateless, safe)
# ---------------------------------------------------

MAX_WORDS = 120


def handle_material_knowledge(question: str) -> str:
    """
    LLM-powered material knowledge handler.
    Safe, stateless, no memory mutation.
    """

    prompt = build_material_knowledge_prompt(question)

    try:
        answer = openai_client.generate(
            prompt=prompt,
            temperature=0.1,
        )

        if not answer or not answer.strip():
            raise ValueError("Empty LLM response")

        answer = answer.strip()

        # 🔒 Safety guard: limit verbosity
        words = answer.split()
        if len(words) > MAX_WORDS:
            answer = " ".join(words[:MAX_WORDS])

        # 🔒 Safety guard: prevent accidental links or product mentions
        if "http" in answer.lower():
            raise ValueError("Unsafe content")

        return answer

    except Exception:
        # Deterministic safe fallback
        return (
            "I materiali come vetro, acciaio e plastica hanno "
            "caratteristiche diverse in termini di resistenza, "
            "durabilità e utilizzo. Se vuoi, dimmi in quale "
            "contesto li useresti così posso darti un consiglio più mirato."
        )
