class SimpleExecutor:

    def handle_goal(self, goal, memory):
        return None

    def handle_intent(self, intent, text, memory):
        from rag.workflow.intent import Intent
        from rag.workflow.handlers.material_knowledge import handle_material_knowledge
        from rag.workflow.handlers.store_info import handle_store_info
        from rag.workflow.handlers.promotion import handle_promotion

        if intent == Intent.MATERIAL_KNOWLEDGE:
            reply = handle_material_knowledge(text)
            return reply, memory, {"intent": intent.value}

        if intent == Intent.STORE_INFO:
            from rag.workflow.handlers.store_info import handle_store_info
            reply = handle_store_info(text)
            return reply, memory, {"intent": intent.value}

        if intent == Intent.PROMOTION:
            from rag.workflow.handlers.promotion import handle_promotion
            reply = handle_promotion(text)
            return reply, memory, {"intent": intent.value}

        return None
