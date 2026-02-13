class WorkflowEngine:

    def __init__(
        self,
        normalizer,
        intent_classifier,
        extractor,
        memory_reducer,
        goal_decider,
        executor,
        search_pipeline,
    ):
        self.normalizer = normalizer
        self.intent_classifier = intent_classifier
        self.extractor = extractor
        self.memory_reducer = memory_reducer
        self.goal_decider = goal_decider
        self.executor = executor
        self.search_pipeline = search_pipeline

    # =====================================================
    # MAIN PIPELINE
    # =====================================================



    def run(self, user_message, memory):

        from rag.workflow.intent import Intent
        print("\n======================")
        print("NEW REQUEST:", user_message)
        print("======================")

     

        # 1️⃣ Normalize
        normalized = self.normalizer.normalize(user_message)
        print("NORMALIZED:", normalized)

        # 🔥 Intent باید با متن خام تشخیص داده شود
        initial_intent = self.intent_classifier.classify(user_message.lower())
        intent = initial_intent
        print("INTENT INITIAL:", intent)

        # 3️⃣ Extraction
        rule_updates = self.extractor.extract(normalized, memory)
        print("RULE UPDATES:", rule_updates)

        # 4️⃣ Item conflict
        interrupt = self.handle_item_conflict(normalized, intent, memory)
        if interrupt:
            print("ITEM CONFLICT TRIGGERED")
            return interrupt

        # 5️⃣ Attribute override
        before_override = intent
        intent = self.handle_attribute_intent_override(normalized, intent)
        print("INTENT AFTER ATTRIBUTE OVERRIDE:", intent)

        # 6️⃣ Intent stabilization
        intent = self.stabilize_intent(intent, rule_updates)
        print("INTENT AFTER STABILIZATION:", intent)

        # 7️⃣ Memory update
        if intent.value == "product_search":
            memory = self.memory_reducer.reduce(memory, rule_updates)
            print("UPDATED MEMORY:", memory.dict())

        # 8️⃣ Goal decision
        goal = self.goal_decider.decide(intent, memory, normalized)
        print("GOAL DECISION:", goal)

        # 9️⃣ Goal hard gates
        early = self.handle_goal_gate(goal, memory)
        if early:
            print("GOAL GATE TRIGGERED")
            return early

        # 🔟 Slot ask-back
        slot_question = self.handle_slot_ask_back(intent, memory)
        if slot_question:
            print("SLOT ASK-BACK TRIGGERED")
            return slot_question

        # 1️⃣1️⃣ Execution (NON SEARCH)
        print("CHECKING EXECUTION FOR INTENT:", intent)
        execution = self.executor.handle_intent(intent, normalized, memory)
        if execution:
            reply, memory, _ = execution
            return (
                reply,
                memory,
                self._build_debug(
                    intent=intent.value,
                    rag_called=False,
                )
            )


        print("FALLING BACK TO SEARCH PIPELINE")
        # 🔒 RAG guard (IMPORTANT)
        from rag.workflow.intent import Intent
        if intent != Intent.PRODUCT_SEARCH:
            return (
                "Come posso aiutarti?",
                memory,
                self._build_debug(
                    intent=intent.value,
                    rag_called=False,
                )
            )


        # 1️⃣2️⃣ Search
        return self.search_pipeline.run(normalized, memory)

    # =====================================================
    # STAGES
    # =====================================================

    def _build_debug(
        self,
        intent: str,
        rag_called: bool = False,
        num_candidates: int = 0,
        num_groups: int = 0,
        recommendations=None,
    ):
        return {
            "engine_version": "v4",
            "intent": intent,
            "rag_called": rag_called,
            "num_candidates": num_candidates,
            "num_groups": num_groups,
            "recommendations": recommendations or [],
        }


    def handle_item_conflict(self, text, intent, memory):

        from rag.workflow.signals import (
            extract_product_signals,
            detect_item_mode,
            ItemMode,
        )
        from rag.workflow.ask_back_questions import build_item_ambiguity_question_it

        signals = extract_product_signals(text)
        print("ITEM SIGNALS:", signals)

        items = signals.get("items", [])

        if len(items) < 2:
            return None

        item_mode = detect_item_mode(text, items)
        print("ITEM MODE:", item_mode)

        if item_mode == ItemMode.COMPARISON:
            question = build_item_ambiguity_question_it(items)
            return question, memory, self._build_debug(
                intent="ask_back",
                rag_called=False,
            )


        return None

    def handle_attribute_intent_override(self, text, intent):

        from rag.workflow.signals import (
            extract_product_signals,
            detect_attribute_mode,
            AttributeMode,
        )
        from rag.workflow.intent import Intent

        signals = extract_product_signals(text)
        print("ATTRIBUTE SIGNALS:", signals)

        for group in ("colors", "materials", "sizes", "shapes"):
            values = signals.get(group)

            if not values or len(values) < 2:
                continue

            mode = detect_attribute_mode(text, values)
            print(f"ATTRIBUTE MODE for {group}:", mode)

            if mode == AttributeMode.COMPARISON:
                print("ATTRIBUTE OVERRIDE → MATERIAL_KNOWLEDGE")
                return Intent.MATERIAL_KNOWLEDGE

        return intent

    def stabilize_intent(self, intent, updates):

        from rag.workflow.intent import Intent

        if intent == Intent.SMALL_TALK:
            if updates.get("product_type"):
                print("INTENT STABILIZED → PRODUCT_SEARCH")
                return Intent.PRODUCT_SEARCH

        return intent

    def handle_goal_gate(self, goal, memory):

        from rag.workflow.goal import GoalDecision
        from rag.workflow.ask_back_questions import build_ask_back_question_it

        if goal == GoalDecision.SUGGEST:
            reply = (
                "Posso aiutarti con qualche idea. "
                "Ad esempio: piatti, bicchieri o accessori "
                f"per {memory.occasion or 'la tua occasione'}?"
            )
            return reply, memory, self._build_debug(
                intent="suggest",
                rag_called=False,
            )



        if goal == GoalDecision.ASK_BACK:
            question = build_ask_back_question_it("product_type", memory)
            return question, memory, self._build_debug(
                intent="ask_back",
                rag_called=False,
            )


        return None

    def handle_slot_ask_back(self, intent, memory):

        from rag.workflow.intent import Intent
        from rag.workflow.ask_back import decide_ask_back
        from rag.workflow.ask_back_questions import build_ask_back_question_it

        if intent != Intent.PRODUCT_SEARCH:
            return None

        ask_back = decide_ask_back(memory)
        print("ASK BACK RESULT:", ask_back)

        if ask_back.should_ask:
            question = build_ask_back_question_it(ask_back.slot, memory)
            return question, memory, self._build_debug(
                intent="ask_back",
                rag_called=False,
            )


        return None
