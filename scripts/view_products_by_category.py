import json
from collections import defaultdict


# ===============================
# Load catalog
# ===============================

with open("data/processed/catalog.json", encoding="utf-8") as f:
    products = json.load(f)


# ===============================
# Group by category
# ===============================

by_category = defaultdict(list)

for p in products:
    category = p.get("category", "UNKNOWN")
    by_category[category].append(p)


# ===============================
# Print summary
# ===============================

print(f"\nTotal categories: {len(by_category)}")
print(f"Total products: {len(products)}\n")


# ===============================
# Print products per category
# ===============================

MAX_PRODUCTS_PER_CATEGORY = 5  # 👈 برای شلوغ نشدن ترمینال

for category_name in sorted(by_category.keys()):
    items = by_category[category_name]

    print("=" * 60)
    print(f"Category: {category_name}")
    print(f"Products: {len(items)}\n")

    for p in items[:MAX_PRODUCTS_PER_CATEGORY]:
        print(f"- {p['name']} | {p['price']}")

    if len(items) > MAX_PRODUCTS_PER_CATEGORY:
        print(f"... ({len(items) - MAX_PRODUCTS_PER_CATEGORY} more products)")

print("\nDONE")
