import hashlib
from bs4 import BeautifulSoup


def make_id(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def parse_product_page(html: str, product_stub: dict) -> dict:
    """
    Parse a PrestaShop product page.

    Args:
        html (str): HTML of product page
        product_stub (dict): product data from catalog phase (name, url, category...)

    Returns:
        dict: enriched product data
    """
    soup = BeautifulSoup(html, "html.parser")

    # -----------------------
    # NAME (canonical)
    # -----------------------
    name_tag = soup.select_one("h1")
    name = name_tag.get_text(strip=True) if name_tag else product_stub.get("name")

    # -----------------------
    # PRICE
    # -----------------------
    price = None
    price_tag = soup.select_one(".current-price span, .product-price")
    if price_tag:
        price = price_tag.get_text(strip=True)

    # -----------------------
    # DESCRIPTION
    # -----------------------
    description = None

    desc_candidates = [
        "#description",
        ".product-description",
        "[itemprop='description']"
    ]

    for selector in desc_candidates:
        desc_tag = soup.select_one(selector)
        if desc_tag:
            description = desc_tag.get_text(" ", strip=True)
            break

    # -----------------------
    # FEATURES / SPECS
    # -----------------------
    features = []

    # table-based specs (very common in PrestaShop)
    for row in soup.select("table tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) == 2:
            key = cells[0].get_text(strip=True)
            val = cells[1].get_text(strip=True)
            if key and val:
                features.append(f"{key}: {val}")

    # list-based features
    if not features:
        for li in soup.select(".product-features li"):
            text = li.get_text(" ", strip=True)
            if text:
                features.append(text)

    # -----------------------
    # IMAGES
    # -----------------------
    images = []
    for img in soup.select("img"):
        src = img.get("src")
        if src and "product" in src:
            images.append(src)

    images = list(dict.fromkeys(images))  # dedupe

    # -----------------------
    # AVAILABILITY
    # -----------------------
    availability = None
    avail_tag = soup.select_one(".product-availability")
    if avail_tag:
        text = avail_tag.get_text(strip=True).lower()
        availability = "in_stock" if "dispon" in text else "out_of_stock"

    # -----------------------
    # CATEGORY PATH (optional)
    # -----------------------
    category_path = []
    for crumb in soup.select(".breadcrumb a"):
        label = crumb.get_text(strip=True)
        if label and label.lower() not in ("home", "homepage"):
            category_path.append(label)

    # -----------------------
    # FINAL OBJECT
    # -----------------------
    return {
        "id": make_id(product_stub["url"]),
        "name": name,
        "url": product_stub["url"],
        "price": price,
        "description": description,
        "features": features,
        "images": images,
        "availability": availability,
        "category_path": category_path or [
            product_stub.get("parent_category"),
            product_stub.get("category"),
        ],
        "source": product_stub.get("source", "prestashop"),
    }
