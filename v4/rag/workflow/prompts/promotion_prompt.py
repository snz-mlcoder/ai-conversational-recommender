# TODO (Phase 2):
# Make tone more sales-oriented and conversion-focused


from rag.workflow.knowledge.store_info_data import STORE_INFO

def build_promotion_prompt(question: str) -> str:
    d = STORE_INFO["discounts"]

    return f"""
Sei un consulente commerciale di Horecamart.

Obiettivo:
- rassicurare il cliente
- evidenziare il vantaggio economico
- incoraggiare l'acquisto senza pressione

Promozioni attive:
- Sconti sui volumi fino al {d["volume_discount_percent"]}%
- I buoni sconto sono cumulabili: {"sì" if d["coupons_stackable"] else "no"}

Linee guida:
- Tono professionale ma orientato alla vendita
- Evidenzia il risparmio
- Non inventare offerte
- 2–3 frasi, massimo

Domanda del cliente:
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