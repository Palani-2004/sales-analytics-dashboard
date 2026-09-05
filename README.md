# Enterprise Sales Analytics & Forecasting Platform

An end-to-end business intelligence and sales forecasting application built using **MySQL, Python, Pandas, Streamlit, and Plotly**.

The platform transforms transactional sales data into interactive performance analytics, profitability insights, customer and regional analysis, and a six-month company-wide sales forecast.

> **Dataset note:** The project uses synthetic transactional sales data designed to simulate a realistic business sales environment.

---

## Project Overview

The platform analyzes historical sales transactions across multiple business dimensions to answer questions such as:

- How are sales, profit, and margins performing?
- Which categories generate the highest sales and profit?
- Which regions perform strongest and weakest?
- Which products and customers contribute the most revenue?
- How does sales performance change month over month?
- How does the selected year compare with the previous year?
- Which areas represent business opportunities or risks?
- What does the historical sales pattern suggest about the next six months?

The project combines:

- Relational database design
- SQL business intelligence queries
- Python/Pandas data processing
- Interactive Streamlit dashboarding
- Plotly visualizations
- Time-series forecasting
- Model validation
- Data quality validation

---

## Key Features

### Executive Sales Analytics

Interactive KPIs for:

- Total Sales
- Total Profit
- Units Sold
- Profit Margin
- Latest Month Sales
- Total Orders
- Average Order Value
- Sales per Unit

### Interactive Filtering

Users can filter the dashboard by:

- Year
- Category
- Region

The selected filters dynamically update the relevant analytical sections.

### Sales Trend Analysis

- Monthly sales trend
- Historical performance
- Monthly year-over-year comparison
- Category and regional analysis

### Profitability Analysis

- Profit by category
- Profit margins
- Sales versus profit relationships
- Identification of weaker-performing business areas

### Product & Customer Analytics

- Top 10 products
- Top customers
- Product-level sales and profitability
- Customer contribution analysis

### Six-Month Sales Forecast

The platform generates a six-month company-wide sales forecast for:

**January 2026 – June 2026**

The forecast includes:

- Forecasted monthly sales
- Forecast versus recent actual performance
- Forecast variance analysis
- Forecast intelligence
- Forecast details
- Business interpretation

### Business Intelligence

The dashboard automatically surfaces:

- Strongest category
- Weakest category
- Strongest region
- Weakest region
- Profitability risks
- Growth opportunities
- Forecast outlook
- Business recommendations

---

## Technology Stack

| Layer | Technology |
|---|---|
| Database | MySQL |
| Data Processing | Python, Pandas, NumPy |
| Forecasting | Statsmodels, Scikit-learn |
| Dashboard | Streamlit |
| Visualization | Plotly |
| SQL Analytics | MySQL Views & Queries |
| Configuration | Python Dotenv |
| Environment | Python Virtual Environment |

---

## Project Architecture

```text
                 Raw Sales Data
                       |
                       v
              Data Cleaning / ETL
                       |
                       v
                    MySQL
                       |
                       v
                  sales_raw
                       |
          +------------+------------+
          |            |            |
          v            v            v
     SQL Views    Business SQL   Validation
          |
          v
   Python / Pandas
          |
    +-----+------+
    |            |
    v            v
Analytics     Forecasting
    |            |
    |       Model Evaluation
    |            |
    |            v
    |     Seasonal Naive
    |            |
    +-----+------+
          |
          v
   Streamlit Dashboard
          |
    +-----+----------------------+
    |                            |
    v                            v
Interactive BI            Forecast Intelligence
    |
    v
Business Recommendations