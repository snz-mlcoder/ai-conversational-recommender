from abc import ABC, abstractmethod
from rag.workflow.intent import Intent

class IntentClassifier(ABC):

    @abstractmethod
    def classify(self, text: str) -> Intent:
        pass
