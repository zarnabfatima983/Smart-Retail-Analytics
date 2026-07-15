"""
Import SampleSuperstore.csv into the smart_retail MySQL database.

Usage:
    py dashboard/import_csv.py
"""

import os
import logging

import mysql.connector
import pandas as pd
from mysql.connector import Error

from config import CSV_FILE_PATH, CSV_ENCODING, DB_CONFIG, BATCH_SIZE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)

CSV_PATH = CSV_FILE_PATH

COLUMN_MAP = {
    "Row ID": "row_id",
    "Order ID": "order_id",
    "Order Date": "order_date",
    "Ship Date": "ship_date",
    "Ship Mode": "ship_mode",
    "Customer ID": "customer_id",
    "Customer Name": "customer_name",
    "Segment": "segment",
    "Country": "country",
    "City": "city",
    "State": "state",
    "Postal Code": "postal_code",
    "Region": "region",
    "Product ID": "product_id",
    "Category": "category",
    "Sub-Category": "sub_category",
    "Product Name": "product_name",
    "Sales": "sales",
    "Quantity": "quantity",
    "Discount": "discount",
    "Profit": "profit",
}

INSERT_SQL = """
INSERT INTO orders(
row_id,
order_id,
order_date,
ship_date,
ship_mode,
customer_id,
customer_name,
segment,
country,
city,
state,
postal_code,
region,
product_id,
category,
sub_category,
product_name,
sales,
quantity,
discount,
profit)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""


def load_csv():

    logger.info("Reading CSV...")

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(CSV_PATH)

    df = pd.read_csv(CSV_PATH, encoding=CSV_ENCODING)

    # Remove spaces
    df.columns = df.columns.str.strip()

    # Fix broken first header
    if "Row ID" not in df.columns:
        first = df.columns[0]
        if "Row ID" in first:
            df.rename(columns={first: "Row ID"}, inplace=True)

    df.rename(columns=COLUMN_MAP, inplace=True)

    df["order_date"] = pd.to_datetime(df["order_date"])
    df["ship_date"] = pd.to_datetime(df["ship_date"])

    logger.info("Loaded %d rows", len(df))

    return df


def main():

    df = load_csv()

    try:
        conn = mysql.connector.connect(**DB_CONFIG)

        cur = conn.cursor()

        cur.execute("TRUNCATE TABLE orders")

        records = []

        for _, r in df.iterrows():

            records.append((
                int(r["row_id"]),
                r["order_id"],
                r["order_date"].date(),
                r["ship_date"].date(),
                r["ship_mode"],
                r["customer_id"],
                r["customer_name"],
                r["segment"],
                r["country"],
                r["city"],
                r["state"],
                None if pd.isna(r["postal_code"]) else str(r["postal_code"]),
                r["region"],
                r["product_id"],
                r["category"],
                r["sub_category"],
                r["product_name"],
                float(r["sales"]),
                int(r["quantity"]),
                float(r["discount"]),
                float(r["profit"]),
            ))

        for i in range(0, len(records), BATCH_SIZE):
            cur.executemany(INSERT_SQL, records[i:i+BATCH_SIZE])

        conn.commit()

        cur.execute("SELECT COUNT(*) FROM orders")

        total = cur.fetchone()[0]

        print("\n===================================")
        print("✅ IMPORT SUCCESSFUL")
        print("===================================")
        print("Rows Imported :", len(records))
        print("Rows in MySQL :", total)
        print("===================================\n")

    except Error as e:
        print("\n❌ MYSQL ERROR")
        print(e)

    finally:
        if 'cur' in locals():
            cur.close()

        if 'conn' in locals() and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    main()