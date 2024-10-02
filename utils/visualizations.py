import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_monthly_summary_chart(df):
    df['year_month'] = df['date'].dt.to_period('M')
    monthly_summary = df.groupby(['year_month','year','type'])['amount'].sum().unstack(fill_value=0).reset_index()
    monthly_summary['year_month'] = monthly_summary['year_month'].dt.to_timestamp()

    if 'Revenue' not in monthly_summary.columns:
        monthly_summary['Revenue'] = 0
    if 'Cost' not in monthly_summary.columns:
        monthly_summary['Cost'] = 0

    monthly_summary['Net'] = monthly_summary['Revenue'] - monthly_summary['Cost']
                  
    fig = go.Figure()

    for year in monthly_summary['year'].unique():
        year_data = monthly_summary[monthly_summary['year'] == year]

        fig.add_trace(go.Bar(  # Changed from go.bar to go.Bar
            x=year_data['year_month'],
            y=year_data['Revenue'],
            name=f'Revenue {year}',
            marker_color='green' if year == max(monthly_summary['year']) else 'lightgreen'
        ))

        fig.add_trace(go.Bar(  # Changed from go.bar to go.Bar
            x=year_data['year_month'],
            y=year_data['Cost'],
            name=f'Cost {year}',
            marker_color='red' if year == max(monthly_summary['year']) else 'lightcoral'
        ))

        fig.add_trace(go.Scatter(
            x=year_data['year_month'],
            y=year_data['Net'],
            name=f'Net Balance {year}',
            mode='lines+markers',
            line=dict(color='blue' if year == max(monthly_summary['year']) else 'lightblue', width=2),  # Fixed typo 'witdth' to 'width'
        ))

    fig.update_layout(
        title='Monthly Financial Summary',
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        barmode='group',
        legend=dict(x=0, y=1.1, orientation='h'),
        margin=dict(l=50,r=50,t=80,b=50),
    )

    fig.update_xaxes(tickformat='%Y-%m')

    return fig

## Revenue Trend is not needed hence not created
def create_revenue_trend_chart(df_revenue):
    fig = px.line(df_revenue, x='date', y='amount', color='year', title='Revenue Trend')
    fig.update_layout(xaxis_title='Date', yaxis_title='Amount ($)')
    fig.update_xaxes(tickformat='%Y-%m-%d')
    return fig


def create_cost_trend_chart(df_costs):
    if 'category' not in df_costs.columns:
        fig = px.line(df_costs, x='date', y='amount', color='type',line_dash='year',title='Cost Trend')
    else:
        fig = px.line(df_costs, x='date', y='amount', color='category',line_dash='year',title='Cost Trend by Category')
                      
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Amount ($)')
    fig.update_xaxes(tickformat='%Y-%m')
    return fig
    
def create_cumulative_balance_chart(df):
    df_sorted = df.sort_values('date')
    df_sorted['cumulative_balance'] = df_sorted.apply(lambda row: row['amount'] if row['type'] == 'Revenue' else -row['amount'], axis=1).cumsum()

    fig = px.line(df_sorted, x='date', y='cumulative_balance', color='year', title='Cumulative Balance Over Time')
    fig.update_layout(xaxis_title='Date', yaxis_title='Cumulative Balance ($)')
    fig.update_xaxes(tickformat='%Y-%m-%d')
    return fig

def create_year_over_year_comparison_chart(df):
    df['month'] = df['date'].dt.month
    yearly_comparison = df.groupby(['year', 'month', 'type'])['amount'].sum().unstack(fill_value=0).reset_index()
    
    # Ensure 'Revenue' and 'Cost' columns exist
    if 'Revenue' not in yearly_comparison.columns:
        yearly_comparison['Revenue'] = 0
    if 'Cost' not in yearly_comparison.columns:
        yearly_comparison['Cost'] = 0
    
    yearly_comparison['Net'] = yearly_comparison['Revenue'] - yearly_comparison['Cost']

    fig = go.Figure()

    for year in yearly_comparison['year'].unique():
        year_data = yearly_comparison[yearly_comparison['year'] == year]
        
        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data['Revenue'],
            name=f'Revenue {year}',
            mode='lines+markers',
            line=dict(color='green' if year == max(yearly_comparison['year']) else 'lightgreen')
        ))

        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data['Cost'],
            name=f'Cost {year}',
            mode='lines+markers',
            line=dict(color='red' if year == max(yearly_comparison['year']) else 'lightcoral')
        ))

        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data['Net'],
            name=f'Net Balance {year}',
            mode='lines+markers',
            line=dict(color='blue' if year == max(yearly_comparison['year']) else 'lightblue')
        ))

    fig.update_layout(
        title='Year-over-Year Comparison',
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        legend=dict(x=0, y=1.1, orientation='h'),
        margin=dict(l=50, r=50, t=80, b=50),
    )

    fig.update_xaxes(tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

    return fig
