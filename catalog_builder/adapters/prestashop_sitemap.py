from ..fetch import fetch_page
import xml.etree.ElementTree as ET


class PrestaShopSitemapAdapter:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def discover_categories(self) -> list:
        sitemap_urls = self._discover_sitemaps()
        categories = []

        for sitemap_url in sitemap_urls:
            urls = self._parse_sitemap(sitemap_url)
            for url in urls:
                if self._is_category_url(url):
                    categories.append({
                        "parent": None,
                        "name": self._slug_to_name(url),
                        "url": url
                    })

        return categories

    # ---------- helpers ----------

    def _discover_sitemaps(self) -> list:
        candidates = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/index.php?controller=sitemap",
        ]

        valid = []
        for url in candidates:
            try:
                fetch_page(url)
                valid.append(url)
            except Exception:
                continue

        return valid

    def _parse_sitemap(self, sitemap_url: str) -> list:
        print(f"Parsing sitemap: {sitemap_url}")

        xml_text = fetch_page(sitemap_url)

        # Quick sanity check: must look like XML
        if not xml_text.strip().startswith("<"):
            return []

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return []

        urls = []

        # Case 1: sitemap index
        if root.tag.endswith("sitemapindex"):
            for sitemap in root.findall(".//{*}sitemap"):
                loc = sitemap.find("{*}loc")
                if loc is not None and loc.text:
                    urls.extend(self._parse_sitemap(loc.text.strip()))

        # Case 2: normal urlset
        if root.tag.endswith("urlset"):
            for url in root.findall(".//{*}url"):
                loc = url.find("{*}loc")
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())

        return urls

    def _is_category_url(self, url: str) -> bool:
        last = url.rstrip("/").split("/")[-1]
        return "-" in last and last.split("-")[0].isdigit()

    def _slug_to_name(self, url: str) -> str:
        slug = url.rstrip("/").split("/")[-1]
        parts = slug.split("-", 1)
        return parts[1].replace("-", " ").title() if len(parts) > 1 else slug
