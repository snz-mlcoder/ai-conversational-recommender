from rag.llm.openai_client  import openai_client
from rag.workflow.knowledge.store_info_data import STORE_INFO


def classify_store_topic_with_llm(question: str) -> str | None:

    prompt = f"""
Classify the user's question into ONE of these topics:

- shipping
- returns
- payments
- contacts
- unknown

Return only one word.

User question:
{question}
"""

    response = openai_client.generate(prompt, temperature=0.0).strip().lower()

    if response in {"shipping", "returns", "payments", "contacts"}:
        return response

    return None

def generate_store_reply_with_llm(topic: str, data: dict) -> str:
    """
    LLM layer for natural, seller-like responses.
    Uses structured data only. No hallucination allowed.
    """
    prompt = f"""
    You are a customer support assistant.

    Answer ONLY what the user asked.

    Do NOT list all store information.
    Do NOT add promotional text.
    Be short and direct (max 3 sentences).
    Do NOT invite the user to leave email unless explicitly asked.

    Topic: {topic}
    Data: {data}

        User question: {data.get('question', 'N/A')}
    Return only the final reply in Italian.
    """


    return openai_client.generate(prompt).strip()

def handle_store_info(question: str) -> str:
    text = question.lower()

    topic = None
    data = {}

    # 1️⃣ rule first (fast path)
    if any(k in text for k in {"spedizione", "consegna", "corriere", "arriva", "giorni", "tempi", "spedisce", "spediamo", "spedite"}):
        topic = "shipping"
    elif any(k in text for k in {"reso", "resi", "rimborso", "restituzione", "restituire", "cambio", "cambiare", "restituisco", "restituisce"  ,"restituiamo", "restituite", "restituiscono"}):
        topic = "returns"
    elif any(k in text for k in {"pagamento", "pagare", "pagamenti", "carte", "carta", "circuiti", "paypal", "metodi", "metodo", "pago", "paghiamo", "pagate", "pagano", "paghi", "pagano", "pago", "paghiamo", "pagate", "pagano"}):
        topic = "payments"
    elif any(k in text for k in {"telefono", "email", "indirizzo","address" ,"tel","contatti", "contatto", "assistenza", "supporto", "aiuto", "aiutare", "contattare", "contatti", "contatta", "contattiamo", "contattate", "contattano", "assisto", "assistiamo", "assistete", "assistono", "supporto", "supportiamo", "supportate", "supportano"}):
        topic = "contacts"

    # 2️⃣ fallback to LLM classification
    if not topic:
        topic = classify_store_topic_with_llm(question)

    if not topic:
        return (
            "Posso aiutarti con informazioni su spedizioni, resi, "
            "pagamenti o assistenza clienti."
        )

    if topic == "shipping":
        data = STORE_INFO["shipping"]
    elif topic == "returns":
        data = STORE_INFO["returns"]
    elif topic == "payments":
        data = STORE_INFO["payments"]
    elif topic == "contacts":
        data = {
            "email": STORE_INFO["email"],
            "phone": STORE_INFO["phone"],
        }

    return generate_store_reply_with_llm(topic, data)
