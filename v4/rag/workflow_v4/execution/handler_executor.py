class SimpleExecutor:

    def handle_goal(self, goal, memory):
        return None

    def handle_intent(self, intent, text, memory):
        from rag.workflow.intent import Intent
        from rag.workflow.handlers.material_knowledge import handle_material_knowledge
        from rag.workflow.handlers.knowledge_handler import handle_structured_knowledge
        from rag.workflow.knowledge.knowledge_loader import load_knowledge_data

        if intent == Intent.MATERIAL_KNOWLEDGE:
            reply = handle_material_knowledge(text)
            return reply, memory, {"intent": intent.value}

        if intent in {Intent.STORE_INFO, Intent.PROMOTION}:
            knowledge_data = load_knowledge_data()
            reply = handle_structured_knowledge(
                question=text,
                knowledge_data=knowledge_data,
                system_instruction="customer_support"
            )
            return reply, memory, {"intent": intent.value}

        return None
