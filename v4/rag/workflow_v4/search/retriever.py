from abc import ABC, abstractmethod
from typing import List


class Retriever(ABC):

    @abstractmethod
    def retrieve(self, query: str) -> List[dict]:
        pass
