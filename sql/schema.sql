-- Create the smart_retail database and orders table.
-- Usage: mysql -u root -p < sql/schema.sql

CREATE DATABASE IF NOT EXISTS smart_retail
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE smart_retail;

DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    id            INT            AUTO_INCREMENT PRIMARY KEY,
    row_id        INT            NOT NULL,
    order_id      VARCHAR(50)    NOT NULL,
    order_date    DATE           NOT NULL,
    ship_date     DATE           NOT NULL,
    ship_mode     VARCHAR(50)    NOT NULL,
    customer_id   VARCHAR(50)    NOT NULL,
    customer_name VARCHAR(100)   NOT NULL,
    segment       VARCHAR(50)    NOT NULL,
    country       VARCHAR(100)   NOT NULL,
    city          VARCHAR(100)   NOT NULL,
    state         VARCHAR(100)   NOT NULL,
    postal_code   VARCHAR(20),
    region        VARCHAR(50)    NOT NULL,
    product_id    VARCHAR(50)    NOT NULL,
    category      VARCHAR(50)    NOT NULL,
    sub_category  VARCHAR(50)    NOT NULL,
    product_name  VARCHAR(255)   NOT NULL,
    sales         DECIMAL(10,4)  NOT NULL,
    quantity      INT            NOT NULL,
    discount      DECIMAL(5,4)   NOT NULL,
    profit        DECIMAL(10,4)  NOT NULL,

    INDEX idx_order_id    (order_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_category    (category),
    INDEX idx_region      (region),
    INDEX idx_segment     (segment),
    INDEX idx_order_date  (order_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
