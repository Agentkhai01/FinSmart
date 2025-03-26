import streamlit as st
import pandas as pd
from datetime import datetime
import data_visualization

def show_expense_tracker():
    st.header("Expense Tracker")
    
    # Create tabs for adding expenses and viewing history
    tab1, tab2 = st.tabs(["Add Expense", "Expense History"])
    
    with tab1:
        st.subheader("Record a New Expense")
        
        # Expense input form
        with st.form(key="expense_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Date", datetime.now().date())
                amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
            
            with col2:
                categories = [
                    "Food & Drinks", "Groceries", "Transportation", 
                    "Entertainment", "Shopping", "Bills & Utilities",
                    "Education", "Housing & Rent", "Health", "Other"
                ]
                category = st.selectbox("Category", categories)
                description = st.text_input("Description (Optional)")
            
            submit_button = st.form_submit_button(label="Add Expense")
            
            if submit_button:
                # Add the expense to the session state
                new_expense = pd.DataFrame({
                    'date': [date],
                    'amount': [amount],
                    'category': [category],
                    'description': [description]
                })
                
                # Append to existing expenses
                st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], 
                                                     ignore_index=True)
                
                st.success("Expense added successfully!")
                
        # Quick expense summary
        if not st.session_state.expenses.empty:
            st.subheader("Recent Expenses")
            recent_expenses = st.session_state.expenses.sort_values(
                by='date', ascending=False).head(3)
            
            for _, expense in recent_expenses.iterrows():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.write(f"**₹{expense['amount']:.2f}**")
                with col2:
                    st.write(f"{expense['category']} • {expense['date']}")
                    if expense['description']:
                        st.write(f"*{expense['description']}*")
    
    with tab2:
        st.subheader("Expense History")
        
        if st.session_state.expenses.empty:
            st.info("No expenses recorded yet. Start by adding your first expense!")
        else:
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                # Date range filter
                date_filter = st.radio(
                    "Filter by date",
                    ["All time", "This month", "Last 7 days", "Custom"]
                )
                
                if date_filter == "Custom":
                    start_date = st.date_input("Start date", 
                                               datetime.now().date() - pd.Timedelta(days=30))
                    end_date = st.date_input("End date", datetime.now().date())
            
            with col2:
                # Category filter
                all_categories = st.session_state.expenses['category'].unique().tolist()
                selected_categories = st.multiselect(
                    "Filter by category",
                    options=all_categories,
                    default=all_categories
                )
            
            # Apply filters
            filtered_expenses = st.session_state.expenses.copy()
            
            # Apply date filter
            if date_filter == "This month":
                current_month = datetime.now().month
                current_year = datetime.now().year
                filtered_expenses = filtered_expenses[
                    (pd.to_datetime(filtered_expenses['date']).dt.month == current_month) &
                    (pd.to_datetime(filtered_expenses['date']).dt.year == current_year)
                ]
            elif date_filter == "Last 7 days":
                last_week = datetime.now().date() - pd.Timedelta(days=7)
                filtered_expenses = filtered_expenses[
                    pd.to_datetime(filtered_expenses['date']).dt.date >= last_week
                ]
            elif date_filter == "Custom":
                filtered_expenses = filtered_expenses[
                    (pd.to_datetime(filtered_expenses['date']).dt.date >= start_date) &
                    (pd.to_datetime(filtered_expenses['date']).dt.date <= end_date)
                ]
            
            # Apply category filter
            if selected_categories:
                filtered_expenses = filtered_expenses[
                    filtered_expenses['category'].isin(selected_categories)
                ]
            
            # Display filtered data
            if filtered_expenses.empty:
                st.info("No expenses match your filters.")
            else:
                # Display summary statistics
                total_filtered = filtered_expenses['amount'].sum()
                st.write(f"Total: **₹{total_filtered:.2f}**")
                
                # Display expense breakdown
                st.subheader("Expense Breakdown")
                data_visualization.plot_expense_by_category(filtered_expenses)
                
                # Display expense table
                st.subheader("Expense Details")
                # Sort by date (most recent first)
                display_df = filtered_expenses.sort_values(by='date', ascending=False)
                # Format for display
                display_df = display_df.copy()
                display_df['amount'] = display_df['amount'].apply(lambda x: f"₹{x:.2f}")
                display_df = display_df.rename(columns={
                    'date': 'Date',
                    'amount': 'Amount',
                    'category': 'Category',
                    'description': 'Description'
                })
                st.dataframe(display_df, use_container_width=True)
            
            # Export option
            if st.button("Export expense data as CSV"):
                csv = filtered_expenses.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="my_expenses.csv",
                    mime="text/csv"
                )
