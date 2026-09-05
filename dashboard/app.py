import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM DASHBOARD STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* Main application background */
    .stApp {
        background-color: #f8fafc;
    }

    /* KPI cards */
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
    }

    /* Section spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid #e2e8f0;
    }

    /* Dataframes */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 2. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(override=True)


# ============================================================
# 3. DATABASE CONNECTION
# ============================================================

@st.cache_resource
def get_database_engine():

    host = os.getenv("MYSQL_HOST")
    port = os.getenv("MYSQL_PORT")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DATABASE")

    if not all([host, port, user, password, database]):
        raise ValueError(
            "Missing MySQL environment variables. "
            "Check your .env file."
        )

    connection_url = URL.create(
        drivername="mysql+mysqlconnector",
        username=user,
        password=password,
        host=host,
        port=int(port),
        database=database,
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True,
    )


# ============================================================
# 4. LOAD MYSQL VIEWS
# ============================================================

@st.cache_data(ttl=300)
def load_view(view_name):

    engine = get_database_engine()

    query = text(f"SELECT * FROM {view_name}")

    with engine.connect() as connection:
        return pd.read_sql(query, connection)

@st.cache_data(ttl=300)
def load_raw_sales():

    engine = get_database_engine()

    query = text("""
        SELECT
            order_id,
            order_date,
            customer_id,
            customer_name,
            segment,
            region,
            product_id,
            category,
            sub_category,
            product_name,
            sales,
            quantity,
            discount,
            profit
        FROM sales_raw
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    df["order_date"] = pd.to_datetime(df["order_date"])

    return df

# ============================================================
# 5. LOAD FORECAST
# ============================================================

@st.cache_data(ttl=300)
def load_forecast():

    forecast_path = "data/processed/sales_forecast.csv"

    if not os.path.exists(forecast_path):
        return pd.DataFrame()

    df = pd.read_csv(forecast_path)

    df["sales_month"] = pd.to_datetime(
        df["sales_month"]
    )

    return df


# ============================================================
# 6. LOAD PROJECT DATA
# ============================================================

try:

    monthly_sales = load_view(
        "vw_monthly_sales"
    )

    category_performance = load_view(
        "vw_category_performance"
    )

    region_performance = load_view(
        "vw_region_performance"
    )

    product_performance = load_view(
        "vw_product_performance"
    )

    customer_performance = load_view(
        "vw_customer_performance"
    )
    raw_sales = load_raw_sales()
    forecast = load_forecast()

except Exception as e:

    st.error(
        f"Unable to load dashboard data: {e}"
    )

    st.stop()


# ============================================================
# 7. DATA PREPARATION
# ============================================================

monthly_sales["sales_month"] = pd.to_datetime(
    monthly_sales["sales_month"]
)

monthly_sales = monthly_sales.sort_values(
    "sales_month"
)

if not forecast.empty:

    forecast["sales_month"] = pd.to_datetime(
        forecast["sales_month"]
    )

# ============================================================
# PLOTLY CHART CONFIGURATION
# ============================================================

def style_chart(fig, height=420):

    fig.update_layout(
        height=height,
        template="plotly_white",
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
        font=dict(
            size=13,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    fig.update_xaxes(
        showgrid=False,
    )

    fig.update_yaxes(
        gridcolor="lightgray",
    )

    return fig

# ============================================================
# 8. SIDEBAR
# ============================================================

st.sidebar.title("📊 Sales Analytics")

st.sidebar.markdown(
    """
    **Executive Sales Intelligence**

    Explore sales performance, profitability,
    customers, products, regions and forecasts.
    """
)

st.sidebar.caption(
    "Interactive Business Intelligence Dashboard"
)

st.sidebar.divider()

st.sidebar.caption(
    "Built with MySQL • Python • Streamlit • Plotly"
)

st.sidebar.subheader("Filters")


# -----------------------------
# Year Filter
# -----------------------------

available_years = sorted(
    raw_sales["order_date"]
    .dt.year
    .unique()
)

selected_years = st.sidebar.multiselect(
    "Year",
    options=available_years,
    default=available_years,
)


# -----------------------------
# Category Filter
# -----------------------------

available_categories = sorted(
    raw_sales["category"]
    .dropna()
    .unique()
)

selected_categories = st.sidebar.multiselect(
    "Category",
    options=available_categories,
    default=available_categories,
)


# -----------------------------
# Region Filter
# -----------------------------

available_regions = sorted(
    raw_sales["region"]
    .dropna()
    .unique()
)

selected_regions = st.sidebar.multiselect(
    "Region",
    options=available_regions,
    default=available_regions,
)


st.sidebar.divider()

st.sidebar.info(
    """
    **Data Source**

    MySQL

    **Forecast Model**

    Seasonal Naive
    """
)


# ============================================================
# 9. APPLY FILTERS TO TRANSACTION DATA
# ============================================================

filtered_raw = raw_sales[
    raw_sales["order_date"].dt.year.isin(selected_years)
    & raw_sales["category"].isin(selected_categories)
    & raw_sales["region"].isin(selected_regions)
].copy()

if filtered_raw.empty:

    st.warning(
        "No data matches the selected filters. "
        "Please select at least one Year, Category and Region."
    )

    st.stop()
# ============================================================
# CREATE FILTERED MONTHLY DATA
# ============================================================

filtered_raw["sales_month"] = (
    filtered_raw["order_date"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

filtered_monthly = (
    filtered_raw
    .groupby("sales_month", as_index=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
    )
)

filtered_monthly["profit_margin"] = (
    filtered_monthly["total_profit"]
    / filtered_monthly["total_sales"]
    * 100
)

filtered_monthly = filtered_monthly.sort_values(
    "sales_month"
)

# ============================================================
# CREATE FILTERED CATEGORY DATA
# ============================================================

filtered_category = (
    filtered_raw
    .groupby("category", as_index=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
    )
)

filtered_category["profit_margin"] = (
    filtered_category["total_profit"]
    / filtered_category["total_sales"]
    * 100
)

# ============================================================
# CREATE FILTERED REGION DATA
# ============================================================

filtered_region = (
    filtered_raw
    .groupby("region", as_index=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
    )
)

filtered_region["profit_margin"] = (
    filtered_region["total_profit"]
    / filtered_region["total_sales"]
    * 100
)

filtered_product = (
    filtered_raw
    .groupby(
        [
            "product_id",
            "product_name",
            "category",
            "sub_category",
        ],
        as_index=False,
    )
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
    )
)

filtered_product["profit_margin"] = (
    filtered_product["total_profit"]
    / filtered_product["total_sales"]
    * 100
)

# ============================================================
# PORTFOLIO BENCHMARK DATA
# ============================================================
# Strategic benchmarking uses the selected YEAR only.
# Category and Region filters do NOT affect these rankings.

benchmark_raw = raw_sales[
    raw_sales["order_date"].dt.year.isin(selected_years)
].copy()


# -----------------------------
# Category Benchmark
# -----------------------------

benchmark_category = (
    benchmark_raw
    .groupby("category", as_index=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
    )
)

benchmark_category["profit_margin"] = (
    benchmark_category["total_profit"]
    / benchmark_category["total_sales"]
    * 100
)


# -----------------------------
# Region Benchmark
# -----------------------------

benchmark_region = (
    benchmark_raw
    .groupby("region", as_index=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
    )
)

benchmark_region["profit_margin"] = (
    benchmark_region["total_profit"]
    / benchmark_region["total_sales"]
    * 100
)


# -----------------------------
# Product Benchmark
# -----------------------------

benchmark_product = (
    benchmark_raw
    .groupby(
        [
            "product_id",
            "product_name",
            "category",
            "sub_category",
        ],
        as_index=False,
    )
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
    )
)

benchmark_product["profit_margin"] = (
    benchmark_product["total_profit"]
    / benchmark_product["total_sales"]
    * 100
)

# ============================================================
# CREATE FILTERED CUSTOMER DATA
# ============================================================

filtered_customer = (
    filtered_raw
    .groupby(
        [
            "customer_id",
            "customer_name",
            "segment",
        ],
        as_index=False,
    )
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
        total_orders=("order_id", "nunique"),
    )
)

filtered_customer["profit_margin"] = (
    filtered_customer["total_profit"]
    / filtered_customer["total_sales"]
    * 100
)

# ============================================================
# PORTFOLIO BENCHMARK DATA
# ============================================================
# Strategic benchmarking uses the selected YEAR only.
# Category and Region filters do NOT affect these rankings.

benchmark_raw = raw_sales[
    raw_sales["order_date"].dt.year.isin(selected_years)
].copy()


# -----------------------------
# Category Benchmark
# -----------------------------

benchmark_category = (
    benchmark_raw
    .groupby("category", as_index=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
    )
)

benchmark_category["profit_margin"] = (
    benchmark_category["total_profit"]
    / benchmark_category["total_sales"]
    * 100
)


# -----------------------------
# Region Benchmark
# -----------------------------

benchmark_region = (
    benchmark_raw
    .groupby("region", as_index=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
    )
)

benchmark_region["profit_margin"] = (
    benchmark_region["total_profit"]
    / benchmark_region["total_sales"]
    * 100
)


# -----------------------------
# Product Benchmark
# -----------------------------

benchmark_product = (
    benchmark_raw
    .groupby(
        [
            "product_id",
            "product_name",
            "category",
            "sub_category",
        ],
        as_index=False,
    )
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
    )
)

benchmark_product["profit_margin"] = (
    benchmark_product["total_profit"]
    / benchmark_product["total_sales"]
    * 100
)


# ============================================================
# FILTER SUMMARY
# ============================================================

filter_summary = []

if selected_years:
    filter_summary.append(
        f"Years: {', '.join(map(str, selected_years))}"
    )

if selected_categories:
    filter_summary.append(
        f"Categories: {len(selected_categories)} selected"
    )

if selected_regions:
    filter_summary.append(
        f"Regions: {len(selected_regions)} selected"
    )

if filter_summary:

    st.caption(
        " | ".join(filter_summary)
    )

# ============================================================
# 10. DASHBOARD HEADER
# ============================================================

st.title("📊 Sales Analytics Dashboard")

st.markdown(
    """
    ### Executive Overview

    Monitor sales performance, profitability,
    product performance, regional trends and
    future sales forecasts.
    """
)

st.divider()


# ============================================================
# 11. EXECUTIVE KPIs
# ============================================================

# ============================================================
# KPI CALCULATIONS
# ============================================================

total_sales = filtered_raw["sales"].sum()

total_profit = filtered_raw["profit"].sum()

total_quantity = filtered_raw["quantity"].sum()

total_orders = filtered_raw["order_id"].nunique()

overall_margin = (
    total_profit / total_sales * 100
    if total_sales != 0
    else 0
)

average_order_value = (
    total_sales / total_orders
    if total_orders != 0
    else 0
)

# ============================================================
# YEAR-OVER-YEAR KPI COMPARISON
# ============================================================

sales_delta = None
profit_delta = None
quantity_delta = None
margin_delta = None

if len(selected_years) == 1:

    current_year = selected_years[0]
    previous_year = current_year - 1

    current_year_data = raw_sales[
        (raw_sales["order_date"].dt.year == current_year)
        & raw_sales["category"].isin(selected_categories)
        & raw_sales["region"].isin(selected_regions)
    ]

    previous_year_data = raw_sales[
        (raw_sales["order_date"].dt.year == previous_year)
        & raw_sales["category"].isin(selected_categories)
        & raw_sales["region"].isin(selected_regions)
    ]

    if not previous_year_data.empty:

        previous_sales = previous_year_data["sales"].sum()
        previous_profit = previous_year_data["profit"].sum()
        previous_quantity = previous_year_data["quantity"].sum()

        previous_margin = (
            previous_profit / previous_sales * 100
            if previous_sales != 0
            else 0
        )

        # Sales YoY %
        if previous_sales != 0:
            sales_delta = (
                (total_sales - previous_sales)
                / previous_sales
            ) * 100

        # Profit YoY %
        if previous_profit != 0:
            profit_delta = (
                (total_profit - previous_profit)
                / abs(previous_profit)
            ) * 100

        # Units YoY %
        if previous_quantity != 0:
            quantity_delta = (
                (total_quantity - previous_quantity)
                / previous_quantity
            ) * 100

        # Margin = percentage-point change
        margin_delta = overall_margin - previous_margin


if not filtered_monthly.empty:

    latest_month = filtered_monthly[
        "sales_month"
    ].max()

    latest_month_sales = filtered_monthly.loc[
        filtered_monthly["sales_month"] == latest_month,
        "total_sales",
    ].iloc[0]

else:

    latest_month_sales = 0


# ============================================================
# KPI ROW
# ============================================================

if not filtered_monthly.empty:

    first_month = filtered_monthly["sales_month"].min()
    last_month = filtered_monthly["sales_month"].max()

    period_text = (
        f"{first_month.strftime('%b %Y')} - "
        f"{last_month.strftime('%b %Y')}"
    )

else:
    period_text = "No data"


# ============================================================
# KPI ROW WITH YOY COMPARISON
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)


# ------------------------------------------------------------
# SALES KPI
# ------------------------------------------------------------

col1.metric(
    "Total Sales",
    f"${total_sales / 1_000_000:.2f}M",
    delta=(
        f"{sales_delta:+.2f}% YoY"
        if sales_delta is not None
        else None
    ),
)


# ------------------------------------------------------------
# PROFIT KPI
# ------------------------------------------------------------

col2.metric(
    "Total Profit",
    f"${total_profit / 1_000_000:.2f}M",
    delta=(
        f"{profit_delta:+.2f}% YoY"
        if profit_delta is not None
        else None
    ),
)


# ------------------------------------------------------------
# UNITS KPI
# ------------------------------------------------------------

col3.metric(
    "Units Sold",
    f"{total_quantity / 1_000:.1f}K",
    delta=(
        f"{quantity_delta:+.2f}% YoY"
        if quantity_delta is not None
        else None
    ),
)


# ------------------------------------------------------------
# MARGIN KPI
# ------------------------------------------------------------

col4.metric(
    "Profit Margin",
    f"{overall_margin:.2f}%",
    delta=(
        f"{margin_delta:+.2f} pp YoY"
        if margin_delta is not None
        else None
    ),
)

# ============================================================
# SECONDARY KPI ROW
# ============================================================

st.markdown("")

secondary_col1, secondary_col2, secondary_col3 = st.columns(3)


secondary_col1.metric(
    "Total Orders",
    f"{total_orders:,}",
)


secondary_col2.metric(
    "Average Order Value",
    f"${average_order_value:,.0f}",
)


secondary_col3.metric(
    "Sales per Unit",
    (
        f"${total_sales / total_quantity:,.2f}"
        if total_quantity != 0
        else "$0.00"
    ),
)

# ------------------------------------------------------------
# LATEST MONTH SALES
# ------------------------------------------------------------

col5.metric(
    "Latest Month Sales",
    f"${latest_month_sales / 1_000_000:.2f}M",
    help=f"Sales recorded in {latest_month.strftime('%B %Y')}.",
)


st.caption(
    f"Analysis period: **{period_text}**"
)

st.caption(
    "KPI values reflect the current dashboard filters."
)


# ============================================================
# 12. MONTHLY SALES TREND
# ============================================================

st.subheader("📈 Monthly Sales Trend")

if filtered_monthly.empty:

    st.warning(
        "No monthly sales data available for the selected filters."
    )

else:

    fig = px.line(
        filtered_monthly,
        x="sales_month",
        y="total_sales",
        markers=True,
        title="Monthly Sales Trend",
    )
    fig.update_yaxes(
        tickprefix="$",
        tickformat=",.0f",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x|%b %Y}</b><br>"
            "Sales: $%{y:,.0f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Sales",
    hovermode="x unified",
    )

    fig = style_chart(fig, height=450)

    st.plotly_chart(
        fig,
        width="stretch",
    )

# ============================================================
# MONTHLY YEAR-OVER-YEAR COMPARISON
# ============================================================

st.subheader("📈 Monthly YoY Sales Comparison")

st.markdown(
    """
    Compare monthly sales performance against the previous year
    to identify specific periods of growth or decline.
    """
)

# ------------------------------------------------------------
# Determine comparison years
# ------------------------------------------------------------

available_years = sorted(
    raw_sales["order_date"].dt.year.dropna().unique()
)

if len(available_years) >= 2:

    

    if len(selected_years) == 1:

        comparison_year = int(selected_years[0])

        previous_years = [
            year
            for year in available_years
            if year < comparison_year
        ]

        if previous_years:
            previous_year = max(previous_years)
        else:
            previous_year = None

    else:

        # When All years are selected, compare the
        # latest two available years.
        previous_year = int(available_years[-2])
        comparison_year = int(available_years[-1])

    if previous_year is not None:

        # ----------------------------------------------------
        # Apply Category and Region filters only
        # ----------------------------------------------------

        yoy_base = raw_sales.copy()

        if selected_categories:
            yoy_base = yoy_base[
                yoy_base["category"].isin(
                    selected_categories
                )
            ]

        if selected_regions:
            yoy_base = yoy_base[
                yoy_base["region"].isin(
                    selected_regions
                )
            ]

        # ----------------------------------------------------
        # Filter comparison years
        # ----------------------------------------------------

        yoy_base = yoy_base[
            yoy_base["order_date"].dt.year.isin(
                [
                    previous_year,
                    comparison_year,
               ]
            )
        ].copy()

        # ----------------------------------------------------
        # Aggregate monthly sales
        # ----------------------------------------------------

        yoy_base["order_year"] = (  
            yoy_base["order_date"].dt.year
        )

        yoy_base["month_number"] = (
            yoy_base["order_date"].dt.month
        )

        yoy_monthly = (
            yoy_base
            .groupby(
                [
                    "month_number",
                    "order_year",
                ],
                as_index=False
            )["sales"]
            .sum()
        )

        yoy_monthly = (
            yoy_base
            .groupby(
                [
                    "month_number",
                    "order_year",
                ],
                as_index=False
            )["sales"]
            .sum()
        )

        yoy_pivot = (
            yoy_monthly
            .pivot(
                index="month_number",
                columns="order_year",
                values="sales",
            )
            .reset_index()
        )

        # ----------------------------------------------------
        # Make sure both years exist as columns
        # ----------------------------------------------------

        if previous_year not in yoy_pivot.columns:
            yoy_pivot[previous_year] = 0

        if comparison_year not in yoy_pivot.columns:
            yoy_pivot[comparison_year] = 0

        yoy_pivot = yoy_pivot[
            [
                "month_number",
                previous_year,
                comparison_year,
            ]
        ]

        # ----------------------------------------------------
        # Calculate YoY %
        # ----------------------------------------------------

        yoy_pivot["yoy_pct"] = (
            (
                yoy_pivot[comparison_year]
                - yoy_pivot[previous_year]
            )
            / yoy_pivot[previous_year]
            * 100
        ).where(
            yoy_pivot[previous_year] != 0
        )

        # ----------------------------------------------------
        # Month names
        # ----------------------------------------------------

        month_names = {
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec",
        }

        yoy_pivot["Month"] = (
            yoy_pivot["month_number"]
            .map(month_names)
        )

        # ----------------------------------------------------
        # Rename columns
        # ----------------------------------------------------

        yoy_display = yoy_pivot[
            [
                "Month",
                previous_year,
                comparison_year,
                "yoy_pct",
            ]
        ].copy()

        yoy_display = yoy_display.rename(
            columns={
                previous_year:
                    f"{previous_year} Sales",

                comparison_year:
                    f"{comparison_year} Sales",

                "yoy_pct":
                    "YoY Change",
            }
        )

        # ----------------------------------------------------
        # Format values
        # ----------------------------------------------------

        yoy_display[
            f"{previous_year} Sales"
        ] = yoy_display[
            f"{previous_year} Sales"
        ].map(
            "${:,.0f}".format
        )

        yoy_display[
            f"{comparison_year} Sales"
        ] = yoy_display[
            f"{comparison_year} Sales"
        ].map(
            "${:,.0f}".format
        )

        yoy_display["YoY Change"] = (
            yoy_display["YoY Change"]
            .map(
                lambda x:
                f"{x:+.2f}%"
                if pd.notna(x)
                else "N/A"
            )
        )

        # ----------------------------------------------------
        # Display table
        # ----------------------------------------------------

        st.dataframe(
            yoy_display,
            width="stretch",
            hide_index=True,
        )

        # ----------------------------------------------------
        # YoY interpretation
        # ----------------------------------------------------

        valid_yoy = yoy_pivot[
            yoy_pivot["yoy_pct"].notna()
        ]

        if not valid_yoy.empty:

            strongest_month = valid_yoy.loc[
                valid_yoy["yoy_pct"].idxmax()
            ]

            weakest_month = valid_yoy.loc[
                valid_yoy["yoy_pct"].idxmin()
            ]

            yoy_col1, yoy_col2 = st.columns(2)

            yoy_col1.metric(
                "Strongest YoY Month",
                strongest_month["Month"],
                f"{strongest_month['yoy_pct']:+.2f}%",
            )

            yoy_col2.metric(
                "Weakest YoY Month",
                weakest_month["Month"],
                f"{weakest_month['yoy_pct']:+.2f}%",
            )

else:

    st.info(
        "Monthly YoY comparison requires at least two years "
        "of historical sales data."
    )

# ============================================================
# 13. CATEGORY + REGION PERFORMANCE
# ============================================================

col1, col2 = st.columns(2)


# ============================================================
# CATEGORY
# ============================================================

with col1:

    st.subheader("🏷️ Category Performance")
    st.caption(
        "Sales contribution across the selected period and filters."
    )

    if filtered_category.empty:

        st.warning(
            "No category data available."
        )

    else:

        category_chart = px.bar(
            filtered_category.sort_values(
                "total_sales",
                ascending=False,
            ),
            x="category",
            y="total_sales",
            text_auto=".2s",
            title="Category Sales",
        )

        category_chart.update_layout(
            xaxis_title="Category",
            yaxis_title="Sales",
            height=400,
        )

        category_chart.update_yaxes(
            tickprefix="$",
            tickformat=",.0f",
        )

        st.plotly_chart(
            category_chart,
            width="stretch",
        )


# ============================================================
# REGION
# ============================================================

with col2:

    st.subheader("🌎 Regional Performance")
    st.caption(
        "Regional sales performance within the selected filters."
    )

    if filtered_region.empty:

        st.warning(
            "No regional data available."
        )

    else:

        region_chart = px.bar(
            filtered_region.sort_values(
                "total_sales",
                ascending=False,
            ),
            x="region",
            y="total_sales",
            text_auto=".2s",
            title="Regional Sales",
        )

        region_chart.update_layout(
            xaxis_title="Region",
            yaxis_title="Sales",
            height=400,
        )

        region_chart.update_yaxes(
        tickprefix="$",
        tickformat=",.0f",
        )


        st.plotly_chart(
            region_chart,
            width="stretch",
        )


# ============================================================
# 14. PROFITABILITY ANALYSIS
# ============================================================

st.subheader("💰 Profitability Analysis")

profit_data = filtered_category[
    [
        "category",
        "total_sales",
        "total_profit",
        "profit_margin",
    ]
].copy()

profit_data = profit_data.sort_values(
    "total_profit",
    ascending=False,
)


if not profit_data.empty:

    profit_chart = px.bar(
        profit_data,
        x="category",
        y="total_profit",
        text_auto=".2s",
        title="Profit by Category",
    )

    profit_chart.update_layout(
        xaxis_title="Category",
        yaxis_title="Profit",
        height=400,
    )

    profit_chart.update_yaxes(
        tickprefix="$",
        tickformat=",.0f",
    )

    st.plotly_chart(
        profit_chart,
        width="stretch",
    )


# ============================================================
# 15. TOP PRODUCTS
# ============================================================

st.subheader("🏆 Top 10 Products")
st.caption(
    "Top products within the currently selected filters."
)

top_products = (
    filtered_product
    .sort_values(
        "total_sales",
        ascending=False,
    )
    .head(10)
)


if not top_products.empty:

    product_chart = px.bar(
        top_products.sort_values(
            "total_sales"
        ),
        x="total_sales",
        y="product_name",
        orientation="h",
        text_auto=".2s",
        title="Top 10 Products",
    )

    product_chart.update_layout(
        xaxis_title="Sales",
        yaxis_title="Product",
        height=500,
    )

    st.plotly_chart(
        product_chart,
        width="stretch",
    )


# ============================================================
# 16. FORECASTING & FUTURE OUTLOOK
# ============================================================

st.subheader("🔮 Six-Month Company Sales Forecast")

st.markdown(
    """
    The forecast estimates expected company-wide monthly sales
    for the next six months using the **Seasonal Naive forecasting model**.

    **Note:** The forecast is based on the complete historical sales
    series and is independent of the dashboard filters.
    """
)


if forecast.empty:

    st.warning(
        "Forecast file not found. "
        "Run `python python\\forecast.py` first."
    )

else:

    # ========================================================
    # FORECAST VS RECENT ACTUAL INTELLIGENCE
    # ========================================================

    recent_months = 3

    recent_actual = (
        monthly_sales
        .sort_values("sales_month")
        .tail(recent_months)
    )

    recent_actual_average = (
        recent_actual["total_sales"].mean()
    )

    forecast_average = forecast["forecast_sales"].mean()

    forecast_vs_recent_pct = (
        (
            forecast_average
            - recent_actual_average
        )
        / recent_actual_average
        * 100
        if recent_actual_average != 0
        else 0
    )
    # ========================================================
    # FORECAST METRICS
    # ========================================================

    forecast_values = forecast[
        "forecast_sales"
    ]

    average_forecast = forecast_values.mean()

    highest_forecast = forecast_values.max()

    lowest_forecast = forecast_values.min()

    highest_forecast_month = forecast.loc[
        forecast["forecast_sales"].idxmax(),
        "sales_month"
    ]

    lowest_forecast_month = forecast.loc[
        forecast["forecast_sales"].idxmin(),
        "sales_month"
    ]


    # ========================================================
    # FORECAST KPI CARDS
    # ========================================================

    forecast_col1, forecast_col2, forecast_col3, forecast_col4, forecast_col5 = (
        st.columns(5)
    )


    forecast_col1.metric(
        "Average Monthly Forecast",
        f"${average_forecast / 1_000_000:.2f}M"
    )


    forecast_col2.metric(
        "Highest Forecast",
        f"${highest_forecast / 1_000_000:.2f}M"
    )


    forecast_col3.metric(
        "Lowest Forecast",
        f"${lowest_forecast / 1_000_000:.2f}M"
    )


    forecast_col4.metric(
        "Forecast Horizon",
        f"{len(forecast)} Months"
    )
    forecast_col5.metric(
        "Forecast vs Recent Actual",
        f"{forecast_vs_recent_pct:+.2f}%",
    )


    st.markdown("")

    # ========================================================
    # FORECAST OUTLOOK INTERPRETATION
    # ========================================================

    if forecast_vs_recent_pct > 10:

        st.success(
            f"""
            📈 **Positive Forecast Outlook**

            The average forecast is **{forecast_vs_recent_pct:.2f}%**
            higher than the average sales of the last
            **{recent_months} actual months**.

            This indicates a strong expected sales outlook relative
            to recent performance.
            """
        )

    elif forecast_vs_recent_pct < -10:

        st.warning(
            f"""
            📉 **Cautious Forecast Outlook**

            The average forecast is **{abs(forecast_vs_recent_pct):.2f}%**
            lower than the average sales of the last
            **{recent_months} actual months**.

            This suggests that future sales may soften relative
            to recent performance.
            """
        )

    else:

        st.info(
            f"""
            📊 **Stable Forecast Outlook**

            The average forecast is **{abs(forecast_vs_recent_pct):.2f}%**
            {"higher" if forecast_vs_recent_pct > 0 else "lower"}
            than the average sales of the last
            **{recent_months} actual months**.

            Forecasted demand is broadly consistent with recent
            sales performance.
            """
        )


    # ========================================================
    # HISTORICAL + FORECAST DATA
    # ========================================================

    historical_chart = monthly_sales[
        [
            "sales_month",
            "total_sales",
        ]
    ].copy()

    historical_chart = historical_chart.rename(
        columns={
            "total_sales": "sales"
        }
    )

    historical_chart["type"] = "Historical"


    forecast_chart = forecast[
        [
            "sales_month",
            "forecast_sales",
        ]
    ].copy()

    forecast_chart = forecast_chart.rename(
        columns={
            "forecast_sales": "sales"
        }
    )

    forecast_chart["type"] = "Forecast"


    combined_forecast = pd.concat(
        [
            historical_chart,
            forecast_chart,
        ],
        ignore_index=True,
    )
    # ========================================================
    # FORECAST START DATE
    # ========================================================

    forecast_start = forecast["sales_month"].min()


    # ========================================================
    # FORECAST CHART
    # ========================================================

    forecast_fig = px.line(
        combined_forecast,
        x="sales_month",
        y="sales",
        color="type",
        markers=True,
        title="Company-Wide Historical Sales vs Future Forecast",
    )


    forecast_fig.update_traces(
        hovertemplate=(
            "<b>%{x|%b %Y}</b><br>"
            "Sales: $%{y:,.0f}"
            "<extra></extra>"
        )
    )


    forecast_fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Sales ($)",
        hovermode="x unified",
    )

    forecast_fig.update_yaxes(
        tickprefix="$",
        tickformat=",.0f",
    )


    forecast_fig = style_chart(
        forecast_fig,
        height=500
    )

    forecast_fig.add_vline(
        x=forecast_start.timestamp() * 1000,
        line_dash="dash",
        annotation_text="Forecast Start",
        annotation_position="top",
    )


    st.plotly_chart(
        forecast_fig,
        width="stretch",
    )

    # ========================================================
    # FORECAST VARIANCE ANALYSIS
    # ========================================================

    st.markdown("### 📊 Forecast Variance Analysis")

    variance_data = forecast.copy()

    variance_data["forecast_vs_recent"] = (
        (
            variance_data["forecast_sales"]
            - recent_actual_average
        )
        / recent_actual_average
        * 100
    )

    variance_data["variance_direction"] = (
        variance_data["forecast_vs_recent"]
        .apply(
            lambda x:
            "Above Recent Actual"
            if x > 0
            else "Below Recent Actual"
        )
    )

    variance_display = variance_data[
        [
            "sales_month",
            "forecast_sales",
            "forecast_vs_recent",
            "variance_direction",
        ]
    ].copy()

    variance_display["sales_month"] = (
        variance_display["sales_month"]
        .dt.strftime("%b %Y")
    )

    variance_display["forecast_sales"] = (
        variance_display["forecast_sales"]
        .map("${:,.0f}".format)
    )

    variance_display["forecast_vs_recent"] = (
        variance_display["forecast_vs_recent"]
        .map("{:+.2f}%".format)
    )

    variance_display = variance_display.rename(
        columns={
            "sales_month": "Month",
            "forecast_sales": "Forecast Sales",
            "forecast_vs_recent": "Vs Recent Actual",
            "variance_direction": "Outlook",
        }
    )

    st.dataframe(
        variance_display,
        width="stretch",
        hide_index=True,
    )

    # ========================================================
    # FORECAST INTELLIGENCE
    # ========================================================

    st.markdown("### 🧠 Forecast Intelligence")

    if forecast_vs_recent_pct > 0:
        outlook_word = "above"
    elif forecast_vs_recent_pct < 0:
        outlook_word = "below"
    else:
        outlook_word = "equal to"

    st.markdown(
        f"""
        **Forecast Signal**

        The six-month forecast averages
        **${forecast_average:,.0f} per month**, which is
        **{abs(forecast_vs_recent_pct):.2f}% {outlook_word}**
        the average monthly sales of the last
        **{recent_months} actual months**
        (**${recent_actual_average:,.0f}**).

        This comparison provides a near-term demand signal while
        the forecast period remains in the future.
        """
    )


    # ========================================================
    # FORECAST DETAILS
    # ========================================================

    st.markdown("### 📅 Forecast Details")


    forecast_display = forecast.copy()


    forecast_display["sales_month"] = (
        forecast_display["sales_month"]
        .dt.strftime("%b %Y")
    )


    forecast_display["forecast_sales"] = (
        forecast_display["forecast_sales"]
        .map("${:,.0f}".format)
    )


    forecast_display = forecast_display.rename(
        columns={
            "sales_month": "Month",
            "forecast_sales": "Forecast Sales",
        }
    )


    st.dataframe(
        forecast_display,
        width="stretch",
        hide_index=True,
    )




    # ========================================================
    # MODEL EXPLANATION
    # ========================================================

    st.markdown("### 🤖 Forecasting Methodology")


    with st.expander(
        "Why was Seasonal Naive selected?"
    ):

        st.markdown(
            """
            The forecasting pipeline evaluated multiple models
            using a historical holdout validation period.

            **Model comparison:**

            | Model | MAPE |
            |---|---:|
            | Seasonal Naive | **5.81%** |
            | ARIMA(1,1,0) | 9.81% |
            | ARIMA(0,1,1) | 9.85% |
            | ARIMA(0,1,0) | 10.66% |

            The **Seasonal Naive model achieved the lowest validation
            MAPE**, so it was selected as the final forecasting
            approach.

            Seasonal Naive forecasting assumes that the sales for
            a future month will resemble the sales observed during
            the corresponding month in the previous seasonal cycle.

            This approach is particularly useful when recurring
            seasonal patterns are present in the historical data.
            """
        )


    # ========================================================
    # FORECAST CAVEAT
    # ========================================================

    st.caption(
        "Forecasts are estimates based on historical patterns "
        "and should be interpreted as planning guidance rather "
        "than guaranteed future sales."
    )


# ============================================================
# 17. TOP CUSTOMERS
# ============================================================

st.subheader("👥 Top Customers")

top_customers = (
    filtered_customer
    .sort_values(
        "total_sales",
        ascending=False,
    )
    .head(10)
    .copy()
)


if not top_customers.empty:

    customer_display = top_customers[
        [
            "customer_id",
            "customer_name",
            "segment",
            "total_sales",
            "total_profit",
            "total_orders",
            "profit_margin",
        ]
    ].copy()

    customer_display["total_sales"] = (
        customer_display["total_sales"]
        .map("${:,.0f}".format)
    )

    customer_display["total_profit"] = (
        customer_display["total_profit"]
        .map("${:,.0f}".format)
    )

    customer_display["profit_margin"] = (
        customer_display["profit_margin"]
        .map("{:.2f}%".format)
    )

    customer_display = customer_display.rename(
        columns={
            "customer_id": "Customer ID",
            "customer_name": "Customer",
            "segment": "Segment",
            "total_sales": "Sales",
            "total_profit": "Profit",
            "total_orders": "Orders",
            "profit_margin": "Margin",
        }
    )

    st.dataframe(
        customer_display,
        width="stretch",
        hide_index=True,
    )



# ============================================================
# 18. AUTOMATED BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Key Business Insights")


# ============================================================
# 18.1 SALES PERFORMANCE INSIGHT
# ============================================================

yearly_sales = (
    filtered_raw
    .assign(
        year=filtered_raw["order_date"].dt.year
    )
    .groupby("year")["sales"]
    .sum()
    .sort_index()
)

sales_growth = None

if len(yearly_sales) >= 2:

    previous_year = yearly_sales.index[-2]
    current_year = yearly_sales.index[-1]

    previous_sales = yearly_sales.iloc[-2]
    current_sales = yearly_sales.iloc[-1]

    if previous_sales != 0:

        sales_growth = (
            (current_sales - previous_sales)
            / previous_sales
        ) * 100

        if sales_growth > 0:

            sales_message = (
                f"Sales increased by "
                f"**{sales_growth:.2f}%** from "
                f"**{previous_year}** to "
                f"**{current_year}**."
            )

        elif sales_growth < 0:

            sales_message = (
                f"Sales decreased by "
                f"**{abs(sales_growth):.2f}%** from "
                f"**{previous_year}** to "
                f"**{current_year}**."
            )

        else:

            sales_message = (
                f"Sales remained stable from "
                f"**{previous_year}** to "
                f"**{current_year}**."
            )

    else:

        sales_message = (
            "Year-over-year growth could not be calculated "
            "because the previous year's sales are zero."
        )

else:

    selected_year = (
        yearly_sales.index[0]
        if len(yearly_sales) == 1
        else None
    )

    if selected_year is not None:

        selected_year_sales = yearly_sales.iloc[0]

        sales_message = (
            f"**{selected_year}** generated "
            f"**${selected_year_sales:,.0f}** in sales "
            f"with a profit margin of "
            f"**{overall_margin:.2f}%**."
        )

    else:

        sales_message = (
            "Select at least one year to evaluate "
            "annual sales performance."
        )


# ============================================================
# 18.2 CATEGORY INSIGHT
# ============================================================

if not filtered_category.empty:

    top_category = (
        filtered_category
        .sort_values(
            "total_sales",
            ascending=False,
        )
        .iloc[0]
    )

    top_profit_category = (
        filtered_category
        .sort_values(
            "total_profit",
            ascending=False,
        )
        .iloc[0]
    )

else:

    top_category = None
    top_profit_category = None


# ============================================================
# 18.3 REGION INSIGHT
# ============================================================

if not filtered_region.empty:

    top_region = (
        filtered_region
        .sort_values(
            "total_sales",
            ascending=False,
        )
        .iloc[0]
    )

else:

    top_region = None


# ============================================================
# 18.4 FORECAST INSIGHT
# ============================================================

if not forecast.empty:

    highest_forecast = forecast.loc[
        forecast["forecast_sales"].idxmax()
    ]

    lowest_forecast = forecast.loc[
        forecast["forecast_sales"].idxmin()
    ]

    average_forecast = (
        forecast["forecast_sales"].mean()
    )

    forecast_message = (
    f"The six-month forecast averages "
    f"${average_forecast:,.0f} per month. "
    f"The highest projected sales are "
    f"${highest_forecast['forecast_sales']:,.0f} in "
    f"{highest_forecast['sales_month'].strftime('%B %Y')}, "
    f"while the lowest are "
    f"${lowest_forecast['forecast_sales']:,.0f} in "
    f"{lowest_forecast['sales_month'].strftime('%B %Y')}."
)

else:

    forecast_message = (
        "Forecast data is not available."
    )


# ============================================================
# 18.5 INSIGHT CARDS
# ============================================================

insight_col1, insight_col2 = st.columns(2)


with insight_col1:

    st.info(
        f"""
        ### 📈 Sales Performance

        {sales_message}
        """
    )


    if top_category is not None:

        st.info(
            f"""
            ### 🏷️ Category Performance

            **{top_category["category"]}** is the
            highest-selling category.

            Sales:
            **${top_category["total_sales"]:,.0f}**
            """
        )


with insight_col2:

    if top_region is not None:

        st.info(
            f"""
            ### 🌎 Regional Performance

            **{top_region["region"]}** is the
            leading region by sales.

            Sales:
            **${top_region["total_sales"]:,.0f}**
            """
        )


    st.info(
        f"""
        ### 🔮 Forecast Outlook

        {forecast_message}
        """
    )


# ============================================================
# 18.6 PROFITABILITY INSIGHT
# ============================================================

if top_profit_category is not None:

    st.success(
        f"""
        ### 💰 Most Profitable Category

        **{top_profit_category["category"]}** generates the
        highest total profit.

        Profit:
        **${top_profit_category["total_profit"]:,.0f}**

        Profit Margin:
        **{top_profit_category["profit_margin"]:.2f}%**
        """
    )
# ============================================================
# 18.5 RISK & OPPORTUNITY INTELLIGENCE
# ============================================================

st.markdown("### ⚠️ Risk & Opportunity Intelligence")

if benchmark_category.empty or benchmark_region.empty:

    st.info(
        "Insufficient benchmark data available for risk and "
        "opportunity analysis."
    )

else:

    # ========================================================
    # CATEGORY BENCHMARKS
    # ========================================================

    strongest_category = (
        benchmark_category
        .sort_values("total_sales", ascending=False)
        .iloc[0]
    )

    weakest_category = (
        benchmark_category
        .sort_values("total_sales", ascending=True)
        .iloc[0]
    )

    lowest_margin_category = (
        benchmark_category
        .sort_values("profit_margin", ascending=True)
        .iloc[0]
    )


    # ========================================================
    # REGION BENCHMARKS
    # ========================================================

    strongest_region = (
        benchmark_region
        .sort_values("total_sales", ascending=False)
        .iloc[0]
    )

    weakest_region = (
        benchmark_region
        .sort_values("total_sales", ascending=True)
        .iloc[0]
    )


    # ========================================================
    # PRODUCT BENCHMARK
    # ========================================================

    strongest_product = (
        benchmark_product
        .sort_values("total_sales", ascending=False)
        .iloc[0]
    )


    # ========================================================
    # RISK CARDS
    # ========================================================

    risk_col1, risk_col2, risk_col3 = st.columns(3)


    with risk_col1:

        st.warning(
            f"""
            ### 🔴 Weakest Category

            **{weakest_category["category"]}**

            Sales:
            **${weakest_category["total_sales"]:,.0f}**

            Margin:
            **{weakest_category["profit_margin"]:.2f}%**
            """
        )


    with risk_col2:

        st.warning(
            f"""
            ### 🔴 Weakest Region

            **{weakest_region["region"]}**

            Sales:
            **${weakest_region["total_sales"]:,.0f}**

            Margin:
            **{weakest_region["profit_margin"]:.2f}%**
            """
        )


    with risk_col3:

        st.warning(
            f"""
            ### 🔴 Lowest Profit Margin

            **{lowest_margin_category["category"]}**

            Margin:
            **{lowest_margin_category["profit_margin"]:.2f}%**

            Profit:
            **${lowest_margin_category["total_profit"]:,.0f}**
            """
        )


    # ========================================================
    # OPPORTUNITY CARDS
    # ========================================================

    opportunity_col1, opportunity_col2, opportunity_col3 = (
        st.columns(3)
    )


    with opportunity_col1:

        st.success(
            f"""
            ### 🟢 Top Category

            **{strongest_category["category"]}**

            Sales:
            **${strongest_category["total_sales"]:,.0f}**

            Profit:
            **${strongest_category["total_profit"]:,.0f}**
            """
        )


    with opportunity_col2:

        st.success(
            f"""
            ### 🟢 Top Region

            **{strongest_region["region"]}**

            Sales:
            **${strongest_region["total_sales"]:,.0f}**

            Profit:
            **${strongest_region["total_profit"]:,.0f}**
            """
        )


    with opportunity_col3:

        st.success(
            f"""
            ### 🟢 Top Product

            **{strongest_product["product_name"]}**

            Sales:
            **${strongest_product["total_sales"]:,.0f}**

            Profit:
            **${strongest_product["total_profit"]:,.0f}**
            """
        )


    # ========================================================
    # BENCHMARK CONTEXT
    # ========================================================

    benchmark_year_text = ", ".join(
        map(str, selected_years)
    )

    st.caption(
        f"Strategic benchmark period: **{benchmark_year_text}**. "
        "Category and Region filters do not affect these rankings."
    )

# ============================================================
# 18.8 BUSINESS RECOMMENDATIONS
# ============================================================

st.markdown("### 🎯 Business Recommendations")


recommendations = []


# Sales recommendation

if sales_growth is not None:

    if sales_growth < 0:

        recommendations.append(
            "📉 Review the causes of year-over-year sales decline "
            "and identify underperforming months, categories and regions."
        )

    elif sales_growth > 0:

        recommendations.append(
            "📈 Maintain focus on the factors driving year-over-year "
            "sales growth and replicate successful strategies."
        )

    else:

        recommendations.append(
            "📊 Sales are relatively stable year-over-year. "
            "Focus on improving high-potential categories and regions."
        )

else:

    recommendations.append(
        "📊 Select multiple years to evaluate year-over-year "
        "sales performance."
    )


# Category recommendation

if top_category is not None:

    recommendations.append(
        f"🏷️ **{strongest_category['category']}** is the strongest "
        f"category in the selected year by sales. Protect its momentum "
        f"while investigating **{weakest_category['category']}**, "
        f"the weakest category."
    )


# Region recommendation

if top_region is not None:

    recommendations.append(
        f"🌎 **{strongest_region['region']}** is the strongest region "
        f"in the selected year by sales. Maintain its performance while "
        f"investigating opportunities in **{weakest_region['region']}**, "
        f"the weakest region."
    )


# Forecast recommendation

if lowest_forecast is not None:

    recommendations.append(
        f"🔮 Prepare for the forecasted low-sales period in "
        f"**{lowest_forecast['sales_month'].strftime('%B %Y')}** "
        f"and evaluate inventory, promotions and demand-generation "
        f"strategies."
    )


for recommendation in recommendations:

    st.markdown(
        f"- {recommendation}"
    )


# ============================================================
# 19. DATA SOURCE INFORMATION
# ============================================================

st.divider()

with st.expander("ℹ️ Dashboard Information"):

    st.markdown(
        """
        **Data Source:** MySQL

        **Analytics Layer:** SQL Views

        **Data Processing:** Python + Pandas

        **Forecast Model:** Seasonal Naive

        **Visualization:** Plotly

        **Dashboard Framework:** Streamlit

        **Forecast Horizon:** 6 months
        """
    )


# ============================================================
# 20. FOOTER
# ============================================================

st.divider()

st.caption(
    "Sales Analytics Dashboard | "
    "MySQL + Python + Streamlit + Plotly"
)
