import json
import pandas as pd
from pathlib import Path


# =======================
# CONFIGURATION
# =======================

# Input catalog file (CSV or Excel)
INPUT_FILE = Path("rag/data/raw/company_catalog.csv")

# Output unified catalog JSON
OUTPUT_JSON = Path("rag/data/processed/company_catalog.json")

# Ensure output directory exists
OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)


# =======================
# HELPERS
# =======================

def load_table(path: Path) -> pd.DataFrame:
    """
    Load a tabular catalog file (CSV or Excel) into a pandas DataFrame.
    Automatically handles common CSV settings used in EU/IT exports.
    """
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(
            path,
            sep=";",              # Common CSV separator in Italian exports
            encoding="utf-8-sig"  # Handles BOM from Excel / Google Sheets
        )

    elif suffix in [".xls", ".xlsx"]:
        return pd.read_excel(path)

    else:
        raise ValueError(f"Unsupported file format: {suffix}")


# =======================
# MAIN
# =======================

def run():
    """
    Convert a company catalog file into a unified JSON schema
    suitable for downstream RAG processing.
    """
    if not INPUT_FILE.exists():
        print("❌ Input file not found.")
        return

    print(f"📊 Reading catalog: {INPUT_FILE.name}")
    df = load_table(INPUT_FILE)

    products = []

    for _, row in df.iterrows():
        product = {
            # Unique product identifier
            "id": str(row.get("Product ID")),

            # Product name/title
            "name": str(row.get("Nome")).strip()
                if pd.notna(row.get("Nome")) else None,

            # Hierarchical category path (used by RAG)
            "category_path": [
                str(row.get("Categoria")).strip()
            ] if pd.notna(row.get("Categoria")) else [],

            # Product features (optional, can be enriched later)
            "features": [],

            # Stored for display/filtering but NOT embedded
            "price": float(row.get("Prezzo (tasse incl.)"))
                if pd.notna(row.get("Prezzo (tasse incl.)")) else None,

            # Stock quantity / availability
            "availability": int(row.get("Quantità"))
                if pd.notna(row.get("Quantità")) else None,

            # Product page URL (used by chatbot for linking)
            "url": str(row.get("Immagine")).strip()
                if pd.notna(row.get("Immagine")) else None,

            # Image URLs (optional future enrichment)
            "images": [],

            # Data source identifier
            "source": "company_catalog",
        }

        products.append(product)

    # Write unified catalog to JSON
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print("🎉 DONE")
    print(f"📦 Products exported: {len(products)}")
    print(f"💾 Output: {OUTPUT_JSON}")


if __name__ == "__main__":
    run()
