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
from datetime import datetime
import json

# Load the secret and initialize DataManager
try:
    secret_file = st.secrets["accounting_data"]["data"]
    accounting_data = json.loads(secret_file)  # Parse the JSON string
    data_manager = DataManager(accounting_data)
except KeyError:
    st.error("Unable to load accounting data. Please check the Streamlit secrets configuration.")
    st.stop()

def reports_page():
    st.title("예산 보고서")
    
    current_year = datetime.now().year
    last_year = current_year - 1

    # Fetch data for the current and last years
    revenues_current = data_manager.get_revenues(current_year)
    costs_current = data_manager.get_costs(current_year)
    revenues_last = data_manager.get_revenues(last_year)
    costs_last = data_manager.get_costs(last_year)
    
    # Convert revenue and cost data to DataFrames for current year
    df_revenue_current = pd.DataFrame(revenues_current)
    if not df_revenue_current.empty:
        df_revenue_current['date'] = pd.to_datetime(df_revenue_current['date'], errors='coerce')
        df_revenue_current['type'] = '수입'
        df_revenue_current['year'] = current_year

    df_costs_current = pd.DataFrame()
    for event, subcategories in costs_current.items():
        for subcategory, subcategory_costs in subcategories.items():
            df_category = pd.DataFrame(subcategory_costs)
            df_category['event'] = event
            df_category['subcategory'] = subcategory
            df_costs_current = pd.concat([df_costs_current, df_category], ignore_index=True)

    if not df_costs_current.empty:
        df_costs_current['date'] = pd.to_datetime(df_costs_current['date'], errors='coerce')
        df_costs_current['type'] = '지출'
        df_costs_current['year'] = current_year

    # Convert revenue and cost data to DataFrames for last year
    df_revenue_last = pd.DataFrame(revenues_last)
    if not df_revenue_last.empty:
        df_revenue_last['date'] = pd.to_datetime(df_revenue_last['date'], errors='coerce')
        df_revenue_last['type'] = '수입'
        df_revenue_last['year'] = last_year

    df_costs_last = pd.DataFrame()
    for event, subcategories in costs_last.items():
        for subcategory, subcategory_costs in subcategories.items():
            df_category = pd.DataFrame(subcategory_costs)
            df_category['event'] = event
            df_category['subcategory'] = subcategory
            df_costs_last = pd.concat([df_costs_last, df_category], ignore_index=True)

    if not df_costs_last.empty:
        df_costs_last['date'] = pd.to_datetime(df_costs_last['date'], errors='coerce')
        df_costs_last['type'] = '지출'
        df_costs_last['year'] = last_year

    # Combine all data for filtering and reports
    df_combined = pd.concat([df_revenue_current, df_costs_current, df_revenue_last, df_costs_last])
    
    if df_combined.empty:
        st.warning("No data available for the selected period.")
        return

    df_combined = df_combined.sort_values('date')

    # Date range filter
    start_date = st.date_input("Start Date", min(df_combined['date'].min(), pd.Timestamp.today()))
    end_date = st.date_input("End Date", max(df_combined['date'].max(), pd.Timestamp.today()))
    
    df_filtered = df_combined[(df_combined['date'] >= pd.Timestamp(start_date)) & 
                              (df_combined['date'] <= pd.Timestamp(end_date))]
    
    if df_filtered.empty:
        st.warning("No data found for the selected date range.")
        return

    # Summary statistics
    total_revenue_current = df_filtered[(df_filtered['type'] == '수입') & (df_filtered['year'] == current_year)]['amount'].sum()
    total_costs_current = df_filtered[(df_filtered['type'] == '지출') & (df_filtered['year'] == current_year)]['amount'].sum()
    net_balance_current = total_revenue_current - total_costs_current
    
    total_revenue_last = df_filtered[(df_filtered['type'] == '수입') & (df_filtered['year'] == last_year)]['amount'].sum()
    total_costs_last = df_filtered[(df_filtered['type'] == '지출') & (df_filtered['year'] == last_year)]['amount'].sum()
    net_balance_last = total_revenue_last - total_costs_last
    
    col1, col2, col3 = st.columns(3)
    col1.metric("총 수입", f"${total_revenue_current:,.2f}", f"${total_revenue_current - total_revenue_last:,.2f}")
    col2.metric("총 지출", f"${total_costs_current:,.2f}", f"${total_costs_current - total_costs_last:,.2f}")
    col3.metric("총 잔액", f"${net_balance_current:,.2f}", f"${net_balance_current - net_balance_last:,.2f}")

    # Year-over-Year Comparison
    st.subheader("연간 비교")
    yearly_totals = df_filtered.groupby(['year', 'event'])['amount'].sum().reset_index()
    color_map = {2023: '#1f77b4', 2024: '#ff7f0e'}
    
    yoy_chart = px.bar(yearly_totals, x='event', y='amount', color='year',
                       title='Year-over-Year Comparison',
                       labels={'amount': '금액', 'event': '이벤트', 'year': '연도'},
                       barmode='group',
                       color_discrete_map=color_map)
    
    yoy_chart.update_layout(
        bargap=0.2,
        bargroupgap=0.1,
        xaxis={'categoryorder':'total descending'}
    )

    # Add labels above the bars
    for i, row in yearly_totals.iterrows():
        yoy_chart.add_annotation(
            x=row['event'],
            y=row['amount'],
            text=f"${row['amount']:,.2f}",
            showarrow=False,
            yshift=10,
            font=dict(size=9),
            xanchor='center',
            yanchor='bottom'
        )

    yoy_chart.update_layout(
        yaxis=dict(
            range=[0, yearly_totals['amount'].max() * 1.2]
        ),
        barmode='group',
        legend_title_text='Year'
    )

    st.plotly_chart(yoy_chart, use_container_width=True)

    # Monthly summary chart
    st.subheader("월별 요약")
    
    # Multiselect for events
    selected_events = st.multiselect("이벤트 선택", df_filtered['event'].unique(), default=df_filtered['event'].unique())
    
    # Filter by selected events
    df_filtered_events = df_filtered[df_filtered['event'].isin(selected_events)]
    
    monthly_summary = df_filtered_events.groupby([df_filtered_events['date'].dt.to_period('M'), 'subcategory'])['amount'].sum().unstack(fill_value=0)
    monthly_summary_reset = monthly_summary.reset_index()
    monthly_summary_melted = monthly_summary_reset.melt(id_vars='date', var_name='subcategory', value_name='amount')
    monthly_summary_melted['date'] = monthly_summary_melted['date'].dt.to_timestamp()

    # Create chart
    fig = px.bar(monthly_summary_melted, x='date', y='amount', color='subcategory',
                 title='Monthly Summary by Subcategory',
                 labels={'date': '월', 'amount': '금액', 'subcategory': '하위 카테고리'})
    
    fig.update_layout(barmode='stack', xaxis_tickformat='%Y-%m')
    st.plotly_chart(fig, use_container_width=True)

    # Cumulative Expenses by Subcategories
    st.subheader("누적 지출 (하위 카테고리별)")
    selected_years = st.multiselect("연도 선택", [2023, 2024], default=[2023, 2024])
    df_expenses = df_filtered[(df_filtered['type'] == '지출') & (df_filtered['year'].isin(selected_years))]

    if not df_expenses.empty:
        df_expenses = df_expenses.sort_values('date')
        df_cumulative = df_expenses.groupby(['date', 'subcategory'])['amount'].sum().unstack(fill_value=0).cumsum()

        fig_cumulative = px.line(df_cumulative, x=df_cumulative.index, y=df_cumulative.columns,
                                 title='Cumulative Expenses by Subcategory',
                                 labels={'value': '누적 금액', 'date': '날짜', 'variable': '하위 카테고리'})
        fig_cumulative.update_layout(legend_title_text='하위 카테고리')
        st.plotly_chart(fig_cumulative, use_container_width=True)
    else:
        st.write("선택한 기간에 대한 지출 데이터가 없습니다.")

# Detailed transaction list
    st.subheader("거래 목록")
    
    # Filters for events and subcategories
    events = df_filtered['event'].unique().tolist()
    subcategories = df_filtered['subcategory'].unique().tolist()
    events.insert(0, "All Events")
    subcategories.insert(0, "All Subcategories")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_event = st.selectbox("이벤트 선택", events)
    with col2:
        selected_subcategory = st.selectbox("하위 카테고리 선택", subcategories)
    with col3:
        start_date = st.date_input("시작 날짜", min(df_filtered['date']))
    with col4:
        end_date = st.date_input("종료 날짜", max(df_filtered['date']))
    
    # Filter based on selections
    df_display = df_filtered
    if selected_event != "All Events":
        df_display = df_display[df_display['event'] == selected_event]
    if selected_subcategory != "All Subcategories":
        df_display = df_display[df_display['subcategory'] == selected_subcategory]
    df_display = df_display[(df_display['date'] >= pd.Timestamp(start_date)) & (df_display['date'] <= pd.Timestamp(end_date))]

    columns_to_display = ['date', 'year', 'type', 'event', 'subcategory', 'description', 'amount']
    st.dataframe(df_display[columns_to_display])

    # Show total amount
    total_amount = df_display['amount'].sum()
    st.write(f"총액: ₩{total_amount:,.0f}")
    
    # Export to CSV
    if st.button("데이터를 CSV로 내보내기"):
        csv = df_filtered.to_csv(index=False)
        st.download_button(label="CSV 다운로드", data=csv, file_name="financial_report.csv", mime="text/csv")

if __name__ == "__main__":
    reports_page()
