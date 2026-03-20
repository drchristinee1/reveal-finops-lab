import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="FinOps Operating Dashboard", layout="wide")

st.title("📊 FinOps Operating Dashboard")
st.caption("Action-oriented visibility into cost drivers, ownership, priority, and savings opportunities.")

st.markdown("**Purpose:** Translate cost signals into accountable engineering actions.")
# Load data
with open("data/action_plan.json") as f:
    data = json.load(f)

df = pd.DataFrame(data["action_items"])

trend_data = pd.DataFrame(
    {
        "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "savings": [420, 510, 610, 720, 840, 970],
        "issues": [8, 7, 6, 5, 4, 3],
    }
)

st.sidebar.header("Filters")

selected_driver = st.sidebar.multiselect(
    "Cost Driver",
    options=sorted(df["driver"].unique()),
    default=sorted(df["driver"].unique()),
)

selected_priority = st.sidebar.multiselect(
    "Priority",
    options=sorted(df["priority"].unique()),
    default=sorted(df["priority"].unique()),
)

selected_owner = st.sidebar.multiselect(
    "Owner",
    options=sorted(df["owner"].unique()),
    default=sorted(df["owner"].unique()),
)

filtered_df = df[
    df["driver"].isin(selected_driver)
    & df["priority"].isin(selected_priority)
    & df["owner"].isin(selected_owner)
]

total_savings = int(filtered_df["estimated_monthly_savings"].sum())
high_priority = int((filtered_df["priority"] == "high").sum())
total_issues = len(filtered_df)

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Savings", f"${total_savings}")
col2.metric("🔥 High Priority Issues", high_priority)
col3.metric("📦 Total Issues", total_issues)

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Savings Trend")
    st.line_chart(trend_data.set_index("month")["savings"])

with right:
    st.subheader("Issue Reduction Trend")
    st.line_chart(trend_data.set_index("month")["issues"])

st.divider()

st.subheader("Action Items")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.divider()

left2, right2 = st.columns(2)

with left2:
    st.subheader("Savings by Cost Driver")
    st.bar_chart(
        filtered_df.groupby("driver")["estimated_monthly_savings"]
        .sum()
        .sort_values(ascending=False)
    )

with right2:
    st.subheader("Priority Distribution")
    st.bar_chart(filtered_df["priority"].value_counts())

st.divider()

st.subheader("Savings by Owner")
st.bar_chart(
    filtered_df.groupby("owner")["estimated_monthly_savings"]
    .sum()
    .sort_values(ascending=False)
)