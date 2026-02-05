from rag.workflow.ask_back import decide_ask_back
from rag.workflow.schemas import SearchMemory


def test_missing_everything():
    memory = SearchMemory()
    result = decide_ask_back(memory)

    print(result)
    assert result.should_ask is True
    assert result.slot == "product_type"


def test_missing_use_case():
    memory = SearchMemory(product_type="piatto")
    result = decide_ask_back(memory)

    print(result)
    assert result.should_ask is True
    assert result.slot == "use_case"


def test_ready_memory():
    memory = SearchMemory(
        product_type="piatto",
        use_case="casa",
        attributes={"color": "bianco"},
    )
    result = decide_ask_back(memory)

    print(result)
    assert result.should_ask is False


if __name__ == "__main__":
    test_missing_everything()
    test_missing_use_case()
    test_ready_memory()
