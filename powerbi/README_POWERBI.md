# Power BI Integration — Smart Retail Analytics

This folder contains all assets required to connect Power BI Desktop
to the Smart Retail Analytics MySQL database and build an interactive report.

---

## Folder Contents

| File | Purpose |
|------|---------|
| `README_POWERBI.md` | This quick-start guide |
| `powerbi_queries.m` | Power Query (M) scripts — one per analytical dataset |
| `dax_measures.dax` | DAX measures covering KPIs, time intelligence, and RFM |
| `powerbi_setup_guide.md` | Complete step-by-step connection and report-building guide |

A Python export script is available at `dashboard/export_for_powerbi.py`.
Use it to generate an Excel workbook when a direct MySQL connection is not available.

---

## Connection Options

### Option A — Direct MySQL Connection (recommended)

1. Install the [MySQL ODBC Connector 8.x](https://dev.mysql.com/downloads/connector/odbc/)
2. Open Power BI Desktop → **Home → Get Data → MySQL database**
3. Server: `localhost` | Database: `smart_retail`
4. Load queries from `powerbi_queries.m`
5. Add DAX measures from `dax_measures.dax`

### Option B — Excel Export (no ODBC driver required)

```bash
python dashboard/export_for_powerbi.py
```

Then in Power BI Desktop:
**Home → Get Data → Excel Workbook → select `reports/smart_retail_powerbi.xlsx` → Load all sheets**

---

For full step-by-step instructions, see [`powerbi_setup_guide.md`](powerbi_setup_guide.md).
