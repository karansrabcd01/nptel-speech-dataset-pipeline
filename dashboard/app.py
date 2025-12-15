"""
Task 5: Interactive Dashboard for Dataset Visualization
Displays comprehensive statistics and visualizations of the speech dataset.
"""

import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from collections import Counter
import string

# Configuration
MANIFEST_FILE = "../output/train_manifest.jsonl"
APP_PORT = 8050

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True
)

app.title = "AI4Bharat Speech Dataset Dashboard"

def load_manifest_data():
    """Load and parse manifest file."""
    if not os.path.exists(MANIFEST_FILE):
        return None
    
    data = []
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            data.append(entry)
    
    return pd.DataFrame(data)

def calculate_statistics(df):
    """Calculate global statistics from dataframe."""
    if df is None or df.empty:
        return {}
    
    # Calculate word and character counts
    df['word_count'] = df['text'].apply(lambda x: len(x.split()))
    df['char_count'] = df['text'].apply(lambda x: len(x))
    
    # Calculate vocabulary
    all_words = ' '.join(df['text'].tolist()).split()
    vocabulary = set(all_words)
    
    # Calculate alphabet distribution
    all_text = ''.join(df['text'].tolist())
    alphabet_counts = Counter(c.lower() for c in all_text if c.isalpha())
    
    stats = {
        'total_files': len(df),
        'total_duration': df['duration'].sum(),
        'total_hours': df['duration'].sum() / 3600,
        'total_utterances': len(df),
        'vocabulary_size': len(vocabulary),
        'total_words': df['word_count'].sum(),
        'total_characters': df['char_count'].sum(),
        'avg_duration': df['duration'].mean(),
        'min_duration': df['duration'].min(),
        'max_duration': df['duration'].max(),
        'avg_words': df['word_count'].mean(),
        'avg_chars': df['char_count'].mean(),
        'alphabet_counts': alphabet_counts
    }
    
    return stats

def create_global_stats_cards(stats):
    """Create statistics cards for the dashboard."""
    if not stats:
        return html.Div("No data available", className="text-center text-muted")
    
    cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📊 Total Files", className="card-title"),
                    html.H2(f"{stats['total_files']:,}", className="text-primary")
                ])
            ], className="mb-3 shadow")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("⏱️ Total Duration", className="card-title"),
                    html.H2(f"{stats['total_hours']:.2f} hrs", className="text-success")
                ])
            ], className="mb-3 shadow")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("💬 Total Words", className="card-title"),
                    html.H2(f"{stats['total_words']:,}", className="text-info")
                ])
            ], className="mb-3 shadow")
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📚 Vocabulary Size", className="card-title"),
                    html.H2(f"{stats['vocabulary_size']:,}", className="text-warning")
                ])
            ], className="mb-3 shadow")
        ], width=3),
    ])
    
    return cards

def create_alphabet_chart(alphabet_counts):
    """Create alphabet distribution bar chart."""
    if not alphabet_counts:
        return go.Figure()
    
    # Sort by alphabet
    sorted_alphabet = sorted(alphabet_counts.items())
    letters = [item[0] for item in sorted_alphabet]
    counts = [item[1] for item in sorted_alphabet]
    
    fig = go.Figure(data=[
        go.Bar(
            x=letters,
            y=counts,
            marker=dict(
                color=counts,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Frequency")
            ),
            text=counts,
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Alphabet Distribution",
        xaxis_title="Letter",
        yaxis_title="Frequency",
        template="plotly_dark",
        height=400,
        showlegend=False
    )
    
    return fig

def create_duration_histogram(df):
    """Create duration distribution histogram."""
    if df is None or df.empty:
        return go.Figure()
    
    fig = px.histogram(
        df,
        x='duration',
        nbins=50,
        title="Duration Distribution (per utterance)",
        labels={'duration': 'Duration (seconds)', 'count': 'Number of Files'},
        template="plotly_dark",
        color_discrete_sequence=['#00d4ff']
    )
    
    fig.update_layout(
        xaxis_title="Duration (seconds)",
        yaxis_title="Count",
        height=400,
        showlegend=False
    )
    
    return fig

def create_word_count_histogram(df):
    """Create word count distribution histogram."""
    if df is None or df.empty:
        return go.Figure()
    
    fig = px.histogram(
        df,
        x='word_count',
        nbins=50,
        title="Number of Words (per utterance)",
        labels={'word_count': 'Word Count', 'count': 'Number of Files'},
        template="plotly_dark",
        color_discrete_sequence=['#00ff88']
    )
    
    fig.update_layout(
        xaxis_title="Number of Words",
        yaxis_title="Count",
        height=400,
        showlegend=False
    )
    
    return fig

def create_char_count_histogram(df):
    """Create character count distribution histogram."""
    if df is None or df.empty:
        return go.Figure()
    
    fig = px.histogram(
        df,
        x='char_count',
        nbins=50,
        title="Number of Characters (per utterance)",
        labels={'char_count': 'Character Count', 'count': 'Number of Files'},
        template="plotly_dark",
        color_discrete_sequence=['#ff6b6b']
    )
    
    fig.update_layout(
        xaxis_title="Number of Characters",
        yaxis_title="Count",
        height=400,
        showlegend=False
    )
    
    return fig

# Load data
df = load_manifest_data()
stats = calculate_statistics(df)

# Create layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🎙️ AI4Bharat Speech Dataset Dashboard", className="text-center mb-4 mt-4"),
            html.P("Interactive visualization of NPTEL Deep Learning course dataset", 
                   className="text-center text-muted mb-4")
        ])
    ]),
    
    html.Hr(),
    
    # Global Statistics Cards
    html.H3("📊 Global Statistics", className="mt-4 mb-3"),
    create_global_stats_cards(stats),
    
    html.Hr(className="my-4"),
    
    # Alphabet Distribution
    html.H3("🔤 Alphabet Distribution", className="mt-4 mb-3"),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='alphabet-chart',
                figure=create_alphabet_chart(stats.get('alphabet_counts', {}))
            )
        ])
    ]),
    
    html.Hr(className="my-4"),
    
    # Duration and Word Count Distributions
    html.H3("📈 Distribution Analysis", className="mt-4 mb-3"),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='duration-histogram',
                figure=create_duration_histogram(df)
            )
        ], width=6),
        
        dbc.Col([
            dcc.Graph(
                id='word-count-histogram',
                figure=create_word_count_histogram(df)
            )
        ], width=6),
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='char-count-histogram',
                figure=create_char_count_histogram(df)
            )
        ], width=12),
    ], className="mt-3"),
    
    html.Hr(className="my-4"),
    
    # Additional Statistics Table
    html.H3("📋 Detailed Statistics", className="mt-4 mb-3"),
    dbc.Row([
        dbc.Col([
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Metric"),
                        html.Th("Value")
                    ])
                ]),
                html.Tbody([
                    html.Tr([html.Td("Average Duration"), html.Td(f"{stats.get('avg_duration', 0):.2f} seconds")]),
                    html.Tr([html.Td("Min Duration"), html.Td(f"{stats.get('min_duration', 0):.2f} seconds")]),
                    html.Tr([html.Td("Max Duration"), html.Td(f"{stats.get('max_duration', 0):.2f} seconds")]),
                    html.Tr([html.Td("Average Words per File"), html.Td(f"{stats.get('avg_words', 0):.0f}")]),
                    html.Tr([html.Td("Average Characters per File"), html.Td(f"{stats.get('avg_chars', 0):.0f}")]),
                    html.Tr([html.Td("Total Utterances"), html.Td(f"{stats.get('total_utterances', 0):,}")]),
                ])
            ], bordered=True, hover=True, striped=True, className="table-dark")
        ])
    ]),
    
    # Footer
    html.Hr(className="my-4"),
    html.P("AI4Bharat Data Engineering Hiring Challenge | Speech Dataset Dashboard", 
           className="text-center text-muted mb-4")
    
], fluid=True, className="px-4")

def main():
    """Run the dashboard application."""
    print("=" * 60)
    print("TASK 5: LAUNCHING DASHBOARD")
    print("=" * 60)
    
    if df is None or df.empty:
        print(f"❌ No data found in manifest file: {MANIFEST_FILE}")
        print("   Please run Task 4 first to create the manifest file.")
        return
    
    print(f"✅ Loaded {len(df)} entries from manifest")
    print(f"\n🚀 Starting dashboard server...")
    print(f"   Open your browser to: http://localhost:{APP_PORT}")
    print(f"\n   Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, port=APP_PORT, host='0.0.0.0')

if __name__ == "__main__":
    main()
