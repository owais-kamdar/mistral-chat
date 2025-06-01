# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime
from system_monitor import system_monitor

def load_session_data():
    """Load all available session data."""
    sessions = []
    for file in os.listdir('logs'):
        if file.startswith('summary_') and file.endswith('.json'):
            # Load the summary file
            with open(os.path.join('logs', file), 'r') as f:
                session = json.load(f)
                session['session_id'] = file.replace('summary_', '').replace('.json', '')
                sessions.append(session)
    return pd.DataFrame(sessions)

def load_metrics_data(session_id):
    """Load detailed metrics for a specific session."""
    metrics_file = f'logs/metrics_{session_id}.jsonl'
    if not os.path.exists(metrics_file):
        return pd.DataFrame()
    # Load the metrics file
    metrics = []
    with open(metrics_file, 'r') as f:
        for line in f:
            metric = json.loads(line)
            metrics.append(metric)
    return pd.DataFrame(metrics)

def create_gauge_chart(value, title, min_val=0, max_val=None):
    """Create a gauge chart for metrics."""
    if max_val is None:
        max_val = value * 1.5
    
    # Create a gauge chart for response time
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, max_val/3], 'color': "lightgray"},
                {'range': [max_val/3, 2*max_val/3], 'color': "gray"},
                {'range': [2*max_val/3, max_val], 'color': "darkgray"}
            ]
        }
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def main():
    """Main dashboard function that sets up the Streamlit interface."""
    # Configure page
    st.set_page_config(page_title="LLM Metrics Dashboard", layout="wide")
    st.title("LLM Chat Metrics Dashboard")
    
    # Load and validate session data
    sessions_df = load_session_data()
    if sessions_df.empty:
        st.warning("No session data available.")
        return
    
    # Session selection in sidebar
    session_ids = sessions_df['session_id'].tolist()
    selected_session = st.sidebar.selectbox(
        "Select Session",
        session_ids,
        format_func=lambda x: datetime.strptime(x, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S"),
        index=len(session_ids)-1 if len(session_ids) > 0 else 0
    )
    
    # Display session start time
    session_date = datetime.strptime(selected_session, "%Y%m%d_%H%M%S")
    st.caption(f"Session started: {session_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get current session data
    session_data = sessions_df[sessions_df['session_id'] == selected_session].iloc[0]
    
    # Display main metrics in gauge charts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_gauge_chart(
            session_data['avg_inference_time'],
            "Avg Response Time (s)",
            max_val=10
        ), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_gauge_chart(
            session_data['current_memory_usage_mb'],
            "Memory Usage (MB)",
            max_val=100
        ), use_container_width=True)
    
    # Calculate session duration
    st.subheader("Session Summary")
    end_time = session_data.get('end_time', datetime.now().isoformat())
    start_time = session_data.get('start_time', session_data['start_time'])
    duration = (datetime.fromisoformat(end_time) - datetime.fromisoformat(start_time)).total_seconds()
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    
    # Calculate character metrics
    metrics_df = load_metrics_data(selected_session)
    total_input_chars = metrics_df['input_chars'].sum() if not metrics_df.empty else 0
    total_output_chars = metrics_df['output_chars'].sum() if not metrics_df.empty else 0
    total_queries = len(metrics_df) if not metrics_df.empty else 1
    
    # Display session summary table
    summary_data = {
        'Total Duration': f"{minutes}m {seconds}s",
        'Total Queries': str(session_data['total_queries']),
        'Queries per Minute': f"{session_data['total_queries'] / (duration/60):.1f}" if duration > 0 else "0.0",
        'Average Input Characters': f"{total_input_chars/total_queries:.1f}",
        'Average Output Characters': f"{total_output_chars/total_queries:.1f}",
        'Errors': str(session_data['errors'])
    }
    df = pd.DataFrame([summary_data]).T
    df.columns = ['Value']
    st.dataframe(df, use_container_width=True)
    
    # Display detailed metrics if available
    metrics_df = load_metrics_data(selected_session)
    if not metrics_df.empty:
        # Add query numbering and convert timestamps
        metrics_df['query_number'] = range(1, len(metrics_df) + 1)
        metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
        
        # Plot response time trend
        st.subheader("Response Time by Query")
        fig = px.line(
            metrics_df,
            x='query_number',
            y='inference_time',
            title='Response Time per Query'
        )
        fig.update_layout(
            xaxis_title="Query Number",
            yaxis_title="Response Time (seconds)",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display query/response history
        st.subheader("All Queries and Responses")
        all_queries = metrics_df.sort_values('timestamp', ascending=False)
        
        for _, row in all_queries.iterrows():
            with st.expander(f"Query at {row['timestamp'].strftime('%H:%M:%S')}"):
                st.markdown("**Query:**")
                st.info(row['input'].split('Assistant:')[0].strip()) 
                st.markdown("**Response:**")
                st.success(row['output'])
                st.caption(f"Response Time: {row['inference_time']:.2f}s")

if __name__ == "__main__":
    main()