from rag.llm.openai_client  import openai_client
from rag.workflow.knowledge.store_info_data import STORE_INFO

def generate_store_reply_with_llm(topic: str, data: dict) -> str:
    """
    LLM layer for natural, seller-like responses.
    Uses structured data only. No hallucination allowed.
    """

    prompt = f"""
You are a friendly e-commerce assistant.

Based ONLY on the structured data below,
write a natural, helpful Italian response.

Rules:
- Do NOT invent numbers.
- Do NOT change values.
- Keep it friendly and professional.
- Suggest contacting via email or phone if appropriate.
- Optionally invite the user to leave their email for more details.

Topic: {topic}
Data: {data}

Return only the final reply in Italian.
"""

    return openai_client.generate(prompt).strip()

def handle_store_info(question: str) -> str:
    text = question.lower()

    data = {}
    topic = None

    if any(k in text for k in {"spedizione", "consegna", "corriere", "arriva", "giorni"}):
        topic = "shipping"
        data = STORE_INFO["shipping"]

    elif any(k in text for k in {"reso", "resi", "rimborso"}):
        topic = "returns"
        data = STORE_INFO["returns"]

    elif any(k in text for k in {"pagamento", "pagare", "pagamenti"}):
        topic = "payments"
        data = STORE_INFO["payments"]

    elif any(k in text for k in {"telefono", "email", "contatti"}):
        topic = "contacts"
        data = {
            "email": STORE_INFO["email"],
            "phone": STORE_INFO["phone"],
        }

    if not topic:
        return (
            "Posso aiutarti con informazioni su spedizioni, resi, "
            "pagamenti o assistenza clienti."
        )

    return generate_store_reply_with_llm(topic, data)
