import pytest
from unittest.mock import patch

from rag.workflow.orchestrator import handle_user_message
from rag.workflow.schemas import SearchMemory
from rag.workflow.intent import Intent

def test_llm_rescues_intent_from_small_talk():
    memory = SearchMemory()

    user_message = "bicchere"

    # mock LLM extraction
    llm_result = {
        "product_type": "bicchiere",
        "attributes": {},
    }

    with patch("rag.workflow.orchestrator.llm_extract", return_value=llm_result):
        reply, updated_memory, debug = handle_user_message(user_message, memory)

    assert updated_memory.product_type == "bicchiere"
    assert debug["intent"] == Intent.PRODUCT_SEARCH.value




def test_rule_based_wins_over_llm():
    memory = SearchMemory()

    user_message = "bicchiere rosso"

    llm_result = {
        "product_type": "tazza",  # غلط
        "attributes": {"color": "rosso"},
    }

    with patch("rag.workflow.orchestrator.llm_extract", return_value=llm_result):
        _, updated_memory, debug = handle_user_message(user_message, memory)

    assert updated_memory.product_type == "bicchiere"



def test_llm_negation_does_not_add_attributes():
    memory = SearchMemory()

    user_message = "bicchiere non plastica"

    llm_result = {
        "product_type": "bicchiere",
        "negations": {"material": "__ANY__"},
    }

    with patch("rag.workflow.orchestrator.llm_extract", return_value=llm_result):
        _, updated_memory, _ = handle_user_message(user_message, memory)

    assert "material" not in updated_memory.attributes
