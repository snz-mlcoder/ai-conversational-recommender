import json
from typing import Dict
from rag.llm.ollama_client import ollama_client


LLM_EXTRACTION_PROMPT = """
You are an information extraction engine.

Extract structured product search signals from the user's message.

Rules:
- Output ONLY valid JSON
- Do not invent information
- Use null when unsure
- Allowed keys only:
  product_type, use_case, attributes, negations
- attributes keys: color, material, size, shape
- negations values: "__ANY__" or specific value

User message:
{message}
""".strip()


def llm_extract(message: str) -> Dict:
    prompt = LLM_EXTRACTION_PROMPT.format(message=message)

    try:
        raw = ollama_client.generate(prompt, temperature=0.0)
        data = json.loads(raw)

        if not isinstance(data, dict):
            return {}

        return data

    except Exception:
        return {}
