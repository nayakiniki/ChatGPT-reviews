import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from textblob import TextBlob
import os

# ---- Custom CSS for Edgy Look ----
st.markdown("""
    <style>
    body {background-color: #18181b;}
    .stApp {background-color: #18181b;}
    h1, h2, h3, h4 {color: #06d6a0;}
    .block-container {padding-top: 2rem;}
    .stMetric {color: #f8f8f2;}
    hr {border-top: 2px solid #06d6a0;}
    .sidebar .sidebar-content {background-color: #23272f;}
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="ChatGPT Reviews Edgy Dashboard", layout="wide")

# ---- Load CSV automatically ----
CSV_PATH = os.path.join("data", "ChatGPT_Reviews.csv")
try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Could not load CSV file from {CSV_PATH}. Error: {e}")
    st.stop()

# ---- Robust Review Length ----
df['Review Length'] = df['Review'].apply(lambda x: len(str(x)) if pd.notnull(x) else 0)

# ---- Sentiment Analysis ----
df['Sentiment'] = df['Review'].apply(lambda x: TextBlob(str(x)).sentiment.polarity if pd.notnull(x) else 0)
df['Sentiment_Class'] = df['Sentiment'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))

# ---- Dashboard Header ----
st.markdown("<h1 style='text-align:center'>💬 ChatGPT Reviews: Edgy Insights</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#f8f8f2;font-size:18px;'>"
    "Explore real user feedback on ChatGPT with modern sentiment analytics, stylish charts, and interactive insights."
    "</p>", unsafe_allow_html=True
)

# ---- Sidebar Filters ----
st.sidebar.header("Filters")
rating_options = sorted(df['Ratings'].unique())
sentiment_options = ['Positive', 'Negative', 'Neutral']

selected_ratings = st.sidebar.multiselect("Select Rating(s)", rating_options, default=rating_options)
selected_sentiments = st.sidebar.multiselect("Select Sentiment(s)", sentiment_options, default=sentiment_options)

filtered_df = df[df['Ratings'].isin(selected_ratings) & df['Sentiment_Class'].isin(selected_sentiments)]

# ---- Metrics Row ----
col1, col2, col3 = st.columns(3)
col1.metric("Total Reviews", len(filtered_df))
col2.metric("Avg. Rating", f"{filtered_df['Ratings'].mean():.2f}")
col3.metric("Positive Sentiment (%)", f"{(filtered_df['Sentiment_Class'] == 'Positive').mean()*100:.1f}%")

st.markdown("<hr>", unsafe_allow_html=True)

# ---- Ratings Distribution ----
st.subheader("📊 Ratings Distribution")
fig, ax = plt.subplots()
sns.countplot(x='Ratings', data=filtered_df, palette='cool')
ax.set_facecolor("#23272f")
st.pyplot(fig)

# ---- Sentiment Distribution ----
st.subheader("😎 Sentiment Breakdown")
fig, ax = plt.subplots()
sns.countplot(x='Sentiment_Class', data=filtered_df, palette='mako')
ax.set_facecolor("#23272f")
st.pyplot(fig)

# ---- Word Cloud ----
st.subheader("🌌 Review Word Cloud")
all_reviews = ' '.join(filtered_df['Review'].dropna().astype(str))
if all_reviews.strip():
    wordcloud = WordCloud(width=800, height=400, background_color='#18181b', colormap='cool').generate(all_reviews)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
else:
    st.info("No review text available for word cloud in current filter.")

# ---- Sentiment vs Rating ----
st.subheader("📈 Sentiment Polarity by Rating")
fig, ax = plt.subplots()
sns.boxplot(x='Ratings', y='Sentiment', data=filtered_df, palette='Set2')
ax.set_facecolor("#23272f")
st.pyplot(fig)

# ---- Temporal Trends ----
st.subheader("⏳ Trends Over Time")
if 'Review Date' in filtered_df.columns:
    try:
        filtered_df['Date'] = pd.to_datetime(filtered_df['Review Date']).dt.date
        rating_trend = filtered_df.groupby('Date')['Ratings'].mean()
        sentiment_trend = filtered_df.groupby('Date')['Sentiment'].mean()
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(rating_trend.index, rating_trend, label='Average Rating', color="#06d6a0", marker="o")
        ax.plot(sentiment_trend.index, sentiment_trend, label='Average Sentiment', color="#118ab2", linestyle='--', marker="x")
        ax.set_xlabel('Date')
        ax.set_ylabel('Score')
        ax.set_facecolor("#23272f")
        ax.legend()
        st.pyplot(fig)
    except Exception as e:
        st.info("Could not plot trends. Check date column format.")
else:
    st.info("No 'Review Date' column found for time trends.")

# ---- Data Table ----
with st.expander("🔍 Show Raw Data Table"):
    st.dataframe(filtered_df[['Review Date', 'Ratings', 'Review', 'Sentiment', 'Sentiment_Class', 'Review Length']])

# ---- Footer ----
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;font-size:16px;color:#06d6a0;'>"
    "Made with ❤️ using Streamlit | <a href='https://github.com/nayakiniki/chatgpt-reviews-analysis' style='color:#06d6a0;'>GitHub Repo</a>"
    "</p>", unsafe_allow_html=True
)
