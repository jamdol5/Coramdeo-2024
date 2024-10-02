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

data_manager = DataManager()

def reports_page():
    st.title("예산 보고서")
    
    current_year = datetime.now().year
    last_year = current_year - 1

    revenues_current = data_manager.get_revenues(current_year)
    costs_current = data_manager.get_costs(current_year)
    revenues_last = data_manager.get_revenues(last_year)
    costs_last = data_manager.get_costs(last_year)
    
    # Prepare data for reports
    df_revenue_current = pd.DataFrame(revenues_current)
    if not df_revenue_current.empty:
        df_revenue_current['date'] = pd.to_datetime(df_revenue_current['date'])
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
        df_costs_current['date'] = pd.to_datetime(df_costs_current['date'])
        df_costs_current['type'] = '지출'
        df_costs_current['year'] = current_year
    
    df_revenue_last = pd.DataFrame(revenues_last)
    if not df_revenue_last.empty:
        df_revenue_last['date'] = pd.to_datetime(df_revenue_last['date'])
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
        df_costs_last['date'] = pd.to_datetime(df_costs_last['date'])
        df_costs_last['type'] = '지출'
        df_costs_last['year'] = last_year
    
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
    # Group by year and event, then sum the amounts
    yearly_totals = df_filtered.groupby(['year', 'event'])['amount'].sum().reset_index()
    
    # Define colors for 2023 and 2024
    color_map = {2023: '#1f77b4', 2024: '#ff7f0e'}
    
    # Create the chart
    yoy_chart = px.bar(yearly_totals, x='event', y='amount', color='year',
                       title='Year-over-Year Comparison',
                       labels={'amount': '금액', 'event': '이벤트', 'year': '연도'},
                       barmode='group',
                       color_discrete_map=color_map)
    
    # Customize the chart
    yoy_chart.update_layout(
        bargap=0.2,  # Increase gap between event groups
        bargroupgap=0.1,  # Increase gap between bars within a group
        xaxis={'categoryorder':'total descending'}  # Sort events by total amount
    )

    # Add total labels above the bars
    for i, row in yearly_totals.iterrows():
        yoy_chart.add_annotation(
            x=row['event'],
            y=row['amount'],
            text=f"${row['amount']:,.2f}",
            showarrow=False,
            yshift=10,  # Adjust yshift to position label just above the bar
            font=dict(size=9),
            xanchor='center',
            yanchor='bottom'
        )

    # Update bar positions and adjust y-axis to accommodate labels
    yoy_chart.update_traces(
        offsetgroup='year',
    )
    yoy_chart.update_layout(
        yaxis=dict(
            range=[0, yearly_totals['amount'].max() * 1.2]  # Extend y-axis range by 20% to accommodate labels
        ),
        barmode='group',  # Ensure bars are grouped by event
        legend_title_text='Year'
    )

    st.plotly_chart(yoy_chart, use_container_width=True)

    # Monthly summary chart
    st.subheader("월별 요약")
    
    # Create a multiselect for events
    selected_events = st.multiselect("이벤트 선택", df_filtered['event'].unique(), default=df_filtered['event'].unique())
    
    # Filter the data based on selected events
    df_filtered_events = df_filtered[df_filtered['event'].isin(selected_events)]
    
    # Group by month and subcategory, then sum the amounts
    monthly_summary = df_filtered_events.groupby([df_filtered_events['date'].dt.to_period('M'), 'subcategory'])['amount'].sum().unstack(fill_value=0)
    
    # Reset index to make 'date' a column
    monthly_summary_reset = monthly_summary.reset_index()
    
    # Melt the dataframe to long format
    monthly_summary_melted = monthly_summary_reset.melt(id_vars='date', var_name='subcategory', value_name='amount')
    
    # Convert Period to datetime for proper plotting
    monthly_summary_melted['date'] = monthly_summary_melted['date'].dt.to_timestamp()
    
    # Create the chart
    fig = px.bar(monthly_summary_melted,
                 x='date',
                 y='amount',
                 color='subcategory',
                 title='Monthly Summary by Subcategory',
                 labels={'date': '월', 'amount': '금액', 'subcategory': '하위 카테고리'})
    
    # Customize the chart
    fig.update_layout(barmode='stack', xaxis_tickformat='%Y-%m')
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    # Cumulative Expenses by Subcategories
    st.subheader("누적 지출 (하위 카테고리별)")
    
    # Year selection
    selected_years = st.multiselect("연도 선택", [2023, 2024], default=[2023, 2024])
    
    # Filter data for selected years and expenses only
    df_expenses = df_filtered[(df_filtered['type'] == '지출') & (df_filtered['year'].isin(selected_years))]
    
    if not df_expenses.empty:
        # Sort data by date
        df_expenses = df_expenses.sort_values('date')
        
        # Calculate cumulative sum for each subcategory
        df_cumulative = df_expenses.groupby(['date', 'subcategory'])['amount'].sum().unstack(fill_value=0).cumsum()
        
        # Create the cumulative expenses chart
        fig_cumulative = px.line(df_cumulative, x=df_cumulative.index, y=df_cumulative.columns,
                                 title='Cumulative Expenses by Subcategory',
                                 labels={'value': '누적 금액', 'date': '날짜', 'variable': '하위 카테고리'})
        
        fig_cumulative.update_layout(legend_title_text='하위 카테고리')
        
        st.plotly_chart(fig_cumulative, use_container_width=True)
    else:
        st.write("선택한 기간에 대한 지출 데이터가 없습니다.")
    
    # Cost breakdown by event and subcategory
    st.subheader("지출 분석")
    df_costs = df_filtered[df_filtered['type'] == '지출']
    if not df_costs.empty:
        # Year selection
        available_years = sorted(df_costs['year'].unique())
        selected_years = st.multiselect("연도 선택", available_years, default=available_years, key="cost_breakdown_years")
        
        df_costs_filtered = df_costs[df_costs['year'].isin(selected_years)]
        
        # Group data
        df_cost_breakdown = df_costs_filtered.groupby(['year', 'event', 'subcategory'])['amount'].sum().reset_index()
        
        # Create a treemap
        fig_cost_breakdown = px.treemap(
            df_cost_breakdown,
            path=['year', 'event', 'subcategory'],
            values='amount',
            title='지출 분석: 연도, 이벤트, 하위 카테고리별',
            color='amount',
            color_continuous_scale='RdYlBu_r',
            hover_data=['amount']
        )
        
        fig_cost_breakdown.update_traces(
            textinfo='label+value',
            hovertemplate='<b>%{label}</b><br>금액: ₩%{value:,.0f}'
        )
        
        fig_cost_breakdown.update_layout(
            height=600,
            coloraxis_colorbar=dict(title='금액')
        )
        
        st.plotly_chart(fig_cost_breakdown, use_container_width=True)
        
        # Bar chart for top subcategories
        st.subheader("상위 지출 하위 카테고리")
        top_n = st.slider("표시할 상위 카테고리 수", min_value=5, max_value=20, value=10, key="top_subcategories_slider")
        
        df_top_subcategories = df_costs_filtered.groupby('subcategory')['amount'].sum().nlargest(top_n).reset_index()
        
        fig_top_subcategories = px.bar(
            df_top_subcategories,
            x='subcategory',
            y='amount',
            title=f'상위 {top_n} 지출 하위 카테고리',
            labels={'subcategory': '하위 카테고리', 'amount': '총 금액'},
            color='amount',
            color_continuous_scale='Viridis'
        )
        
        fig_top_subcategories.update_layout(xaxis_tickangle=-45)
        
        st.plotly_chart(fig_top_subcategories, use_container_width=True)
    else:
        st.write("선택한 기간에 대한 지출 데이터가 없습니다.")

# Detailed transaction list
    st.subheader("거래 목록")
    
    # Get unique events and subcategories from the filtered dataframe
    events = df_filtered['event'].unique().tolist()
    subcategories = df_filtered['subcategory'].unique().tolist()
    
    # Add an "All Events" and "All Subcategories" option at the beginning of the lists
    events.insert(0, "All Events")
    subcategories.insert(0, "All Subcategories")
    
    # Create selectboxes for event and subcategory selection
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_event = st.selectbox("이벤트 선택", events)
    with col2:
        selected_subcategory = st.selectbox("하위 카테고리 선택", subcategories)
    with col3:
        start_date = st.date_input("시작 날짜", min(df_filtered['date']))
    with col4:
        end_date = st.date_input("종료 날짜", max(df_filtered['date']))
    
    # Filter the dataframe based on the selected event, subcategory, and date range
    df_display = df_filtered
    if selected_event != "All Events":
        df_display = df_display[df_display['event'] == selected_event]
    if selected_subcategory != "All Subcategories":
        df_display = df_display[df_display['subcategory'] == selected_subcategory]
    df_display = df_display[(df_display['date'] >= pd.Timestamp(start_date)) & 
                            (df_display['date'] <= pd.Timestamp(end_date))]
    
    columns_to_display = ['date', 'year', 'type', 'event', 'subcategory', 'description', 'amount']
    st.dataframe(df_display[columns_to_display])
    
    # Display total amount
    total_amount = df_display['amount'].sum()
    st.write(f"총액: ₩{total_amount:,.0f}")
        
    # Export data
    if st.button("데이터를 CSV로 내보내기"):
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="CSV 다운로드",
            data=csv,
            file_name="financial_report.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    reports_page()
