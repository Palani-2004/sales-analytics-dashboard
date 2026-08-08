CREATE TABLE sales_raw (
    order_id VARCHAR(20),
    order_date DATE,
    ship_date DATE,
    ship_mode VARCHAR(50),

    customer_id VARCHAR(20),
    customer_name VARCHAR(100),
    segment VARCHAR(50),

    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code INT,
    region VARCHAR(50),

    product_id VARCHAR(20),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    product_name VARCHAR(255),

    sales DECIMAL(12,2),
    quantity INT,
    discount DECIMAL(5,2),
    profit DECIMAL(12,2),

    order_year INT,
    order_month VARCHAR(20),
    quarter INT,
    delivery_days INT,
    profit_margin DECIMAL(8,2)
);