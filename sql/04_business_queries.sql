USE sales_analytics_db;

-- ==========================================
-- 1. OVERALL BUSINESS KPIs
-- ==========================================

SELECT
    COUNT(*) AS total_records,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    SUM(quantity) AS total_quantity,
    ROUND(AVG(sales), 2) AS average_sales,
    ROUND(AVG(profit), 2) AS average_profit
FROM sales_raw;

SELECT
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(
        (SUM(profit) / NULLIF(SUM(sales), 0)) * 100,
        2
    ) AS profit_margin_percentage
FROM sales_raw;

SELECT
    category,
    COUNT(*) AS total_records,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity
FROM sales_raw
GROUP BY category
ORDER BY total_sales DESC;

SELECT
    category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(
        (SUM(profit) / NULLIF(SUM(sales), 0)) * 100,
        2
    ) AS profit_margin
FROM sales_raw
GROUP BY category
ORDER BY profit_margin DESC;

SELECT
    region,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity,
    ROUND(
        (SUM(profit) / NULLIF(SUM(sales), 0)) * 100,
        2
    ) AS profit_margin
FROM sales_raw
GROUP BY region
ORDER BY total_sales DESC;

SELECT
    product_name,
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity
FROM sales_raw
GROUP BY
    product_name,
    category,
    sub_category
ORDER BY total_sales DESC
LIMIT 10;

SELECT
    customer_id,
    customer_name,
    segment,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0) * 100,
        2
    ) AS profit_margin
FROM sales_raw
GROUP BY
    customer_id,
    customer_name,
    segment
ORDER BY total_profit DESC
LIMIT 10;

SELECT
    segment,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(*) AS total_records,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0) * 100,
        2
    ) AS profit_margin
FROM sales_raw
GROUP BY segment
ORDER BY total_sales DESC;

SELECT
    product_id,
    product_name,
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity
FROM sales_raw
GROUP BY
    product_id,
    product_name,
    category,
    sub_category
ORDER BY total_sales DESC
LIMIT 10;

SELECT
    product_id,
    product_name,
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM sales_raw
GROUP BY
    product_id,
    product_name,
    category,
    sub_category
ORDER BY total_profit DESC
LIMIT 10;

SELECT
    product_id,
    product_name,
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM sales_raw
GROUP BY
    product_id,
    product_name,
    category,
    sub_category
ORDER BY total_profit ASC
LIMIT 10;

SELECT
    product_id,
    product_name,
    category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0) * 100,
        2
    ) AS profit_margin
FROM sales_raw
GROUP BY
    product_id,
    product_name,
    category
HAVING SUM(sales) > 50000
   AND SUM(profit) < 5000
ORDER BY total_sales DESC;

-- ==========================================
-- 4.3 TIME-SERIES ANALYSIS
-- ==========================================

-- 1. Yearly Performance

SELECT
    order_year,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity,
    ROUND(
        SUM(profit) / NULLIF(SUM(sales), 0) * 100,
        2
    ) AS profit_margin
FROM sales_raw
GROUP BY order_year
ORDER BY order_year;

SELECT
    order_year,
    quarter,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM sales_raw
GROUP BY
    order_year,
    quarter
ORDER BY
    order_year,
    quarter;
    
    
SELECT
    order_year,
    MONTH(order_date) AS month_number,
    MONTHNAME(order_date) AS month_name,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM sales_raw
GROUP BY
    order_year,
    MONTH(order_date),
    MONTHNAME(order_date)
ORDER BY
    order_year,
    month_number;
    
    
WITH monthly_sales AS (
    SELECT
        DATE_FORMAT(order_date, '%Y-%m-01') AS sales_month,
        SUM(sales) AS total_sales
    FROM sales_raw
    GROUP BY DATE_FORMAT(order_date, '%Y-%m-01')
)

SELECT
    sales_month,
    ROUND(total_sales, 2) AS total_sales,
    ROUND(
        (
            total_sales -
            LAG(total_sales) OVER (ORDER BY sales_month)
        )
        /
        NULLIF(
            LAG(total_sales) OVER (ORDER BY sales_month),
            0
        ) * 100,
        2
    ) AS month_over_month_growth
FROM monthly_sales
ORDER BY sales_month;

SELECT
    MONTH(order_date) AS month_number,
    MONTHNAME(order_date) AS month_name,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM sales_raw
GROUP BY
    MONTH(order_date),
    MONTHNAME(order_date)
ORDER BY total_sales DESC;

SELECT
    quarter,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM sales_raw
GROUP BY quarter
ORDER BY total_sales DESC;


SELECT
    product_name,
    category,
    ROUND(SUM(sales), 2) AS total_sales,

    RANK() OVER (
        ORDER BY SUM(sales) DESC
    ) AS sales_rank

FROM sales_raw

GROUP BY
    product_name,
    category

ORDER BY sales_rank;


SELECT
    product_name,
    category,
    ROUND(SUM(sales), 2) AS total_sales,

    DENSE_RANK() OVER (
        ORDER BY SUM(sales) DESC
    ) AS sales_rank

FROM sales_raw

GROUP BY
    product_name,
    category

ORDER BY sales_rank;


SELECT
    product_name,
    category,
    ROUND(SUM(sales), 2) AS total_sales,

    ROW_NUMBER() OVER (
        ORDER BY SUM(sales) DESC
    ) AS rn

FROM sales_raw

GROUP BY
    product_name,
    category

ORDER BY rn;


WITH product_sales AS (

    SELECT
        product_id,
        product_name,
        category,
        SUM(sales) AS total_sales

    FROM sales_raw

    GROUP BY
        product_id,
        product_name,
        category
),

ranked_products AS (

    SELECT
        product_id,
        product_name,
        category,
        total_sales,

        ROW_NUMBER() OVER (
            PARTITION BY category
            ORDER BY total_sales DESC
        ) AS category_rank

    FROM product_sales
)

SELECT
    product_id,
    product_name,
    category,
    ROUND(total_sales, 2) AS total_sales,
    category_rank

FROM ranked_products

WHERE category_rank <= 3

ORDER BY
    category,
    category_rank;
    
WITH monthly_sales AS (
    SELECT
        DATE_FORMAT(order_date, '%Y-%m-01') AS sales_month,
        SUM(sales) AS total_sales
    FROM sales_raw
    GROUP BY DATE_FORMAT(order_date, '%Y-%m-01')
)
SELECT
    sales_month,
    ROUND(total_sales, 2) AS monthly_sales,
    ROUND(
        SUM(total_sales) OVER (
            ORDER BY sales_month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS cumulative_sales
FROM monthly_sales
ORDER BY sales_month;