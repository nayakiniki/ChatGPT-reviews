import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from textblob import TextBlob

# ---- Spiral-inspired Animated Background + Shining Text CSS ----
st.markdown("""
    <style>
    body {background: #18181b;}
    .stApp {background: #18181b;}
    h1, h2, h3, h4 {color: #5efc8d;}
    .block-container {padding-top: 2rem;}
    hr {border-top: 2px solid #5efc8d;}
    .sidebar .sidebar-content {background-color: #23272f;}
    /* Shining header effect */
    .shining-title {
        font-size: 3.3rem;
        font-weight: 900;
        text-align: center;
        letter-spacing: 0.12em;
        background: linear-gradient(90deg, #00eaff 10%, #5efc8d 40%, #a259f7 60%, #ffd166 90%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 2.9s linear infinite, pop 1.2s cubic-bezier(.22,1.61,.36,.98) 1;
        filter: drop-shadow(0 0 22px #ffd166) drop-shadow(0 0 12px #a259f7);
        margin-bottom: 2.7rem;
    }
    @keyframes shine {
      to {
        background-position: 200% center;
      }
    }
    @keyframes pop {
      0% {
        transform: scale(0.4);
        opacity: 0;
      }
      60% {
        transform: scale(1.13);
        opacity: 1;
      }
      100% {
        transform: scale(1);
        opacity: 1;
      }
    }
    .shining-sub {
        font-size: 1.4rem;
        font-weight: 700;
        text-align: center;
        letter-spacing: 0.09em;
        background: linear-gradient(90deg, #ffd166 10%, #00eaff 90%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3.5s linear infinite, pop 1.4s cubic-bezier(.22,1.61,.36,.98) 1;
        filter: drop-shadow(0 0 9px #ffd166);
        margin-bottom: 1.7rem;
        margin-top: 0.5rem;
    }
    /* Spiral-inspired animated background */
    .spiral-bg {
        position: fixed;
        inset: 0;
        z-index: 0;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: radial-gradient(ellipse 70% 70% at 50% 50%, #23272f 40%, #00eaff 60%, #a259f7 85%, #18181b 100%);
        animation: spiralmove 12s linear infinite;
    }
    @keyframes spiralmove {
        0% {background-position: 0% 0%;}
        50% {background-position: 100% 100%;}
        100% {background-position: 0% 0%;}
    }
    </style>
    <div class='spiral-bg'></div>
""", unsafe_allow_html=True)

st.set_page_config(page_title="ChatGPT Feedback Hub", layout="wide")

if "csv_uploaded" not in st.session_state:
    st.session_state.csv_uploaded = False

if not st.session_state.csv_uploaded:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='shining-title'>ChatGPT Feedback Hub</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='shining-sub'>Upload your ChatGPT Reviews CSV</div>",
        unsafe_allow_html=True
    )
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file is not None:
        st.session_state.csv_uploaded = True
        df = pd.read_csv(uploaded_file)
else:
    st.markdown("<div class='shining-title'>ChatGPT Feedback Hub</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

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
    selected_ratings = st.sidebar.multiselect("Select Rating(s)", rating_options, default=rating_options)
    selected_sentiments = st.sidebar.multiselect("Select Sentiment(s)", sentiment_options, default=sentiment_options)
    filtered_df = df[df['Ratings'].isin(selected_ratings) & df['Sentiment_Class'].isin(selected_sentiments)]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", len(filtered_df))
    col2.metric("Avg. Rating", f"{filtered_df['Ratings'].mean():.2f}" if len(filtered_df) else "--")
    col3.metric("Positive Sentiment (%)", f"{(filtered_df['Sentiment_Class']=='Positive').mean()*100:.1f}%" if len(filtered_df) else "--")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<div class='shining-sub'>Ratings Distribution</div>", unsafe_allow_html=True)
    if len(filtered_df):
        fig, ax = plt.subplots()
        sns.countplot(x='Ratings', data=filtered_df, palette='cool')
        ax.set_facecolor("#23272f")
        st.pyplot(fig)
    else:
        st.info("No data for selected filters.")

    st.markdown("<div class='shining-sub'>Sentiment Breakdown</div>", unsafe_allow_html=True)
    if len(filtered_df):
        fig, ax = plt.subplots()
        sns.countplot(x='Sentiment_Class', data=filtered_df, palette='mako')
        ax.set_facecolor("#23272f")
        st.pyplot(fig)
    else:
        st.info("No data for selected filters.")

    st.markdown("<div class='shining-sub'>Review Word Cloud</div>", unsafe_allow_html=True)
    all_reviews = ' '.join(filtered_df['Review'].dropna().astype(str))
    if all_reviews.strip():
        wordcloud = WordCloud(width=800, height=400, background_color='#18181b', colormap='cool').generate(all_reviews)
        fig, ax = plt.subplots(figsize=(12,6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.info("No review text available for word cloud in current filter.")

    st.markdown("<div class='shining-sub'>Sentiment Polarity by Rating</div>", unsafe_allow_html=True)
    if len(filtered_df):
        fig, ax = plt.subplots()
        sns.boxplot(x='Ratings', y='Sentiment', data=filtered_df, palette='Set2')
        ax.set_facecolor("#23272f")
        st.pyplot(fig)
    else:
        st.info("No data for sentiment vs rating.")

    st.markdown("<div class='shining-sub'>Trends Over Time</div>", unsafe_allow_html=True)
    if 'Review Date' in filtered_df.columns and len(filtered_df):
        try:
            filtered_df['Date'] = pd.to_datetime(filtered_df['Review Date'], errors='coerce').dt.date
            rating_trend = filtered_df.groupby('Date')['Ratings'].mean()
            sentiment_trend = filtered_df.groupby('Date')['Sentiment'].mean()
            fig, ax = plt.subplots(figsize=(12,6))
            ax.plot(rating_trend.index, rating_trend, label='Avg Rating', color="#5efc8d", marker="o")
            ax.plot(sentiment_trend.index, sentiment_trend, label='Avg Sentiment', color="#00eaff", linestyle='--', marker="x")
            ax.set_xlabel('Date')
            ax.set_ylabel('Score')
            ax.set_facecolor("#23272f")
            ax.legend()
            st.pyplot(fig)
        except Exception as e:
            st.info("Could not plot trends. Check date column format.")
    else:
        st.info("No 'Review Date' column found for time trends.")

    with st.expander("Show Raw Data Table"):
        st.dataframe(filtered_df[['Review Date','Ratings','Review','Sentiment','Sentiment_Class','Review Length']] if len(filtered_df) else filtered_df)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;font-size:16px;color:#5efc8d;'>"
        "Made with ❤️ using Streamlit | <a href='https://github.com/nayakiniki/ChatGPT-reviews' style='color:#5efc8d;'>GitHub Repo</a>"
        "</p>", unsafe_allow_html=True
    )
