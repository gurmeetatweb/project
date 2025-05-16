import streamlit as st
from data_processor import load_data
from pages.overview import show_overview
from pages.funding_analysis import show_funding_analysis
from pages.geographic_analysis import show_geographic_analysis
from pages.temporal_analysis import show_temporal_analysis
from pages.category_analysis import show_category_analysis
from pages.correlation_analysis import show_correlation_analysis
from utils import set_page_config

def main():
    # Set page configuration
    set_page_config()
    
    # Load data All countries Data
    df = load_data()
    

    

    # Sidebar navigation
    st.sidebar.title("Startup Analysis Dashboard")
    
    # Add logo/icon
    st.sidebar.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24" fill="none" 
                stroke="#4F8BF9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 20h.01M7 20v-4"></path>
                <path d="M12 20v-8"></path>
                <path d="M17 20V8"></path>
                <path d="M22 4v16h.01"></path>
            </svg>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation options
    pages = {
        "Overview": show_overview,
        "Funding Analysis": show_funding_analysis,
        "Geographic Distribution": show_geographic_analysis,
        "Temporal Analysis": show_temporal_analysis,
        "Category & Market Analysis": show_category_analysis,
        "Correlation Explorer": show_correlation_analysis
    }
    
    # Page selection
    selection = st.sidebar.radio("Navigate", list(pages.keys()))
    
    
    # Display filters in sidebar for all pages
    st.sidebar.markdown("---")
    st.sidebar.subheader("Global Filters")
    
    # Year range filter
    if 'founded_year' in df.columns and df['founded_year'].notna().any():
        min_year = int(df['founded_year'].min())
        max_year = int(df['founded_year'].max())
        year_range = st.sidebar.slider(
            "Founded Year Range",
            min_year, max_year, (min_year, max_year)
        )
        df_filtered = df[(df['founded_year'] >= year_range[0]) & (df['founded_year'] <= year_range[1])]
    else:
        df_filtered = df
    
    # Funding range filter (log scale for better distribution)
    if 'funding_total_usd' in df.columns and df['funding_total_usd'].notna().any():
        min_funding = float(df['funding_total_usd'].min())
        max_funding = float(df['funding_total_usd'].max())
        funding_range = st.sidebar.slider(
            "Total Funding Range ($)",
            min_funding, max_funding, (min_funding, max_funding),
            format="$%.2f"
        )
        df_filtered = df_filtered[
            (df_filtered['funding_total_usd'] >= funding_range[0]) & 
            (df_filtered['funding_total_usd'] <= funding_range[1])
        ]
    
    # Market/category filter (multi-select)
    if 'market' in df.columns and df['market'].notna().any():
        top_markets = df['market'].value_counts().nlargest(20).index.tolist()
        selected_markets = st.sidebar.multiselect(
            "Markets",
            options=["All"] + top_markets,
            default=["All"]
        )
        
        if "All" not in selected_markets and selected_markets:
            df_filtered = df_filtered[df_filtered['market'].isin(selected_markets)]
    
    # Status filter
    if 'status' in df.columns and df['status'].notna().any():
        statuses = df['status'].unique().tolist()
        selected_status = st.sidebar.multiselect(
            "Company Status",
            options=["All"] + statuses,
            default=["All"]
        )
        
        if "All" not in selected_status and selected_status:
            df_filtered = df_filtered[df_filtered['status'].isin(selected_status)]
    
    # Region/country filter
    if 'country_code' in df.columns and df['country_code'].notna().any():
        top_countries = df['country_code'].value_counts().nlargest(10).index.tolist()
        selected_countries = st.sidebar.multiselect(
            "Countries",
            options=["All"] + top_countries,
            default=["All"]
        )
        
        if "All" not in selected_countries and selected_countries:
            df_filtered = df_filtered[df_filtered['country_code'].isin(selected_countries)]
    
    # Display selected page with filtered data
    if(selection != 'Geographic Distribution'):
        df_filtered = df_filtered[df_filtered['country_code'].str.upper() == 'IND']

    
    print(df_filtered['state'])
    pages[selection](df_filtered)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info(
        "This interactive dashboard analyzes startup funding data. "
        "Use the filters to explore different aspects of the startup ecosystem."
    )

if __name__ == "__main__":
    main()