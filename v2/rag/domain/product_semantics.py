import re
from rag.domain.vocabulary import build_domain_vocabulary

def extract_signals_from_name(name: str, vocab: set[str]) -> list[str]:
    name = name.lower()
    return [
        w for w in vocab
        if re.search(rf"\b{w}\b", name)
    ]
