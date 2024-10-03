import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_manager import DataManager
from utils.visualizations import (
    create_monthly_summary_chart,
    create_revenue_trend_chart,
    create_cost_trend_chart,
    create_cumulative_balance_chart,
    create_year_over_year_comparison_chart
)

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] == st.secrets["credentials"]["username"]
            and st.session_state["password"] == st.secrets["credentials"]["password"]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct
        return True

from datetime import datetime
import json

# Set page config at the very beginning
st.set_page_config(page_title="Accounting System",
                   page_icon="💼",
                   layout="wide")

# Load the secret
try:
    secret_file = st.secrets["accounting_data"]["data"]
    accounting_data = json.loads(secret_file)  # Parse the JSON string
except json.JSONDecodeError as e:
    st.error(f"Failed to load accounting data: {e}")
    accounting_data = {"revenues": {}, "costs": {}}

# Initialize DataManager with the secret file
data_manager = DataManager(accounting_data)

def main():
    if not check_password():
        return

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["전체보기"])

    if page == "전체보기":
        overview_page()

def overview_page():
    st.title("코람데오 예산 - 전체보기")

    # Year selection
    current_year = datetime.now().year
    years = list(range(current_year - 1, current_year + 2))  # Previous year, current year, next year
    selected_years = st.multiselect("연도 선택", years, default=[current_year])

    # Load data for selected years
    revenues = []
    costs = []
    for year in selected_years:
        revenues.extend(data_manager.get_revenues(year))
        year_costs = data_manager.get_costs(year)
        if isinstance(year_costs, dict):
            for event, subcategories in year_costs.items():
                for subcategory, subcategory_costs in subcategories.items():
                    costs.extend(subcategory_costs)
        elif isinstance(year_costs, list):
            costs.extend(year_costs)

    # Calculate summary
    total_revenue = sum(item['amount'] for item in revenues if isinstance(item, dict) and 'amount' in item)
    total_costs = sum(cost['amount'] for cost in costs if isinstance(cost, dict) and 'amount' in cost)
    net_balance = total_revenue - total_costs

    # Display summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}", delta=None)
    col2.metric("Total Costs", f"${total_costs:,.2f}", delta=None)
    col3.metric("Net Balance", f"${net_balance:,.2f}", delta=None)

    # Display recent entries
    st.subheader("Recent Entries")
    recent_revenues = sorted([r for r in revenues if isinstance(r, dict) and 'date' in r], key=lambda x: x['date'], reverse=True)[:5]
    recent_costs = sorted([c for c in costs if isinstance(c, dict) and 'date' in c], key=lambda x: x['date'], reverse=True)[:5]

    col1, col2 = st.columns(2)

    with col1:
        st.write("Recent Revenues")
        df_revenue = pd.DataFrame(recent_revenues)
        if not df_revenue.empty:
            df_revenue['date'] = pd.to_datetime(df_revenue['date'])
            df_revenue = df_revenue.sort_values('date', ascending=False)
            st.dataframe(df_revenue[['date', 'description', 'amount']])
        else:
            st.write("No recent revenues")

    with col2:
        st.write("Recent Costs")
        df_costs = pd.DataFrame(recent_costs)
        if not df_costs.empty:
            df_costs['date'] = pd.to_datetime(df_costs['date'])
            df_costs = df_costs.sort_values('date', ascending=False)
            columns_to_display = ['date', 'event', 'subcategory', 'description', 'amount']
            columns_to_display = [col for col in columns_to_display if col in df_costs.columns]
            st.dataframe(df_costs[columns_to_display])
        else:
            st.write("No recent costs")

    # Year-wise breakdown
    st.subheader("Year-wise Breakdown")
    year_data = []
    for year in selected_years:
        year_revenues = sum(item['amount'] for item in revenues if isinstance(item, dict) and 'amount' in item and item['date'].startswith(str(year)))
        year_costs = sum(cost['amount'] for cost in costs if isinstance(cost, dict) and 'amount' in cost and cost['date'].startswith(str(year)))
        year_data.append({"Year": year, "Revenue": year_revenues, "Costs": year_costs, "Net": year_revenues - year_costs})
    
    df_year_breakdown = pd.DataFrame(year_data)
    if df_year_breakdown.empty:
        st.write("No data available for the selected years.")
    else:
        st.dataframe(df_year_breakdown)

if __name__ == "__main__":
    main()
