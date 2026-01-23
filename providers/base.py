from abc import ABC, abstractmethod
from typing import List, Dict


class CatalogProvider(ABC):
    """
    Abstract interface for catalog sources
    (Excel, ERP, Scraping, API, ...)
    """

    @abstractmethod
    def load(self) -> List[Dict]:
        pass
