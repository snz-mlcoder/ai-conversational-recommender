from rag.workflow_v4.intent.base import IntentClassifier
from rag.workflow.intent import detect_intent

class RuleBasedIntentClassifier(IntentClassifier):

    def classify(self, text: str):
        return detect_intent(text)
