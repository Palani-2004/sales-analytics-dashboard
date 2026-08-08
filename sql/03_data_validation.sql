USE sales_analytics_db;

-- Total records
SELECT COUNT(*) AS total_records
FROM sales_raw;

-- Date range and overall performance
SELECT
    MIN(order_date) AS first_order,
    MAX(order_date) AS last_order,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    SUM(quantity) AS total_quantity
FROM sales_raw;

-- Category performance
SELECT
    category,
    COUNT(*) AS order_count,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit
FROM sales_raw
GROUP BY category
ORDER BY total_sales DESC;