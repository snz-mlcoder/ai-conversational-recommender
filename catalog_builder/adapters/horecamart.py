from bs4 import BeautifulSoup
from typing import List, Optional

from .base import BaseCatalogAdapter
from ..fetch import fetch_page
from ..config import BASE_URL
import json


class HorecaMartAdapter(BaseCatalogAdapter):
    """
    Adapter for horecamart.it
    - Discovers leaf categories from nested menus
    - Extracts products from category pages
    - Supports pagination
    """

    # ===============================
    # CATEGORY DISCOVERY
    # ===============================

    def discover_categories(self) -> list:
        html = fetch_page(BASE_URL)
        soup = BeautifulSoup(html, "html.parser")

        categories: List[dict] = []

        # Walk all menus (Prestashop + Elementor safe)
        for ul in soup.find_all("ul"):
            self._walk_menu(ul, parent=None, results=categories)

        # Remove duplicates by URL
        unique = {c["url"]: c for c in categories}
        return list(unique.values())

    def _walk_menu(
        self,
        ul,
        parent: Optional[str],
        results: List[dict]
    ):
        for li in ul.find_all("li", recursive=False):
            a_tag = li.find("a", href=True)
            if not a_tag:
                continue

            name = a_tag.get_text(strip=True)
            url = a_tag["href"].strip()

            if not name or not self._is_category_url(url):
                continue

            full_url = self._normalize_url(url)

            sub_ul = li.find("ul")

            if sub_ul:
                # Not a leaf → go deeper
                self._walk_menu(
                    sub_ul,
                    parent=name,
                    results=results
                )
            else:
                # Leaf category → keep it
                results.append({
                    "name": name,
                    "url": full_url,
                    "parent": parent
                })

    def _is_category_url(self, url: str) -> bool:
        """
        Matches PrestaShop category URLs:
        /3-tavola
        /138-posate
        """
        last = url.rstrip("/").split("/")[-1]
        return "-" in last and last.split("-")[0].isdigit()

    def _normalize_url(self, url: str) -> str:
        if url.startswith("http"):
            return url
        return f"{BASE_URL.rstrip('/')}/{url.lstrip('/')}"

    # ===============================
    # PRODUCT EXTRACTION
    # ===============================

    def parse_category_page(self, html: str, category: dict) -> list:
        soup = BeautifulSoup(html, "html.parser")
        products = []
        seen = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]

            # product URLs in PrestaShop
            if not href.endswith(".html"):
                continue

            url = self._normalize_url(href)
            if url in seen:
                continue

            name = a.get_text(strip=True)
            if not name or len(name) < 5:
                continue

            seen.add(url)

            products.append({
                "name": name,
                "url": url,
                "price": None,  # fetch later from product page
                "category": category["name"],
                "parent_category": category.get("parent"),
                "source": "horecamart"
            })

        return products



    # ===============================
    # PAGINATION
    # ===============================

    def find_next_page(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        link = soup.find("link", rel="next")

        if link and link.get("href"):
            return link["href"]

        return None
