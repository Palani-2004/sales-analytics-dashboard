CREATE OR REPLACE VIEW vw_monthly_sales AS
SELECT
    DATE_FORMAT(order_date, '%Y-%m-01') AS sales_month,
    YEAR(order_date) AS order_year,
    MONTH(order_date) AS month_number,
    MONTHNAME(order_date) AS month_name,

    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity,

    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0) * 100,
        2
    ) AS profit_margin

FROM sales_raw

GROUP BY
    DATE_FORMAT(order_date, '%Y-%m-01'),
    YEAR(order_date),
    MONTH(order_date),
    MONTHNAME(order_date);
    
SELECT *
FROM vw_monthly_sales
ORDER BY sales_month;

CREATE OR REPLACE VIEW vw_category_performance AS
SELECT
    category,

    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity,

    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0) * 100,
        2
    ) AS profit_margin

FROM sales_raw

GROUP BY category;

SELECT *
FROM vw_category_performance
ORDER BY total_sales DESC;

CREATE OR REPLACE VIEW vw_region_performance AS
SELECT
    region,

    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity,

    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0) * 100,
        2
    ) AS profit_margin

FROM sales_raw

GROUP BY region;

SELECT *
FROM vw_region_performance
ORDER BY total_sales DESC;

CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    product_id,
    product_name,
    category,
    sub_category,

    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity,

    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0) * 100,
        2
    ) AS profit_margin

FROM sales_raw

GROUP BY
    product_id,
    product_name,
    category,
    sub_category;
    
SELECT *
FROM vw_product_performance
ORDER BY total_sales DESC
LIMIT 10;


CREATE OR REPLACE VIEW vw_customer_performance AS
SELECT
    customer_id,
    customer_name,
    segment,

    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity,

    COUNT(DISTINCT order_id) AS total_orders,

    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0) * 100,
        2
    ) AS profit_margin

FROM sales_raw

GROUP BY
    customer_id,
    customer_name,
    segment;
    
SELECT *
FROM vw_customer_performance
ORDER BY total_sales DESC
LIMIT 10;


SHOW FULL TABLES
WHERE Table_type = 'VIEW';