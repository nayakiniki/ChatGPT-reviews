import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from textblob import TextBlob

# ---- Spiral-inspired Animated Background + Shining Edgy Title CSS ----
st.markdown("""
    <style>
    body {background: #18181b;}
    .stApp {background: #18181b;}
    h1, h2, h3, h4 {color: #eaeaea;}
    .block-container {padding-top: 2rem;}
    hr {border-top: 2px solid #eaeaea;}
    .sidebar .sidebar-content {background-color: #23272f;}
    /* Edgy Shining Title */
    .edgy-title {
        font-size: 3.3rem;
        font-family: 'Montserrat', 'Segoe UI', 'Arial', sans-serif;
        font-weight: 900;
        text-align: center;
        letter-spacing: 0.15em;
        background: linear-gradient(90deg, #eaeaea 8%, #bdbdbd 30%, #f8f8f8 50%, #f72585 65%, #eaeaea 80%);
        background-size: 400% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 2.7s linear infinite, pop 1.1s cubic-bezier(.22,1.61,.36,.98) 1;
        filter: drop-shadow(0 0 18px #f72585) drop-shadow(0 0 7px #eaeaea);
        margin-bottom: 2.8rem;
        margin-top: 1.5rem;
        text-transform: uppercase;
    }
    @keyframes shine {
      to {
        background-position: 400% center;
      }
    }
    @keyframes pop {
      0% {
        transform: scale(0.6);
        opacity: 0;
      }
      70% {
        transform: scale(1.15);
        opacity: 1;
      }
      100% {
        transform: scale(1);
        opacity: 1;
      }
    }
    .spiral-bg {
        position: fixed;
        inset: 0;
        z-index: 0;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: radial-gradient(ellipse 70% 70% at 50% 50%, #18181b 35%, #23272f 60%, #f72585 85%, #eaeaea 100%);
        animation: spiralmove 16s linear infinite;
    }
    @keyframes spiralmove {
        0% {background-position: 0% 0%;}
        50% {background-position: 100% 100%;}
        100% {background-position: 0% 0%;}
    }
    .edgy-sub {
        font-size: 1.35rem;
        font-weight: 700;
        text-align: center;
        letter-spacing: 0.09em;
        color: #eaeaea !important;
        background: linear-gradient(90deg, #f72585 0%, #eaeaea 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3.6s linear infinite, pop 1.4s cubic-bezier(.22,1.61,.36,.98) 1;
        filter: drop-shadow(0 0 7px #f72585);
        margin-bottom: 2.1rem;
        margin-top: 0.25rem;
    }
    </style>
    <div class='spiral-bg'></div>
""", unsafe_allow_html=True)

st.set_page_config(page_title="ChatGPT Feedback Hub", layout="wide")

if "csv_uploaded" not in st.session_state:
    st.session_state.csv_uploaded = False

if not st.session_state.csv_uploaded:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='edgy-title'>ChatGPT Feedback Hub</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='edgy-sub'>Upload your ChatGPT Reviews CSV</div>",
        unsafe_allow_html=True
    )
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file is not None:
        st.session_state.csv_uploaded = True
        df = pd.read_csv(uploaded_file)
else:
    st.markdown("<div class='edgy-title'>ChatGPT Feedback Hub</div>", unsafe_allow_html=True)
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

    st.markdown("<div class='edgy-sub'>Ratings Distribution</div>", unsafe_allow_html=True)
    if len(filtered_df):
        fig, ax = plt.subplots()
        sns.countplot(x='Ratings', data=filtered_df, palette='cool')
        ax.set_facecolor("#23272f")
        st.pyplot(fig)
    else:
        st.info("No data for selected filters.")

    st.markdown("<div class='edgy-sub'>Sentiment Breakdown</div>", unsafe_allow_html=True)
    if len(filtered_df):
        fig, ax = plt.subplots()
        sns.countplot(x='Sentiment_Class', data=filtered_df, palette='mako')
        ax.set_facecolor("#23272f")
        st.pyplot(fig)
    else:
        st.info("No data for selected filters.")

    st.markdown("<div class='edgy-sub'>Review Word Cloud</div>", unsafe_allow_html=True)
    all_reviews = ' '.join(filtered_df['Review'].dropna().astype(str))
    if all_reviews.strip():
        wordcloud = WordCloud(width=800, height=400, background_color='#18181b', colormap='cool').generate(all_reviews)
        fig, ax = plt.subplots(figsize=(12,6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.info("No review text available for word cloud in current filter.")

    st.markdown("<div class='edgy-sub'>Sentiment Polarity by Rating</div>", unsafe_allow_html=True)
    if len(filtered_df):
        fig, ax = plt.subplots()
        sns.boxplot(x='Ratings', y='Sentiment', data=filtered_df, palette='Set2')
        ax.set_facecolor("#23272f")
        st.pyplot(fig)
    else:
        st.info("No data for sentiment vs rating.")

    st.markdown("<div class='edgy-sub'>Trends Over Time</div>", unsafe_allow_html=True)
    if 'Review Date' in filtered_df.columns and len(filtered_df):
        try:
            filtered_df['Date'] = pd.to_datetime(filtered_df['Review Date'], errors='coerce').dt.date
            rating_trend = filtered_df.groupby('Date')['Ratings'].mean()
            sentiment_trend = filtered_df.groupby('Date')['Sentiment'].mean()
            fig, ax = plt.subplots(figsize=(12,6))
            ax.plot(rating_trend.index, rating_trend, label='Avg Rating', color="#eaeaea", marker="o")
            ax.plot(sentiment_trend.index, sentiment_trend, label='Avg Sentiment', color="#f72585", linestyle='--', marker="x")
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
        "<p style='text-align:center;font-size:16px;color:#eaeaea;'>"
        "Made with ❤️ using Streamlit | <a href='https://github.com/nayakiniki/ChatGPT-reviews' style='color:#eaeaea;'>GitHub Repo</a>"
        "</p>", unsafe_allow_html=True
    )
