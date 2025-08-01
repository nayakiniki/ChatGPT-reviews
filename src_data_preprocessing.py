import pandas as pd

def load_data(csv_path):
    df = pd.read_csv(csv_path)
    return df

def preprocess_reviews(df):
    df = df.copy()
    # Convert date
    df['Review Date'] = pd.to_datetime(df['Review Date'])
    df['Review Length'] = df['Review'].apply(len)
    return df

def drop_missing(df):
    return df.dropna(subset=['Review', 'Ratings', 'Review Date'])

def filter_by_rating(df, ratings):
    return df[df['Ratings'].isin(ratings)]