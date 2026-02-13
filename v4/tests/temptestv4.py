from rag.workflow_v4.api.workflow_api_v4 import build_engine
from rag.workflow.schemas import SearchMemory




def test_item_conflict():
    engine = build_engine()
    memory = SearchMemory()

    reply, updated_memory, debug = engine.run(
        "piatto o bicchiere?",
        memory
    )

    assert debug["intent"] == "ask_back"
    assert updated_memory is not None



def test_single_item():
    engine = build_engine()
    memory = SearchMemory()

    reply, updated_memory, debug = engine.run(
        "piatto",
        memory
    )

    assert debug["engine_version"] == "v4"



def test_simple_search():
    engine = build_engine()
    memory = SearchMemory()

    reply, updated_memory, debug = engine.run(
        "piatti rossi",
        memory
    )

    assert debug["engine_version"] == "v4"
    assert debug["rag_called"] is True
    assert updated_memory is not None


def test_material_comparison():
    engine = build_engine()
    memory = SearchMemory()

    reply, updated_memory, debug = engine.run(
        "acciaio o vetro?",
        memory
    )

    # فعلاً احتمالاً هنوز search می‌رود
    assert updated_memory is not None



def test_intent_stabilization():
    engine = build_engine()
    memory = SearchMemory()

    reply, updated_memory, debug = engine.run(
        "ciao cerco piatti rossi",
        memory
    )

    print("\n=== INTENT STABILIZATION ===")
    print("Reply:", reply)
    print("Debug:", debug)

    assert debug["engine_version"] == "v4"
