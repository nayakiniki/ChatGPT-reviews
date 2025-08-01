import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from textblob import TextBlob

# ---- Simple Dark Theme CSS ----
st.markdown("""
    <style>
    body, .stApp {background: #18181b;}
    h1, h2, h3, h4, p, div, label, .markdown-text-container, .css-1d391kg, .css-1v0mbdj, .css-1c7y2kd, .css-1f0v6h7, .css-1o72pil, .css-1f2kwz6, .css-1r6slb0, .css-1w2y31u {
        color: #eaeaea !important;
    }
    .block-container {padding-top: 2rem;}
    .sidebar .sidebar-content {background-color: #23272f;}
    hr {border-top: 2px solid #23272f;}
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="ChatGPT Feedback Hub", layout="wide")

if "csv_uploaded" not in st.session_state:
    st.session_state.csv_uploaded = False

if not st.session_state.csv_uploaded:
    st.markdown("<h1 style='text-align:center;'>ChatGPT Feedback Hub</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Upload your ChatGPT Reviews CSV</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file is not None:
        st.session_state.csv_uploaded = True
        df = pd.read_csv(uploaded_file)
else:
    st.markdown("<h1 style='text-align:center;'>ChatGPT Feedback Hub</h1>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV to reload", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    elif "df" not in locals():
        st.warning("Please upload a CSV file to continue.")
        st.stop()

    df['Review Length'] = df['Review'].apply(lambda x: len(str(x)) if pd.notnull(x) else 0)
    try:
        df['Sentiment'] = df['Review'].apply(lambda x: TextBlob(str(x)).sentiment.polarity if pd.notnull(x) else 0)
        df['Sentiment_Class'] = df['Sentiment'].apply(lambda x: 'Positive' if x > 0.05 else ('Negative' if x < -0.05 else 'Neutral'))
    except Exception:
        df['Sentiment'] = 0
        df['Sentiment_Class'] = "Neutral"

    st.sidebar.header("Filters")
    rating_options = sorted(df['Ratings'].dropna().unique())
    sentiment_options = ['Positive', 'Negative', 'Neutral']
    selected_ratings = st.sidebar.multiselect("Ratings", rating_options, default=rating_options)
    selected_sentiments = st.sidebar.multiselect("Sentiment", sentiment_options, default=sentiment_options)
    filtered_df = df[df['Ratings'].isin(selected_ratings) & df['Sentiment_Class'].isin(selected_sentiments)]

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", len(filtered_df))
    col2.metric("Avg. Rating", f"{filtered_df['Ratings'].mean():.2f}" if len(filtered_df) else "--")
    col3.metric("Positive Sentiment (%)", f"{(filtered_df['Sentiment_Class']=='Positive').mean()*100:.1f}%" if len(filtered_df) else "--")

    st.markdown("---")

    st.subheader("Ratings Distribution")
    if len(filtered_df):
        fig, ax = plt.subplots()
        sns.countplot(x='Ratings', data=filtered_df, palette='gray')
        ax.set_facecolor("#18181b")
        st.pyplot(fig)
    else:
        st.info("No data for selected filters.")

    st.subheader("Sentiment Breakdown")
    if len(filtered_df):
        fig, ax = plt.subplots()
        sns.countplot(x='Sentiment_Class', data=filtered_df, palette='gray')
        ax.set_facecolor("#18181b")
        st.pyplot(fig)
    else:
        st.info("No data for selected filters.")

    st.subheader("Review Word Cloud")
    all_reviews = ' '.join(filtered_df['Review'].dropna().astype(str))
    if all_reviews.strip():
        wordcloud = WordCloud(width=800, height=400, background_color='#18181b', colormap='gray').generate(all_reviews)
        fig, ax = plt.subplots(figsize=(12,6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.info("No review text available for word cloud in current filter.")

    st.subheader("Sentiment Polarity by Rating")
    if len(filtered_df):
        fig, ax = plt.subplots()
        sns.boxplot(x='Ratings', y='Sentiment', data=filtered_df, palette='gray')
        ax.set_facecolor("#18181b")
        st.pyplot(fig)
    else:
        st.info("No data for sentiment vs rating.")

    st.subheader("Trends Over Time")
    if 'Review Date' in filtered_df.columns and len(filtered_df):
        try:
            filtered_df['Date'] = pd.to_datetime(filtered_df['Review Date'], errors='coerce').dt.date
            rating_trend = filtered_df.groupby('Date')['Ratings'].mean()
            sentiment_trend = filtered_df.groupby('Date')['Sentiment'].mean()
            fig, ax = plt.subplots(figsize=(12,6))
            ax.plot(rating_trend.index, rating_trend, label='Avg Rating', color="#eaeaea", marker="o")
            ax.plot(sentiment_trend.index, sentiment_trend, label='Avg Sentiment', color="#888888", linestyle='--', marker="x")
            ax.set_xlabel('Date')
            ax.set_ylabel('Score')
            ax.set_facecolor("#18181b")
            ax.legend()
            st.pyplot(fig)
        except Exception as e:
            st.info("Could not plot trends. Check date column format.")
    else:
        st.info("No 'Review Date' column found for time trends.")

    with st.expander("Show Raw Data Table"):
        st.dataframe(filtered_df[['Review Date','Ratings','Review','Sentiment','Sentiment_Class','Review Length']] if len(filtered_df) else filtered_df)

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;font-size:15px;color:#eaeaea;'>"
        "Made with Streamlit | <a href='https://github.com/nayakiniki/ChatGPT-reviews' style='color:#eaeaea;'>GitHub Repo</a>"
        "</p>", unsafe_allow_html=True
    )
