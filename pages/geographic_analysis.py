import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import filter_country
from utils import (
    format_large_number,
    create_plotly_choropleth,
    create_bar_chart,
    create_pie_chart
)

def show_geographic_analysis(df):
    """
    Display the geographic analysis page with location-based insights.
    
    Args:
        df (pd.DataFrame): Filtered dataframe
    """
    st.title("Geographic Distribution Analysis")
    st.write("Explore how startups and funding are distributed across different geographical locations.")
    
    # Check if geographic columns exist
    geo_cols = ['country_code', 'region', 'state_code', 'city']
    existing_geo_cols = [col for col in geo_cols if col in df.columns]
    
    if not existing_geo_cols:
        st.warning("No geographic information available in the dataset.")
        return
    
    # Global map
    st.subheader("Global Distribution of Startups")
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["Company Count", "Total Funding"])
    
    with tab1:
        if 'country_code' in df.columns:
            country_counts = df['country_code'].value_counts().reset_index()
            country_counts.columns = ['country_code', 'count']
            
            # Create world map
            fig = create_plotly_choropleth(
                country_counts,
                'count',
                'Number of Startups by Country'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show top countries
            st.subheader("Top Countries by Number of Startups")
            top_countries = country_counts.head(15)
            
            country_fig = create_bar_chart(
                top_countries,
                'country_code',
                'count',
                'Top 15 Countries by Number of Startups',
                horizontal=True
            )
            st.plotly_chart(country_fig, use_container_width=True)
        else:
            st.info("Country information not available in the dataset.")
    
    with tab2:
        if 'country_code' in df.columns and 'funding_total_usd' in df.columns:
            # Group by country and calculate total funding
            country_funding = df.groupby('country_code')['funding_total_usd'].sum().reset_index()
            
            # Create world map
            fig = create_plotly_choropleth(
                country_funding,
                'funding_total_usd',
                'Total Funding by Country (USD)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show top countries by funding
            st.subheader("Top Countries by Total Funding")
            top_countries = country_funding.sort_values('funding_total_usd', ascending=False).head(15)
            
            country_fig = create_bar_chart(
                top_countries,
                'country_code',
                'funding_total_usd',
                'Top 15 Countries by Total Funding',
                horizontal=True
            )
            st.plotly_chart(country_fig, use_container_width=True)
        else:
            st.info("Country or funding information not available in the dataset.")
    
    # India Section
    st.subheader("Distribution of Startups in India")

    # Regional analysis
    df = df[df['country_code'].str.upper() == 'IND']
    if 'region' in df.columns:        
        # Get region counts
        region_counts = df['region'].value_counts().reset_index()
        region_counts.columns = ['Region', 'Count']
        
        # Create pie chart
        region_fig = create_pie_chart(
            region_counts,
            'Region',
            'Count',
            'Distribution of Startups by Region'
        )
        st.plotly_chart(region_fig, use_container_width=True)
        
        # Regional funding analysis
        if 'funding_total_usd' in df.columns:
            # Group by region and calculate total/average funding
            region_funding = df.groupby('region').agg({
                'funding_total_usd': ['sum', 'mean', 'count']
            }).reset_index()
            
            region_funding.columns = ['region', 'total_funding', 'avg_funding', 'company_count']
            
            # Create tabs for different views
            tab1, tab2 = st.tabs(["Total Funding by Region", "Average Funding by Region"])
            
            with tab1:
                total_fig = create_bar_chart(
                    region_funding.sort_values('total_funding', ascending=False),
                    'region',
                    'total_funding',
                    'Total Funding by Region',
                    horizontal=True
                )
                st.plotly_chart(total_fig, use_container_width=True)
            
            with tab2:
                avg_fig = create_bar_chart(
                    region_funding.sort_values('avg_funding', ascending=False),
                    'region',
                    'avg_funding',
                    'Average Funding by Region',
                    horizontal=True
                )
                st.plotly_chart(avg_fig, use_container_width=True)
    else:
        st.info("Region information not available in the dataset.")
    
    # City analysis
    st.subheader("City Analysis")
    
    if 'city' in df.columns:
        # Get top cities
        city_counts = df['city'].value_counts().reset_index()
        city_counts.columns = ['City', 'Count']
        top_cities = city_counts.head(20)
        
        # Create bar chart
        city_fig = create_bar_chart(
            top_cities,
            'City',
            'Count',
            'Top 20 Cities by Number of Startups',
            horizontal=True
        )
        st.plotly_chart(city_fig, use_container_width=True)
        
        # City funding analysis
        if 'funding_total_usd' in df.columns:
            # Group by city and calculate total funding
            city_funding = df.groupby('city')['funding_total_usd'].sum().reset_index()
            city_funding = city_funding.sort_values('funding_total_usd', ascending=False).head(20)
            
            # Create bar chart
            funding_fig = create_bar_chart(
                city_funding,
                'city',
                'funding_total_usd',
                'Top 20 Cities by Total Funding',
                horizontal=True
            )
            st.plotly_chart(funding_fig, use_container_width=True)
    else:
        st.info("City information not available in the dataset.")
    
    # State analysis (for US)
    if 'country_code' in df.columns and 'state_code' in df.columns:
        # Filter to US companies
        us_df = df[df['country_code'] == 'IND']
        
        if not us_df.empty:
            st.subheader("State Analysis")
            
            # Get state counts
            state_counts = us_df['state'].value_counts().reset_index()
            state_counts.columns = ['State', 'Count']
            #shp_gdf = gpd.read_file('../input/india-gis-data/India States/Indian_states.shp')
            #shp_gdf.head()
            # Create US map
            '''fig = px.choropleth(
                state_counts,
                locations='state',
                locationmode='USA-states',
                color='Count',
                scope='usa',
                color_continuous_scale='Blues',
                title='Number of Startups by US State'
            )
            st.plotly_chart(fig, use_container_width=True)'''

            #df1 = pd.read_csv("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/active_cases_2020-07-17_0800.csv")
            
            fig = px.choropleth(
                us_df,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM',
                locations='region',
                color='funding_total_usd',
                color_continuous_scale='Reds'
            )

            fig.update_geos(fitbounds="locations", visible=False)

            fig.show()
            
            # State funding analysis
            if 'funding_total_usd' in us_df.columns:
                # Group by state and calculate total funding
                state_funding = us_df.groupby('state_code')['funding_total_usd'].sum().reset_index()
                
                # Create US map
                funding_fig = px.choropleth(
                    state_funding,
                    locations='state_code',
                    locationmode='USA-states',
                    color='funding_total_usd',
                    scope='usa',
                    color_continuous_scale='Greens',
                    title='Total Funding by US State (USD)'
                )
                st.plotly_chart(funding_fig, use_container_width=True)
                
                # Top states by funding
                top_states = state_funding.sort_values('funding_total_usd', ascending=False).head(10)
                
                # Create bar chart
                state_fig = create_bar_chart(
                    top_states,
                    'state_code',
                    'funding_total_usd',
                    'Top 10 US States by Total Funding',
                    horizontal=True
                )
                st.plotly_chart(state_fig, use_container_width=True)
    
    # Cross-geographical analysis
    st.subheader("Cross-Geographical Analysis")
    
    # Market distribution by region
    if 'region' in df.columns and 'market' in df.columns:
        # Get top markets
        top_markets = df['market'].value_counts().nlargest(5).index.tolist()
        
        # Filter to top markets
        market_region_df = df[df['market'].isin(top_markets)]
        
        # Create grouped bar chart
        fig = px.histogram(
            market_region_df,
            x='region',
            color='market',
            barmode='group',
            title='Distribution of Top 5 Markets Across Regions',
            labels={'count': 'Number of Companies', 'region': 'Region', 'market': 'Market'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Status distribution by country
    if 'country_code' in df.columns and 'status' in df.columns:
        # Get top countries
        top_countries = df['country_code'].value_counts().nlargest(5).index.tolist()
        
        # Filter to top countries
        country_status_df = df[df['country_code'].isin(top_countries)]
        
        # Create grouped bar chart
        fig = px.histogram(
            country_status_df,
            x='country_code',
            color='status',
            barmode='group',
            title='Distribution of Company Status Across Top 5 Countries',
            labels={'count': 'Number of Companies', 'country_code': 'Country', 'status': 'Status'}
        )
        st.plotly_chart(fig, use_container_width=True)