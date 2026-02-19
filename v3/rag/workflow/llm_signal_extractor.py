from rag.llm.openai_client import openai_client
import json


def extract_semantic_signals(text: str) -> dict:
    """
    Extract conversational semantic signals.
    """

    prompt = f"""
You are a semantic signal extractor for an Italian tableware shop.

Extract structured signals from the user query.

Possible fields:
- use_case
- occasion
- style
- target
- mood

Return ONLY valid JSON.
If not present, return null.

User query:
{text}
"""

    response = openai_client.generate(prompt)

    try:
        return json.loads(response)
    except Exception:
        return {}
