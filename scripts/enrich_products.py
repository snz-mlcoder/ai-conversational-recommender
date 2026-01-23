import json
import time
from pathlib import Path

from catalog_builder.fetch import fetch_page
from catalog_builder.adapters.prestashop_product import parse_product_page
from catalog_builder.config import SCRAPE_DELAY


# -----------------------
# Paths
# -----------------------
INPUT_PATH = Path("data/processed/catalog.json")
OUTPUT_PATH = Path("data/processed/products_full.json")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# -----------------------
# Runner
# -----------------------
def run():
    if not INPUT_PATH.exists():
        print("❌ catalog.json not found. Run build_catalog.py first.")
        return

    with INPUT_PATH.open("r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"🔍 Enriching {len(products)} products...\n")

    enriched = []

    for idx, product in enumerate(products, start=1):
        print(f"[{idx}/{len(products)}] {product['name']}")

        try:
            html = fetch_page(product["url"])
            full = parse_product_page(html, product)
            enriched.append(full)
        except Exception as e:
            print(f"   ⚠️ Failed: {e}")

        time.sleep(SCRAPE_DELAY)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print("\n🎉 DONE")
    print(f"💾 Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    run()
