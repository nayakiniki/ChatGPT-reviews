import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from textblob import TextBlob

# ---- Enhanced Dark Theme with Purple Accent ----
st.markdown("""
    <style>
    :root {
        --primary-bg: #0e1117;
        --secondary-bg: #1a1d24;
        --accent: #9d4edd;
        --text: #f0f0f0;
        --border: #2d3748;
    }
    
    body, .stApp {
        background: var(--primary-bg);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 {
        color: var(--accent) !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .st-b7, .st-b8, .st-b9, .markdown-text-container {
        color: var(--text) !important;
    }
    
    .block-container {
        padding-top: 1.5rem;
    }
    
    .sidebar .sidebar-content {
        background: var(--secondary-bg) !important;
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
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background: var(--accent) !important;
        color: white !important;
    }
    
    .stMetric {
        background: var(--secondary-bg);
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid var(--accent);
    }
    
    .stDataFrame {
        border: 1px solid var(--border);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--primary-bg);
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

# ---- Initialize Session State ----
if "df" not in st.session_state:
    st.session_state.df = None

# ---- Header ----
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 0.25rem; color: #9d4edd !important;'>
        ChatGPT Feedback Hub
    </h1>
    <p style='text-align: center; color: #b392f0; font-size: 1.1rem; margin-bottom: 1.5rem;'>
        Analyze user reviews with powerful insights
    </p>
""", unsafe_allow_html=True)

# ---- File Upload ----
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"], 
                                help="Upload your ChatGPT reviews CSV with columns: Ratings, Review")

if uploaded_file:
    try:
        st.session_state.df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")

# ---- Dashboard ----
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Data Processing
    df['Review Length'] = df['Review'].apply(lambda x: len(str(x)) if pd.notnull(x) else 0)
    try:
        df['Sentiment'] = df['Review'].apply(lambda x: TextBlob(str(x)).sentiment.polarity if pd.notnull(x) else 0)
        df['Sentiment_Class'] = df['Sentiment'].apply(
            lambda x: 'Positive' if x > 0.05 else ('Negative' if x < -0.05 else 'Neutral'))
    except Exception as e:
        st.warning(f"Sentiment analysis error: {str(e)}")
        df['Sentiment'] = 0
        df['Sentiment_Class'] = "Neutral"

    # Sidebar Filters
    with st.sidebar:
        st.header("Filters")
        rating_options = sorted(df['Ratings'].dropna().unique())
        selected_ratings = st.multiselect(
            "Select Ratings", 
            rating_options, 
            default=rating_options
        )
        selected_sentiments = st.multiselect(
            "Select Sentiment",
            ['Positive', 'Neutral', 'Negative'],
            default=['Positive', 'Neutral', 'Negative']
        )
    
    filtered_df = df[
        df['Ratings'].isin(selected_ratings) & 
        df['Sentiment_Class'].isin(selected_sentiments)
    ]

    # Metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", len(filtered_df))
    col2.metric("Avg. Rating", f"{filtered_df['Ratings'].mean():.2f}")
    col3.metric("Positive Sentiment", 
               f"{(filtered_df['Sentiment_Class'] == 'Positive').mean() * 100:.1f}%")

    # Visualizations
    st.markdown("---")
    
    # Row 1
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ratings Distribution")
        if not filtered_df.empty:
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.countplot(x='Ratings', data=filtered_df, palette='viridis')
            ax.set_facecolor("#0e1117")
            plt.xticks(color='white')
            plt.yticks(color='white')
            st.pyplot(fig)
    
    with col2:
        st.subheader("Sentiment Breakdown")
        if not filtered_df.empty:
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.countplot(
                x='Sentiment_Class', 
                data=filtered_df, 
                order=['Positive', 'Neutral', 'Negative'],
                palette='viridis'
            )
            ax.set_facecolor("#0e1117")
            plt.xticks(color='white')
            plt.yticks(color='white')
            st.pyplot(fig)

    # Word Cloud
    st.subheader("Review Word Cloud")
    if not filtered_df.empty:
        all_reviews = ' '.join(filtered_df['Review'].dropna().astype(str))
        if all_reviews.strip():
            wordcloud = WordCloud(
                width=1000,
                height=500,
                background_color='#0e1117',
                colormap='viridis',
                contour_width=1,
                contour_color='#9d4edd'
            ).generate(all_reviews)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #b392f0; font-size: 0.9rem; margin-top: 2rem;'>
        Made with Streamlit • <a href='https://github.com/nayakiniki/ChatGPT-reviews' style='color: #b392f0;'>GitHub Repo</a>
    </div>
    """, unsafe_allow_html=True)
