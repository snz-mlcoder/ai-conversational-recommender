from abc import ABC, abstractmethod
from typing import List, Dict


class Ranker(ABC):

    @abstractmethod
    def rerank(self, results: List[Dict]) -> List[Dict]:
        pass
