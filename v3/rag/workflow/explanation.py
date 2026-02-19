# rag/workflow/explanation.py
# [PHASE-2]: richer explanation based on clusters and attributes
# rag/workflow/explanation.py
# PHASE-2: polished explanation layer (demo-ready)

import random
import re
from rag.workflow.product_description import generate_product_snippet


INTRO_TEMPLATES = [
    "Ho trovato {count} {product_phrase} che potrebbero interessarti.",
    "Ecco {count} {product_phrase} che potrebbero fare al caso tuo.",
    "Ti propongo {count} {product_phrase} selezionati per te.",
]

GENERIC_INTROS = [
    "Ho trovato alcune opzioni interessanti per te.",
    "Ecco alcune proposte che potrebbero piacerti.",
]


# ----------------------------------
# Helpers
# ----------------------------------

IRREGULAR_PLURALS = {
    "bicchiere": "bicchieri",
    "piatto": "piatti",
    "tazza": "tazze",
}

def pluralize_it(word: str) -> str:
    word = word.lower()

    if word in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[word]

    if word.endswith("o"):
        return word[:-1] + "i"

    if word.endswith("a"):
        return word[:-1] + "e"

    if word.endswith("e"):
        return word[:-1] + "i"

    return word + "i"


def build_product_phrase(memory, count: int) -> str:
    product_type = memory.product_type or "prodotti"

    if count > 1:
        product_type = pluralize_it(product_type)

    attributes = []
    if memory.attributes:
        for value in memory.attributes.values():
            attributes.append(value)

    if attributes:
        return f"{product_type} in {' e '.join(attributes)}"

    return product_type


def clean_filename_from_url(url: str) -> str:
    """
    Deterministic filename cleaning.
    TEMPORARY SOLUTION until structured titles exist.
    """

    name = url.split("/")[-1]

    # remove extension
    name = re.sub(r"\.(jpg|jpeg|png|webp)$", "", name, flags=re.IGNORECASE)

    # replace hyphens with spaces
    name = name.replace("-", " ")

    # separate numbers stuck to words
    name = re.sub(r"(\d+)([a-zA-Z])", r"\1 \2", name)

    # collapse multiple spaces
    name = re.sub(r"\s+", " ", name).strip()

    return name.capitalize()


def safe_generate_snippet(result: dict) -> str:
    """
    Try LLM rewrite first.
    If anything fails, use cleaned filename.
    """

    try:
        snippet = generate_product_snippet(result)

        if snippet and len(snippet) > 5:
            return snippet.strip()

    except Exception:
        pass

    # deterministic fallback
    url = result.get("url", "")
    return clean_filename_from_url(url)


# ----------------------------------
# Main Explanation
# ----------------------------------

def generate_explanation(results, memory=None):
    count = len(results)

    if count == 0:
        return "Al momento non ho trovato risultati."

    # Intro
    if memory and memory.product_type:
        product_phrase = build_product_phrase(memory, count)
        intro = random.choice(INTRO_TEMPLATES).format(
            count=count,
            product_phrase=product_phrase,
        )
    else:
        intro = random.choice(GENERIC_INTROS)

    lines = [intro, ""]

    # Limit to first 3 for demo stability
    for r in results[:3]:
        snippet = safe_generate_snippet(r)
        url = r.get("url", "")

        lines.append(f"• <strong>{snippet}</strong>")
        lines.append(
            f'<a href="{url}" target="_blank" '
            f'style="color:#2563eb;text-decoration:none;font-size:13px;">'
            f'🔗 Vedi prodotto</a>'
        )
        lines.append("")

    return "\n".join(lines).strip()

'''
📌 deliberately ساده
📌 بدون LLM
📌 بدون hallucination
📌 فقط برای اینکه flow کامل بشه

🧠 چرا این کار درسته (و سرسری نیست)؟
چون:

interface نهایی explanation رو تثبیت کردی

orchestrator به abstraction وابسته‌ست، نه implementation

فردا می‌تونی اینو عوض کنی با:

Ollama

Gemini

Template-based explanation
بدون دست زدن به هیچ جای دیگه

این همون professional staging ـه.'''

