from catalog_builder.adapters.horecamart import HorecaMartAdapter

adapter = HorecaMartAdapter()
categories = adapter.discover_categories()

print(f"\nFound {len(categories)} categories:\n")

for c in categories[:15]:
    print(c)
