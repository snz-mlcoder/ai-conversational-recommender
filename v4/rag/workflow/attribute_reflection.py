from rag.llm.openai_client import openai_client


def generate_attribute_reflection(memory, results):
    """
    LLM checks whether requested attributes
    are present in retrieved results and
    builds a smart seller intro.
    """

    requested = memory.attributes or {}
    product_type = memory.product_type

    # extract visible titles
    titles = []
    for r in results[:5]:
        title = r.get("title") or r.get("url", "")
        titles.append(title)

    prompt = f"""
You are an intelligent e-commerce assistant.

The user requested:
Product type: {product_type}
Attributes: {requested}

Retrieved product titles:
{titles}

Task:
1. Check whether the requested attributes are clearly present.
2. If NOT present, write a short, polite Italian message:
   - Apologize briefly
   - Mention which attribute is missing
   - Offer these as alternatives
3. If attributes ARE present, return: MATCH

Rules:
- Do NOT invent products
- Keep it short (1-2 sentences)
- Italian language
- Professional seller tone

Return ONLY the final text.
"""

    try:
        response = openai_client.generate(prompt, temperature=0.2).strip()

        if response.upper() == "MATCH":
            return None

        return response + "\n\n"

    except Exception:
        return None
