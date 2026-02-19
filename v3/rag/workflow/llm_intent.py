# rag/workflow/llm_intent.py

from typing import Optional
from rag.llm.ollama_client import ollama_client
from rag.workflow.intent import Intent


LLM_INTENT_PROMPT = """
Classify the user message into ONE of these intents:

- product_search
- store_info
- material_knowledge
- small_talk

Rules:
- Output ONLY one label
- No explanation
- No extra text
- Lowercase only

User message:
{message}
""".strip()


def llm_intent_disambiguation(message: str) -> Optional[Intent]:
    prompt = LLM_INTENT_PROMPT.format(message=message)

    try:
        raw = ollama_client.generate(
            prompt,
            temperature=0.0,
        ).strip().lower()

        for intent in Intent:
            if raw == intent.value:
                return intent

    except Exception:
        pass

    return None
