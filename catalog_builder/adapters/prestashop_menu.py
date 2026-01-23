from bs4 import BeautifulSoup
from typing import List, Optional

from ..fetch import fetch_page


class PrestaShopMenuAdapter:
    """
    Discover categories by parsing the HTML navigation menu.
    Works as a fallback when sitemap does not expose categories.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def discover_categories(self) -> List[dict]:
        html = fetch_page(self.base_url)
        soup = BeautifulSoup(html, "html.parser")

        categories: List[dict] = []

        # Try common navigation containers
        nav_candidates = soup.find_all(["nav", "ul"], recursive=True)

        for nav in nav_candidates:
            self._parse_menu_node(
                node=nav,
                categories=categories,
                parent=None
            )

        # Remove duplicates by URL
        unique = {}
        for c in categories:
            unique[c["url"]] = c

        return list(unique.values())

    # ---------- internal helpers ----------

    def _parse_menu_node(
        self,
        node,
        categories: List[dict],
        parent: Optional[str]
    ):
        """
        Recursively parse <ul>/<li> menu structures.
        """
        for li in node.find_all("li", recursive=False):
            link = li.find("a", href=True)
            if not link:
                continue

            url = link["href"].strip()
            name = link.get_text(strip=True)

            if not name or not self._is_category_url(url):
                continue

            category = {
                "name": name,
                "url": self._normalize_url(url),
                "parent": parent,
            }

            categories.append(category)

            # Look for nested menus (dropdowns)
            sub_menu = li.find("ul")
            if sub_menu:
                self._parse_menu_node(
                    node=sub_menu,
                    categories=categories,
                    parent=category["name"]
                )

    def _is_category_url(self, url: str) -> bool:
        """
        Heuristic to detect PrestaShop category URLs.
        Example:
        /3-tavola
        https://horecamart.it/138-posate
        """
        last = url.rstrip("/").split("/")[-1]
        return "-" in last and last.split("-")[0].isdigit()

    def _normalize_url(self, url: str) -> str:
        if url.startswith("http"):
            return url
        return f"{self.base_url}/{url.lstrip('/')}"
