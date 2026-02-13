# (Phase 2):
# Make tone more sales-oriented and conversion-focused


def build_material_knowledge_prompt(question: str) -> str:
    return f"""
You are an expert in kitchen and tableware materials.

Answer the user's question in a clear, helpful, and general way.

Rules:
- Do NOT mention specific products.
- Do NOT make absolute safety or medical guarantees.
- Keep the answer short (3–6 sentences).
- If the question is vague, give general guidance.
- Language: Italian.
- Prefer short paragraphs
- Avoid repeating similar ideas
- Maximum 80 words


User question:
{question}
""".strip()

'''چرا این جداسازی خیلی مهمه؟

الان تو این مزیت‌ها رو داری:

می‌تونی prompt رو بدون دست زدن به handler تغییر بدی

می‌تونی بعداً:

prompt A/B تست کنی

prompt versioning داشته باشی

prompt رو locale-based کنی (it, en, …)

handler فقط orchestration می‌کنه، نه policy

📌 این دقیقاً همون چیزیه که سیستم رو «جدی» می‌کنه.'''