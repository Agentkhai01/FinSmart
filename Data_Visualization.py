import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def plot_expense_by_category(expenses_df=None):
    """
    Plot a pie chart showing expenses by category
    
    Parameters:
    - expenses_df: DataFrame containing expense data (optional)
                   If not provided, uses the data from session state
    """
    # If no DataFrame is provided, use the one from session state
    if expenses_df is None:
        if st.session_state.expenses.empty:
            st.info("No expense data available for visualization.")
            return
        expenses_df = st.session_state.expenses.copy()
    
    if expenses_df.empty:
        st.info("No expenses match your current filters.")
        return
    
    # Group expenses by category
    category_totals = expenses_df.groupby('category')['amount'].sum().reset_index()
    
    # Create pie chart
    fig = px.pie(
        category_totals,
        values='amount',
        names='category',
        title='Expenses by Category',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Update layout
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        height=400
    )
    
    # Add rupee symbol and formatting to hover text
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>₹%{value:.2f}<br>%{percent}'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Also display as a bar chart for better comparison
    fig2 = px.bar(
        category_totals.sort_values('amount', ascending=False),
        x='category',
        y='amount',
        title='Expense Amount by Category',
        labels={'amount': 'Amount (₹)', 'category': 'Category'},
        color='category',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Format y-axis to show rupee symbol
    fig2.update_layout(
        yaxis=dict(tickprefix="₹"),
        height=400
    )
    
    st.plotly_chart(fig2, use_container_width=True)

def plot_expense_over_time(expenses_df=None, period='daily'):
    """
    Plot expenses over time as a line chart
    
    Parameters:
    - expenses_df: DataFrame containing expense data (optional)
    - period: 'daily', 'weekly', or 'monthly'
    """
    # If no DataFrame is provided, use the one from session state
    if expenses_df is None:
        if st.session_state.expenses.empty:
            st.info("No expense data available for visualization.")
            return
        expenses_df = st.session_state.expenses.copy()
    
    if expenses_df.empty:
        st.info("No expenses match your current filters.")
        return
    
    # Convert date to datetime if it's not already
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    
    # Group by the selected period
    if period == 'daily':
        expenses_df['period'] = expenses_df['date'].dt.date
        title = 'Daily Expenses Over Time'
        x_title = 'Date'
    elif period == 'weekly':
        expenses_df['period'] = expenses_df['date'].dt.isocalendar().week
        expenses_df['year'] = expenses_df['date'].dt.isocalendar().year
        expenses_df['period'] = expenses_df['year'].astype(str) + '-W' + expenses_df['period'].astype(str)
        title = 'Weekly Expenses Over Time'
        x_title = 'Week'
    elif period == 'monthly':
        expenses_df['period'] = expenses_df['date'].dt.strftime('%Y-%m')
        title = 'Monthly Expenses Over Time'
        x_title = 'Month'
    
    # Group by period and calculate total
    period_totals = expenses_df.groupby('period')['amount'].sum().reset_index()
    
    # Create line chart
    fig = px.line(
        period_totals,
        x='period',
        y='amount',
        title=title,
        labels={'amount': 'Total Amount (₹)', 'period': x_title},
        markers=True
    )
    
    # Add dots for each data point
    fig.update_traces(mode='lines+markers')
    
    # Format y-axis to show rupee symbol
    fig.update_layout(
        yaxis=dict(tickprefix="₹"),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_budget_vs_actual():
    """Plot a comparison of budgeted amounts vs actual spending by category"""
    # Return early if no data is available
    if st.session_state.expenses.empty or not st.session_state.budgets:
        st.info("Both expense data and budget settings are needed for this visualization.")
        return
    
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Filter expenses for the current month
    monthly_expenses = st.session_state.expenses[
        (pd.to_datetime(st.session_state.expenses['date']).dt.month == current_month) &
        (pd.to_datetime(st.session_state.expenses['date']).dt.year == current_year)
    ]
    
    # Get category totals
    category_expenses = monthly_expenses.groupby('category')['amount'].sum().to_dict()
    
    # Prepare data for the chart
    categories = []
    budget_amounts = []
    actual_amounts = []
    
    for category, budget in st.session_state.budgets.items():
        if budget > 0:  # Only include categories with a budget
            categories.append(category)
            budget_amounts.append(budget)
            actual_amounts.append(category_expenses.get(category, 0))
    
    # Create DataFrame for plotting
    comparison_df = pd.DataFrame({
        'Category': categories,
        'Budget': budget_amounts,
        'Actual': actual_amounts
    })
    
    # Sort by budget amount (descending)
    comparison_df = comparison_df.sort_values('Budget', ascending=False)
    
    # Create bar chart
    fig = go.Figure()
    
    # Add budget bars
    fig.add_trace(go.Bar(
        x=comparison_df['Category'],
        y=comparison_df['Budget'],
        name='Budget',
        marker_color='blue',
        opacity=0.7
    ))
    
    # Add actual expense bars
    fig.add_trace(go.Bar(
        x=comparison_df['Category'],
        y=comparison_df['Actual'],
        name='Actual Spending',
        marker_color='red',
        opacity=0.7
    ))
    
    # Update layout
    fig.update_layout(
        title=f"Budget vs. Actual Spending ({datetime.now().strftime('%B %Y')})",
        xaxis_title="Category",
        yaxis_title="Amount (₹)",
        yaxis=dict(tickprefix="₹"),
        barmode='group',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_budget_allocation(budgets):
    """Plot a pie chart showing budget allocation across categories"""
    # Convert budget dictionary to DataFrame
    budget_df = pd.DataFrame({
        'Category': list(budgets.keys()),
        'Amount': list(budgets.values())
    })
    
    # Create pie chart
    fig = px.pie(
        budget_df,
        values='Amount',
        names='Category',
        title='Budget Allocation by Category',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Update layout
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        height=400
    )
    
    # Add rupee symbol and formatting to hover text
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>₹%{value:.2f}<br>%{percent}'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_spending_plan(days, amounts):
    """Plot a bar chart showing the daily spending plan"""
    # Create DataFrame for plotting
    plan_df = pd.DataFrame({
        'Day': days,
        'Amount': amounts
    })
    
    # Create bar chart
    fig = px.bar(
        plan_df,
        x='Day',
        y='Amount',
        title='Daily Spending Plan',
        labels={'Amount': 'Amount (₹)', 'Day': 'Day of Week'},
        color='Day',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Format y-axis to show rupee symbol
    fig.update_layout(
        yaxis=dict(tickprefix="₹"),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
