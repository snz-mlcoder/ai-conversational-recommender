from abc import ABC, abstractmethod


class BaseCatalogAdapter(ABC):
    """
    Abstract base class for e-commerce catalog adapters.
    """

    @abstractmethod
    def discover_categories(self) -> list:
        """
        Discover product categories.

        Returns:
            list of dicts:
            [
              {
                "parent": str | None,
                "name": str,
                "url": str
              }
            ]
        """
        pass

    @abstractmethod
    def parse_category_page(self, html: str, category: dict) -> list:
        """
        Parse a category page and extract product data.

        Args:
            html (str): HTML content
            category (dict): Category metadata

        Returns:
            list of product dicts
        """
        pass
