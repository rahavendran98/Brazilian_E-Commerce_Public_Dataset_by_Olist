from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

FILES = {
    "customers":   "olist_customers_dataset.csv",
    "orders":      "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments":    "olist_order_payments_dataset.csv",
    "reviews":     "olist_order_reviews_dataset.csv",
    "products":    "olist_products_dataset.csv",
    "sellers":     "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category":    "product_category_name_translation.csv",
}

def load_table(name, raw_dir=RAW_DIR):
    if name not in FILES:
        raise KeyError(f"Unknown table {name}. Valid: {list(FILES)}")
    return pd.read_csv(raw_dir / FILES[name])

def load_all(raw_dir=RAW_DIR):
    return {name: pd.read_csv(raw_dir / fname) for name, fname in FILES.items()}
