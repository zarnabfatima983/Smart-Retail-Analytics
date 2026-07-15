# Power BI Setup Guide — Smart Retail Analytics

Step-by-step instructions to connect Power BI Desktop to the Smart Retail
Analytics MySQL database and build a report that matches the Streamlit dashboard.

---

## Prerequisites

| Requirement | Link |
|-------------|------|
| Power BI Desktop (free) | https://powerbi.microsoft.com/downloads |
| MySQL ODBC Connector 8.x | https://dev.mysql.com/downloads/connector/odbc/ |
| `smart_retail` database populated | See main `README.md` |

---

## Option A — Direct MySQL Connection

### 1. Install the MySQL ODBC Connector

1. Download **MySQL Connector/ODBC 8.x** (64-bit, Windows)
2. Run the installer and complete the setup
3. Restart Power BI Desktop if it was open during installation

### 2. Connect Power BI to MySQL

1. Open Power BI Desktop
2. Click **Home → Get Data → More...**
3. Search **MySQL** → select **MySQL database** → click **Connect**
4. Enter connection details:
   - **Server:** `localhost`
   - **Database:** `smart_retail`
5. Click **OK**
6. Select **Database** authentication and enter your MySQL credentials
7. Click **Connect**

### 3. Import the Power Query Scripts

1. In the Navigator, select the `orders` table → click **Transform Data**
2. In Power Query Editor, click **Advanced Editor**
3. Replace all content with **Query 1** from `powerbi/powerbi_queries.m`
4. Click **Done → Close & Apply**
5. For each additional query (Sales by Category, RFM, etc.):
   - **Home → New Query → Blank Query**
   - Open Advanced Editor and paste the relevant M script block
   - Rename the query to match the comment header

### 4. Add DAX Measures

1. Select the **Orders** table in the Fields pane
2. Click **Home → New Measure**
3. Open `powerbi/dax_measures.dax` in any text editor
4. Copy and paste each measure block individually, pressing **Enter** to confirm

---

## Option B — Excel Export (no ODBC driver required)

### 1. Generate the Excel workbook

Run from the project root:

```bash
python dashboard/export_for_powerbi.py
```

Output: `reports/smart_retail_powerbi.xlsx`

| Sheet | Contents |
|-------|----------|
| `Orders` | Full fact table with derived Month, Year, Profit Margin % |
| `Sales_by_Category` | Total sales per product category |
| `Sales_by_Region` | Total sales per geographic region |
| `Monthly_Trend` | Monthly sales totals (month 1–12) |
| `SubCategory_Sales` | Sales and profit by sub-category |
| `Heatmap_Data` | Sales totals by Category × Region |
| `RFM_Analysis` | Customer RFM scores and segment labels |

### 2. Load into Power BI

1. Open Power BI Desktop
2. **Home → Get Data → Excel Workbook**
3. Select `reports/smart_retail_powerbi.xlsx`
4. In the Navigator, tick **all sheets** → click **Load**
5. Add DAX measures from `powerbi/dax_measures.dax` (see Step 4 above)

---

## Recommended Report Pages

| Page | Visuals |
|------|---------|
| **Executive Summary** | 4 KPI cards (Sales, Profit, Orders, Products), bar chart by Category, donut by Region, slicers |
| **Sales Trends** | Line chart monthly trend, bar chart sub-category, area chart Sales YTD |
| **Profitability** | Clustered bar by Category, scatter Sales vs Profit, matrix heatmap, Profit Margin % card |
| **Customer Segmentation** | RFM table top 20, donut segment distribution, bar Avg Monetary by Segment, segment KPI cards |
| **Geo Map** | Filled map by State, top-15 cities bar chart |

---

## Syncing Slicers Across Pages

1. Add **Category**, **Region**, and **Segment** slicers on each page
2. Open **View → Sync Slicers**
3. Enable sync for all three slicers across all pages

This replicates the sidebar filter behaviour from the Streamlit dashboard.

---

## Refreshing Data

| Source | How to refresh |
|--------|---------------|
| MySQL (direct) | **Home → Refresh** in Power BI Desktop |
| Excel export | Re-run `python dashboard/export_for_powerbi.py`, then click **Refresh** |

---

## Publishing to Power BI Service (optional)

1. Sign in with a Power BI Pro or Premium Per User licence
2. **Home → Publish → Select workspace**
3. For scheduled refresh from MySQL, install a [Data Gateway](https://powerbi.microsoft.com/gateway):
   - Add `smart_retail` as a MySQL data source in Gateway settings
   - Configure a refresh schedule under **Dataset → Settings** in Power BI Service
