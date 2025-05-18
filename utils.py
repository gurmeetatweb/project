import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set the page configuration with styling
def set_page_config():
    st.set_page_config(
        page_title="Startup Ecosystem Analysis",
        page_icon="./favicon.ico",
        layout="centered",        
        initial_sidebar_state="expanded",        
    )

    
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            background-color: #f8f9fa;
        }
        .stApp {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .stSidebar {
            background-color: #ffffff;
        }
        .metric-card {
            background-color: white;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #4F8BF9;
        }
        .metric-label {
            font-size: 1rem;
            color: #7F8C8D;
        }
        .plot-container {
            background-color: white;
            border-radius: 5px;
            padding: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }        
        </style>
    """, unsafe_allow_html=True)

def display_metric_card(title, value, delta=None, delta_color="normal", help_text=None):
    """
    Display a metric in a styled card.
    
    Args:
        title (str): Metric title
        value (str/int/float): Metric value
        delta (str/int/float, optional): Delta value for the metric
        delta_color (str, optional): Color of delta (normal, inverse, off)
        help_text (str, optional): Help text to display with the metric
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )

def display_metric_row(metrics_data):
    """
    Display a row of metrics in cards.
    
    Args:
        metrics_data (list): List of dicts with metric data
    """
    cols = st.columns(len(metrics_data))
    for i, metric in enumerate(metrics_data):
        with cols[i]:
            display_metric_card(
                title=metric['title'],
                value=metric['value'],
                delta=metric.get('delta'),
                delta_color=metric.get('delta_color', 'normal'),
                help_text=metric.get('help_text')
            )

def format_large_number(num):
    """
    Format large numbers with appropriate suffixes (K, M, B).
    
    Args:
        num (float/int): Number to format
        
    Returns:
        str: Formatted number
    """
    if pd.isna(num):
        return "N/A"
    
    if num == 0:
        return "0"
        
    magnitude = 0
    suffixes = ['', 'K', 'M', 'B', 'T']
    while abs(num) >= 1000 and magnitude < len(suffixes)-1:
        magnitude += 1
        num /= 1000.0
    
    # Format with appropriate decimal places
    if magnitude == 0:
        return f"{num:.0f}"
    else:
        if num >= 100:
            return f"{num:.0f}{suffixes[magnitude]}"
        elif num >= 10:
            return f"{num:.1f}{suffixes[magnitude]}"
        else:
            return f"{num:.2f}{suffixes[magnitude]}"

def create_plotly_choropleth(df, value_column, title, color_scale='Blues'):
    """
    Create a plotly choropleth map.
    
    Args:
        df (pd.DataFrame): DataFrame with country data
        value_column (str): Column with values to plot
        title (str): Chart title
        color_scale (str): Color scale for the map
        
    Returns:
        plotly figure: Choropleth map
    """
    # Group by country and get the count or sum
    country_data = df.groupby('country_code')[value_column].sum().reset_index()
    
    fig = px.choropleth(
        country_data,
        locations='country_code',
        color=value_column,
        hover_name='country_code',
        color_continuous_scale=color_scale,
        projection='natural earth',
        title=title
    )
    
    fig.update_layout(
        margin={"r":0,"t":50,"l":0,"b":0},
        coloraxis_colorbar=dict(
            title=value_column
        )
    )
    
    return fig

def create_heatmap(df, x_col, y_col, value_col, title):
    """
    Create a heatmap visualization.
    
    Args:
        df (pd.DataFrame): DataFrame with data
        x_col (str): Column for x-axis
        y_col (str): Column for y-axis
        value_col (str): Column with values
        title (str): Chart title
        
    Returns:
        plotly figure: Heatmap visualization
    """
    # Create pivot table for heatmap
    pivot_data = df.pivot_table(
        values=value_col, 
        index=y_col, 
        columns=x_col, 
        aggfunc='mean'
    ).fillna(0)
    
    fig = px.imshow(
        pivot_data,
        labels=dict(x=x_col, y=y_col, color=value_col),
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale='Blues',
        title=title
    )
    
    fig.update_layout(
        height=600,
        xaxis_nticks=len(pivot_data.columns),
        yaxis_nticks=len(pivot_data.index)
    )
    
    return fig
'''
def create_wordcloud(text_series, title, max_words=100):
    """
    Create a word cloud visualization.
    
    Args:
        text_series (pd.Series): Series with text data
        title (str): Chart title
        max_words (int): Maximum number of words to include
        
    Returns:
        matplotlib figure: Word cloud visualization
    """
    # Combine all text
    text = ' '.join(text_series.dropna().astype(str))
    
    # Create word cloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        max_words=max_words, 
        background_color='white',
        colormap='viridis'
    ).generate(text)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(title, fontsize=16)
    
    return fig
'''
def create_time_series(df, time_col, value_col, title, color='#4F8BF9'):
    """
    Create a time series visualization.
    
    Args:
        df (pd.DataFrame): DataFrame with data
        time_col (str): Column with time data
        value_col (str): Column with values
        title (str): Chart title
        color (str): Line color
        
    Returns:
        plotly figure: Time series visualization
    """
    # Group by time column
    time_data = df.groupby(time_col)[value_col].mean().reset_index()
    
    fig = px.line(
        time_data,
        x=time_col,
        y=value_col,
        title=title,
        markers=True
    )
    
    fig.update_traces(line_color=color, line_width=3)
    
    fig.update_layout(
        xaxis_title=time_col,
        yaxis_title=value_col,
        hovermode="x"
    )
    
    return fig

def create_bar_chart(df, x_col, y_col, title, color='#4F8BF9', horizontal=False):
    """
    Create a bar chart visualization.
    
    Args:
        df (pd.DataFrame): DataFrame with data
        x_col (str): Column for x-axis
        y_col (str): Column for y-axis
        title (str): Chart title
        color (str): Bar color
        horizontal (bool): Whether to create a horizontal bar chart
        
    Returns:
        plotly figure: Bar chart visualization
    """
    if horizontal:
        fig = px.bar(
            df,
            y=x_col,
            x=y_col,
            title=title,
            orientation='h',
            color_discrete_sequence=[color]
        )
    else:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            title=title,
            color_discrete_sequence=[color]
        )
    
    fig.update_layout(
        xaxis_title=x_col if not horizontal else y_col,
        yaxis_title=y_col if not horizontal else x_col,
        hovermode="closest"
    )
    
    return fig

def create_scatter_plot(df, x_col, y_col, title, color_col=None, size_col=None):
    """
    Create a scatter plot visualization.
    
    Args:
        df (pd.DataFrame): DataFrame with data
        x_col (str): Column for x-axis
        y_col (str): Column for y-axis
        title (str): Chart title
        color_col (str, optional): Column for point colors
        size_col (str, optional): Column for point sizes
        
    Returns:
        plotly figure: Scatter plot visualization
    """
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        size=size_col,
        title=title,
        opacity=0.7
    )
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col
    )
    
    return fig

def create_pie_chart(df, names_col, values_col, title):
    """
    Create a pie chart visualization.
    
    Args:
        df (pd.DataFrame): DataFrame with data
        names_col (str): Column for slice names
        values_col (str): Column for slice values
        title (str): Chart title
        
    Returns:
        plotly figure: Pie chart visualization
    """
    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        title=title
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def create_histogram(df, column, title, nbins=30, color='#4F8BF9'):
    """
    Create a histogram visualization.
    
    Args:
        df (pd.DataFrame): DataFrame with data
        column (str): Column to plot
        title (str): Chart title
        nbins (int): Number of bins
        color (str): Bar color
        
    Returns:
        plotly figure: Histogram visualization
    """
    fig = px.histogram(
        df,
        x=column,
        nbins=nbins,
        title=title,
        color_discrete_sequence=[color]
    )
    
    fig.update_layout(
        xaxis_title=column,
        yaxis_title="Count"
    )
    
    return fig

def create_box_plot(df, x_col, y_col, title, color='#4F8BF9'):
    """
    Create a box plot visualization.
    
    Args:
        df (pd.DataFrame): DataFrame with data
        x_col (str): Column for x-axis (categories)
        y_col (str): Column for y-axis (values)
        title (str): Chart title
        color (str): Box color
        
    Returns:
        plotly figure: Box plot visualization
    """
    fig = px.box(
        df,
        x=x_col,
        y=y_col,
        title=title,
        color_discrete_sequence=[color]
    )
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col
    )
    
    return fig

def create_correlation_matrix(df, columns, title):
    """
    Create a correlation matrix visualization.
    
    Args:
        df (pd.DataFrame): DataFrame with data
        columns (list): Columns to include in correlation
        title (str): Chart title
        
    Returns:
        plotly figure: Correlation matrix visualization
    """
    # Calculate correlation matrix
    corr = df[columns].corr()
    
    # Create heatmap
    fig = px.imshow(
        corr,
        x=corr.columns,
        y=corr.columns,
        color_continuous_scale='RdBu_r',
        title=title,
        zmin=-1,
        zmax=1
    )
    
    # Add correlation values as text
    for i, row in enumerate(corr.values):
        for j, val in enumerate(row):
            fig.add_annotation(
                x=j,
                y=i,
                text=f"{val:.2f}",
                showarrow=False,
                font=dict(
                    color="white" if abs(val) > 0.5 else "black"
                )
            )
    
    fig.update_layout(
        height=600,
        width=800
    )
    
    return fig