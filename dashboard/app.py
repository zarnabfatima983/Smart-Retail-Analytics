"""Smart Retail Analytics — Streamlit dashboard."""

import datetime as dt

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.linear_model import LinearRegression

from config import AUTH_CREDENTIALS, CACHE_TTL_SECONDS, CSV_ENCODING, CSV_FILE_PATH
from database import get_connection

# Colour palette
PRIMARY = "#2F5597"
TEAL    = "#1AA6B7"
ACCENT  = "#F28E2B"
GRAY    = "#A0A0A0"

QUERY = """
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


# --- Page setup ---

def configure_page() -> None:
    st.set_page_config(page_title="Retail Dashboard", layout="wide")
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "figure.facecolor": "#0e1117",
        "axes.facecolor":   "#0e1117",
        "axes.edgecolor":   GRAY,
        "axes.labelcolor":  GRAY,
        "xtick.color":      GRAY,
        "ytick.color":      GRAY,
        "text.color":       GRAY,
    })


# --- Auth ---

def handle_login() -> None:
    if "login" not in st.session_state:
        st.session_state.login = False
    if st.session_state.login:
        return

    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username == AUTH_CREDENTIALS["username"] and password == AUTH_CREDENTIALS["password"]:
            st.session_state.login = True
        else:
            st.sidebar.error("Invalid credentials")

    if not st.session_state.login:
        st.stop()


# --- Data ---

@st.cache_data(ttl=CACHE_TTL_SECONDS)
@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_data():
    conn = get_connection()

    if conn:
        st.success("✅ Connected to MySQL")

        try:
            return pd.read_sql(QUERY, conn)
        finally:
            conn.close()

    st.error("❌ MySQL Connection Failed")
    st.warning("⚠️ Using CSV")

    return pd.read_csv(CSV_FILE_PATH, encoding=CSV_ENCODING)

def prepare(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        st.error("No data found in the database.")
        st.stop()

    # Convert dates
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")

    # Convert numeric columns
    numeric_cols = ["Sales", "Profit", "Quantity", "Discount"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove rows with invalid numeric values
    df = df.dropna(subset=["Sales", "Profit"])

    # Create Month column
    df["Month"] = df["Order Date"].dt.month

    # Debug information
    print("\n===== DATA TYPES =====")
    print(df.dtypes)
    print("\n===== FIRST 5 ROWS =====")
    print(df.head())

    return df
# --- Filters ---

def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.title("🔎 Filters")
    category = st.sidebar.selectbox("Category", sorted(df["Category"].unique()))
    region   = st.sidebar.selectbox("Region",   sorted(df["Region"].unique()))
    segment  = st.sidebar.selectbox("Segment",  sorted(df["Segment"].unique()))
    return df[(df["Category"] == category) & (df["Region"] == region) & (df["Segment"] == segment)]


# --- KPIs ---

def render_kpis(df: pd.DataFrame) -> None:
    st.markdown("### 📌 Executive Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Sales",    f"${df['Sales'].sum():,.0f}")
    c2.metric("📈 Profit",   f"${df['Profit'].sum():,.0f}")
    c3.metric("🧾 Orders",   df["Order ID"].nunique())
    c4.metric("📦 Products", df["Product Name"].nunique())
    st.divider()


# --- Charts ---

def render_category_sales(df: pd.DataFrame) -> None:
    data = df.groupby("Category")["Sales"].sum()
    fig, ax = plt.subplots(figsize=(8, 4))
    data.plot(kind="bar", ax=ax, color=PRIMARY)
    ax.set_title("Sales by Category")
    ax.set_ylabel("Sales ($)")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.tick_params(axis="x", rotation=0)
    st.pyplot(fig)
    plt.close(fig)


def render_region_sales(df: pd.DataFrame) -> None:
    data = df.groupby("Region")["Sales"].sum()
    fig, ax = plt.subplots(figsize=(6, 6))
    data.plot(kind="pie", autopct="%1.1f%%", ax=ax, startangle=90,
              colors=sns.color_palette("YlGn", len(data)),
              textprops={"color": "white"})
    ax.set_ylabel("")
    ax.set_title("Sales by Region", color="white")
    st.pyplot(fig)
    plt.close(fig)


def render_monthly_trend(df: pd.DataFrame) -> None:
    data = df.groupby("Month")["Sales"].sum()
    fig, ax = plt.subplots(figsize=(10, 4))
    data.plot(ax=ax, marker="o", color=TEAL)
    ax.set_title("Monthly Sales Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Sales ($)")
    ax.grid(True, linestyle="--", alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)


def render_subcategory_sales(filtered: pd.DataFrame) -> None:
    data = filtered.groupby("Sub-Category")["Sales"].sum()
    fig, ax = plt.subplots(figsize=(8, 4))
    data.sort_values().plot(kind="barh", ax=ax, color=ACCENT)
    ax.set_title("Sub-Category Sales (Filtered)")
    ax.set_xlabel("Sales ($)")
    ax.grid(True, linestyle="--", alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)


def render_heatmap(df: pd.DataFrame) -> None:
    pivot = df.pivot_table(values="Sales", index="Category", columns="Region", aggfunc="sum")
    fig, ax = plt.subplots()
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGn", ax=ax)
    ax.set_title("Sales Heatmap (Category × Region)")
    st.pyplot(fig)
    plt.close(fig)


# --- AI Insights ---

def render_ai_insights(df: pd.DataFrame) -> None:
    total_sales  = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    margin       = (total_profit / total_sales) * 100

    if margin > 20:
        note = "Business is highly profitable and performing well."
    elif margin > 10:
        note = "Business is moderately profitable."
    else:
        note = "Business needs improvement in cost or pricing strategy."

    st.info(
        f"**Total Sales:** ${total_sales:,.0f}  \n"
        f"**Total Profit:** ${total_profit:,.0f}  \n"
        f"**Profit Margin:** {margin:.2f}%  \n\n"
        f"📌 **Key Insight:** {note}"
    )


# --- Forecast ---

def render_forecast(df: pd.DataFrame) -> None:
    monthly = df.groupby("Month")["Sales"].sum().reset_index()
    model   = LinearRegression().fit(monthly[["Month"]], monthly["Sales"])
    future  = pd.DataFrame({"Month": [13, 14, 15]})
    st.dataframe(
        pd.DataFrame({"Month": [13, 14, 15], "Predicted Sales": model.predict(future).round(2)}),
        use_container_width=True,
    )


# --- RFM ---

def render_rfm(df: pd.DataFrame) -> None:
    snapshot = df["Order Date"].max() + dt.timedelta(days=1)
    rfm = (
        df.groupby("Customer ID")
          .agg(
              Recency   =("Order Date", lambda x: (snapshot - x.max()).days),
              Frequency =("Order ID",   "count"),
              Monetary  =("Sales",      "sum"),
          )
          .sort_values("Monetary", ascending=False)
    )
    st.dataframe(rfm.head(20), use_container_width=True)


# --- Layout ---

def render_dashboard(df: pd.DataFrame, filtered: pd.DataFrame) -> None:
    st.title("📊 Smart Retail Analytics Dashboard")

    render_kpis(df)

    col_l, col_r = st.columns([3, 2])
    with col_l:
        render_category_sales(df)
    with col_r:
        render_region_sales(df)

    render_monthly_trend(df)
    render_subcategory_sales(filtered)

    st.divider()
    st.subheader("🤖 AI Business Insights")
    render_ai_insights(df)

    st.divider()
    st.subheader("📈 Future Sales Forecast (Next 3 Months)")
    render_forecast(df)

    st.divider()
    st.subheader("🔥 Sales Heatmap")
    render_heatmap(df)

    st.divider()
    st.subheader("👥 Customer Segmentation — RFM Analysis")
    render_rfm(df)


# --- Entry point ---

def main() -> None:
    configure_page()
    handle_login()
    df      = prepare(load_data())
    filtered = render_filters(df)
    render_dashboard(df, filtered)


if __name__ == "__main__":
    main()
