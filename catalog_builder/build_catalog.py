import json
from pathlib import Path

from catalog_builder.fetch import fetch_page
from catalog_builder.adapters.horecamart import HorecaMartAdapter


# ===============================
# Output configuration
# ===============================

OUTPUT_PATH = Path("data/processed/catalog.json")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# ===============================
# Main runner
# ===============================

def run():
    """
    Build full product catalog:
    - Discover categories
    - Crawl each category
    - Follow pagination
    - Extract all products
    - Save to JSON
    """

    adapter = HorecaMartAdapter()

    print("🔍 Discovering categories...")
    categories = adapter.discover_categories()

    if not categories:
        print("❌ No categories found. Aborting.")
        return

    print(f"✅ Found {len(categories)} categories\n")

    all_products = []

    for idx, category in enumerate(categories, start=1):
        print(f"[{idx}/{len(categories)}] Category: {category['name']}")

        page_url = category["url"]
        page_num = 1

        while page_url:
            print(f"   ↳ Page {page_num}: {page_url}")

            html = fetch_page(page_url)
            if not html:
                break

            products = adapter.parse_category_page(html, category)

            if products:
                all_products.extend(products)
                print(f"     + {len(products)} products")
            else:
                print("     + 0 products")

            page_url = adapter.find_next_page(html)
            page_num += 1

    if not all_products:
        print("\n❌ No products extracted.")
        return

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print("\n🎉 DONE")
    print(f"📦 Total products: {len(all_products)}")
    print(f"💾 Saved to: {OUTPUT_PATH}")


# ===============================
# Entry point
# ===============================

if __name__ == "__main__":
    run()
