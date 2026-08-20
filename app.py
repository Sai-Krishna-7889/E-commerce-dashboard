import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide"
)

# -----------------------------
# Generate sample e-commerce data
# -----------------------------

@st.cache_data
def generate_data():
    np.random.seed(42)

    products = [
        "Laptop", "Smartphone", "Headphones", "Smart Watch",
        "Keyboard", "Mouse", "Tablet", "Monitor",
        "Shoes", "Backpack"
    ]

    categories = {
        "Laptop": "Electronics",
        "Smartphone": "Electronics",
        "Headphones": "Electronics",
        "Smart Watch": "Electronics",
        "Keyboard": "Accessories",
        "Mouse": "Accessories",
        "Tablet": "Electronics",
        "Monitor": "Electronics",
        "Shoes": "Fashion",
        "Backpack": "Fashion"
    }

    n = 1000

    dates = pd.date_range(
        start="2015-01-01",
        end="2026-06-30",
        periods=n
    )

    product_data = np.random.choice(products, n)

    data = pd.DataFrame({
        "Order_ID": [f"ORD{i+1:04d}" for i in range(n)],
        "Order_Date": dates,
        "Customer_ID": [
            f"CUST{np.random.randint(1, 251):03d}"
            for _ in range(n)
        ],
        "Product": product_data,
        "Category": [categories[p] for p in product_data],
        "Quantity": np.random.randint(1, 6, n),
        "Unit_Price": np.random.randint(500, 50000, n),
        "Location": np.random.choice(
            ["Chennai", "Bangalore", "Hyderabad",
             "Mumbai", "Delhi", "Kochi"],
            n
        )
    })

    data["Total_Sales"] = (
        data["Quantity"] * data["Unit_Price"]
    )

    data["Month"] = data["Order_Date"].dt.strftime("%b")
    data["Month_Number"] = data["Order_Date"].dt.month

    return data


df = generate_data()

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("Dashboard Filters")

categories = ["All"] + sorted(df["Category"].unique().tolist())

selected_category = st.sidebar.selectbox(
    "Select Category",
    categories
)

if selected_category != "All":
    filtered_df = df[df["Category"] == selected_category]
else:
    filtered_df = df.copy()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [
        df["Order_Date"].min().date(),
        df["Order_Date"].max().date()
    ]
)

if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["Order_Date"].dt.date >= start_date) &
        (filtered_df["Order_Date"].dt.date <= end_date)
    ]

# -----------------------------
# Header
# -----------------------------

st.title("🛒 E-Commerce Sales Analytics Dashboard")
st.write(
    "Interactive dashboard for analysing customer purchases, "
    "sales performance, products and seasonal shopping trends."
)

# -----------------------------
# KPIs
# -----------------------------

total_revenue = filtered_df["Total_Sales"].sum()
total_orders = filtered_df["Order_ID"].nunique()
total_customers = filtered_df["Customer_ID"].nunique()

if total_orders > 0:
    average_order_value = total_revenue / total_orders
else:
    average_order_value = 0

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Revenue",
    f"₹{total_revenue:,.0f}"
)

col2.metric(
    "Total Orders",
    f"{total_orders:,}"
)

col3.metric(
    "Customers",
    f"{total_customers:,}"
)

col4.metric(
    "Average Order Value",
    f"₹{average_order_value:,.0f}"
)

st.divider()

# -----------------------------
# Monthly Revenue
# -----------------------------

st.subheader("📈 Monthly Revenue Trend")

monthly_sales = (
    filtered_df
    .groupby(["Month_Number", "Month"])["Total_Sales"]
    .sum()
    .reset_index()
    .sort_values("Month_Number")
)

fig_monthly = px.line(
    monthly_sales,
    x="Month",
    y="Total_Sales",
    markers=True,
    title="Monthly Revenue"
)

fig_monthly.update_layout(
    xaxis_title="Month",
    yaxis_title="Revenue (₹)"
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)

# -----------------------------
# Category and Product Analysis
# -----------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Revenue by Category")

    category_sales = (
        filtered_df
        .groupby("Category")["Total_Sales"]
        .sum()
        .reset_index()
        .sort_values("Total_Sales", ascending=False)
    )

    fig_category = px.bar(
        category_sales,
        x="Category",
        y="Total_Sales",
        title="Revenue by Category"
    )

    fig_category.update_layout(
        xaxis_title="Category",
        yaxis_title="Revenue (₹)"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )

with col2:
    st.subheader("🏆 Top Products")

    product_sales = (
        filtered_df
        .groupby("Product")["Total_Sales"]
        .sum()
        .reset_index()
        .sort_values("Total_Sales", ascending=False)
        .head(10)
    )

    fig_products = px.bar(
        product_sales,
        x="Total_Sales",
        y="Product",
        orientation="h",
        title="Top 10 Products by Revenue"
    )

    fig_products.update_layout(
        xaxis_title="Revenue (₹)",
        yaxis_title="Product"
    )

    st.plotly_chart(
        fig_products,
        use_container_width=True
    )

# -----------------------------
# Customer Lifetime Value
# -----------------------------

st.subheader("👥 Customer Lifetime Value")

customer_value = (
    filtered_df
    .groupby("Customer_ID")
    .agg(
        Total_Spent=("Total_Sales", "sum"),
        Number_of_Orders=("Order_ID", "nunique"),
        Average_Order_Value=("Total_Sales", "mean")
    )
    .reset_index()
    .sort_values("Total_Spent", ascending=False)
)

top_customers = customer_value.head(10)

fig_customers = px.bar(
    top_customers,
    x="Customer_ID",
    y="Total_Spent",
    title="Top 10 Customers by Lifetime Value"
)

fig_customers.update_layout(
    xaxis_title="Customer",
    yaxis_title="Lifetime Value (₹)"
)

st.plotly_chart(
    fig_customers,
    use_container_width=True
)

# -----------------------------
# Purchase Pattern
# -----------------------------

st.subheader("🛍️ Customer Purchase Patterns")

purchase_pattern = (
    filtered_df
    .groupby("Customer_ID")
    .agg(
        Orders=("Order_ID", "nunique"),
        Total_Spent=("Total_Sales", "sum")
    )
    .reset_index()
)

fig_purchase = px.scatter(
    purchase_pattern,
    x="Orders",
    y="Total_Spent",
    title="Orders vs Customer Spending",
    hover_data=["Customer_ID"]
)

fig_purchase.update_layout(
    xaxis_title="Number of Orders",
    yaxis_title="Total Amount Spent (₹)"
)

st.plotly_chart(
    fig_purchase,
    use_container_width=True
)

# -----------------------------
# Seasonal Analysis
# -----------------------------

st.subheader("🌦️ Seasonal Shopping Trends")

seasonal_data = (
    filtered_df
    .groupby("Month")["Total_Sales"]
    .sum()
    .reset_index()
)

month_order = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

seasonal_data["Month"] = pd.Categorical(
    seasonal_data["Month"],
    categories=month_order,
    ordered=True
)

seasonal_data = seasonal_data.sort_values("Month")

fig_season = px.area(
    seasonal_data,
    x="Month",
    y="Total_Sales",
    title="Seasonal Sales Trend"
)

fig_season.update_layout(
    xaxis_title="Month",
    yaxis_title="Revenue (₹)"
)

st.plotly_chart(
    fig_season,
    use_container_width=True
)

# -----------------------------
# Location Analysis
# -----------------------------

st.subheader("📍 Sales by Location")

location_sales = (
    filtered_df
    .groupby("Location")["Total_Sales"]
    .sum()
    .reset_index()
    .sort_values("Total_Sales", ascending=False)
)

fig_location = px.bar(
    location_sales,
    x="Location",
    y="Total_Sales",
    title="Revenue by Location"
)

fig_location.update_layout(
    xaxis_title="Location",
    yaxis_title="Revenue (₹)"
)

st.plotly_chart(
    fig_location,
    use_container_width=True
)

# -----------------------------
# Data Table
# -----------------------------

with st.expander("View Transaction Data"):
    st.dataframe(
        filtered_df,
        use_container_width=True
    )

st.success("Dashboard analysis completed successfully.")
