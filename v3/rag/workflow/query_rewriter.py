from rag.llm.openai_client import openai_client


def rewrite_query_with_llm(memory, user_message: str) -> str:

    # 🔒 Always build deterministic base query first
    parts = []

    if memory.product_type:
        parts.append(memory.product_type)

    if memory.attributes:
        for v in memory.attributes.values():
            parts.append(v)

    if memory.use_case:
        parts.append(memory.use_case)

    if memory.occasion:
        parts.append(memory.occasion)

    base_query = " ".join(parts).strip()

    # اگر structured چیزی نداریم
    if not base_query:
        return user_message

    # اگر فقط product_type داریم rewrite نکن
    if (
        memory.product_type
        and not memory.attributes
        and not memory.use_case
        and not memory.occasion
    ):
        return base_query

    # -------------------------
    # LLM Optimization Layer
    # -------------------------

    prompt = f"""
You are an e-commerce search optimizer.

Improve the following search query slightly for semantic retrieval.
Keep ALL original keywords.
Do NOT translate.
Do NOT remove attributes.
Return ONLY the improved query.

Query:
{base_query}
"""

    try:
        print(">>> LLM QUERY REWRITE CALLED")

        raw = openai_client.generate(prompt, temperature=0.0)

        if not raw:
            return base_query

        clean = raw.strip()

        # Safety guard
        if len(clean.split()) > 25:
            return base_query

        # 🔒 Ensure structured keywords are preserved
        for token in parts:
            if token not in clean:
                return base_query

        print(">>> LLM REWRITTEN:", clean)

        return clean

    except Exception as e:
        print("LLM rewrite failed:", str(e))
        return base_query
