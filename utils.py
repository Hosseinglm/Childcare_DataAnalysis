import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np


def load_and_process_data(file_path):
    """Load and preprocess the childcare data."""
    df = pd.read_csv(file_path)

    # Convert dates to datetime
    date_columns = ['Survey Response Date [GMT]', 'Survey Sent Date [GMT]', 'Start Date']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col])

    # Convert ratings to numeric scores
    rating_columns = ['Ambience And Atmosphere', 'Curriculum and Activities',
                      'Environment And Facilities', 'Information and Experience',
                      'Questions', 'Nutritious Meals', 'Value For Money']

    rating_map = {
        '5. Strongly Agree': 5,
        '4. Agree': 4,
        '3. Neither Agree nor Disagree': 3,
        '2. Disagree': 2,
        '1. Strongly Disagree': 1
    }

    for col in rating_columns:
        df[f'{col}_Score'] = df[col].map(rating_map)

    return df


def get_nps_distribution(df):
    """Calculate NPS distribution percentages."""
    total = len(df)
    promoters = (df['NPS Label'] == 'Promoter').sum()
    passives = (df['NPS Label'] == 'Neutral').sum()
    detractors = (df['NPS Label'] == 'Detractor').sum()

    return {
        'Promoters': (promoters / total) * 100,
        'Passives': (passives / total) * 100,
        'Detractors': (detractors / total) * 100
    }


def create_nps_distribution_chart(df):
    """Create NPS distribution pie chart."""
    dist = get_nps_distribution(df)
    fig = go.Figure(data=[go.Pie(
        labels=list(dist.keys()),
        values=list(dist.values()),
        hole=.3,
        marker_colors=['#00B050', '#FFC000', '#FF0000']
    )])
    fig.update_layout(title='NPS Distribution')
    return fig


def create_correlation_heatmap(df):
    """Create correlation heatmap for satisfaction metrics."""
    # Select only the score columns and NPS
    metrics = ['NPS', 'Ambience And Atmosphere', 'Curriculum and Activities',
               'Environment And Facilities', 'Information and Experience',
               'Questions', 'Nutritious Meals', 'Value For Money']

    # Create correlation matrix
    corr_matrix = df[metrics].corr()

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=metrics,
        y=metrics,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        text=np.round(corr_matrix, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        hoverongaps=False
    ))

    # Update layout
    fig.update_layout(
        title='Correlation between Satisfaction Metrics',
        height=700,
        width=800,
        xaxis_tickangle=-45,
        yaxis_tickangle=0
    )

    return fig


def analyze_feedback_categories(df):
    """Analyze feedback categories and create bar chart."""
    # all_categories = []
    # df['NPS Feedback Categories'].fillna('').str.strip('"').apply(
    #     lambda x: all_categories.extend([c.strip() for c in x.split(',') if c.strip()])
    # )
    #
    # category_counts = pd.Series(all_categories).value_counts()
    categories = []
    for col in ['NPS Feedback Categories', 'Improvement Feedback Categories']:
        df[col] = df[col].fillna('')  # Fill NaNs with empty string
        categories.extend([
            cat.strip('"') for row in df[col] if row
            for cat in str(row).split(',') if cat.strip() and cat.lower() != 'nan'  # Remove empty and 'nan' strings
        ])

    category_counts = pd.Series(categories).value_counts()

    # Remove 'nan' from the counts if it still exists
    category_counts = category_counts[category_counts.index != 'nan']

    fig = px.bar(
        y=category_counts.values[:10],
        x=category_counts.index[:10],
        title='Top 10 Feedback Categories'
    )
    fig.update_traces(marker_color='#FF4B4B')
    fig.update_layout(
        xaxis_title="Feedback Category",
        yaxis_title="Count",
        xaxis_tickangle=-45
    )
    return fig


def calculate_weekly_response_rate(df):
    """Calculate and visualize weekly response rates."""
    weekly_counts = df.resample('W', on='Survey Response Date [GMT]').size()

    fig = px.line(
        x=weekly_counts.index,
        y=weekly_counts.values,
        title='Weekly Response Rate'
    )
    fig.update_traces(line_color='#FF4B4B')
    return fig


def create_monthly_trends(df):
    """Create monthly trends for key metrics."""
    # Group by month and calculate mean for each metric
    monthly_trends = df.groupby('Response Month (YYYY-MM)').agg({
        'NPS': 'mean',
        'Ambience And Atmosphere': 'mean',
        'Curriculum and Activities': 'mean',
        'Value For Money': 'mean'
    }).round(2)

    # Create the figure
    fig = go.Figure()

    # Define metrics and their colors
    metrics = {
        'NPS': '#FF4B4B',
        'Ambience And Atmosphere': '#00B050',
        'Curriculum and Activities': '#FFC000',
        'Value For Money': '#4B4BFF'
    }

    # Plot each metric
    for metric, color in metrics.items():
        fig.add_trace(go.Scatter(
            x=monthly_trends.index,
            y=monthly_trends[metric],
            name=metric,
            mode='lines+markers',
            line=dict(color=color, width=2),
            marker=dict(size=8)
        ))

    # Update layout
    fig.update_layout(
        title='Monthly Trends in Key Metrics',
        xaxis_title='Month',
        yaxis_title='Average Score',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    # Set axis ranges to match the screenshot
    fig.update_yaxes(range=[8.45, 8.8])

    # Update gridline density and axis tick formatting
    fig.update_xaxes(
        dtick="M1",
        tickformat="%b %Y",
        tickangle=-45,
        gridcolor='LightGrey',
        showgrid=True,
        gridwidth=1
    )
    fig.update_yaxes(
        dtick=0.05,
        gridcolor='LightGrey',
        showgrid=True,
        gridwidth=1
    )

    return fig


def calculate_nps_score(df):
    """Calculate NPS score from promoters and detractors."""
    promoters = (df['NPS Label'] == 'Promoter').mean()
    detractors = (df['NPS Label'] == 'Detractor').mean()
    nps_score = (promoters - detractors) * 100
    return round(nps_score, 1)


def get_top_concerns(df):
    """Extract top improvement categories."""
    all_concerns = []
    # Clean and process feedback categories
    df['Improvement Feedback Categories'].fillna('').str.strip('"').apply(
        lambda x: all_concerns.extend([c.strip().strip('"') for c in x.split(',') if c.strip()])
    )
    concern_counts = pd.Series(all_concerns).value_counts()
    return concern_counts


def create_nps_trend(df):
    """Create NPS trend over time."""
    monthly_nps = df.groupby('Response Month (YYYY-MM)').apply(
        lambda x: calculate_nps_score(x)
    ).reset_index()
    monthly_nps.columns = ['Month', 'NPS Score']

    fig = px.line(monthly_nps, x='Month', y='NPS Score',
                  title='NPS Score Trend Over Time')
    fig.update_traces(line_color='#FF4B4B')
    return fig


def create_satisfaction_heatmap(df):
    """Create satisfaction metrics heatmap."""
    metrics = ['Ambience And Atmosphere', 'Curriculum and Activities',
               'Environment And Facilities', 'Information and Experience',
               'Questions', 'Nutritious Meals', 'Value For Money']

    # Calculate average scores, handling NaN values
    avg_scores = {}
    for metric in metrics:
        scores = df[f'{metric}_Score']
        avg_scores[metric] = scores.mean()

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=[[score] for score in avg_scores.values()],
        y=list(avg_scores.keys()),
        x=['Average Score'],
        colorscale='RdYlGn',
        text=[[f'{score:.2f}'] for score in avg_scores.values()],
        texttemplate='%{text}',
        textfont={"size": 12},
        showscale=True
    ))

    fig.update_layout(title='Satisfaction Metrics Overview')
    return fig
