import json
import re
from typing import Dict
from rag.workflow.vocab import PRODUCT_SIGNAL_GROUPS
from rag.llm.openai_client import openai_client

ALLOWED_KEYS = {
    "product_type",
    "use_case",
    "attributes",
    "negations",
}

def canonicalize_value(value: str) -> str | None:
    if not value:
        return None

    value = value.lower()

    for group in PRODUCT_SIGNAL_GROUPS.values():
        if value in group:
            return value

    return None

LLM_EXTRACTION_PROMPT = """
You are an information extraction engine for an Italian tableware e-commerce assistant.

Your task:
Extract structured product search signals from the user's message.

General rules:
- Detect product types (e.g. piatto, bicchiere, tazza).
- Detect use_case if present.
- Detect attributes:
  - color
  - material
  - size
  - shape
- Convert plural to singular canonical form (e.g. arancioni -> arancione).
- If the message contains ONLY an attribute (e.g. "arancioni", "in vetro", "quadrati"),
  still return it inside attributes.
- Do NOT invent values not present in the message.
- Do not hallucinate product types.

Output rules:
- Output ONLY valid JSON.
- Allowed top-level keys:
  product_type, use_case, attributes, negations.
- attributes keys allowed:
  color, material, size, shape.
- Use null when unsure.

User message:
{message}
""".strip()




def safe_json_parse(raw: str) -> Dict:
    """
    Extract first JSON object from LLM response safely.
    """
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}

    try:
        return json.loads(match.group())
    except Exception:
        return {}


def filter_allowed_keys(data: Dict) -> Dict:
    """
    Keep only allowed top-level keys.
    """
    return {k: v for k, v in data.items() if k in ALLOWED_KEYS}


def canonicalize_output(data: Dict) -> Dict:
    """
    Ensure LLM output matches domain vocabulary.
    """

    # product_type
    if "product_type" in data:
        canonical = canonicalize_value(data["product_type"])
        data["product_type"] = canonical

    # attributes
    if "attributes" in data and isinstance(data["attributes"], dict):
        new_attrs = {}

        for key, value in data["attributes"].items():
            canonical = canonicalize_value(value)
            if canonical:
                new_attrs[key] = canonical

        data["attributes"] = new_attrs

    return data


def llm_extract(message: str) -> Dict:
    print(">>> LLM EXTRACTION CALLED")

    prompt = LLM_EXTRACTION_PROMPT.format(message=message)

    try:
        raw = openai_client.generate(prompt, temperature=0.0)

        parsed = safe_json_parse(raw)

        if not isinstance(parsed, dict):
            return {}

        cleaned = filter_allowed_keys(parsed)
        canonical = canonicalize_output(cleaned)
        return canonical
        

    except Exception as e:
        print("LLM extraction error:", e)
        return {}
    

