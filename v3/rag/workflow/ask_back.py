from rag.workflow.schemas import AskBackResult, SearchMemory


def decide_ask_back(memory: SearchMemory) -> AskBackResult:

    # 1️⃣ Blocking: product type
    if not memory.product_type:
        return AskBackResult(
            should_ask=True,
            slot="product_type",
            reason="missing_product_type",
        )

    # 2️⃣ Blocking: use case
    if not memory.use_case:
        return AskBackResult(
            should_ask=True,
            slot="use_case",
            reason="missing_use_case",
        )

    # 3️⃣ Non-blocking attributes ❌ REMOVED
    return AskBackResult(should_ask=False)

