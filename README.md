## Startup Ecosystem Analysis Dashboard

This interactive Streamlit dashboard provides comprehensive exploratory data analysis (EDA) for startup funding data. It enables users to gain insights into startup funding patterns, geographic distribution, industry trends, and more.

### Features

- **Interactive Filters**: Slice and dice data by year, funding amount, market, status, and more
- **Comprehensive Analysis**: Explore funding patterns, geographic distribution, temporal trends, and industry analysis
- **Visualizations**: Rich, interactive charts and graphs for insightful data exploration
- **Correlation Explorer**: Discover relationships between different variables in the dataset

### How to Run

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

### Data Format

The dashboard expects a CSV file with startup data containing columns such as:
- `permalink`, `name`, `homepage_url`
- `category_list`, `market`
- `funding_total_usd`, `status`
- `country_code`, `state_code`, `region`, `city`
- `funding_rounds`, `founded_at`, `founded_month`, `founded_quarter`, `founded_year`
- `first_funding_at`, `last_funding_at`
- Various funding round types: `seed`, `venture`, `equity_crowdfunding`, etc.

### Structure

- `app.py`: Main application entry point
- `data_processor.py`: Data loading and preprocessing
- `utils.py`: Utility functions for visualization and formatting
- `pages/`: Individual analysis pages
  - `overview.py`: Key metrics and high-level insights
  - `funding_analysis.py`: Detailed funding patterns
  - `geographic_analysis.py`: Location-based insights
  - `temporal_analysis.py`: Time-based trends
  - `category_analysis.py`: Industry and market analysis
  - `correlation_analysis.py`: Variable relationships and patterns

### Sample Data

If no data file is provided, the application will generate sample data for demonstration purposes.