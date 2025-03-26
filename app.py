import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import expense_tracker
import budget_manager
import investment_calculator
import data_visualization
import utils

# Page configuration
st.set_page_config(
    page_title="Fin Smart: Student Finance Manager",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for data persistence
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=[
        'date', 'amount', 'category', 'description'
    ])

if 'budgets' not in st.session_state:
    st.session_state.budgets = {}

# Main application header
st.title("Fin Smart: Self Finance Management Platform")
st.subheader("Your personal finance companion for college life")

# Navigation sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a feature:",
    ["Dashboard", "Expense Tracker", "Budget Manager", "Investment Calculator", "Spending Planner"]
)

# Render the selected page
if page == "Dashboard":
    st.header("Finance Dashboard")
    
    # Display summary statistics
    if not st.session_state.expenses.empty:
        col1, col2, col3 = st.columns(3)
        
        # Calculate total expenses
        total_expenses = st.session_state.expenses['amount'].sum()
        col1.metric("Total Expenses", f"₹{total_expenses:.2f}")
        
        # Calculate expenses this month
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_expenses = st.session_state.expenses[
            (pd.to_datetime(st.session_state.expenses['date']).dt.month == current_month) &
            (pd.to_datetime(st.session_state.expenses['date']).dt.year == current_year)
        ]['amount'].sum()
        col2.metric("This Month", f"₹{monthly_expenses:.2f}")
        
        # Calculate today's expenses
        today = datetime.now().date()
        today_expenses = st.session_state.expenses[
            pd.to_datetime(st.session_state.expenses['date']).dt.date == today
        ]['amount'].sum()
        col3.metric("Today", f"₹{today_expenses:.2f}")
        
        # Display budget vs actual
        st.subheader("Budget vs. Actual Spending")
        if st.session_state.budgets:
            data_visualization.plot_budget_vs_actual()
        else:
            st.info("Set up your budgets in the Budget Manager to see comparisons here.")
        
        # Display expense breakdown by category
        st.subheader("Expense Breakdown by Category")
        data_visualization.plot_expense_by_category()
        
        # Display recent expense history
        st.subheader("Recent Expenses")
        st.dataframe(
            st.session_state.expenses.sort_values(by='date', ascending=False).head(5),
            use_container_width=True
        )
    else:
        st.info("Start tracking your expenses to see your financial summary here!")
        st.write("Use the navigation sidebar to access different features of Fin Smart.")

elif page == "Expense Tracker":
    expense_tracker.show_expense_tracker()

elif page == "Budget Manager":
    budget_manager.show_budget_manager()

elif page == "Investment Calculator":
    investment_calculator.show_investment_calculator()

elif page == "Spending Planner":
    st.header("Weekly Spending Planner")
    
    pocket_money = st.number_input("Enter your weekly pocket money (₹)", 
                                   min_value=0.0, 
                                   value=1000.0, 
                                   step=100.0)
    
    st.subheader("Recommended Daily Spending Limits")
    
    # Calculate daily spending allowance
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Default distribution: equal allocation
    default_distribution = [1/7] * 7
    
    # Custom distribution option
    custom_dist = st.checkbox("Set custom distribution?")
    
    if custom_dist:
        st.write("Adjust the percentage allocation for each day (must sum to 100%)")
        
        # Initialize percentages in session state if not already present
        if 'day_percentages' not in st.session_state:
            st.session_state.day_percentages = [14.3, 14.3, 14.3, 14.3, 14.3, 14.3, 14.2]
        
        # Collect user inputs for percentages
        percentages = []
        cols = st.columns(7)
        total_percentage = 0
        
        for i, day in enumerate(days_of_week):
            with cols[i]:
                pct = st.number_input(day, min_value=0.0, max_value=100.0, 
                                      value=st.session_state.day_percentages[i],
                                      step=0.1, key=f"pct_{day}")
                percentages.append(pct)
                total_percentage += pct
        
        # Store the new percentages
        st.session_state.day_percentages = percentages
        
        # Validate that percentages sum to 100
        if abs(total_percentage - 100.0) > 0.1:  # Allow small floating point error
            st.error(f"Total percentage must be 100%. Current total: {total_percentage:.1f}%")
            distribution = default_distribution
        else:
            distribution = [p/100 for p in percentages]
    else:
        distribution = default_distribution
    
    # Calculate and display the daily allowances
    daily_amounts = [pocket_money * dist for dist in distribution]
    
    # Create a DataFrame for the spending plan
    spending_plan = pd.DataFrame({
        'Day': days_of_week,
        'Percentage': [f"{dist*100:.1f}%" for dist in distribution],
        'Amount (₹)': [f"₹{amt:.2f}" for amt in daily_amounts]
    })
    
    st.dataframe(spending_plan, use_container_width=True)
    
    # Visualization of the spending plan
    st.subheader("Visual Spending Plan")
    data_visualization.plot_spending_plan(days_of_week, daily_amounts)
    
    # Tips for daily spending management
    with st.expander("Tips for managing your daily spending"):
        st.write("""
        - Save a small percentage of your daily allowance for unexpected expenses
        - Avoid borrowing from tomorrow's budget unless absolutely necessary
        - Consider saving unused money at the end of each day for special purchases
        - Use cash instead of digital payments to make spending more tangible
        - Keep track of your daily expenses to see where your money is going
        """)

# Footer
st.markdown("---")
st.markdown(
    "Fin Smart: Helping Indian students manage their finances smartly. "
    "© 2023 Fin Smart"
)
