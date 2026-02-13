from rag.workflow_v4.engine.workflow_engine import WorkflowEngine
from rag.workflow_v4.intent.rule_based import RuleBasedIntentClassifier
from rag.workflow.schemas import SearchMemory

# temporary adapters (reuse v1 logic)
from rag.workflow.normalization import normalize_text
from rag.workflow.extraction import extract_memory
from rag.workflow.memory import update_memory
from rag.workflow.goal import decide_goal
from rag.workflow.handlers.store_info import handle_store_info
from rag.workflow.handlers.promotion import handle_promotion
from rag.workflow.handlers.material_knowledge import handle_material_knowledge
from rag.workflow.search_step import build_rag_query, call_rag
from rag.workflow.explanation import generate_explanation
from rag.workflow_v4.execution.handler_executor import SimpleExecutor

from rag.workflow_v4.search.semantic_retriever import SemanticRetriever
from rag.workflow_v4.search.search_pipeline import SearchPipeline
from rag.workflow_v4.search.business_ranker import BusinessAwareRanker

from rag.workflow_v4.search.reasoning_pipeline import ReasoningPipeline

# Temporary lightweight adapters
class SimpleNormalizer:
    def normalize(self, text):
        return normalize_text(text)

class SimpleExtractor:
    def extract(self, text, memory):
        return extract_memory(text, memory)

class SimpleMemoryReducer:
    def reduce(self, memory, updates):
        return update_memory(memory, updates)

class SimpleGoalDecider:
    def decide(self, intent, memory, text):
        return decide_goal(intent, memory, text)

class SimpleSearchPipeline:

    def __init__(self):
        self.reasoning = ReasoningPipeline(debug=True)

    def run(self, text, memory):

        rag_query = build_rag_query(memory, text)
        candidates = call_rag(rag_query)

        aggregated = self.reasoning.run(
            query=rag_query.text,
            candidates=candidates,
        )

        recommendations = aggregated.get("recommendations", [])

        return (
            "Ecco alcune proposte per te:",
            memory,
            {
                "engine_version": "v4",
                "intent": "product_search",
                "rag_called": True,
                "num_candidates": len(candidates),
                "num_groups": len(recommendations),
                "recommendations": recommendations,
            },
        )

def build_engine():

    retriever = SemanticRetriever()
    ranker = BusinessAwareRanker()

    return WorkflowEngine(
        normalizer=SimpleNormalizer(),
        intent_classifier=RuleBasedIntentClassifier(),
        extractor=SimpleExtractor(),
        memory_reducer=SimpleMemoryReducer(),
        goal_decider=SimpleGoalDecider(),
        executor=SimpleExecutor(),
        search_pipeline=SearchPipeline(retriever, ranker),
    )
