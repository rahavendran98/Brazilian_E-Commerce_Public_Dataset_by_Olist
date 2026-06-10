from pathlib import Path
import pandas as pd
from src.data_ingestion import load_all

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"

def missing_report(df):
    n = len(df)
    out = pd.DataFrame({
        "missing_count": df.isnull().sum(),
        "missing_pct": (df.isnull().sum() / n * 100).round(2),
    })
    return out[out.missing_count > 0].sort_values("missing_pct", ascending=False)

def duplicate_report(df, key=None):
    res = {"full_row_duplicates": int(df.duplicated().sum())}
    if key:
        res["key_duplicates"] = int(df.duplicated(subset=key).sum())
        res["key"] = key
    return res

def invalid_value_report(df):
    pur = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")
    deliv = pd.to_datetime(df["order_delivered_customer_date"], errors="coerce")
    return {
        "price_non_positive": int((df["price"] <= 0).sum()),
        "freight_negative": int((df["freight_value"] < 0).sum()),
        "payment_non_positive": int((df["payment_total"] <= 0).sum()),
        "review_out_of_range": int((~df["review_score"].dropna().between(1, 5)).sum()),
        "delivered_before_purchase": int((deliv < pur).sum()),
    }

def referential_integrity(data):
    def orphans(child, ck, parent, pk):
        return len(set(data[child][ck]) - set(data[parent][pk]))
    return {
        "items_order_id_orphans": orphans("order_items", "order_id", "orders", "order_id"),
        "items_product_id_orphans": orphans("order_items", "product_id", "products", "product_id"),
        "items_seller_id_orphans": orphans("order_items", "seller_id", "sellers", "seller_id"),
        "orders_customer_id_orphans": orphans("orders", "customer_id", "customers", "customer_id"),
    }

def completeness_score(df):
    return round((df.size - df.isnull().sum().sum()) / df.size * 100, 2)

def run_full_assessment():
    data = load_all()
    m = pd.read_parquet(PROCESSED / "integrated_dataset.parquet")
    return {
        "shape": m.shape,
        "completeness_pct": completeness_score(m),
        "missing": missing_report(m),
        "duplicates": duplicate_report(m, key=["order_id", "order_item_id"]),
        "invalid": invalid_value_report(m),
        "referential": referential_integrity(data),
    }
