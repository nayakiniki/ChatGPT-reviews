from textblob import TextBlob

def get_sentiment(text):
    try:
        return TextBlob(str(text)).sentiment.polarity
    except:
        return 0

def add_sentiment(df):
    df = df.copy()
    df['Sentiment'] = df['Review'].apply(get_sentiment)
    df['Sentiment_Class'] = df['Sentiment'].apply(
        lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral')
    )
    return df