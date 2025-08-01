import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from wordcloud import WordCloud

st.set_page_config(page_title="ChatGPT Reviews Analysis", layout="wide")

st.title("ChatGPT Reviews Analysis Dashboard")
st.markdown("Minimal, elegant insights into user reviews of ChatGPT.")

# File upload
uploaded_file = st.file_uploader("Upload your ChatGPT_Reviews.csv", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['Review Date'] = pd.to_datetime(df['Review Date'])
    df['Review Length'] = df['Review'].apply(lambda x: len(str(x)) if pd.notnull(x) else 0)
    df['Sentiment'] = df['Review'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    df['Sentiment_Class'] = df['Sentiment'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))

    st.sidebar.header("Filters")
    rating = st.sidebar.multiselect("Select Rating(s)", sorted(df['Ratings'].unique()), default=sorted(df['Ratings'].unique()))
    sentiment = st.sidebar.multiselect("Select Sentiment(s)", ['Positive', 'Negative', 'Neutral'], default=['Positive','Negative','Neutral'])

    filtered_df = df[df['Ratings'].isin(rating) & df['Sentiment_Class'].isin(sentiment)]

    st.subheader("Rating Distribution")
    fig, ax = plt.subplots()
    sns.countplot(x='Ratings', data=filtered_df, palette='viridis', ax=ax)
    st.pyplot(fig)

    st.subheader("Sentiment Distribution")
    fig, ax = plt.subplots()
    sns.countplot(x='Sentiment_Class', data=filtered_df, palette='Set2', ax=ax)
    st.pyplot(fig)

    st.subheader("Word Cloud")
    all_reviews = ' '.join(filtered_df['Review'])
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_reviews)
    fig, ax = plt.subplots(figsize=(12,6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

    st.subheader("Raw Data (filtered)")
    st.dataframe(filtered_df)
else:
    st.info("Please upload a CSV file to begin analysis.")
