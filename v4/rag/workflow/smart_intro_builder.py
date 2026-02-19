def build_smart_mismatch_intro(memory, mismatches: dict):

    if not mismatches:
        return ""

    messages = []

    for attr, value in mismatches.items():
        messages.append(f"{memory.product_type} in {value}")

    joined = " e ".join(messages)

    return (
        f"Al momento non risultano {joined} con tutte le caratteristiche richieste.\n"
        "Ti propongo alcune alternative simili 👇\n\n"
    )
