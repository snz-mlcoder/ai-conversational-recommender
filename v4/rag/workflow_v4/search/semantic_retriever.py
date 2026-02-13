from rag.workflow_v4.search.retriever import Retriever
from rag.retrieval.search_product import ProductSearchEngine


class SemanticRetriever(Retriever):

    def __init__(self):
        self.engine = ProductSearchEngine()

    def retrieve(self, query: str):
        results = self.engine.search(query)
        return results
    