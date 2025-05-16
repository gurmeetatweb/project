import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils import (
    create_pie_chart,
    create_bar_chart,
    create_wordcloud,
    create_heatmap
)

def show_category_analysis(df):
    """
    Display the category and market analysis page with industry-based insights.
    
    Args:
        df (pd.DataFrame): Filtered dataframe
    """
    st.title("Category & Market Analysis")
    st.write("Explore startup distribution across different categories and markets, including funding and success metrics.")
    
    # Check if category/market columns exist
    cat_cols = ['category_list', 'market', 'categories', 'main_category']
    existing_cat_cols = [col for col in cat_cols if col in df.columns]
    
    if not existing_cat_cols:
        st.warning("No category or market information available in the dataset.")
        return
    
    # Market distribution
    st.subheader("Market Distribution")
    
    if 'market' in df.columns:
        # Get market counts
        market_counts = df['market'].value_counts().reset_index()
        market_counts.columns = ['Market', 'Count']
        top_markets = market_counts.head(10)
        
        # Create pie chart for top markets
        market_fig = create_pie_chart(
            top_markets,
            'Market',
            'Count',
            'Distribution of Top 10 Markets'
        )
        st.plotly_chart(market_fig, use_container_width=True)
        
        # Create bar chart for more markets
        top_markets_bar = market_counts.head(20)
        market_bar_fig = create_bar_chart(
            top_markets_bar,
            'Market',
            'Count',
            'Top 20 Markets by Number of Companies',
            horizontal=True
        )
        st.plotly_chart(market_bar_fig, use_container_width=True)
        
        # Market word cloud
        st.subheader("Market Word Cloud")
        
        # Create word cloud
        word_cloud_fig = create_wordcloud(
            df['market'],
            'Market Word Cloud',
            max_words=100
        )
        st.pyplot(word_cloud_fig)
    else:
        st.info("Market information not available in the dataset.")
    
    # Category analysis
    st.subheader("Category Analysis")
    
    # Main category distribution
    if 'main_category' in df.columns:
        # Get category counts
        category_counts = df['main_category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        top_categories = category_counts.head(15)
        
        # Create bar chart
        category_fig = create_bar_chart(
            top_categories,
            'Category',
            'Count',
            'Top 15 Categories by Number of Companies',
            horizontal=True
        )
        st.plotly_chart(category_fig, use_container_width=True)
    elif 'category_list' in df.columns:
        # Process category list
        categories = []
        for cat_list in df['category_list'].dropna():
            for category in cat_list.split('|'):
                categories.append(category.strip())
        
        # Count categories
        category_counts = pd.Series(categories).value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        top_categories = category_counts.head(15)
        
        # Create bar chart
        category_fig = create_bar_chart(
            top_categories,
            'Category',
            'Count',
            'Top 15 Categories by Number of Companies',
            horizontal=True
        )
        st.plotly_chart(category_fig, use_container_width=True)
    else:
        st.info("Category information not available in the dataset.")
    
    # Funding by market/category
    st.subheader("Funding by Market/Category")
    
    # Tabs for market and category
    tab1, tab2 = st.tabs(["Market", "Category"])
    
    with tab1:
        if 'market' in df.columns and 'funding_total_usd' in df.columns:
            # Group by market and calculate total/average funding
            market_funding = df.groupby('market').agg({
                'funding_total_usd': ['sum', 'mean', 'count']
            }).reset_index()
            
            market_funding.columns = ['market', 'total_funding', 'avg_funding', 'company_count']
            market_funding = market_funding.sort_values('total_funding', ascending=False).head(15)
            
            # Create sub-tabs for different metrics
            subtab1, subtab2, subtab3 = st.tabs(["Total Funding", "Average Funding", "Company Count"])
            
            with subtab1:
                total_fig = create_bar_chart(
                    market_funding,
                    'market',
                    'total_funding',
                    'Top 15 Markets by Total Funding',
                    horizontal=True
                )
                st.plotly_chart(total_fig, use_container_width=True)
            
            with subtab2:
                avg_funding_markets = df.groupby('market').agg({
                    'funding_total_usd': ['mean', 'count']
                }).reset_index()
                
                avg_funding_markets.columns = ['market', 'avg_funding', 'company_count']
                
                # Filter to markets with at least 5 companies
                avg_funding_markets = avg_funding_markets[avg_funding_markets['company_count'] >= 5]
                avg_funding_markets = avg_funding_markets.sort_values('avg_funding', ascending=False).head(15)
                
                avg_fig = create_bar_chart(
                    avg_funding_markets,
                    'market',
                    'avg_funding',
                    'Top 15 Markets by Average Funding (Min 5 Companies)',
                    horizontal=True
                )
                st.plotly_chart(avg_fig, use_container_width=True)
            
            with subtab3:
                count_fig = create_bar_chart(
                    market_funding.sort_values('company_count', ascending=False).head(15),
                    'market',
                    'company_count',
                    'Top 15 Markets by Company Count',
                    horizontal=True
                )
                st.plotly_chart(count_fig, use_container_width=True)
        else:
            st.info("Market or funding information not available in the dataset.")
    
    with tab2:
        if 'main_category' in df.columns and 'funding_total_usd' in df.columns:
            # Group by category and calculate total/average funding
            category_funding = df.groupby('main_category').agg({
                'funding_total_usd': ['sum', 'mean', 'count']
            }).reset_index()
            
            category_funding.columns = ['category', 'total_funding', 'avg_funding', 'company_count']
            category_funding = category_funding.sort_values('total_funding', ascending=False).head(15)
            
            # Create sub-tabs for different metrics
            subtab1, subtab2, subtab3 = st.tabs(["Total Funding", "Average Funding", "Company Count"])
            
            with subtab1:
                total_fig = create_bar_chart(
                    category_funding,
                    'category',
                    'total_funding',
                    'Top 15 Categories by Total Funding',
                    horizontal=True
                )
                st.plotly_chart(total_fig, use_container_width=True)
            
            with subtab2:
                avg_funding_categories = df.groupby('main_category').agg({
                    'funding_total_usd': ['mean', 'count']
                }).reset_index()
                
                avg_funding_categories.columns = ['category', 'avg_funding', 'company_count']
                
                # Filter to categories with at least 5 companies
                avg_funding_categories = avg_funding_categories[avg_funding_categories['company_count'] >= 5]
                avg_funding_categories = avg_funding_categories.sort_values('avg_funding', ascending=False).head(15)
                
                avg_fig = create_bar_chart(
                    avg_funding_categories,
                    'category',
                    'avg_funding',
                    'Top 15 Categories by Average Funding (Min 5 Companies)',
                    horizontal=True
                )
                st.plotly_chart(avg_fig, use_container_width=True)
            
            with subtab3:
                count_fig = create_bar_chart(
                    category_funding.sort_values('company_count', ascending=False).head(15),
                    'category',
                    'company_count',
                    'Top 15 Categories by Company Count',
                    horizontal=True
                )
                st.plotly_chart(count_fig, use_container_width=True)
        elif 'category_list' in df.columns and 'funding_total_usd' in df.columns:
            st.info("Category analysis requires preprocessing of category_list column. See overview for more information.")
        else:
            st.info("Category or funding information not available in the dataset.")
    
    # Category and status relationship
    st.subheader("Market Success Analysis")
    
    if 'market' in df.columns and 'status' in df.columns:
        # Define successful statuses
        success_statuses = ['ipo', 'acquired']
        
        # Create success column
        df['success'] = df['status'].isin(success_statuses)
        
        # Calculate success rate by market
        market_success = df.groupby('market').agg({
            'success': ['mean', 'count']
        }).reset_index()
        
        market_success.columns = ['market', 'success_rate', 'company_count']
        
        # Filter to markets with at least 10 companies
        market_success = market_success[market_success['company_count'] >= 10]
        market_success = market_success.sort_values('success_rate', ascending=False).head(15)
        
        # Format success rate as percentage
        market_success['success_rate'] = market_success['success_rate'] * 100
        
        # Create bar chart
        success_fig = create_bar_chart(
            market_success,
            'market',
            'success_rate',
            'Top 15 Markets by Success Rate (Min 10 Companies)',
            horizontal=True
        )
        
        success_fig.update_layout(
            xaxis_title='Success Rate (%)'
        )
        
        st.plotly_chart(success_fig, use_container_width=True)
        
        # Status distribution by top markets
        top_markets = df['market'].value_counts().nlargest(5).index.tolist()
        
        # Filter to top markets
        top_markets_df = df[df['market'].isin(top_markets)]
        
        # Create stacked bar chart
        fig = px.histogram(
            top_markets_df,
            x='market',
            color='status',
            barmode='stack',
            title='Status Distribution in Top 5 Markets',
            labels={
                'market': 'Market',
                'count': 'Number of Companies',
                'status': 'Status'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Market or status information not available in the dataset.")
    
    # Market trends over time
    st.subheader("Market Trends Over Time")
    
    if 'market' in df.columns and 'founded_year' in df.columns:
        # Get top markets
        top_markets = df['market'].value_counts().nlargest(5).index.tolist()
        
        # Filter to top markets
        top_markets_df = df[df['market'].isin(top_markets)]
        
        # Group by year and market
        market_years = top_markets_df.groupby(['founded_year', 'market']).size().reset_index(name='count')
        
        # Create line chart
        fig = px.line(
            market_years,
            x='founded_year',
            y='count',
            color='market',
            title='Top 5 Markets Growth Over Time',
            labels={
                'founded_year': 'Founding Year',
                'count': 'Number of Companies',
                'market': 'Market'
            }
        )
        
        fig.update_layout(
            xaxis_title='Founding Year',
            yaxis_title='Number of Companies'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Market heatmap by year
        if len(top_markets) > 0:
            # Create pivot table
            market_year_pivot = market_years.pivot(
                index='market',
                columns='founded_year',
                values='count'
            ).fillna(0)
            
            # Create heatmap
            heatmap_fig = create_heatmap(
                market_years,
                'founded_year',
                'market',
                'count',
                'Market Activity Heatmap by Year'
            )
            st.plotly_chart(heatmap_fig, use_container_width=True)
    else:
        st.info("Market or founding year information not available in the dataset.")
    
    # Category co-occurrence
    st.subheader("Category Co-occurrence")
    
    if 'categories' in df.columns:
        # Extract unique categories
        all_categories = []
        for cats in df['categories'].dropna():
            if isinstance(cats, list):
                all_categories.extend(cats)
        
        # Get top categories
        top_categories = pd.Series(all_categories).value_counts().nlargest(15).index.tolist()
        
        # Create co-occurrence matrix
        co_occurrence = pd.DataFrame(0, index=top_categories, columns=top_categories)
        
        # Calculate co-occurrences
        for cats in df['categories'].dropna():
            if isinstance(cats, list):
                # Filter to top categories
                filtered_cats = [cat for cat in cats if cat in top_categories]
                
                # Calculate co-occurrences
                for i, cat1 in enumerate(filtered_cats):
                    for cat2 in filtered_cats[i:]:
                        co_occurrence.loc[cat1, cat2] += 1
                        if cat1 != cat2:
                            co_occurrence.loc[cat2, cat1] += 1
        
        # Create heatmap
        fig = px.imshow(
            co_occurrence,
            labels=dict(x='Category', y='Category', color='Co-occurrences'),
            x=co_occurrence.columns,
            y=co_occurrence.index,
            color_continuous_scale='Blues',
            title='Category Co-occurrence Matrix'
        )
        
        fig.update_layout(
            height=700,
            width=700
        )
        
        st.plotly_chart(fig, use_container_width=True)
    elif 'category_list' in df.columns:
        st.info("Category co-occurrence analysis requires preprocessing of category_list column. See overview for more information.")
    else:
        st.info("Category information not available in the dataset.")