import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

def plot_rating_distribution(df):
    plt.figure(figsize=(8,5))
    sns.countplot(x='Ratings', data=df, palette='viridis')
    plt.title('Rating Distribution')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.show()

def plot_sentiment_distribution(df):
    plt.figure(figsize=(8,5))
    sns.countplot(x='Sentiment_Class', data=df, palette='Set2')
    plt.title('Sentiment Distribution')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.show()

def plot_wordcloud(text, title='Word Cloud'):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(12,6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    plt.tight_layout()
    plt.show()

def plot_rating_vs_sentiment(df):
    plt.figure(figsize=(8,5))
    sns.boxplot(x='Ratings', y='Sentiment', data=df, palette='mako')
    plt.title('Sentiment Polarity by Rating')
    plt.xlabel('Rating')
    plt.ylabel('Sentiment Polarity')
    plt.tight_layout()
    plt.show()

def plot_temporal_trends(df):
    df['Date'] = pd.to_datetime(df['Review Date']).dt.date
    rating_trend = df.groupby('Date')['Ratings'].mean()
    sentiment_trend = df.groupby('Date')['Sentiment'].mean()
    plt.figure(figsize=(12,6))
    plt.plot(rating_trend, label='Average Rating')
    plt.plot(sentiment_trend, label='Average Sentiment', linestyle='--')
    plt.title('Average Rating & Sentiment Over Time')
    plt.xlabel('Date')
    plt.ylabel('Score')
    plt.legend()
    plt.tight_layout()
    plt.show()