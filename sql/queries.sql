USE smart_retail;

-- Full dataset
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
FROM orders;

-- KPI summary
SELECT
    SUM(sales)                   AS total_sales,
    SUM(profit)                  AS total_profit,
    COUNT(DISTINCT order_id)     AS total_orders,
    COUNT(DISTINCT product_name) AS total_products
FROM orders;

-- Sales by category
SELECT category AS `Category`, SUM(sales) AS `Sales`
FROM orders GROUP BY category ORDER BY `Sales` DESC;

-- Sales by region
SELECT region AS `Region`, SUM(sales) AS `Sales`
FROM orders GROUP BY region ORDER BY `Sales` DESC;

-- Monthly sales trend
SELECT MONTH(order_date) AS `Month`, SUM(sales) AS `Sales`
FROM orders GROUP BY MONTH(order_date) ORDER BY `Month`;

-- Sub-category sales (example filter)
SELECT sub_category AS `Sub-Category`, SUM(sales) AS `Sales`
FROM orders
WHERE category = 'Furniture' AND region = 'East' AND segment = 'Consumer'
GROUP BY sub_category ORDER BY `Sales` DESC;

-- Heatmap: category × region
SELECT category AS `Category`, region AS `Region`, SUM(sales) AS `Sales`
FROM orders GROUP BY category, region ORDER BY category, region;

-- RFM analysis
SELECT
    customer_id AS `Customer ID`,
    DATEDIFF((SELECT MAX(order_date) + INTERVAL 1 DAY FROM orders), MAX(order_date)) AS `Recency`,
    COUNT(DISTINCT order_id) AS `Frequency`,
    SUM(sales)               AS `Monetary`
FROM orders GROUP BY customer_id ORDER BY `Monetary` DESC;
