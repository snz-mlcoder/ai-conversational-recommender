from rag.workflow.schemas import AskBackResult, SearchMemory


def decide_ask_back(memory: SearchMemory) -> AskBackResult:

    # 🔥 تنها شرط اجباری
    if not memory.product_type:
        return AskBackResult(
            should_ask=True,
            slot="product_type",
            reason="missing_product_type",
        )

    # use_case دیگر blocking نیست
    return AskBackResult(should_ask=False)


