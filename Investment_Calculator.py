import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def calculate_sip_returns(monthly_investment, annual_return_rate, time_years):
    """
    Calculate returns for SIP investments
    
    Parameters:
    - monthly_investment: Amount invested each month
    - annual_return_rate: Expected annual return rate (in %)
    - time_years: Investment duration in years
    
    Returns:
    - DataFrame with monthly data on investment growth
    """
    # Convert annual return rate to monthly
    monthly_rate = (1 + annual_return_rate/100) ** (1/12) - 1
    
    # Total number of months
    total_months = time_years * 12
    
    # Initialize arrays
    total_investment = np.zeros(total_months)
    investment_value = np.zeros(total_months)
    
    # Calculate values for each month
    for month in range(total_months):
        if month == 0:
            total_investment[month] = monthly_investment
            investment_value[month] = monthly_investment
        else:
            # Add this month's investment
            total_investment[month] = total_investment[month-1] + monthly_investment
            
            # Calculate new value with returns
            investment_value[month] = (investment_value[month-1] * (1 + monthly_rate)) + monthly_investment
    
    # Create DataFrame
    result_df = pd.DataFrame({
        'Month': range(1, total_months + 1),
        'Total_Investment': total_investment,
        'Investment_Value': investment_value
    })
    
    return result_df

def calculate_lumpsum_returns(investment_amount, annual_return_rate, time_years):
    """
    Calculate returns for lumpsum investments
    
    Parameters:
    - investment_amount: Initial investment amount
    - annual_return_rate: Expected annual return rate (in %)
    - time_years: Investment duration in years
    
    Returns:
    - DataFrame with yearly data on investment growth
    """
    # Initialize arrays
    years = np.arange(0, time_years + 1)
    investment_value = np.zeros(len(years))
    
    # Calculate values for each year
    for i, year in enumerate(years):
        investment_value[i] = investment_amount * ((1 + annual_return_rate/100) ** year)
    
    # Create DataFrame
    result_df = pd.DataFrame({
        'Year': years,
        'Investment_Value': investment_value
    })
    
    return result_df

def show_investment_calculator():
    st.header("Investment Calculator")
    
    # Create tabs for different calculators
    tab1, tab2, tab3 = st.tabs(["SIP Calculator", "Lumpsum Calculator", "Investment Education"])
    
    with tab1:
        st.subheader("SIP (Systematic Investment Plan) Calculator")
        
        # Input form for SIP calculator
        with st.form(key="sip_calculator_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                monthly_investment = st.number_input(
                    "Monthly Investment Amount (₹)",
                    min_value=100,
                    value=1000,
                    step=100
                )
                
                annual_return_rate = st.slider(
                    "Expected Annual Return (%)",
                    min_value=1.0,
                    max_value=30.0,
                    value=12.0,
                    step=0.5
                )
            
            with col2:
                time_years = st.slider(
                    "Investment Duration (Years)",
                    min_value=1,
                    max_value=40,
                    value=10
                )
                
                inflation_rate = st.slider(
                    "Expected Inflation Rate (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=6.0,
                    step=0.5
                )
            
            calculate_button = st.form_submit_button("Calculate SIP Returns")
            
            if calculate_button:
                # Calculate returns
                sip_results = calculate_sip_returns(
                    monthly_investment, 
                    annual_return_rate, 
                    time_years
                )
                
                # Display summary results
                st.subheader("SIP Investment Summary")
                
                # Calculate key metrics
                total_invested = monthly_investment * time_years * 12
                final_value = sip_results['Investment_Value'].iloc[-1]
                wealth_gained = final_value - total_invested
                
                # Inflation-adjusted final value
                real_return_rate = (1 + annual_return_rate/100) / (1 + inflation_rate/100) - 1
                inflation_adj_final = monthly_investment * (((1 + real_return_rate) ** (time_years * 12) - 1) / real_return_rate) * (1 + real_return_rate)
                
                # Display metrics in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Amount Invested", f"₹{total_invested:,.2f}")
                
                with col2:
                    st.metric("Expected Final Value", f"₹{final_value:,.2f}")
                
                with col3:
                    st.metric("Wealth Gained", f"₹{wealth_gained:,.2f}", 
                             delta=f"{(wealth_gained/total_invested)*100:.1f}%")
                
                # Additional metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Inflation-Adjusted Value", f"₹{inflation_adj_final:,.2f}")
                
                with col2:
                    st.metric("Real Returns", f"{real_return_rate*100:.2f}%")
                
                # Visualize the growth
                st.subheader("Investment Growth Over Time")
                
                # Plot investment growth
                fig = go.Figure()
                
                # Add total investment line
                fig.add_trace(
                    go.Scatter(
                        x=sip_results['Month'],
                        y=sip_results['Total_Investment'],
                        name="Amount Invested",
                        line=dict(color="blue")
                    )
                )
                
                # Add investment value line
                fig.add_trace(
                    go.Scatter(
                        x=sip_results['Month'],
                        y=sip_results['Investment_Value'],
                        name="Investment Value",
                        line=dict(color="green")
                    )
                )
                
                # Add inflation-adjusted value line
                inflation_adj_values = []
                for month in range(1, time_years * 12 + 1):
                    inflation_factor = (1 + inflation_rate/100) ** (month/12)
                    inflation_adj_value = sip_results['Investment_Value'].iloc[month-1] / inflation_factor
                    inflation_adj_values.append(inflation_adj_value)
                
                fig.add_trace(
                    go.Scatter(
                        x=sip_results['Month'],
                        y=inflation_adj_values,
                        name="Inflation-Adjusted Value",
                        line=dict(color="red", dash="dash")
                    )
                )
                
                # Update layout
                fig.update_layout(
                    title="SIP Investment Growth Visualization",
                    xaxis_title="Months",
                    yaxis_title="Value (₹)",
                    legend=dict(x=0, y=1.1, orientation="h"),
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show data in tabular format
                with st.expander("View detailed growth data"):
                    yearly_data = sip_results[sip_results['Month'] % 12 == 0].copy()
                    yearly_data['Year'] = yearly_data['Month'] // 12
                    yearly_data = yearly_data[['Year', 'Total_Investment', 'Investment_Value']]
                    yearly_data['Wealth_Gained'] = yearly_data['Investment_Value'] - yearly_data['Total_Investment']
                    yearly_data['Returns_Percentage'] = (yearly_data['Wealth_Gained'] / yearly_data['Total_Investment'] * 100)
                    
                    # Format for display
                    display_df = yearly_data.copy()
                    display_df['Total_Investment'] = display_df['Total_Investment'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Investment_Value'] = display_df['Investment_Value'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Wealth_Gained'] = display_df['Wealth_Gained'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Returns_Percentage'] = display_df['Returns_Percentage'].apply(lambda x: f"{x:.2f}%")
                    
                    st.dataframe(display_df, use_container_width=True)
    
    with tab2:
        st.subheader("Lumpsum Investment Calculator")
        
        # Input form for lumpsum calculator
        with st.form(key="lumpsum_calculator_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                investment_amount = st.number_input(
                    "Investment Amount (₹)",
                    min_value=1000,
                    value=100000,
                    step=1000
                )
                
                annual_return_rate = st.slider(
                    "Expected Annual Return (%)",
                    min_value=1.0,
                    max_value=30.0,
                    value=12.0,
                    step=0.5,
                    key="lumpsum_return_rate"
                )
            
            with col2:
                time_years = st.slider(
                    "Investment Duration (Years)",
                    min_value=1,
                    max_value=40,
                    value=10,
                    key="lumpsum_time_years"
                )
                
                inflation_rate = st.slider(
                    "Expected Inflation Rate (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=6.0,
                    step=0.5,
                    key="lumpsum_inflation_rate"
                )
            
            calculate_button = st.form_submit_button("Calculate Lumpsum Returns")
            
            if calculate_button:
                # Calculate returns
                lumpsum_results = calculate_lumpsum_returns(
                    investment_amount, 
                    annual_return_rate, 
                    time_years
                )
                
                # Display summary results
                st.subheader("Lumpsum Investment Summary")
                
                # Calculate key metrics
                initial_investment = investment_amount
                final_value = lumpsum_results['Investment_Value'].iloc[-1]
                wealth_gained = final_value - initial_investment
                
                # Inflation-adjusted final value
                real_return_rate = (1 + annual_return_rate/100) / (1 + inflation_rate/100) - 1
                inflation_adj_final = initial_investment * ((1 + real_return_rate) ** time_years)
                
                # Display metrics in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Initial Investment", f"₹{initial_investment:,.2f}")
                
                with col2:
                    st.metric("Expected Final Value", f"₹{final_value:,.2f}")
                
                with col3:
                    st.metric("Wealth Gained", f"₹{wealth_gained:,.2f}", 
                             delta=f"{(wealth_gained/initial_investment)*100:.1f}%")
                
                # Additional metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Inflation-Adjusted Value", f"₹{inflation_adj_final:,.2f}")
                
                with col2:
                    st.metric("Real Annual Returns", f"{real_return_rate*100:.2f}%")
                
                # Visualize the growth
                st.subheader("Investment Growth Over Time")
                
                # Plot investment growth
                fig = go.Figure()
                
                # Add investment value line
                fig.add_trace(
                    go.Scatter(
                        x=lumpsum_results['Year'],
                        y=lumpsum_results['Investment_Value'],
                        name="Investment Value",
                        line=dict(color="green")
                    )
                )
                
                # Add initial investment line
                fig.add_trace(
                    go.Scatter(
                        x=lumpsum_results['Year'],
                        y=[initial_investment] * len(lumpsum_results),
                        name="Initial Investment",
                        line=dict(color="blue", dash="dash")
                    )
                )
                
                # Add inflation-adjusted value line
                inflation_adj_values = []
                for year in range(time_years + 1):
                    inflation_factor = (1 + inflation_rate/100) ** year
                    inflation_adj_value = lumpsum_results['Investment_Value'].iloc[year] / inflation_factor
                    inflation_adj_values.append(inflation_adj_value)
                
                fig.add_trace(
                    go.Scatter(
                        x=lumpsum_results['Year'],
                        y=inflation_adj_values,
                        name="Inflation-Adjusted Value",
                        line=dict(color="red", dash="dash")
                    )
                )
                
                # Update layout
                fig.update_layout(
                    title="Lumpsum Investment Growth Visualization",
                    xaxis_title="Years",
                    yaxis_title="Value (₹)",
                    legend=dict(x=0, y=1.1, orientation="h"),
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show data in tabular format
                with st.expander("View detailed growth data"):
                    display_df = lumpsum_results.copy()
                    display_df['Initial_Investment'] = initial_investment
                    display_df['Wealth_Gained'] = display_df['Investment_Value'] - display_df['Initial_Investment']
                    display_df['Returns_Percentage'] = (display_df['Wealth_Gained'] / display_df['Initial_Investment'] * 100)
                    
                    # Format for display
                    display_df['Initial_Investment'] = display_df['Initial_Investment'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Investment_Value'] = display_df['Investment_Value'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Wealth_Gained'] = display_df['Wealth_Gained'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Returns_Percentage'] = display_df['Returns_Percentage'].apply(lambda x: f"{x:.2f}%")
                    
                    st.dataframe(display_df, use_container_width=True)
    
    with tab3:
        st.subheader("Investment Education for Students")
        
        # Investment basics accordion
        with st.expander("Investment Basics for Students"):
            st.write("""
            ### Why should students invest?
            
            Starting to invest early gives you a huge advantage due to the power of compounding. 
            Even small investments made during college years can grow significantly over time.
            
            ### Key investment terms:
            
            - **SIP (Systematic Investment Plan)**: A method to invest a fixed amount regularly in mutual funds
            - **Mutual Funds**: Professionally managed investment funds that pool money from many investors
            - **Equity**: Ownership in a company through stocks
            - **Debt**: Fixed income investments like bonds and fixed deposits
            - **Returns**: The profit or loss from your investments
            - **Risk**: The possibility of losing money in an investment
            - **Diversification**: Spreading investments across different assets to reduce risk
            """)
        
        # SIP vs. Lumpsum accordion
        with st.expander("SIP vs. Lumpsum Investment"):
            st.write("""
            ### Systematic Investment Plan (SIP)
            
            **Advantages for students:**
            - Start with small amounts (as low as ₹500 per month)
            - Builds discipline in saving regularly
            - Reduces the impact of market volatility through rupee cost averaging
            - Easier to manage with limited student income
            
            ### Lumpsum Investment
            
            **When it makes sense:**
            - When you receive a large amount at once (scholarship, gift, internship stipend)
            - When markets are significantly down (though timing the market is difficult)
            - For short-term financial goals (1-3 years)
            
            ### Which should you choose?
            
            As a student, SIP is generally more suitable as it:
            - Matches your income pattern (monthly allowances)
            - Allows starting with smaller amounts
            - Builds a healthy financial habit
            """)
        
        # Investment options for students
        with st.expander("Best Investment Options for Students"):
            st.write("""
            ### Investment options suitable for students:
            
            1. **Mutual Funds via SIP**
               - Equity funds for long-term goals (5+ years)
               - Debt funds for medium-term goals (2-4 years)
               - Hybrid funds for balanced approach
            
            2. **Public Provident Fund (PPF)**
               - Long-term tax-free investment
               - Current interest rate: ~7.1%
               - Lock-in period: 15 years
            
            3. **Fixed Deposits**
               - Safe and guaranteed returns
               - Good for short-term goals
               - Current interest rates: 5-7%
            
            4. **Index Funds**
               - Low-cost investment in market indices like Nifty 50
               - Good for beginners
               - Lower risk than active equity funds
            
            5. **Sukanya Samriddhi Yojana** (for girl students)
               - Government-backed scheme with tax benefits
               - Current interest rate: ~7.6%
            """)
        
        # Common mistakes accordion
        with st.expander("Common Investment Mistakes Students Make"):
            st.write("""
            ### Avoid these common mistakes:
            
            1. **Not starting early enough**
               - Even ₹500/month from age 20 can grow significantly by retirement
            
            2. **Investing without financial goals**
               - Define what you're saving for (higher education, travel, first job expenses)
            
            3. **Not building an emergency fund first**
               - Keep 3-6 months of expenses in a liquid account before investing
            
            4. **Trying to time the market**
               - Regular investments work better than waiting for the "perfect time"
            
            5. **Withdrawing investments for small expenses**
               - Let your investments grow; use them only for planned goals
            
            6. **Not understanding tax implications**
               - Learn about STCG, LTCG, and tax-saving investments
            
            7. **Investing in complex products without understanding**
               - Start with simple investment options until you learn more
            """)
        
        # Interactive comparison tool
        st.subheader("Compare Investment Growth")
        
        col1, col2 = st.columns(2)
        
        with col1:
            compare_amount = st.number_input(
                "Monthly SIP Amount (₹)",
                min_value=100,
                value=1000,
                step=100,
                key="compare_sip_amount"
            )
        
        with col2:
            compare_years = st.slider(
                "Investment Duration (Years)",
                min_value=5,
                max_value=40,
                value=20,
                key="compare_years"
            )
        
        # Calculate and compare different return rates
        return_rates = [8, 12, 15]
        results = []
        
        for rate in return_rates:
            sip_results = calculate_sip_returns(compare_amount, rate, compare_years)
            final_value = sip_results['Investment_Value'].iloc[-1]
            total_invested = compare_amount * compare_years * 12
            results.append({
                'Rate': rate,
                'Final_Value': final_value,
                'Total_Invested': total_invested,
                'Wealth_Gained': final_value - total_invested
            })
        
        # Display comparison
        st.write(f"### Comparing a monthly SIP of ₹{compare_amount} for {compare_years} years")
        
        # Create comparison chart
        comparison_df = pd.DataFrame(results)
        
        fig = go.Figure()
        
        # Add bars for total invested
        fig.add_trace(
            go.Bar(
                x=[f"{r}% Return" for r in comparison_df['Rate']],
                y=comparison_df['Total_Invested'],
                name="Amount Invested",
                marker_color="blue"
            )
        )
        
        # Add bars for wealth gained
        fig.add_trace(
            go.Bar(
                x=[f"{r}% Return" for r in comparison_df['Rate']],
                y=comparison_df['Wealth_Gained'],
                name="Wealth Gained",
                marker_color="green"
            )
        )
        
        # Update layout
        fig.update_layout(
            title="Investment Growth Comparison",
            xaxis_title="Expected Return Rate",
            yaxis_title="Value (₹)",
            barmode="stack",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparison table
        for result in results:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(f"{result['Rate']}% Returns", f"₹{result['Final_Value']:,.2f}")
            
            with col2:
                st.metric("Amount Invested", f"₹{result['Total_Invested']:,.2f}")
            
            with col3:
                st.metric("Wealth Gained", f"₹{result['Wealth_Gained']:,.2f}", 
                         delta=f"{(result['Wealth_Gained']/result['Total_Invested'])*100:.1f}%")
