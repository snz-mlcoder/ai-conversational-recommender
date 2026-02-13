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
    if intent.value != "product_search":
        return GoalDecision.ANSWER

    goal_like = is_goal_like(normalized_message)

    # 1️⃣ Idea seeking → SUGGEST
    if not memory.product_type:
        if (memory.occasion or memory.use_case) and goal_like:
            return GoalDecision.SUGGEST

    # 2️⃣ Product mentioned but no criteria → ASK_BACK
    if memory.product_type and goal_like:
        has_any_focus = any([
            memory.use_case,
            memory.occasion,
            bool(memory.attributes),
        ])
        if not has_any_focus:
            return GoalDecision.ASK_BACK

    return GoalDecision.ANSWER
