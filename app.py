import streamlit as st
from data_processor import load_data
from app_pages.overview import show_overview
from app_pages.funding_analysis import show_funding_analysis
from app_pages.geographic_analysis import show_geographic_analysis
from app_pages.temporal_analysis import show_temporal_analysis
from app_pages.category_analysis import show_category_analysis
from app_pages.correlation_analysis import show_correlation_analysis
from app_pages.about import show_about_page
from utils import set_page_config
from PIL import Image

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
            +
            <svg enable-background="new 0 0 128 128" width="50" height="50" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><linearGradient id="a"><stop offset=".4707" stop-color="#ef5451"/><stop offset=".8338" stop-color="#e53a35"/></linearGradient><radialGradient id="b" cx="46.895" cy="35.963" gradientUnits="userSpaceOnUse" r="62.182" xlink:href="#a"/><radialGradient id="c" cx="58.828" cy="53.686" gradientUnits="userSpaceOnUse" r="30.652" xlink:href="#a"/><circle cx="63.99" cy="64" fill="url(#b)" r="59.82"/><path d="m63.99 7.18c31.33 0 56.82 25.49 56.82 56.82s-25.49 56.82-56.82 56.82-56.82-25.49-56.82-56.82 25.49-56.82 56.82-56.82m0-3c-33.04 0-59.82 26.79-59.82 59.82s26.78 59.82 59.82 59.82 59.82-26.78 59.82-59.82-26.79-59.82-59.82-59.82z" fill="#434343" opacity=".2"/><circle cx="63.99" cy="64" fill="#fefce9" r="41.66"/><circle cx="63.99" cy="64" fill="url(#c)" r="26.71"/><circle cx="63.99" cy="64" fill="#fefce9" r="8.01"/><path d="m110.04 18.25.35-8.44c.16-3.8-3.22-6.49-6.97-5.55l-6.96 1.73c-2.4.6-4.32 2.55-4.87 4.96l-7.59 33.34.06-.03 26-26z" fill="#09bcd4"/><path d="m110.05 18.25 8.44-.35c3.8-.16 6.49 3.22 5.55 6.97l-1.73 6.96c-.6 2.4-2.55 4.32-4.96 4.87l-33.34 7.59.03-.06 26-26z" fill="#38a4dd"/><path d="m65.32 65.13c-1.4 1.25-3.35-.7-2.11-2.1l37.53-41.45c1.65-1.65 4.33-1.65 5.98 0s1.65 4.33 0 5.98z" fill="#1b87c9"/><path d="m104.91 6.07c.99 0 1.89.37 2.54 1.05.65.67.98 1.6.94 2.61l-.35 8.42c-.02.39.08.77.27 1.09.09.15.19.28.31.4.37.38.89.61 1.43.61h.08l8.42-.35h.17c1.12 0 2.1.46 2.75 1.29.68.86.9 2.03.61 3.19l-1.73 6.96c-.41 1.65-1.8 3.02-3.46 3.4l-27.64 6.3c-.34.08-.65.24-.9.47l-16.68 15.16 15.1-16.68c.23-.25.39-.56.47-.9l6.31-27.7c.38-1.66 1.74-3.05 3.4-3.46l6.96-1.73c.33-.09.67-.13 1-.13m0-2c-.49 0-.99.06-1.49.19l-6.96 1.73c-2.4.6-4.32 2.55-4.87 4.96l-6.31 27.7-22.07 24.37c-.97 1.09-.01 2.5 1.12 2.5.33 0 .67-.12.98-.4l24.39-22.12 27.64-6.3c2.4-.55 4.36-2.47 4.96-4.87l1.73-6.96c.91-3.67-1.64-6.97-5.3-6.97-.08 0-.17 0-.26.01l-8.42.35h-.02v-.02l.35-8.42c.14-3.3-2.36-5.75-5.47-5.75z" fill="#434343" opacity=".2"/></svg>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation options
    pages = {
        "Overview": show_overview,
        "Funding Analysis": show_funding_analysis,
        "Geographic Distribution": show_geographic_analysis,
        "Temporal Analysis": show_temporal_analysis,
        "Category & Market Analysis": show_category_analysis,
        "Correlation Explorer": show_correlation_analysis,
        "About Us":show_about_page,
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
        df_india = df.copy()
        df_india = df_india[df_india['country_code'].str.upper() == 'IND']    
        min_funding = float(df_india['funding_total_usd'].min())
        max_funding = float(df_india['funding_total_usd'].max())
        funding_range = st.sidebar.slider(
            "Total Funding Range ($ millions)",
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
    if 'region' in df.columns and df['region'].notna().any():
        df_india = df[df['country_code'] == 'IND']
        top_regions = df_india['region'].drop(index=df_india[df_india['region'] == 'Unknown'].index).value_counts().nlargest(10).index.tolist()
        selected_regions = st.sidebar.multiselect(
            "Regions",
            options=["All"] + top_regions,
            default=["All"]
        )
        
        if "All" not in selected_regions and selected_regions:
            df_filtered = df_filtered[df_filtered['region'].isin(selected_regions)]
    
    # Display selected page with filtered data
    if(selection != 'Geographic Distribution'):
        df_filtered = df_filtered[df_filtered['country_code'].str.upper() == 'IND']    
    
    pages[selection](df_filtered)
    
    # Footer
    st.sidebar.markdown("---")    
    st.sidebar.info(
        """
        Hackathon Initiative by ![image](https://cdn.masaischool.com/masai-website/masai_dark_853075d7cd.png)
        [![Masai Hackathon](https://img.shields.io/badge/Masai_School-Hackathon_Project-blue?style=flat&logo=masaischool)](https://masai-school.notion.site/StartUp-Investments-Analysis-3632556b9f614fc8a033328e70589bf0)
        
        🏆 **DataSculpt: The Data Science Hackathon!**  
        *"Sculpt your data, shape your future!"*
        

        **Team QuantumQueries presents:**  
        🚀 *Startup Insights Explorer*  

        **Our Mission:**  
        Transform messy startup data into:  
        - 💡 Actionable business insights  
        - 🌍 Geographic investment trends  
        - 📈 Funding pattern identification  

        **Hackathon Highlights:**          
        • 100% Python (Pandas + Streamlit)  
        • 8+ interactive visualizations  
        • Real-time data processing  

        *"From raw data to boardroom decisions"*
        """
    )

if __name__ == "__main__":
    main()

st.warning("⚠️ Note: All analysis reflects Indian startup data up to 2014 only")