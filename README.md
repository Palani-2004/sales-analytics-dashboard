# Sales Analytics & Forecasting Dashboard

An end-to-end sales analytics and forecasting project built using **MySQL, Python, and Power BI**.

The project transforms raw sales transaction data into business insights, interactive dashboards, and a six-month sales forecast.

---

## Project Overview

This project analyzes historical sales data to answer key business questions such as:

- How are sales and profit performing overall?
- Which categories generate the most sales and profit?
- Which regions and customer segments perform best?
- Which products and customers contribute the most revenue?
- Which products generate losses?
- How does sales performance change over time?
- What can historical sales patterns tell us about future sales?

The project combines **SQL analytics, Power BI visualization, and Python-based time-series forecasting** into a single workflow.

---

## Project Architecture

```text
Raw Sales Data
      │
      ▼
    MySQL
      │
      ▼
  sales_raw
      │
      ├───────────────► SQL Business Analysis
      │
      ▼
   Power BI
      │
      ├── KPI Dashboard
      ├── Category Analysis
      ├── Regional Analysis
      ├── Product Analysis
      └── Customer Analysis
      │
      ▼
    Python
      │
      ├── Monthly Aggregation
      ├── Exploratory Analysis
      ├── Seasonal Naive Baseline
      ├── ARIMA Experiments
      └── Final Forecast
      │
      ▼
Jan–Jun 2026 Sales Forecast
      │
      ▼
   Power BI