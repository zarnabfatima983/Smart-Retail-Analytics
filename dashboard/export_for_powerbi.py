"""
Export data to Excel for Power BI Desktop.

Output : reports/smart_retail_powerbi.xlsx
Usage  : python dashboard/export_for_powerbi.py
"""

import datetime as dt
import logging
import os
import sys
from typing import Callable

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

_HERE       = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.dirname(_HERE)
OUTPUT_PATH = os.path.join(_ROOT, "reports", "smart_retail_powerbi.xlsx")
CSV_PATH    = os.path.join(_HERE, "data", "SampleSuperstore.csv")

_QUERY = """
    SELECT
        row_id AS `Row ID`, order_id AS `Order ID`,
        order_date AS `Order Date`, ship_date AS `Ship Date`,
        ship_mode AS `Ship Mode`, customer_id AS `Customer ID`,
        customer_name AS `Customer Name`, segment AS `Segment`,
        country AS `Country`, city AS `City`, state AS `State`,
        postal_code AS `Postal Code`, region AS `Region`,
        product_id AS `Product ID`, category AS `Category`,
        sub_category AS `Sub-Category`, product_name AS `Product Name`,
        sales AS `Sales`, quantity AS `Quantity`,
        discount AS `Discount`, profit AS `Profit`
    FROM orders
"""


def load_dataframe() -> pd.DataFrame:
    try:
        sys.path.insert(0, _HERE)
        from database import get_connection  # noqa: PLC0415
        conn = get_connection()
        if conn:
            df = pd.read_sql(_QUERY, conn)
            conn.close()
            logger.info("Loaded %s rows from MySQL.", f"{len(df):,}")
            return df
    except Exception as e:
        logger.warning("MySQL unavailable (%s) — using CSV.", e)

    df = pd.read_csv(CSV_PATH, encoding="latin1")
    logger.info("Loaded %s rows from CSV.", f"{len(df):,}")
    return df


def build_orders(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Order Date"]      = pd.to_datetime(out["Order Date"])
    out["Ship Date"]       = pd.to_datetime(out["Ship Date"])
    out["Month"]           = out["Order Date"].dt.month
    out["Month Name"]      = out["Order Date"].dt.strftime("%b")
    out["Year"]            = out["Order Date"].dt.year
    out["Profit Margin %"] = out["Profit"] / out["Sales"].replace(0, float("nan")) * 100
    return out


def build_sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("Category", as_index=False)["Sales"]
              .sum().rename(columns={"Sales": "Total Sales"})
              .sort_values("Total Sales", ascending=False))


def build_sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("Region", as_index=False)["Sales"]
              .sum().rename(columns={"Sales": "Total Sales"})
              .sort_values("Total Sales", ascending=False))


def build_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Order Date"] = pd.to_datetime(out["Order Date"])
    out["Month"]      = out["Order Date"].dt.month
    return (out.groupby("Month", as_index=False)["Sales"]
               .sum().rename(columns={"Sales": "Total Sales"})
               .sort_values("Month"))


def build_subcategory_sales(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby(["Category", "Sub-Category"], as_index=False)
              .agg(**{"Total Sales": ("Sales", "sum"), "Total Profit": ("Profit", "sum")})
              .sort_values("Total Sales", ascending=False))


def build_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby(["Category", "Region"], as_index=False)["Sales"]
              .sum().rename(columns={"Sales": "Total Sales"})
              .sort_values(["Category", "Region"]))


def build_rfm(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Order Date"] = pd.to_datetime(out["Order Date"])
    snapshot = out["Order Date"].max() + dt.timedelta(days=1)

    rfm = (out.groupby(["Customer ID", "Customer Name"])
              .agg(Last_Order=("Order Date", "max"),
                   Frequency=("Order ID", "count"),
                   Monetary=("Sales", "sum"))
              .reset_index())

    rfm["Recency"] = (snapshot - rfm["Last_Order"]).dt.days
    rfm.drop(columns=["Last_Order"], inplace=True)

    rfm["R Score"] = pd.cut(rfm["Recency"],   bins=[0, 30, 90, 180, float("inf")], labels=[4, 3, 2, 1]).astype(int)
    rfm["F Score"] = pd.cut(rfm["Frequency"], bins=[0, 1, 4, 9, float("inf")],     labels=[1, 2, 3, 4]).astype(int)
    rfm["M Score"] = pd.cut(rfm["Monetary"],  bins=[0, 499, 999, 4999, float("inf")], labels=[1, 2, 3, 4]).astype(int)
    rfm["RFM Score"] = rfm["R Score"] + rfm["F Score"] + rfm["M Score"]

    def segment(s: int) -> str:
        if s >= 10: return "Champions"
        if s >= 7:  return "Loyal Customers"
        if s >= 5:  return "At Risk"
        return "Lost"

    rfm["Customer Segment"] = rfm["RFM Score"].apply(segment)
    return rfm.sort_values("Monetary", ascending=False)


SHEETS: list[tuple[str, Callable[[pd.DataFrame], pd.DataFrame]]] = [
    ("Orders",            build_orders),
    ("Sales_by_Category", build_sales_by_category),
    ("Sales_by_Region",   build_sales_by_region),
    ("Monthly_Trend",     build_monthly_trend),
    ("SubCategory_Sales", build_subcategory_sales),
    ("Heatmap_Data",      build_heatmap_data),
    ("RFM_Analysis",      build_rfm),
]


def _autofit(ws) -> None:
    for cols in ws.columns:
        max_len = max((len(str(c.value)) if c.value else 0) for c in cols)
        ws.column_dimensions[cols[0].column_letter].width = min(max_len + 4, 50)


def export(df: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl", date_format="YYYY-MM-DD") as writer:
        for name, fn in SHEETS:
            out = fn(df)
            out.to_excel(writer, sheet_name=name, index=False)
            _autofit(writer.sheets[name])
            logger.info("  ✓  %-22s %6s rows", name, f"{len(out):,}")
    logger.info("✅  Saved → %s", path)


def main() -> None:
    logger.info("Starting Power BI export...")
    export(load_dataframe(), OUTPUT_PATH)
    logger.info("Open reports/smart_retail_powerbi.xlsx in Power BI Desktop.")


if __name__ == "__main__":
    main()
