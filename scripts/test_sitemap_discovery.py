from catalog_builder.adapters.prestashop_sitemap import PrestaShopSitemapAdapter


def main():
    adapter = PrestaShopSitemapAdapter("https://horecamart.it")
    categories = adapter.discover_categories()

    print("Total categories found:", len(categories))
    print("-" * 40)

    for c in categories[:10]:
        print(c)


if __name__ == "__main__":
    main()
