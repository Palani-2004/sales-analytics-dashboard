import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

from dotenv import load_dotenv
import os

load_dotenv()

# -----------------------------
# 1. Connect to MySQL
# -----------------------------
connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT")),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)


# -----------------------------
# 2. SQL query
# -----------------------------
query = """
SELECT
    DATE_FORMAT(order_date, '%Y-%m-01') AS sales_month,
    SUM(sales) AS monthly_sales
FROM sales_raw
GROUP BY
    DATE_FORMAT(order_date, '%Y-%m-01')
ORDER BY
    sales_month;
"""


# -----------------------------
# 3. Load data into Pandas
# -----------------------------
df = pd.read_sql(query, connection)


# -----------------------------
# 4. Close connection
# -----------------------------
connection.close()


# -----------------------------
# 5. Convert date column
# -----------------------------
df["sales_month"] = pd.to_datetime(df["sales_month"])

df["monthly_sales"] = df["monthly_sales"].round(2)


# -----------------------------
# 6. Display dataset
# -----------------------------
print("\nMonthly Sales Dataset:")
print(df.to_string(index=False))

print("\nDataset Information:")
print(df.info())

print("\nNumber of months:", len(df))


import matplotlib.pyplot as plt


# -----------------------------
# 7. Basic statistics
# -----------------------------
print("\nBasic Statistics:")
print(df["monthly_sales"].describe())


# -----------------------------
# 8. Plot monthly sales trend
# -----------------------------
plt.figure(figsize=(12, 6))

plt.plot(
    df["sales_month"],
    df["monthly_sales"],
    marker="o"
)

plt.title("Monthly Sales Trend")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()

# -----------------------------
# 9. Analyze monthly seasonality
# -----------------------------
df["month_number"] = df["sales_month"].dt.month
df["month_name"] = df["sales_month"].dt.month_name()

seasonality = (
    df.groupby(["month_number", "month_name"])["monthly_sales"]
    .mean()
    .reset_index()
    .sort_values("month_number")
)

print("\nAverage Sales by Calendar Month:")
print(seasonality.to_string(index=False))

# -----------------------------
# 10. Year-wise sales
# -----------------------------
df["year"] = df["sales_month"].dt.year

yearly_sales = (
    df.groupby("year")["monthly_sales"]
    .sum()
    .reset_index()
)

print("\nYearly Sales:")
print(yearly_sales.to_string(index=False))

# -----------------------------
# 11. Seasonal Naive Baseline
# -----------------------------

# Use the first 12 months as training
# and the final 12 months as test data

train = df.iloc[:12].copy()
test = df.iloc[12:].copy()

# Seasonal naive prediction:
# each 2025 month is predicted using the corresponding 2024 month
test["naive_prediction"] = train["monthly_sales"].values

print("\nSeasonal Naive Baseline:")
print(
    test[
        ["sales_month", "monthly_sales", "naive_prediction"]
    ].to_string(index=False)
)

# -----------------------------
# 12. Evaluate Seasonal Naive
# -----------------------------

from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

mae = mean_absolute_error(
    test["monthly_sales"],
    test["naive_prediction"]
)

rmse = np.sqrt(
    mean_squared_error(
        test["monthly_sales"],
        test["naive_prediction"]
    )
)

mape = np.mean(
    np.abs(
        (test["monthly_sales"] - test["naive_prediction"])
        / test["monthly_sales"]
    )
) * 100

print("\nSeasonal Naive Baseline Performance:")
print(f"MAE  : {mae:,.2f}")
print(f"RMSE : {rmse:,.2f}")
print(f"MAPE : {mape:.2f}%")

# -----------------------------
# 13. Improved Validation Split
# -----------------------------

# 18 months for training
# 6 months for testing

train_arima = df.iloc[:18].copy()
test_arima = df.iloc[18:].copy()

print("\nARIMA Validation Split:")
print("Training period:",
      train_arima["sales_month"].min().date(),
      "to",
      train_arima["sales_month"].max().date())

print("Testing period:",
      test_arima["sales_month"].min().date(),
      "to",
      test_arima["sales_month"].max().date())

print("Training observations:", len(train_arima))
print("Testing observations:", len(test_arima))

# -----------------------------
# 14. Simple ARIMA Models
# -----------------------------

from statsmodels.tsa.arima.model import ARIMA

arima_train = (
    train_arima
    .set_index("sales_month")["monthly_sales"]
    .asfreq("MS")
)


# -----------------------------
# ARIMA(0,1,0)
# -----------------------------

model_010 = ARIMA(
    arima_train,
    order=(0, 1, 0)
)

result_010 = model_010.fit()

forecast_010 = result_010.forecast(
    steps=len(test_arima)
)

test_arima["arima_010"] = forecast_010.values


print("\nARIMA(0,1,0) Predictions:")
print(
    test_arima[
        ["sales_month", "monthly_sales", "arima_010"]
    ].to_string(index=False)
)


# -----------------------------
# ARIMA(1,1,0)
# -----------------------------

model_110 = ARIMA(
    arima_train,
    order=(1, 1, 0)
)

result_110 = model_110.fit()

forecast_110 = result_110.forecast(
    steps=len(test_arima)
)

test_arima["arima_110"] = forecast_110.values


print("\nARIMA(1,1,0) Predictions:")
print(
    test_arima[
        ["sales_month", "monthly_sales", "arima_110"]
    ].to_string(index=False)
)


# -----------------------------
# ARIMA(0,1,1)
# -----------------------------

model_011 = ARIMA(
    arima_train,
    order=(0, 1, 1)
)

result_011 = model_011.fit()

forecast_011 = result_011.forecast(
    steps=len(test_arima)
)

test_arima["arima_011"] = forecast_011.values


print("\nARIMA(0,1,1) Predictions:")
print(
    test_arima[
        ["sales_month", "monthly_sales", "arima_011"]
    ].to_string(index=False)
)

# -----------------------------
# 15. Evaluate ARIMA Models
# -----------------------------

from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np


def evaluate_model(actual, predicted):
    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    mape = np.mean(
        np.abs(
            (actual - predicted) / actual
        )
    ) * 100

    return mae, rmse, mape


# ARIMA(0,1,0)
mae_010, rmse_010, mape_010 = evaluate_model(
    test_arima["monthly_sales"],
    test_arima["arima_010"]
)


# ARIMA(1,1,0)
mae_110, rmse_110, mape_110 = evaluate_model(
    test_arima["monthly_sales"],
    test_arima["arima_110"]
)


# ARIMA(0,1,1)
mae_011, rmse_011, mape_011 = evaluate_model(
    test_arima["monthly_sales"],
    test_arima["arima_011"]
)


print("\nARIMA Model Performance:")

print(
    f"ARIMA(0,1,0) → "
    f"MAE: {mae_010:,.2f} | "
    f"RMSE: {rmse_010:,.2f} | "
    f"MAPE: {mape_010:.2f}%"
)

print(
    f"ARIMA(1,1,0) → "
    f"MAE: {mae_110:,.2f} | "
    f"RMSE: {rmse_110:,.2f} | "
    f"MAPE: {mape_110:.2f}%"
)

print(
    f"ARIMA(0,1,1) → "
    f"MAE: {mae_011:,.2f} | "
    f"RMSE: {rmse_011:,.2f} | "
    f"MAPE: {mape_011:.2f}%"
)

# -----------------------------
# 16. Final Seasonal Naive Forecast
# -----------------------------

# Use all 24 months of historical data
historical = df.copy()

# Forecast next 6 months
forecast_dates = pd.date_range(
    start=historical["sales_month"].max() + pd.offsets.MonthBegin(1),
    periods=6,
    freq="MS"
)

# Seasonal Naive:
# Each future month uses the same month
# from the previous year.
last_12_months = historical["monthly_sales"].iloc[-12:].values

final_forecast = pd.DataFrame({
    "sales_month": forecast_dates,
    "forecast_sales": last_12_months[:6]
})

print("\nFinal 6-Month Sales Forecast:")
print(
    final_forecast.to_string(index=False)
)

# Save forecast for Power BI
final_forecast.to_csv(
    "data/processed/sales_forecast.csv",
    index=False
)

print("\nSaved: data/processed/sales_forecast.csv")

df.to_csv(
    "data/processed/monthly_sales.csv",
    index=False
)

print("\nSaved: data/processed/monthly_sales.csv")