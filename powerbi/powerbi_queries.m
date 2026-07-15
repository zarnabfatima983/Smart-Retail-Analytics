// ================================================================
//  Smart Retail Analytics — Power Query (M) Scripts
//
//  How to use in Power BI Desktop:
//    1. Home → Transform Data → New Query → Blank Query
//    2. Home → Advanced Editor
//    3. Replace all content with one query block below
//    4. Click Done, then rename the query to match the header
//    5. Repeat for each additional query
//
//  Connection: MySQL  |  Server: localhost  |  DB: smart_retail
// ================================================================


// ----------------------------------------------------------------
//  Query 1 — Orders  (full fact table)
// ----------------------------------------------------------------
let
    Source = MySQL.Database("localhost", "smart_retail"),
    Raw    = Source{[Schema = "smart_retail", Item = "orders"]}[Data],

    Renamed = Table.RenameColumns(Raw, {
        {"row_id",        "Row ID"},
        {"order_id",      "Order ID"},
        {"order_date",    "Order Date"},
        {"ship_date",     "Ship Date"},
        {"ship_mode",     "Ship Mode"},
        {"customer_id",   "Customer ID"},
        {"customer_name", "Customer Name"},
        {"segment",       "Segment"},
        {"country",       "Country"},
        {"city",          "City"},
        {"state",         "State"},
        {"postal_code",   "Postal Code"},
        {"region",        "Region"},
        {"product_id",    "Product ID"},
        {"category",      "Category"},
        {"sub_category",  "Sub-Category"},
        {"product_name",  "Product Name"},
        {"sales",         "Sales"},
        {"quantity",      "Quantity"},
        {"discount",      "Discount"},
        {"profit",        "Profit"}
    }),

    Typed = Table.TransformColumnTypes(Renamed, {
        {"Row ID",     Int64.Type},
        {"Order Date", type date},
        {"Ship Date",  type date},
        {"Sales",      type number},
        {"Quantity",   Int64.Type},
        {"Discount",   type number},
        {"Profit",     type number}
    }),

    WithMonth = Table.AddColumn(Typed, "Month Number",
        each Date.Month([Order Date]), Int64.Type),

    WithMonthName = Table.AddColumn(WithMonth, "Month Name",
        each Date.ToText([Order Date], "MMM"), type text),

    WithYear = Table.AddColumn(WithMonthName, "Year",
        each Date.Year([Order Date]), Int64.Type),

    WithMargin = Table.AddColumn(WithYear, "Profit Margin %",
        each if [Sales] = 0 then 0 else ([Profit] / [Sales]) * 100,
        type number)
in
    WithMargin


// ----------------------------------------------------------------
//  Query 2 — Sales by Category
// ----------------------------------------------------------------
let
    Source = MySQL.Database("localhost", "smart_retail"),
    Raw    = Source{[Schema = "smart_retail", Item = "orders"]}[Data],

    Grouped = Table.Group(Raw, {"category"}, {
        {"Total Sales", each List.Sum([sales]), type number}
    }),

    Sorted  = Table.Sort(Grouped, {{"Total Sales", Order.Descending}}),
    Renamed = Table.RenameColumns(Sorted, {{"category", "Category"}})
in
    Renamed


// ----------------------------------------------------------------
//  Query 3 — Sales by Region
// ----------------------------------------------------------------
let
    Source = MySQL.Database("localhost", "smart_retail"),
    Raw    = Source{[Schema = "smart_retail", Item = "orders"]}[Data],

    Grouped = Table.Group(Raw, {"region"}, {
        {"Total Sales", each List.Sum([sales]), type number}
    }),

    Sorted  = Table.Sort(Grouped, {{"Total Sales", Order.Descending}}),
    Renamed = Table.RenameColumns(Sorted, {{"region", "Region"}})
in
    Renamed


// ----------------------------------------------------------------
//  Query 4 — Monthly Sales Trend
// ----------------------------------------------------------------
let
    Source = MySQL.Database("localhost", "smart_retail"),
    Raw    = Source{[Schema = "smart_retail", Item = "orders"]}[Data],

    WithMonth = Table.AddColumn(Raw, "Month Number",
        each Date.Month([order_date]), Int64.Type),

    Grouped = Table.Group(WithMonth, {"Month Number"}, {
        {"Total Sales", each List.Sum([sales]), type number}
    }),

    Sorted = Table.Sort(Grouped, {{"Month Number", Order.Ascending}})
in
    Sorted


// ----------------------------------------------------------------
//  Query 5 — Sub-Category Sales
// ----------------------------------------------------------------
let
    Source = MySQL.Database("localhost", "smart_retail"),
    Raw    = Source{[Schema = "smart_retail", Item = "orders"]}[Data],

    Grouped = Table.Group(Raw, {"sub_category", "category"}, {
        {"Total Sales",  each List.Sum([sales]),  type number},
        {"Total Profit", each List.Sum([profit]), type number}
    }),

    Sorted  = Table.Sort(Grouped, {{"Total Sales", Order.Descending}}),
    Renamed = Table.RenameColumns(Sorted, {
        {"sub_category", "Sub-Category"},
        {"category",     "Category"}
    })
in
    Renamed


// ----------------------------------------------------------------
//  Query 6 — RFM Analysis
// ----------------------------------------------------------------
let
    Source   = MySQL.Database("localhost", "smart_retail"),
    Raw      = Source{[Schema = "smart_retail", Item = "orders"]}[Data],
    Snapshot = Date.AddDays(List.Max(Raw[order_date]), 1),

    Grouped = Table.Group(Raw, {"customer_id", "customer_name"}, {
        {"Last Order Date", each List.Max([order_date]),   type date},
        {"Frequency",       each List.Count([order_id]),   Int64.Type},
        {"Monetary",        each List.Sum([sales]),        type number}
    }),

    WithRecency = Table.AddColumn(Grouped, "Recency",
        each Duration.Days(Snapshot - [Last Order Date]), Int64.Type),

    WithR = Table.AddColumn(WithRecency, "R Score",
        each if [Recency] <= 30  then 4
             else if [Recency] <= 90  then 3
             else if [Recency] <= 180 then 2
             else 1, Int64.Type),

    WithF = Table.AddColumn(WithR, "F Score",
        each if [Frequency] >= 10 then 4
             else if [Frequency] >= 5  then 3
             else if [Frequency] >= 2  then 2
             else 1, Int64.Type),

    WithM = Table.AddColumn(WithF, "M Score",
        each if [Monetary] >= 5000 then 4
             else if [Monetary] >= 1000 then 3
             else if [Monetary] >= 500  then 2
             else 1, Int64.Type),

    WithScore = Table.AddColumn(WithM, "RFM Score",
        each [R Score] + [F Score] + [M Score], Int64.Type),

    WithSegment = Table.AddColumn(WithScore, "Customer Segment",
        each if [RFM Score] >= 10 then "Champions"
             else if [RFM Score] >= 7  then "Loyal Customers"
             else if [RFM Score] >= 5  then "At Risk"
             else "Lost", type text),

    Renamed = Table.RenameColumns(WithSegment, {
        {"customer_id",   "Customer ID"},
        {"customer_name", "Customer Name"}
    }),

    Sorted = Table.Sort(Renamed, {{"Monetary", Order.Descending}})
in
    Sorted


// ----------------------------------------------------------------
//  Query 7 — Heatmap Data  (Category × Region)
// ----------------------------------------------------------------
let
    Source = MySQL.Database("localhost", "smart_retail"),
    Raw    = Source{[Schema = "smart_retail", Item = "orders"]}[Data],

    Grouped = Table.Group(Raw, {"category", "region"}, {
        {"Total Sales", each List.Sum([sales]), type number}
    }),

    Renamed = Table.RenameColumns(Grouped, {
        {"category", "Category"},
        {"region",   "Region"}
    })
in
    Renamed
