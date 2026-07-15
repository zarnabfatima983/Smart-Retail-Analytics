# 📊 Smart Retail Analytics Dashboard

A professional retail analytics dashboard built with **Python**, **Pandas**, **Plotly**, **Streamlit**, and **MySQL**.

---

## Features

- 🔐 Login authentication
- 📌 KPI summary cards (Sales, Profit, Orders, Products)
- 📊 Sales by Category (bar chart)
- 🌎 Sales by Region (pie chart)
- 📈 Monthly Sales Trend (line chart)
- 🔎 Interactive sidebar filters (Category, Region, Segment)
- 🤖 AI Business Insights
- 📈 ML Sales Forecast (Linear Regression)
- 🔥 Sales Heatmap (Category × Region)
- 👥 Customer Segmentation – RFM Analysis
- 🗄️ MySQL database backend
- 📊 Power BI integration (MySQL direct + Excel export)

---

## Project Structure

```
Smart-Retail-Analytics2/
├── dashboard/
│   ├── app.py                   # Main Streamlit dashboard
│   ├── database.py              # MySQL connection module
│   ├── config.py                # Centralised configuration
│   ├── import_csv.py            # CSV → MySQL import script
│   ├── export_for_powerbi.py    # MySQL/CSV → Excel export for Power BI
│   └── data/
│       └── SampleSuperstore.csv
├── powerbi/
│   ├── README_POWERBI.md        # Power BI quick-start
│   ├── powerbi_queries.m        # Power Query (M) scripts
│   ├── dax_measures.dax         # All DAX measures
│   └── powerbi_setup_guide.md   # Full step-by-step guide
├── sql/
│   ├── schema.sql               # Database & table creation
│   ├── import_data.sql          # SQL LOAD DATA reference
│   └── queries.sql              # All analytical queries
├── notebooks/
│   └── eda.ipynb
├── reports/                     # Output folder for Excel exports
├── screenshot/
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.9+
- MySQL 8.0+

---

## Setup Instructions

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up MySQL database

Open your MySQL client (MySQL Workbench, command line, etc.) and run:

```sql
SOURCE sql/schema.sql;
```

This creates the `smart_retail` database and the `orders` table.

### 3. Configure database credentials

Open `dashboard/database.py` and update the `DB_CONFIG` dictionary:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',  # ← update this
    'database': 'smart_retail'
}
```

Also update the same credentials in `dashboard/import_csv.py`.

### 4. Import CSV data into MySQL

Run the import script from the **project root**:

```bash
python dashboard/import_csv.py
```

Expected output:
```
Reading CSV file...
Loaded 9994 rows from CSV.
Existing data cleared.
  Inserted rows 1–500/9994
  ...
✅ Import complete! 9994 rows inserted into smart_retail.orders
```

### 5. Run the dashboard

```bash
cd dashboard
python -m streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

**Login credentials:**
- Username: `admin`
- Password: `admin`

---

## MySQL Integration Details

| File | Purpose |
|------|---------|
| `dashboard/database.py` | Connection factory – `get_connection()` and `execute_query()` |
| `dashboard/import_csv.py` | Reads CSV, parses dates, inserts into MySQL in batches |
| `sql/schema.sql` | `CREATE DATABASE` + `CREATE TABLE orders` with indexes |
| `sql/import_data.sql` | SQL LOAD DATA reference (alternative manual method) |
| `sql/queries.sql` | All dashboard queries – KPIs, charts, RFM, heatmap |

The dashboard loads all data via `pd.read_sql()` into a DataFrame cached for 5 minutes.
If MySQL is unreachable, it automatically falls back to the CSV file so development is uninterrupted.

---

## Troubleshooting

**Can't connect to MySQL**
- Verify MySQL service is running: `net start MySQL80` (Windows)
- Check `host`, `user`, `password` in `database.py`
- Make sure the `smart_retail` database exists: `SHOW DATABASES;`

**Import script fails**
- Confirm MySQL credentials in `import_csv.py` match your setup
- Check that `sql/schema.sql` was run first to create the table

**Dashboard shows CSV fallback warning**
- This means MySQL is not reachable – check credentials and MySQL service status

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.36.0 | Dashboard UI |
| pandas | 2.2.2 | Data manipulation |
| numpy | 1.26.4 | Numerical operations |
| matplotlib | 3.9.0 | Charts |
| seaborn | 0.13.2 | Statistical charts |
| plotly | 5.22.0 | Interactive charts |
| openpyxl | 3.1.4 | Excel support |
| scikit-learn | 1.5.0 | ML forecast |
| mysql-connector-python | 8.4.0 | MySQL connectivity |

---

## Power BI Integration

The `powerbi/` folder contains everything needed to replicate and extend the
Streamlit dashboard in Power BI Desktop.

### Files

| File | Purpose |
|------|---------|
| `powerbi/powerbi_queries.m` | Power Query (M) scripts — one per dataset |
| `powerbi/dax_measures.dax` | All DAX measures (KPIs, time intelligence, RFM) |
| `powerbi/powerbi_setup_guide.md` | Full step-by-step connection guide |
| `dashboard/export_for_powerbi.py` | Exports all datasets to a multi-sheet Excel file |

### Option A — Direct MySQL Connection (recommended)

1. Install [MySQL ODBC Connector 8.x](https://dev.mysql.com/downloads/connector/odbc/)
2. Open Power BI Desktop → **Get Data → MySQL database**
3. Server: `localhost`  |  Database: `smart_retail`
4. Load the M queries from `powerbi/powerbi_queries.m`
5. Add DAX measures from `powerbi/dax_measures.dax`

### Option B — Excel Export (no ODBC needed)

```bash
python dashboard/export_for_powerbi.py
```

Opens `reports/smart_retail_powerbi.xlsx` with 7 pre-built sheets:
Orders, Sales by Category, Sales by Region, Monthly Trend,
Sub-Category Sales, Heatmap Data, RFM Analysis.

Then in Power BI: **Get Data → Excel Workbook → select all sheets → Load**

See `powerbi/powerbi_setup_guide.md` for the complete walkthrough.

### Recommended Report Pages

| Page | Key Visuals |
|------|------------|
| Executive Summary | 4 KPI cards, bar + donut charts, slicers |
| Sales Trends | Line chart, area chart, sub-category bar |
| Profitability | Scatter plot, matrix heatmap, margin KPI |
| Customer Segmentation | RFM table, donut chart, segment KPIs |
| Geo Map | Filled map by State, top cities bar chart |
