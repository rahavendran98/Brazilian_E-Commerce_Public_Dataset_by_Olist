from pathlib import Path
import pandas as pd
from src.data_ingestion import load_all

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"

def aggregate_payments(payments):
    return payments.groupby("order_id").agg(
        payment_total=("payment_value", "sum"),
        payment_count=("payment_sequential", "max"),
        max_installments=("payment_installments", "max"),
        main_payment_type=("payment_type", lambda s: s.mode().iloc[0]),
    ).reset_index()

def aggregate_reviews(reviews):
    r = reviews.copy()
    r["review_creation_date"] = pd.to_datetime(r["review_creation_date"])
    return (r.sort_values("review_creation_date")
              .groupby("order_id")
              .agg(review_score=("review_score", "last"))
              .reset_index())

def build_master(data=None):
    if data is None:
        data = load_all()
    pay_agg = aggregate_payments(data["payments"])
    rev_agg = aggregate_reviews(data["reviews"])
    products = data["products"].merge(data["category"], on="product_category_name", how="left")
    master = (data["order_items"]
        .merge(data["orders"],    on="order_id",    how="left")
        .merge(data["customers"], on="customer_id", how="left")
        .merge(products,          on="product_id",  how="left")
        .merge(data["sellers"],   on="seller_id",   how="left")
        .merge(pay_agg,           on="order_id",    how="left")
        .merge(rev_agg,           on="order_id",    how="left"))
    return master

def save_master(master):
    PROCESSED.mkdir(parents=True, exist_ok=True)
    master.to_parquet(PROCESSED / "integrated_dataset.parquet", index=False)
    master.to_csv(PROCESSED / "integrated_dataset.csv", index=False)
