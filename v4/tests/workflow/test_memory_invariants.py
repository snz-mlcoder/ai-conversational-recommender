import pytest

from rag.workflow.schemas import SearchMemory
from rag.workflow.memory import (
    update_memory,
    memory_ready,
    memory_to_text,
)
from rag.workflow.extraction import extract_memory

def test_update_memory_is_deterministic():
    memory = SearchMemory()

    updates = extract_memory("bicchiere rosso", memory)

    m1 = update_memory(SearchMemory(), updates)
    m2 = update_memory(SearchMemory(), updates)

    assert m1 == m2

def test_negation_only_removes_attributes():
    memory = SearchMemory(attributes={"material": "plastica"})

    updates = {
        "negations": {
            "material": "__ANY__"
        }
    }

    updated = update_memory(memory, updates)

    assert "material" not in updated.attributes

def test_unknown_keys_are_ignored():
    memory = SearchMemory()

    updates = {
        "price": "cheap",      # ❌ نباید وارد شود
        "brand": "ikea",       # ❌ نباید وارد شود
        "product_type": "bicchiere"  # ✅ مجاز
    }

    updated = update_memory(memory, updates)

    assert updated.product_type == "bicchiere"
    assert not hasattr(updated, "price")
    assert not hasattr(updated, "brand")

def test_memory_ready_only_when_product_type_exists():
    m1 = SearchMemory()
    assert memory_ready(m1) is False

    m2 = SearchMemory(product_type="bicchiere")
    assert memory_ready(m2) is True

def test_memory_to_text_contains_only_explicit_signals():
    memory = SearchMemory(
        product_type="bicchiere",
        attributes={
            "color": "rosso",
            "material": "vetro",
        }
    )

    query = memory_to_text(memory)

    assert "bicchiere" in query
    assert "rosso" in query
    assert "vetro" in query
