-- Import data into smart_retail.orders
-- Recommended: python dashboard/import_csv.py
--
-- Alternative (requires FILE privilege) — update path before running:
/*
LOAD DATA INFILE 'C:/path/to/SampleSuperstore.csv'
INTO TABLE orders
CHARACTER SET latin1
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    row_id, order_id, @order_date, @ship_date, ship_mode,
    customer_id, customer_name, segment, country, city,
    state, postal_code, region, product_id, category,
    sub_category, product_name, sales, quantity, discount, profit
)
SET
    order_date = STR_TO_DATE(@order_date, '%m/%d/%Y'),
    ship_date  = STR_TO_DATE(@ship_date,  '%m/%d/%Y');
*/

USE smart_retail;
SELECT COUNT(*) AS total_rows FROM orders;
