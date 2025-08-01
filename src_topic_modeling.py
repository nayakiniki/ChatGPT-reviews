from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def preprocess(text):
    text = str(text).lower()
    text = ''.join([c for c in text if c.isalpha() or c == ' '])
    return text

def prepare_corpus(df):
    return df['Review'].apply(preprocess)

def lda_topics(corpus, n_topics=5, n_words=10):
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    dtm = vectorizer.fit_transform(corpus)
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(dtm)
    topic_list = []
    feature_names = vectorizer.get_feature_names_out()
    for topic_idx, topic in enumerate(lda.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-n_words - 1:-1]]
        topic_list.append(top_words)
    return topic_list