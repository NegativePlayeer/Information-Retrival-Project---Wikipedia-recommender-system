from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

DATA_PATH = Path(__file__).parent.parent / "output" / "articles_processed.parquet"


class WikiRecommender:
    def __init__(self, df):
        self.df = df.reset_index(drop=True)
        self.vectorizer = TfidfVectorizer(min_df=2)
        self.X = self.vectorizer.fit_transform(self.df["lemmas"])
        self.title_to_idx = {name: i for i, name in enumerate(self.df["title"])}

    def recommend(self, titles, k=10):
        rows = [self.title_to_idx[t] for t in titles]
        selected = self.X[rows]
        profile = np.asarray(selected.mean(axis=0))
        scores = cosine_similarity(profile, self.X).ravel()

        scores[rows] = -1
        top = np.argsort(scores)[::-1][:k]

        result = self.df.iloc[top][["title", "url"]].copy()
        result["score"] = scores[top]
        return result.reset_index(drop=True)


if __name__ == "__main__":
    df = pd.read_parquet(DATA_PATH)
    recommender = WikiRecommender(df)
    print(recommender.recommend(["Attention deficit hyperactivity disorder"]))
