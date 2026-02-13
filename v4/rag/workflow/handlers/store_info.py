from rag.workflow.knowledge.store_info_data import STORE_INFO


def handle_store_info(question: str) -> str:
    text = question.lower()

    if any(k in text for k in {"spedizione", "consegna", "corriere"}):
        s = STORE_INFO["shipping"]
        return (
            f"Spediamo con {', '.join(s['couriers'])}. "
            f"Gli ordini vengono evasi entro {s['handling_time_days']} giorni. "
            f"La consegna richiede {s['delivery_time_days']}. "
            f"La spedizione è gratuita per ordini superiori a {s['free_shipping_threshold']}€."
        )

    if any(k in text for k in {"reso", "resi", "rimborso"}):
        r = STORE_INFO["returns"]
        return (
            f"Puoi effettuare un reso entro {r['return_window_days']} giorni. "
            f"Il rimborso viene elaborato entro {r['refund_window_days']} giorni. "
            f"I costi di spedizione del reso sono a carico del {r['return_shipping_paid_by']}."
        )

    if any(k in text for k in {"pagamento", "pagare", "pagamenti"}):
        p = STORE_INFO["payments"]
        return (
            "Accettiamo pagamenti sicuri tramite connessione SSL. "
            f"Il pagamento deve essere effettuato entro {p['payment_deadline_days']} giorni."
        )

    if any(k in text for k in {"telefono", "email", "contatti"}):
        return (
            f"Puoi contattarci via email a {STORE_INFO['email']} "
            f"oppure telefonicamente al {STORE_INFO['phone']}."
        )

    return (
        "Siamo a disposizione per informazioni su spedizioni, resi, "
        "pagamenti e assistenza clienti."
    )
