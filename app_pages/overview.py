import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import filter_country
from utils import (
    display_metric_row, 
    format_large_number, 
    create_pie_chart,
    create_bar_chart,
    create_plotly_choropleth
)

def create_india_choropleth(data, value_column, title):    
    # Create India-specific choropleth
    fig = px.choropleth(
        data,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        locations='state',  # Column in your dataframe with state names
        featureidkey="properties.ST_NM",  # Key in GeoJSON for state names
        color=value_column,
        color_continuous_scale="Viridis",
        range_color=(0, data[value_column].max()),  # CORRECTED: Removed extra parenthesis
        scope="asia",
        title=title
    )
    
    # Adjust map focus to India
    fig.update_geos(
        visible=False,
        lonaxis_range=[68, 98],  # Longitude range for India
        lataxis_range=[6, 38]    # Latitude range for India
    )
    
    fig.update_layout(
        margin={"r":0,"t":30,"l":0,"b":0},
        height=600
    )
    
    return fig

def show_overview(df):
    """
    Display the overview page with key metrics and high-level insights.
    
    Args:
        df (pd.DataFrame): Filtered dataframe
    """
    # Filter for India
    df = filter_country(df,True)
    st.title("Startup Ecosystem Overview")
    st.write("This dashboard provides insights into the global startup ecosystem based on funding, geographic distribution, and industry trends.")
    
    # Key metrics row
    st.subheader("Key Metrics")
    
    total_companies = len(df)
    if 'funding_total_usd' in df.columns:
        total_funding = df['funding_total_usd'].sum()
        avg_funding = df['funding_total_usd'].mean()
    else:
        total_funding = 0
        avg_funding = 0
        
    if 'funding_rounds' in df.columns:
        avg_rounds = df['funding_rounds'].mean()
    else:
        avg_rounds = 0
    
    # Top status distribution
    if 'status' in df.columns:
        operating_pct = df[df['status'] == 'operating'].shape[0] / total_companies * 100 if total_companies > 0 else 0
    else:
        operating_pct = 0
    
    metrics = [
        {
            'title': 'Total Companies',
            'value': format_large_number(total_companies),
            'help_text': 'Total number of companies in the dataset'
        },
        {
            'title': 'Total Funding',
            'value': f"${format_large_number(total_funding)}",
            'help_text': 'Sum of all funding across companies'
        },
        {
            'title': 'Average Funding',
            'value': f"${format_large_number(avg_funding)}",
            'help_text': 'Average funding per company'
        },
        {
            'title': 'Average Funding Rounds',
            'value': f"{avg_rounds:.1f}",
            'help_text': 'Average number of funding rounds per company'
        },
        {
            'title': 'Operating Companies',
            'value': f"{operating_pct:.1f}%",
            'help_text': 'Percentage of companies currently operating'
        }
    ]
    
    display_metric_row(metrics)
    
    # Create layout for charts
    col1, col2 = st.columns(2)
    
    # Status distribution
    with col1:
        st.subheader("Company Status Distribution")
        if 'status' in df.columns:
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            status_fig = create_pie_chart(
                status_counts,
                'Status',
                'Count',
                'Company Status Distribution'
            )
            st.plotly_chart(status_fig, use_container_width=True)
        else:
            st.info("Status information not available in the dataset.")
    
    # Funding by market
    with col2:
        st.subheader("Top Markets by Funding")
        if 'market' in df.columns and 'funding_total_usd' in df.columns:
            market_funding = df.groupby('market')['funding_total_usd'].sum().reset_index()
            market_funding = market_funding.sort_values('funding_total_usd', ascending=False).head(10)
            
            market_fig = create_bar_chart(
                market_funding,
                'market',
                'funding_total_usd',
                'Top 10 Markets by Total Funding',
                horizontal=True
            )
            st.plotly_chart(market_fig, use_container_width=True)
        else:
            st.info("Market or funding information not available in the dataset.")
    '''
    # Geographic distribution
    st.subheader("Geographic Distribution of Startups")
    
    if 'region' in df.columns:
        region_counts = df['region'].value_counts().reset_index()
        region_counts.columns = ['region', 'count']
        region_counts.rename(columns = {"region": "state"}, inplace = True)
        geo_fig = create_india_choropleth(
                region_counts,  # Should have 'state' column with Indian state names
                'count',         # Column with your values
                'Number of Startups by Indian State'
        )
        st.plotly_chart(geo_fig, use_container_width=True) 
        
       
        
        #geo_fig = create_plotly_choropleth(
        #    region_counts,
        #    'count',
        #    'Number of Startups by Country'
        #)
        #st.plotly_chart(geo_fig, use_container_width=True)
        
    else:
        st.info("Country information not available in the dataset.")
    '''
    # Funding distribution
    st.subheader("Funding Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if all(col in df.columns for col in ['funding_rounds', 'funding_total_usd']):
            funding_by_rounds = df.groupby('funding_rounds')['funding_total_usd'].mean().reset_index()
            
            rounds_fig = create_bar_chart(
                funding_by_rounds,
                'funding_rounds',
                'funding_total_usd',
                'Average Funding by Number of Rounds'
            )
            st.plotly_chart(rounds_fig, use_container_width=True)
        else:
            st.info("Funding rounds information not available in the dataset.")
    
    with col2:
        if 'founded_year' in df.columns and 'funding_total_usd' in df.columns:
            yearly_funding = df.groupby('founded_year')['funding_total_usd'].sum().reset_index()
            
            yearly_fig = px.line(
                yearly_funding,
                x='founded_year',
                y='funding_total_usd',
                title='Total Funding by Founding Year',
                markers=True
            )
            st.plotly_chart(yearly_fig, use_container_width=True)
        else:
            st.info("Founded year or funding information not available in the dataset.")
    
    # Data preview
    st.subheader("Data Preview")
    st.write(f"Showing {len(df)} companies after applying filters")
    st.dataframe(df.head(10))