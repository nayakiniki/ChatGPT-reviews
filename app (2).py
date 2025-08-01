import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from textblob import TextBlob

# ---- Enhanced Dark Theme CSS ----
st.markdown("""
    <style>
    :root {
        --primary: #1e1e2e;
        --secondary: #2a2a3a;
        --accent: #7e57c2;
        --text: #e0e0e0;
        --border: #3a3a4a;
    }
    
    body, .stApp {
        background: var(--primary);
        color: var(--text);
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text) !important;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    .st-b7, .st-b8, .st-b9, .css-1d391kg, .css-1v0mbdj, .markdown-text-container {
        color: var(--text) !important;
    }
    
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    .sidebar .sidebar-content {
        background: var(--secondary) !important;
        border-right: 1px solid var(--border);
    }
    
    hr {
        border-top: 1px solid var(--border);
        margin: 1.5rem 0;
    }
    
    .stButton>button {
        border: 1px solid var(--accent);
        color: var(--accent);
        background: transparent;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background: var(--accent) !important;
        color: white !important;
    }
    
    .stFileUploader>div>div>div>div {
        color: var(--text);
    }
    
    .stMetric {
        background: var(--secondary);
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid var(--accent);
    }
    
    .stDataFrame {
        border: 1px solid var(--border);
    }
    
    .css-1c7y2kd {
        background: var(--secondary);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--primary);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--accent);
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# ---- App Config ----
st.set_page_config(
    page_title="ChatGPT Feedback Hub",
    layout="wide",
    page_icon="🤖"
)

# ---- Session State ----
if "csv_uploaded" not in st.session_state:
    st.session_state.csv_uploaded = False

# ---- Main App ----
if not st.session_state.csv_uploaded:
    st.markdown("<h1 style='text-align: center; margin-bottom: 0.5rem;'>CHATGPT FEEDBACK HUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7e57c2; font-size: 1.1rem;'>Analyze user reviews with powerful insights</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        uploaded_file = st.file_uploader("", type="csv", key="initial_upload")
        if uploaded_file is not None:
            st.session_state.csv_uploaded = True
            st.rerun()
else:
    # ---- Header ----
    st.markdown("<h1 style='text-align: center; margin-bottom: 0.5rem;'>CHATGPT FEEDBACK HUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7e57c2; font-size: 1.1rem; margin-bottom: 2rem;'>Review Analytics Dashboard</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload new CSV", type="csv", key="reload_upload")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    elif "df" not in locals():
        st.warning("Please upload a CSV file to continue.")
        st.stop()

    # ---- Data Processing ----
    df['Review Length'] = df['Review'].apply(lambda x: len(str(x)) if pd.notnull(x) else 0)
    try:
        df['Sentiment'] = df['Review'].apply(lambda x: TextBlob(str(x)).sentiment.polarity if pd.notnull(x) else 0)
        df['Sentiment_Class'] = df['Sentiment'].apply(lambda x: 'Positive' if x > 0.05 else ('Negative' if x < -0.05 else 'Neutral'))
    except Exception:
        df['Sentiment'] = 0
        df['Sentiment_Class'] = "Neutral"

    # ---- Sidebar Filters ----
    with st.sidebar:
        st.markdown("### FILTERS")
        st.markdown("---")
        rating_options = sorted(df['Ratings'].dropna().unique())
        sentiment_options = ['Positive', 'Negative', 'Neutral']
        selected_ratings = st.multiselect("Select Ratings", rating_options, default=rating_options)
        selected_sentiments = st.multiselect("Select Sentiment", sentiment_options, default=sentiment_options)
    
    filtered_df = df[df['Ratings'].isin(selected_ratings) & df['Sentiment_Class'].isin(selected_sentiments)]

    # ---- Metrics ----
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Reviews", len(filtered_df), help="Number of reviews after filters")
    with col2:
        st.metric("Avg. Rating", f"{filtered_df['Ratings'].mean():.2f}" if len(filtered_df) else "--", 
                help="Average star rating")
    with col3:
        st.metric("Positive Sentiment", f"{(filtered_df['Sentiment_Class']=='Positive').mean()*100:.1f}%" if len(filtered_df) else "--", 
                help="Percentage of positive sentiment reviews")

    # ---- Visualizations ----
    st.markdown("---")
    
    # Row 1
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Ratings Distribution")
        if len(filtered_df):
            fig, ax = plt.subplots(figsize=(8,4))
            sns.countplot(x='Ratings', data=filtered_df, palette='viridis', edgecolor='black')
            ax.set_facecolor("#1e1e2e")
            ax.spines['bottom'].set_color('#3a3a4a')
            ax.spines['left'].set_color('#3a3a4a')
            ax.tick_params(colors='#e0e0e0')
            st.pyplot(fig)
        else:
            st.info("No data for selected filters.")

    with col2:
        st.markdown("#### Sentiment Breakdown")
        if len(filtered_df):
            fig, ax = plt.subplots(figsize=(8,4))
            sns.countplot(x='Sentiment_Class', data=filtered_df, palette='viridis', order=['Positive', 'Neutral', 'Negative'], edgecolor='black')
            ax.set_facecolor("#1e1e2e")
            ax.spines['bottom'].set_color('#3a3a4a')
            ax.spines['left'].set_color('#3a3a4a')
            ax.tick_params(colors='#e0e0e0')
            st.pyplot(fig)
        else:
            st.info("No data for selected filters.")

    # Row 2
    st.markdown("#### Review Word Cloud")
    all_reviews = ' '.join(filtered_df['Review'].dropna().astype(str))
    if all_reviews.strip():
        wordcloud = WordCloud(
            width=1000, 
            height=500, 
            background_color='#1e1e2e',
            colormap='viridis',
            contour_width=1,
            contour_color='#7e57c2'
        ).generate(all_reviews)
        
        fig, ax = plt.subplots(figsize=(12,6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.info("No review text available for word cloud in current filter.")

    # Row 3
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Sentiment Polarity by Rating")
        if len(filtered_df):
            fig, ax = plt.subplots(figsize=(8,4))
            sns.boxplot(x='Ratings', y='Sentiment', data=filtered_df, palette='viridis')
            ax.set_facecolor("#1e1e2e")
            ax.spines['bottom'].set_color('#3a3a4a')
            ax.spines['left'].set_color('#3a3a4a')
            ax.tick_params(colors='#e0e0e0')
            st.pyplot(fig)
        else:
            st.info("No data for sentiment vs rating.")

    with col2:
        st.markdown("#### Trends Over Time")
        if 'Review Date' in filtered_df.columns and len(filtered_df):
            try:
                filtered_df['Date'] = pd.to_datetime(filtered_df['Review Date'], errors='coerce').dt.date
                rating_trend = filtered_df.groupby('Date')['Ratings'].mean()
                sentiment_trend = filtered_df.groupby('Date')['Sentiment'].mean()
                
                fig, ax = plt.subplots(figsize=(8,4))
                ax.plot(rating_trend.index, rating_trend, label='Avg Rating', color="#7e57c2", linewidth=2, marker="o")
                ax.plot(sentiment_trend.index, sentiment_trend, label='Avg Sentiment', color="#b39ddb", linestyle='--', linewidth=2, marker="x")
                ax.set_facecolor("#1e1e2e")
                ax.spines['bottom'].set_color('#3a3a4a')
                ax.spines['left'].set_color('#3a3a4a')
                ax.tick_params(colors='#e0e0e0')
                ax.legend(facecolor='#1e1e2e', edgecolor='none', labelcolor='#e0e0e0')
                st.pyplot(fig)
            except Exception as e:
                st.info("Could not plot trends. Check date column format.")
        else:
            st.info("No 'Review Date' column found for time trends.")

    # ---- Data Table ----
    with st.expander("EXPLORE RAW DATA", expanded=False):
        st.dataframe(
            filtered_df[['Review Date','Ratings','Review','Sentiment','Sentiment_Class','Review Length']] if len(filtered_df) else filtered_df,
            height=300,
            use_container_width=True
        )

    # ---- Footer ----
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #7e57c2; font-size: 0.9rem; margin-top: 2rem;">
            <p>CHATGPT FEEDBACK HUB | POWERED BY STREAMLIT</p>
        </div>
        """,
        unsafe_allow_html=True
    )
