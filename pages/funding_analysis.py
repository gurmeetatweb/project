import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    format_large_number,
    create_bar_chart,
    create_histogram,
    create_box_plot,
    create_time_series
)

def show_funding_analysis(df):
    """
    Display the funding analysis page with detailed funding insights.
    
    Args:
        df (pd.DataFrame): Filtered dataframe
    """
    st.title("Startup Funding Analysis")
    st.write("Explore funding patterns, distributions, and trends across different dimensions.")
    
    # Funding statistics
    if 'funding_total_usd' in df.columns:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Average Funding",
                f"${format_large_number(df['funding_total_usd'].mean())}",
                help="Average funding per company"
            )
        
        with col2:
            st.metric(
                "Median Funding",
                f"${format_large_number(df['funding_total_usd'].median())}",
                help="Median funding per company (less affected by outliers)"
            )
        
        with col3:
            st.metric(
                "Maximum Funding",
                f"${format_large_number(df['funding_total_usd'].max())}",
                help="Highest funding received by a single company"
            )
        
        # Funding distribution
        st.subheader("Funding Distribution")
        
        # Use log scale option
        use_log = st.checkbox("Use logarithmic scale (better for skewed distributions)")
        
        # Create distribution chart
        if use_log:
            # Add a small value to avoid log(0)
            log_funding = np.log10(df['funding_total_usd'] + 1)
            
            fig = px.histogram(
                log_funding,
                nbins=30,
                title="Distribution of Funding (Log Scale)",
                labels={'value': 'Log10 of Funding (USD)'}
            )
            
            # Add custom x-axis ticks for better interpretation
            tick_vals = np.arange(0, np.ceil(log_funding.max()) + 1)
            tick_text = [f"${10**i:,.0f}" for i in tick_vals]
            
            fig.update_layout(
                xaxis=dict(
                    tickvals=tick_vals,
                    ticktext=tick_text
                )
            )
        else:
            fig = create_histogram(
                df,
                'funding_total_usd',
                'Distribution of Funding',
                nbins=30
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Funding by rounds
        st.subheader("Funding by Rounds")
        
        # Create funding rounds columns
        funding_rounds_cols = [
            'seed', 'angel', 'venture', 'equity_crowdfunding', 'product_crowdfunding',
            'convertible_note', 'debt_financing', 'grant',
            'round_A', 'round_B', 'round_C', 'round_D', 'round_E', 'round_F', 'round_G', 'round_H'
        ]
        
        # Filter to only include columns that exist in the dataframe
        existing_rounds = [col for col in funding_rounds_cols if col in df.columns]
        
        if existing_rounds:
            # Aggregate funding by round type
            round_sums = []
            for round_type in existing_rounds:
                round_sum = df[round_type].sum()
                round_count = df[df[round_type] > 0].shape[0]
                round_avg = df[df[round_type] > 0][round_type].mean() if round_count > 0 else 0
                
                round_sums.append({
                    'Round Type': round_type.replace('_', ' ').title(),
                    'Total Funding': round_sum,
                    'Company Count': round_count,
                    'Average Funding': round_avg
                })
            
            rounds_df = pd.DataFrame(round_sums)
            
            # Display tabs for different views
            tab1, tab2, tab3 = st.tabs(["Total Funding by Round", "Companies Count by Round", "Average Funding by Round"])
            
            with tab1:
                total_fig = create_bar_chart(
                    rounds_df.sort_values('Total Funding', ascending=False),
                    'Round Type',
                    'Total Funding',
                    'Total Funding by Round Type'
                )
                st.plotly_chart(total_fig, use_container_width=True)
            
            with tab2:
                count_fig = create_bar_chart(
                    rounds_df.sort_values('Company Count', ascending=False),
                    'Round Type',
                    'Company Count',
                    'Number of Companies by Round Type'
                )
                st.plotly_chart(count_fig, use_container_width=True)
            
            with tab3:
                avg_fig = create_bar_chart(
                    rounds_df.sort_values('Average Funding', ascending=False),
                    'Round Type',
                    'Average Funding',
                    'Average Funding by Round Type'
                )
                st.plotly_chart(avg_fig, use_container_width=True)
        else:
            st.info("Detailed funding round information not available in the dataset.")
        
        # Funding by market
        st.subheader("Funding by Market")
        
        if 'market' in df.columns:
            # Get top markets by funding
            market_funding = df.groupby('market').agg({
                'funding_total_usd': ['sum', 'mean', 'count']
            }).reset_index()
            
            market_funding.columns = ['market', 'total_funding', 'avg_funding', 'company_count']
            market_funding = market_funding.sort_values('total_funding', ascending=False).head(15)
            
            # Display tabs for different views
            tab1, tab2, tab3 = st.tabs(["Total Funding by Market", "Average Funding by Market", "Company Count by Market"])
            
            with tab1:
                total_fig = create_bar_chart(
                    market_funding,
                    'market',
                    'total_funding',
                    'Top 15 Markets by Total Funding',
                    horizontal=True
                )
                st.plotly_chart(total_fig, use_container_width=True)
            
            with tab2:
                avg_fig = create_bar_chart(
                    market_funding.sort_values('avg_funding', ascending=False).head(15),
                    'market',
                    'avg_funding',
                    'Top 15 Markets by Average Funding',
                    horizontal=True
                )
                st.plotly_chart(avg_fig, use_container_width=True)
            
            with tab3:
                count_fig = create_bar_chart(
                    market_funding.sort_values('company_count', ascending=False).head(15),
                    'market',
                    'company_count',
                    'Top 15 Markets by Company Count',
                    horizontal=True
                )
                st.plotly_chart(count_fig, use_container_width=True)
        else:
            st.info("Market information not available in the dataset.")
        
        # Funding over time
        st.subheader("Funding Trends Over Time")
        
        if 'founded_year' in df.columns:
            # Create time series for funding trends
            year_funding = df.groupby('founded_year').agg({
                'funding_total_usd': ['sum', 'mean', 'count']
            }).reset_index()
            
            year_funding.columns = ['year', 'total_funding', 'avg_funding', 'company_count']
            
            # Filter out years with too few companies (possibly incomplete data)
            year_funding = year_funding[year_funding['company_count'] >= 5]
            
            # Create tabs for different time series
            tab1, tab2, tab3 = st.tabs(["Total Funding by Year", "Average Funding by Year", "Company Count by Year"])
            
            with tab1:
                total_fig = create_time_series(
                    year_funding,
                    'year',
                    'total_funding',
                    'Total Funding by Founding Year'
                )
                st.plotly_chart(total_fig, use_container_width=True)
            
            with tab2:
                avg_fig = create_time_series(
                    year_funding,
                    'year',
                    'avg_funding',
                    'Average Funding by Founding Year'
                )
                st.plotly_chart(avg_fig, use_container_width=True)
            
            with tab3:
                count_fig = create_time_series(
                    year_funding,
                    'year',
                    'company_count',
                    'Number of Companies by Founding Year'
                )
                st.plotly_chart(count_fig, use_container_width=True)
        else:
            st.info("Founding year information not available in the dataset.")
        
        # Box plot of funding by status
        st.subheader("Funding Distribution by Status")
        
        if 'status' in df.columns:
            # Create box plot for funding by status
            status_fig = create_box_plot(
                df,
                'status',
                'funding_total_usd',
                'Funding Distribution by Company Status'
            )
            st.plotly_chart(status_fig, use_container_width=True)
            
            # Summary statistics
            st.subheader("Summary Statistics by Status")
            
            status_stats = df.groupby('status').agg({
                'funding_total_usd': ['count', 'mean', 'median', 'min', 'max']
            }).reset_index()
            
            status_stats.columns = ['Status', 'Count', 'Mean', 'Median', 'Min', 'Max']
            
            # Format numbers
            for col in ['Mean', 'Median', 'Min', 'Max']:
                status_stats[col] = status_stats[col].apply(lambda x: f"${format_large_number(x)}")
            
            st.dataframe(status_stats, use_container_width=True)
        else:
            st.info("Status information not available in the dataset.")
    else:
        st.warning("Funding information not available in the dataset.")