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
        self.terms = self.vectorizer.get_feature_names_out()  # column index -> word

    def _profile(self, titles):
        """Row numbers of visited articles and their mean TF-IDF vector, shape (1, n_terms)."""
        rows = [self.title_to_idx[t] for t in titles]
        profile = np.asarray(self.X[rows].mean(axis=0))
        return rows, profile

    def recommend(self, titles, k=10):
        rows, profile = self._profile(titles)
        scores = cosine_similarity(profile, self.X).ravel()

        scores[rows] = -1
        top = np.argsort(scores)[::-1][:k]

        result = self.df.iloc[top][["title", "url"]].copy()
        result["score"] = scores[top]
        return result.reset_index(drop=True)

    def explain(self, titles, target, top_n=10):
        """Per-word contributions to the score of `target` for a user who visited `titles`.

        Returns a DataFrame with columns `term` and `contribution`, sorted descending.
        top_n=None returns all words (their contributions should sum to the score).
        """
        _, profile = self._profile(titles)
        profile_unit = profile / np.linalg.norm(profile)
        article = self.X[self.title_to_idx[target]].toarray()
        contribution = (profile_unit * article).ravel()
        top = np.argsort(contribution)[::-1][:top_n]
        return pd.DataFrame(
            {"term": self.terms[top], "contribution": contribution[top]}
        )


if __name__ == "__main__":
    df = pd.read_parquet(DATA_PATH)
    recommender = WikiRecommender(df)

    visited = ["Attention deficit hyperactivity disorder"]
    recs = recommender.recommend(visited)
    print(recs)

    target = recs.loc[0, "title"]
    print(f"\nWhy '{target}'?")
    print(recommender.explain(visited, target))

    # sanity check: all contributions together must equal the score
    full = recommender.explain(visited, target, top_n=None)
    print(f"\nsum of contributions: {full['contribution'].sum():.6f}")
    print(f"score from recommend: {recs.loc[0, 'score']:.6f}")
