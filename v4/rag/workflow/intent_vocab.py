# Intent-level vocab
# NOTE: intentionally minimal – will be expanded later

STORE_INFO_TERMS = set()
PROMOTION_TERMS = set()
MATERIAL_KNOWLEDGE_TERMS = set()

STORE_INFO_TERMS = {
    "spedizione",
    "spedizioni",
    "spedizione gratuita",
    "resi",
    "resi e rimborsi",
    "rimborso",
    "pagamento",
    "pagamenti",
    "corriere",
    "consegna",
    "spedizione",
    "consegna",
    "tempi di consegna",
    "reso",
    "rimborso",
    "pagamento",
    "paypal",
    "contrassegno",
    "carta",
    "bonifico",
    "indirizzo",
    "orari",
    
}


PROMOTION_TERMS = {
    # discounts
    "sconto", "sconti", "offerta", "offerte", "promozione",

    # payment conditions
    "rate", "pagamento a rate", "rateizzazione",
    "pagare a rate", "finanziamento",

    # bulk
    "quantità", "grandi quantità",
}


'''Phase بعدی درست: LLM as Vocabulary Augmenter
ایده‌ی صحیح 👇
static_vocab  +  llm_suggestions  →  candidate_terms
                                  →  filtered / approved
                                  →  runtime vocab'''