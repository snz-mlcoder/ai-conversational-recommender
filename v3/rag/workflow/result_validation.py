from rag.llm.openai_client import openai_client


def validate_results_with_llm(memory, results):

    if not results:
        return "invalid"

    # فقط 3 نتیجه اول رو بده به LLM
    sample = results[:3]

    titles = []
    for r in sample:
        url = r.get("url", "")
        titles.append(url.split("/")[-1])

    prompt = f"""
You are a product relevance validator.

User is searching for:
- product_type: {memory.product_type}
- attributes: {memory.attributes}

Here are the top results:
{titles}

Decide:
- valid → clearly matching product type
- partially_valid → product type matches but attributes not perfect
- invalid → completely unrelated product type

Return only one word: valid / partially_valid / invalid
"""

    decision = openai_client.generate(prompt, temperature=0.0).strip().lower()

    if decision not in {"valid", "partially_valid", "invalid"}:
        return "partially_valid"

    return decision
