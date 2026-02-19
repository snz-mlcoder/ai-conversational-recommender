# rag/workflow/goal.py

from enum import Enum
from rag.workflow.schemas import SearchMemory
from rag.workflow.signals import is_question


class GoalDecision(Enum):
    ANSWER = "answer"
    ASK_BACK = "ask_back"
    SUGGEST = "suggest"
GOAL_CUES = {
    "cosa",
    "che",
    "quale",
    "meglio",
    "va bene",
    "consigli",
    "consigliami",
}

def is_goal_like(text: str) -> bool:
    text = text.lower()
    return "?" in text or any(cue in text for cue in GOAL_CUES)


def decide_goal(intent, memory: SearchMemory, normalized_message: str) -> GoalDecision:

    # Non search intents → just answer
    if intent.value != "product_search":
        return GoalDecision.ANSWER

    goal_like = is_goal_like(normalized_message)

    # -------------------------------------------------
    # 🔒 1️⃣ No product_type → never direct search
    # -------------------------------------------------
    if not memory.product_type:

        # If we have occasion/use_case → suggestion mode
        if memory.occasion or memory.use_case:
            return GoalDecision.SUGGEST

        # Otherwise → ask clarification
        return GoalDecision.ASK_BACK

    # -------------------------------------------------
    # 2️⃣ Product mentioned but no refinement → ask_back
    # -------------------------------------------------
    if goal_like:
        has_any_focus = any([
            memory.use_case,
            memory.occasion,
            bool(memory.attributes),
        ])
        if not has_any_focus:
            return GoalDecision.ASK_BACK

    # -------------------------------------------------
    # 3️⃣ Normal search
    # -------------------------------------------------
    return GoalDecision.ANSWER

