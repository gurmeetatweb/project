import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    create_time_series,
    create_bar_chart,
    create_histogram
)

def show_temporal_analysis(df):
    """
    Display the temporal analysis page with time-based insights.
    
    Args:
        df (pd.DataFrame): Filtered dataframe
    """
    st.title("Temporal Analysis")
    st.write("Explore startup trends over time, including founding dates, funding patterns, and temporal correlations.")
    
    # Check if time-related columns exist
    time_cols = ['founded_year', 'founded_month', 'founded_quarter', 'founded_at', 
                'first_funding_at', 'last_funding_at']
    existing_time_cols = [col for col in time_cols if col in df.columns]
    
    if not existing_time_cols:
        st.warning("No time-related information available in the dataset.")
        return
    
    # Companies founded over time
    st.subheader("Companies Founded Over Time")
    
    if 'founded_year' in df.columns:
        # Count companies by founding year
        year_counts = df['founded_year'].value_counts().sort_index().reset_index()
        year_counts.columns = ['Year', 'Count']
        
        # Create time series
        fig = create_time_series(
            year_counts,
            'Year',
            'Count',
            'Number of Companies Founded by Year'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Cumulative companies over time
        year_counts['Cumulative'] = year_counts['Count'].cumsum()
        
        cumul_fig = create_time_series(
            year_counts,
            'Year',
            'Cumulative',
            'Cumulative Number of Companies Founded',
            color='#F97316'
        )
        st.plotly_chart(cumul_fig, use_container_width=True)
        
        # Seasonal patterns (if month data available)
        if 'founded_month' in df.columns:
            st.subheader("Seasonal Founding Patterns")
            
            # Count companies by founding month
            month_counts = df['founded_month'].value_counts().sort_index().reset_index()
            month_counts.columns = ['Month', 'Count']
            
            # Map month numbers to names
            month_names = {
                1: 'January', 2: 'February', 3: 'March', 4: 'April', 
                5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }
            month_counts['Month Name'] = month_counts['Month'].map(month_names)
            
            # Create bar chart
            month_fig = create_bar_chart(
                month_counts,
                'Month Name',
                'Count',
                'Number of Companies Founded by Month'
            )
            
            # Ensure proper month ordering
            month_fig.update_layout(
                xaxis=dict(
                    categoryorder='array',
                    categoryarray=[month_names[i] for i in range(1, 13)]
                )
            )
            
            st.plotly_chart(month_fig, use_container_width=True)
        
        # Quarter analysis
        if 'founded_quarter' in df.columns:
            # Count companies by founding quarter
            quarter_counts = df['founded_quarter'].value_counts().sort_index().reset_index()
            quarter_counts.columns = ['Quarter', 'Count']
            
            # Create bar chart
            quarter_fig = create_bar_chart(
                quarter_counts,
                'Quarter',
                'Count',
                'Number of Companies Founded by Quarter'
            )
            st.plotly_chart(quarter_fig, use_container_width=True)
    else:
        st.info("Founding year information not available in the dataset.")
    
    # Funding over time
    st.subheader("Funding Trends Over Time")
    
    if 'founded_year' in df.columns and 'funding_total_usd' in df.columns:
        # Calculate total and average funding by year
        yearly_funding = df.groupby('founded_year').agg({
            'funding_total_usd': ['sum', 'mean', 'count']
        }).reset_index()
        
        yearly_funding.columns = ['Year', 'Total Funding', 'Average Funding', 'Company Count']
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Total Funding by Year", "Average Funding by Year", "Funding per Company Count"])
        
        with tab1:
            total_fig = create_time_series(
                yearly_funding,
                'Year',
                'Total Funding',
                'Total Funding by Founding Year'
            )
            st.plotly_chart(total_fig, use_container_width=True)
        
        with tab2:
            avg_fig = create_time_series(
                yearly_funding,
                'Year',
                'Average Funding',
                'Average Funding by Founding Year',
                color='#F97316'
            )
            st.plotly_chart(avg_fig, use_container_width=True)
        
        with tab3:
            # Create scatter plot with size representing company count
            fig = px.scatter(
                yearly_funding,
                x='Year',
                y='Total Funding',
                size='Company Count',
                color='Average Funding',
                title='Funding Trends by Year (Size = Number of Companies)',
                labels={'Total Funding': 'Total Funding (USD)'},
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Founding year or funding information not available in the dataset.")
    
    # Time between founding and funding
    st.subheader("Time Between Founding and Funding")
    
    if all(col in df.columns for col in ['founded_at', 'first_funding_at']):
        # Calculate time to first funding in days
        df['days_to_funding'] = (df['first_funding_at'] - df['founded_at']).dt.days
        
        # Filter out invalid values
        time_to_funding_df = df[df['days_to_funding'] >= 0].copy()
        
        # Calculate years to funding for better visualization
        time_to_funding_df['years_to_funding'] = time_to_funding_df['days_to_funding'] / 365.25
        
        # Create histogram
        fig = create_histogram(
            time_to_funding_df,
            'years_to_funding',
            'Time Between Founding and First Funding',
            nbins=20
        )
        
        fig.update_layout(
            xaxis_title='Years Between Founding and First Funding',
            yaxis_title='Number of Companies'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Time to funding by market
        if 'market' in df.columns:
            # Get top markets
            top_markets = df['market'].value_counts().nlargest(10).index.tolist()
            
            # Filter to top markets
            market_time_df = time_to_funding_df[time_to_funding_df['market'].isin(top_markets)].copy()
            
            # Create box plot
            fig = px.box(
                market_time_df,
                x='market',
                y='years_to_funding',
                title='Time to First Funding by Market',
                labels={
                    'market': 'Market',
                    'years_to_funding': 'Years to First Funding'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Time to funding by status
        if 'status' in df.columns:
            # Create box plot
            fig = px.box(
                time_to_funding_df,
                x='status',
                y='years_to_funding',
                title='Time to First Funding by Company Status',
                labels={
                    'status': 'Company Status',
                    'years_to_funding': 'Years to First Funding'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Founding or first funding date information not available in the dataset.")
    
    # Funding duration
    st.subheader("Funding Duration Analysis")
    
    if all(col in df.columns for col in ['first_funding_at', 'last_funding_at']):
        # Calculate funding duration in days
        df['funding_duration_days'] = (df['last_funding_at'] - df['first_funding_at']).dt.days
        
        # Filter out invalid values
        funding_duration_df = df[df['funding_duration_days'] >= 0].copy()
        
        # Calculate funding duration in years for better visualization
        funding_duration_df['funding_duration_years'] = funding_duration_df['funding_duration_days'] / 365.25
        
        # Create histogram
        fig = create_histogram(
            funding_duration_df,
            'funding_duration_years',
            'Funding Duration (Time Between First and Last Funding)',
            nbins=20,
            color='#4F8BF9'
        )
        
        fig.update_layout(
            xaxis_title='Funding Duration (Years)',
            yaxis_title='Number of Companies'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Funding duration by rounds
        if 'funding_rounds' in df.columns:
            # Group by number of funding rounds
            rounds_duration = funding_duration_df.groupby('funding_rounds')['funding_duration_years'].mean().reset_index()
            
            # Create bar chart
            fig = create_bar_chart(
                rounds_duration,
                'funding_rounds',
                'funding_duration_years',
                'Average Funding Duration by Number of Rounds'
            )
            
            fig.update_layout(
                xaxis_title='Number of Funding Rounds',
                yaxis_title='Average Funding Duration (Years)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("First funding or last funding date information not available in the dataset.")
    
    # Time trends by status
    st.subheader("Temporal Trends by Company Status")
    
    if 'founded_year' in df.columns and 'status' in df.columns:
        # Group by year and status
        year_status = df.groupby(['founded_year', 'status']).size().reset_index(name='count')
        
        # Create grouped bar chart
        fig = px.bar(
            year_status,
            x='founded_year',
            y='count',
            color='status',
            title='Company Status Distribution by Founding Year',
            labels={
                'founded_year': 'Founding Year',
                'count': 'Number of Companies',
                'status': 'Company Status'
            }
        )
        
        fig.update_layout(
            xaxis_title='Founding Year',
            yaxis_title='Number of Companies',
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate success rate by year (consider IPO or acquisition as success)
        if any(status in df['status'].unique() for status in ['ipo', 'acquired']):
            # Create success column
            df['success'] = df['status'].isin(['ipo', 'acquired'])
            
            # Group by year and calculate success rate
            year_success = df.groupby('founded_year')['success'].mean().reset_index()
            year_success.columns = ['Year', 'Success Rate']
            
            # Create line chart
            fig = create_time_series(
                year_success,
                'Year',
                'Success Rate',
                'Company Success Rate by Founding Year',
                color='#10B981'
            )
            
            fig.update_layout(
                yaxis=dict(
                    tickformat=".0%",
                    range=[0, 1]
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Founding year or status information not available in the dataset.")