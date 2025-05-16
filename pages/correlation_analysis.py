import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils import (
    create_correlation_matrix,
    create_scatter_plot,
    create_histogram,
    create_heatmap
)
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

def show_correlation_analysis(df):
    """
    Display the correlation analysis page with relationships between variables.
    
    Args:
        df (pd.DataFrame): Filtered dataframe
    """
    st.title("Correlation Explorer")
    st.write("Explore relationships between different variables in the dataset.")
    
    # Check if numeric columns exist
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.warning("No numeric columns available for correlation analysis.")
        return
    
    # Correlation matrix
    st.subheader("Correlation Matrix")
    
    # Let user select columns for correlation
    default_corr_cols = [col for col in [
        'funding_total_usd', 'funding_rounds', 'founded_year',
        'category_count', 'company_age_years', 'funding_age_years'
    ] if col in numeric_cols]
    
    selected_corr_cols = st.multiselect(
        "Select columns for correlation analysis",
        options=numeric_cols,
        default=default_corr_cols if default_corr_cols else numeric_cols[:min(5, len(numeric_cols))]
    )
    
    if selected_corr_cols:
        # Create correlation matrix
        corr_fig = create_correlation_matrix(
            df,
            selected_corr_cols,
            'Correlation Matrix of Selected Variables'
        )
        st.plotly_chart(corr_fig, use_container_width=True)
    else:
        st.info("Please select at least one column for correlation analysis.")
    
    # Scatter plot explorer
    st.subheader("Scatter Plot Explorer")
    
    # Create columns for inputs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        x_col = st.selectbox(
            "X-Axis",
            options=numeric_cols,
            index=numeric_cols.index('funding_total_usd') if 'funding_total_usd' in numeric_cols else 0
        )
    
    with col2:
        y_col = st.selectbox(
            "Y-Axis",
            options=numeric_cols,
            index=numeric_cols.index('funding_rounds') if 'funding_rounds' in numeric_cols else min(1, len(numeric_cols)-1)
        )
    
    with col3:
        color_options = ['None'] + df.select_dtypes(include=['object', 'category']).columns.tolist() + numeric_cols
        color_col = st.selectbox(
            "Color By",
            options=color_options,
            index=color_options.index('status') if 'status' in color_options else 0
        )
        color_col = None if color_col == 'None' else color_col
    
    with col4:
        size_options = ['None'] + numeric_cols
        size_col = st.selectbox(
            "Size By",
            options=size_options,
            index=0
        )
        size_col = None if size_col == 'None' else size_col
    
    # Use log scale option
    use_log_x = st.checkbox("Use logarithmic scale for X-Axis (better for skewed distributions)", value=True)
    use_log_y = st.checkbox("Use logarithmic scale for Y-Axis", value=False)
    
    # Create scatter plot
    if x_col != y_col:
        # Create figure
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            size=size_col,
            title=f'Relationship between {x_col} and {y_col}',
            opacity=0.7,
            log_x=use_log_x,
            log_y=use_log_y
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select different columns for X and Y axes.")
    
    # Distribution comparison
    st.subheader("Distribution Comparison")
    
    if 'status' in df.columns:
        # Select column for distribution comparison
        dist_col = st.selectbox(
            "Select column for distribution comparison",
            options=numeric_cols,
            index=numeric_cols.index('funding_total_usd') if 'funding_total_usd' in numeric_cols else 0
        )
        
        # Use log scale option
        use_log_dist = st.checkbox("Use logarithmic scale for distribution", value=True)
        
        # Create figure
        fig = px.histogram(
            df,
            x=dist_col,
            color='status',
            marginal='box',
            title=f'Distribution of {dist_col} by Company Status',
            log_x=use_log_dist,
            barmode='overlay',
            opacity=0.7
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Funding vs. age analysis
    st.subheader("Funding vs. Age Analysis")
    
    if all(col in df.columns for col in ['company_age_years', 'funding_total_usd']):
        # Create scatter plot
        fig = create_scatter_plot(
            df,
            'company_age_years',
            'funding_total_usd',
            'Relationship between Company Age and Total Funding',
            color_col='market' if 'market' in df.columns else None,
            size_col='funding_rounds' if 'funding_rounds' in df.columns else None
        )
        
        # Add logarithmic y-axis
        fig.update_layout(
            yaxis_type='log'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Principal Component Analysis (PCA)
    st.subheader("Principal Component Analysis")
    
    if len(numeric_cols) >= 3:
        # Let user select columns for PCA
        pca_cols = st.multiselect(
            "Select columns for PCA",
            options=numeric_cols,
            default=default_corr_cols if default_corr_cols else numeric_cols[:min(5, len(numeric_cols))]
        )
        
        if len(pca_cols) >= 3:
            # Create dataframe for PCA
            pca_df = df[pca_cols].copy()
            
            # Replace infs and drop rows with NaN
            pca_df = pca_df.replace([np.inf, -np.inf], np.nan).dropna()
            
            if len(pca_df) > 10:  # Need enough samples for PCA
                # Scale data
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(pca_df)
                
                # Apply PCA
                pca = PCA(n_components=2)
                principal_components = pca.fit_transform(scaled_data)
                
                # Create dataframe with results
                pca_result_df = pd.DataFrame(
                    data=principal_components,
                    columns=['PC1', 'PC2']
                )
                
                # Add color column if available
                if 'status' in df.columns:
                    pca_result_df['status'] = df.loc[pca_df.index, 'status'].values
                
                if 'market' in df.columns:
                    pca_result_df['market'] = df.loc[pca_df.index, 'market'].values
                
                # Create scatter plot
                if 'market' in pca_result_df.columns:
                    # Get top markets
                    top_markets = df['market'].value_counts().nlargest(10).index.tolist()
                    pca_result_df = pca_result_df[pca_result_df['market'].isin(top_markets)]
                    
                    fig = px.scatter(
                        pca_result_df,
                        x='PC1',
                        y='PC2',
                        color='market',
                        title='PCA Visualization of Startup Data',
                        labels={'PC1': f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)',
                                'PC2': f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)'}
                    )
                elif 'status' in pca_result_df.columns:
                    fig = px.scatter(
                        pca_result_df,
                        x='PC1',
                        y='PC2',
                        color='status',
                        title='PCA Visualization of Startup Data',
                        labels={'PC1': f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)',
                                'PC2': f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)'}
                    )
                else:
                    fig = px.scatter(
                        pca_result_df,
                        x='PC1',
                        y='PC2',
                        title='PCA Visualization of Startup Data',
                        labels={'PC1': f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)',
                                'PC2': f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)'}
                    )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Feature importance
                st.subheader("Feature Importance in PCA")
                
                # Calculate loadings
                loadings = pd.DataFrame(
                    pca.components_.T,
                    columns=['PC1', 'PC2'],
                    index=pca_cols
                )
                
                # Create bar chart for PC1
                pc1_fig = px.bar(
                    x=loadings.index,
                    y=loadings['PC1'],
                    title='Feature Loadings for Principal Component 1',
                    labels={'x': 'Feature', 'y': 'Loading'}
                )
                st.plotly_chart(pc1_fig, use_container_width=True)
                
                # Create bar chart for PC2
                pc2_fig = px.bar(
                    x=loadings.index,
                    y=loadings['PC2'],
                    title='Feature Loadings for Principal Component 2',
                    labels={'x': 'Feature', 'y': 'Loading'}
                )
                st.plotly_chart(pc2_fig, use_container_width=True)
            else:
                st.warning("Not enough complete data points for PCA after removing missing values.")
        else:
            st.info("Please select at least 3 columns for PCA.")
    else:
        st.info("Not enough numeric columns available for PCA.")