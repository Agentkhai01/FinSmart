import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

def get_month_name(month_number):
    """
    Convert month number to month name
    
    Parameters:
    - month_number: Integer representing the month (1-12)
    
    Returns:
    - String with the month name
    """
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    if 1 <= month_number <= 12:
        return month_names[month_number - 1]
    else:
        return "Invalid Month"

def get_current_month_range():
    """
    Get the start and end dates for the current month
    
    Returns:
    - Tuple with (start_date, end_date) as datetime objects
    """
    today = datetime.now()
    start_date = datetime(today.year, today.month, 1)
    
    # Get the last day of the month
    if today.month == 12:
        end_date = datetime(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(today.year, today.month + 1, 1) - timedelta(days=1)
    
    return (start_date, end_date)

def get_week_range():
    """
    Get the start and end dates for the current week (Monday to Sunday)
    
    Returns:
    - Tuple with (start_date, end_date) as datetime objects
    """
    today = datetime.now()
    start_date = today - timedelta(days=today.weekday())  # Monday
    end_date = start_date + timedelta(days=6)  # Sunday
    
    return (start_date, end_date)

def calculate_spending_rate(expenses_df, budget_amount, period='month'):
    """
    Calculate how fast the budget is being spent
    
    Parameters:
    - expenses_df: DataFrame with expense data
    - budget_amount: Total budget amount
    - period: 'month' or 'week'
    
    Returns:
    - Dictionary with spending rate metrics
    """
    if expenses_df.empty or budget_amount <= 0:
        return {
            'spent_percent': 0,
            'days_elapsed_percent': 0,
            'remaining_days': 0,
            'daily_remaining': 0,
            'status': 'no_data'
        }
    
    # Convert dates to datetime
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    
    # Get appropriate date range
    if period == 'month':
        start_date, end_date = get_current_month_range()
        total_days = (end_date - start_date).days + 1
    else:  # week
        start_date, end_date = get_week_range()
        total_days = 7
    
    # Filter expenses for the period
    period_expenses = expenses_df[
        (expenses_df['date'] >= start_date) & 
        (expenses_df['date'] <= end_date)
    ]
    
    # Calculate metrics
    total_spent = period_expenses['amount'].sum()
    spent_percent = (total_spent / budget_amount) * 100
    
    # Days elapsed
    today = datetime.now()
    if today > end_date:
        days_elapsed = total_days
    else:
        days_elapsed = (today - start_date).days + 1
    
    days_elapsed_percent = (days_elapsed / total_days) * 100
    
    # Remaining days and daily budget
    remaining_days = total_days - days_elapsed
    remaining_budget = budget_amount - total_spent
    
    if remaining_days > 0:
        daily_remaining = remaining_budget / remaining_days
    else:
        daily_remaining = 0
    
    # Determine spending status
    if spent_percent > days_elapsed_percent + 10:
        status = 'overspending'
    elif spent_percent < days_elapsed_percent - 10:
        status = 'underspending'
    else:
        status = 'on_track'
    
    return {
        'spent_percent': spent_percent,
        'days_elapsed_percent': days_elapsed_percent,
        'remaining_days': remaining_days,
        'daily_remaining': daily_remaining,
        'status': status
    }

def format_currency(amount):
    """Format a number as Indian Rupees with the ₹ symbol"""
    return f"₹{amount:,.2f}"

def export_to_csv(df, filename="exported_data.csv"):
    """
    Convert a DataFrame to CSV for download
    
    Parameters:
    - df: DataFrame to export
    - filename: Name of the CSV file
    
    Returns:
    - CSV string for download
    """
    return df.to_csv(index=False).encode('utf-8')
