INTENT_PROMPT = """
You are an intent classifier for an e-commerce conversational assistant.

Classify the user's message into ONE of the following intents:

- SEARCH_PRODUCT: the user wants to find or browse products
- REFINE_FILTER: the user wants to refine or filter previous results
- ASK_PRICE: the user asks about price, discounts, or availability
- GREETING: greetings or polite expressions
- OTHER: anything else

Return ONLY the intent name.

User message:
"{message}"
"""



def detect_intent(llm_client, message: str) -> str:
    try:
        response = llm_client.generate(
            prompt=INTENT_PROMPT.format(message=message),
            temperature=0
        )

        intent = response.strip().upper()
        allowed = {
            "SEARCH_PRODUCT",
            "REFINE_FILTER",
            "ASK_PRICE",
            "GREETING",
            "OTHER"
        }

        return intent if intent in allowed else "OTHER"

    except Exception:
        msg = message.lower().strip()

        if msg in {"ciao", "salve", "hello", "hi"}:
            return "GREETING"

        return "OTHER"

