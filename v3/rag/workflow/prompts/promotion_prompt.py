from rag.workflow.knowledge.store_info_data import STORE_INFO


def build_promotion_prompt(question: str) -> str:
    return f"""
You are a customer support assistant.

Known promotions:
- Volume discounts up to {STORE_INFO["discounts"]["volume_discount_percent"]}%
- Discount coupons are cumulative: {STORE_INFO["discounts"]["coupons_stackable"]}

Rules:
- Do NOT invent promotions or codes.
- If the user asks for unavailable discounts, say so clearly.
- Keep it short (2–3 sentences).
- Language: Italian.

User question:
{question}
""".strip()



'''فقط یک توصیه برای آینده (کوچیک ولی مهم)

بهتره promptها رو این‌طوری نگه داری:

prompts/
├── store_info_prompt.txt
├── promotion_prompt.txt
├── shipping_returns_prompt.txt


و در Python فقط:

prompt = render("store_info_prompt", data)'''