import pandas as pd
import numpy as np
import streamlit as st
import os
import json
from datetime import datetime

@st.cache_data
def load_data():
    """
    Load and preprocess the startup dataset.
    
    Returns:
        pd.DataFrame: Preprocessed dataframe
    """
    # Check if data file exists
    data_file = './data/investments_VC.csv'
    
    # For demonstration purposes, create sample data if file doesn't exist
    if not os.path.exists(data_file):
        st.warning("Sample data is being used. Please upload the actual dataset.")
        df = create_sample_data()
    else:
        # Read CSV with proper handling of number formatting
        df = pd.read_csv(data_file)
        
        # Convert funding columns to numeric, removing any currency symbols and commas
        funding_cols = [
            'funding_total_usd', 'seed', 'venture', 'equity_crowdfunding',
            'undisclosed', 'convertible_note', 'debt_financing', 'angel',
            'grant', 'private_equity', 'post_ipo_equity', 'post_ipo_debt',
            'secondary_market', 'product_crowdfunding', 'round_A', 'round_B',
            'round_C', 'round_D', 'round_E', 'round_F', 'round_G', 'round_H'
        ]
        
        for col in funding_cols:
            if col in df.columns:
                # Remove commas and convert to numeric
                df[col] = df[col].astype(str).str.replace(',', '').astype(float)
     # Check if data file exists
    state_file = './data/city_state_mapping.json'
    
    
    # First load the JSON as a dictionary
    with open(state_file, 'r') as f:
        state_data = json.load(f)

    # Then convert to DataFrame
    df_state = pd.DataFrame(list(state_data.items()), columns=['region', 'state'])

    master_list = [
        'Arunachal Pradesh', 'Assam', 'Chandigarh', 'Karnataka', 'Manipur',
        'Meghalaya', 'Mizoram', 'Nagaland', 'Punjab', 'Rajasthan', 'Sikkim',
        'Tripura', 'Uttarakhand', 'Telangana', 'Bihar', 'Kerala', 'Madhya Pradesh',
        'Andaman & Nicobar', 'Gujarat', 'Lakshadweep', 'Odisha',
        'Dadra and Nagar Haveli and Daman and Diu', 'Ladakh', 'Jammu & Kashmir',
        'Chhattisgarh', 'Delhi', 'Goa', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
        'Tamil Nadu', 'Uttar Pradesh', 'West Bengal', 'Andhra Pradesh', 'Puducherry',
        'Maharashtra'
    ]
    city_state_map = dict(zip(df_state["region"], df_state["state"]))
    #df_city_state_map = pd.DataFrame.from_dict(city_state_map, orient='index').reset_index()

    #df_city_state_map.columns = ['region', 'state']
    # Get the resolver function
    resolver_func = get_resolver(city_state_map, master_list)

    #df_state_resolved[["region", "state"]] = df_state["region"].apply(get_resolver)
    # 4. Apply resolver correctly - fixed version
    resolved_data = df_state["region"].apply(resolver_func)
    
    # Convert the Series of Series to DataFrame
    df_state_resolved = pd.DataFrame({
        'region': resolved_data.apply(lambda x: x[0]),
        'state': resolved_data.apply(lambda x: x[1])
    })

    
    df = pd.merge(
        df,
        df_state_resolved[['region', 'state']],  # Select only columns we need
        on='region',
        how='left'  # Keeps all rows from full_df even if no match in state_df
    )                    
    
    # Preprocess the data
    
    df = clean_data(df)
    df = preprocess_data(df)
    

    return df

def get_resolver(city_state_map, master_states):
    # Function to resolve city to state with master list validation
    def resolve_city_state(city):
        if city in city_state_map:
            state = city_state_map[city]
            if state in master_states:
                return pd.Series([city, state])
        return pd.Series([city, None])  # Or default value
    
    return resolve_city_state

def filter_country(df,flag):
    #flag = False
    if flag==True:
        df = df[df['country_code'].str.upper() == 'IND']
    return df

def clean_data(df_uncleaned):
    print("Investments shape is: ", df_uncleaned.shape)
    print(df_uncleaned.head(5))
    print(df_uncleaned.info())

    duplicates_count = df_uncleaned['permalink'].duplicated(keep=False).sum()
    print(f"Number of duplicated entries in 'permalink' column: {duplicates_count}")


    status_counts = df_uncleaned['status'].value_counts(dropna=False)

    check = len(df_uncleaned) - status_counts.get('acquired', 0) - status_counts.get('closed', 0) - status_counts.get('operating', 0)

    missing_values = df_uncleaned["status"].isna().sum()

    other = check - missing_values

    print(f"There are {status_counts.get('acquired', 0)} acquired companies")
    print(f"There are {status_counts.get('closed', 0)} closed companies")
    print(f"There are {status_counts.get('operating', 0)} operating companies")
    print(f"There are {missing_values} NaN values")
    print(f"There are {other} other values")

    # Data Cleaning
    # Remove duplicates
    df_clean = df_uncleaned.copy()

    # Keep data for India only
    # Check if 'country_code' column exists and is not empty
    if 'country_code' in df_clean.columns and not df_clean['country_code'].empty:
        # Convert 'country_code' to uppercase to ensure consistent comparison
        df_clean['country_code'] = df_clean['country_code'].str.upper()
    else:   
        print("Column 'country_code' does not exist or is empty.")  

    



    df_clean = df_clean.drop(["permalink", "homepage_url", "post_ipo_equity", "post_ipo_debt", "debt_financing"], axis=1)
    # Ensure column names are trimmed
    df_clean.columns = df_clean.columns.str.strip()

    # Directly convert 'funding_total_usd' to a float, thereby also transforming "-" to NaN
    df_clean['funding_total_usd'] = pd.to_numeric(df_clean['funding_total_usd'].str.replace(',', ''), errors='coerce')

    df_clean["funding_total_usd"].dtype



    # Since some column names have the wrong format, we fix it
    df_clean.rename(columns={' market ': 'market', ' funding_total_usd ': 'funding_total_usd'}, inplace=True)

    # Turning all of our Date Columns into pd.datetime, to ensure consistency and the right data type 
    df_clean['founded_at'] =  pd.to_datetime(df_clean['founded_at'], format='%Y-%m-%d', errors = 'coerce')
    df_clean['first_funding_at'] =  pd.to_datetime(df_clean['first_funding_at'], format='%Y-%m-%d', errors = 'coerce')
    df_clean['last_funding_at'] =  pd.to_datetime(df_clean['last_funding_at'], format='%Y-%m-%d', errors = 'coerce')
    df_clean['founded_year'] =  pd.to_datetime(df_clean['founded_year'], format='%Y', errors = 'coerce')
    df_clean['founded_month'] =  pd.to_datetime(df_clean['founded_month'], format='%Y-%m', errors = 'coerce')

    # Cleaning the Market column, since it has unnecessary spaces
    df_clean['market'] = df_clean['market'].str.strip()

    # Calculate the number of missing values for each column in df_clean
    missing_counts = df_clean.isnull().sum()

    # Calculate the percentage of missing values for each column
    missing_percentage = (missing_counts / len(df_clean)) * 100

    # Create a DataFrame to analyze missing data
    missing_data = pd.DataFrame({
        'Column': df_clean.columns,
        'Missing Values': missing_counts,
        'Percentage Missing (%)': missing_percentage
    }).sort_values(by='Percentage Missing (%)', ascending=False)

    print(missing_data)
    '''
    plt.figure(figsize=(15, 8))
    sns.barplot(x='Percentage Missing (%)', y='Column', data=missing_data)
    plt.title('Percentage of Missing Data by Feature')
    plt.xlabel('Percentage Missing (%)')
    plt.ylabel('Database Columns')
    plt.show()
    '''

    df_clean["founded_year"].dtypes
    df_clean["founded_year"].isna().sum()


    if not pd.api.types.is_datetime64_any_dtype(df_clean['founded_year']):
        df_clean['founded_year'] = pd.to_datetime(df_clean['founded_year'], errors='coerce', format='%Y')

    # Check if there are any non-conversible values that caused 'coerce' to produce NaT
    print("After conversion, null values:", df_clean['founded_year'].isnull().sum())

    #Convert datetime to integer year
    df_clean['founded_year'] = df_clean['founded_year'].dt.year

    '''
    Comment out the next line if you want to see the distribution of the founded_year column
    # Initialize the KNN imputer and impute
    imputer = KNNImputer(n_neighbors=5, weights="uniform")
    founded_year_imputed = imputer.fit_transform(df_clean[['founded_year']].astype(float))

    # Replace the original 'founded_year' column with the imputed values
    df_clean['founded_year'] = founded_year_imputed.round()  # Round to get integer year values

    # Check the imputation
    print("Null values after imputation:", df_clean['founded_year'].isnull().sum())
    '''
    # Since status is part of our target variable, has a lot of important information and cannot be properly imputed, we will drop all NaN´s in this column
    df_clean = df_clean.dropna(subset=["status"])

    print("Number of NaN: ", df_clean["status"].isna().sum())

    df_clean[['convertible_note', 'angel', 'grant', 'private_equity',
        'secondary_market', 'product_crowdfunding', 'round_A','round_B',
        'round_C', 'round_D', 'round_E', 'round_F', 'round_G','round_H']].fillna(0)

    
    return df_clean

def preprocess_data(df):
    """
    Preprocess the dataframe for analysis.
    
    Args:
        df (pd.DataFrame): Raw dataframe
        
    Returns:
        pd.DataFrame: Preprocessed dataframe
    """
    # Convert columns to appropriate data types
    numeric_cols = ['funding_total_usd', 'funding_rounds', 'seed', 'venture', 
                   'equity_crowdfunding', 'angel', 'grant', 'private_equity',
                   'round_A', 'round_B', 'round_C', 'round_D', 'round_E', 
                   'round_F', 'round_G', 'round_H']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convert date columns to datetime
    date_cols = ['founded_at', 'first_funding_at', 'last_funding_at']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
    # Extract year from founded_at if founded_year is not available
    if 'founded_at' in df.columns and 'founded_year' not in df.columns:
        df['founded_year'] = df['founded_at'].dt.year
    
    # Extract month from founded_at if founded_month is not available
    if 'founded_at' in df.columns and 'founded_month' not in df.columns:
        df['founded_month'] = df['founded_at'].dt.month
    
    # Extract quarter from founded_at if founded_quarter is not available
    if 'founded_at' in df.columns and 'founded_quarter' not in df.columns:
        df['founded_quarter'] = df['founded_at'].dt.quarter
    
    # Calculate funding age (years between first and last funding)
    if 'first_funding_at' in df.columns and 'last_funding_at' in df.columns:
        df['funding_age_years'] = (df['last_funding_at'] - df['first_funding_at']).dt.days / 365.25
        
    # Calculate company age (years since founding)
    if 'founded_at' in df.columns:
        df['company_age_years'] = (datetime.now() - df['founded_at']).dt.days / 365.25
    
    # Process category_list to create individual categories
    if 'category_list' in df.columns:
        # Remove leading/trailing pipes and spaces
        df['category_list'] = df['category_list'].str.strip('|').str.strip()
        df['categories'] = df['category_list'].str.split('|')
        df['category_count'] = df['categories'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        
        # Extract main category (first in the list)
        df['main_category'] = df['categories'].apply(
            lambda x: x[0].strip() if isinstance(x, list) and len(x) > 0 else 'Unknown'
        )
    
    # Fill missing values in categorical columns
    categorical_cols = ['country_code', 'state_code', 'city', 'region', 'market', 'status']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')
    
    # Filter for India
    #df = df[df['country_code'].str.upper() == 'IND']
    

    return df

def create_sample_data():
    """
    Create sample data for demonstration purposes.
    
    Returns:
        pd.DataFrame: Sample dataframe
    """
    # Generate random data
    n_samples = 500
    
    # Sample companies, markets, and countries
    companies = [f"Company {i}" for i in range(1, n_samples + 1)]
    
    markets = [
        'Software', 'E-Commerce', 'FinTech', 'Health', 'AI', 'Mobile', 
        'Enterprise', 'Advertising', 'Games', 'Education', 'Hardware', 'IoT',
        'Security', 'Media', 'Analytics', 'CleanTech', 'Biotech', 'Real Estate'
    ]
    
    categories = [
        'Software|SaaS|Enterprise', 'E-Commerce|Retail|Marketplace', 
        'FinTech|Payments|Blockchain', 'Health|MedTech|Wellness',
        'AI|Machine Learning|Big Data', 'Mobile|Apps|Platforms',
        'EdTech|Learning|Training', 'Hardware|Devices|IoT',
        'Media|Entertainment|Social', 'Security|Privacy|Encryption'
    ]
    
    countries = ['USA', 'GBR', 'CHN', 'IND', 'DEU', 'FRA', 'ISR', 'CAN', 'BRA', 'AUS']
    regions = ['North America', 'Europe', 'Asia', 'South America', 'Africa', 'Oceania']
    cities = ['San Francisco', 'New York', 'London', 'Berlin', 'Beijing', 'Tel Aviv', 'Bangalore', 'Tokyo', 'Paris', 'Sydney']
    statuses = ['operating', 'acquired', 'closed', 'ipo']
    
    # Create DataFrame
    data = {
        'permalink': [f"company_{i}" for i in range(1, n_samples + 1)],
        'name': companies,
        'homepage_url': [f"https://www.company{i}.com" for i in range(1, n_samples + 1)],
        'category_list': np.random.choice(categories, n_samples),
        'market': np.random.choice(markets, n_samples),
        'funding_total_usd': np.random.exponential(scale=5000000, size=n_samples),
        'status': np.random.choice(statuses, n_samples, p=[0.7, 0.15, 0.1, 0.05]),
        'country_code': np.random.choice(countries, n_samples),
        'state_code': np.random.choice(['CA', 'NY', 'TX', 'MA', 'WA'], n_samples),
        'region': np.random.choice(regions, n_samples),
        'city': np.random.choice(cities, n_samples),
        'funding_rounds': np.random.randint(1, 6, n_samples),
        'founded_year': np.random.randint(2000, 2022, n_samples),
        'founded_month': np.random.randint(1, 13, n_samples),
        'founded_quarter': np.random.randint(1, 5, n_samples),
    }
    
    # Create founded_at dates
    founded_at = []
    for i in range(n_samples):
        year = data['founded_year'][i]
        month = data['founded_month'][i]
        day = np.random.randint(1, 28)
        founded_at.append(f"{year}-{month:02d}-{day:02d}")
    
    data['founded_at'] = founded_at
    
    # Create funding rounds data
    for round_type in ['seed', 'venture', 'equity_crowdfunding', 'angel', 'grant', 'private_equity']:
        data[round_type] = np.random.choice([0, np.random.exponential(scale=1000000)], n_samples)
    
    for round_letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        col_name = f'round_{round_letter}'
        # Decrease probability of higher rounds
        prob = max(0.5 - (ord(round_letter) - ord('A')) * 0.1, 0.05)
        data[col_name] = np.random.choice(
            [0, np.random.exponential(scale=2000000 * (1 + (ord(round_letter) - ord('A'))))], 
            n_samples, 
            p=[1-prob, prob]
        )
    
    # Create dataframe
    df = pd.DataFrame(data)
    
    # Generate first_funding_at and last_funding_at
    df['first_funding_at'] = pd.to_datetime(df['founded_at']) + pd.to_timedelta(np.random.randint(30, 365, n_samples), unit='D')
    df['last_funding_at'] = df['first_funding_at'] + pd.to_timedelta(np.random.randint(0, 2000, n_samples), unit='D')
    
    return df

def upload_data():
    """
    Let users upload their own dataset
    
    Returns:
        pd.DataFrame: Uploaded and processed dataframe
    """
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df = preprocess_data(df)
            return df
        except Exception as e:
            st.error(f"Error: {e}")
            return None
    return None