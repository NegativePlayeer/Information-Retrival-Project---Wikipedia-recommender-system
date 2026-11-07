import spacy
import pandas as pd
from pathlib import Path
import time
from tqdm import tqdm

def preprocess(text, nlp):
  doc = nlp(text)
  tokens = [t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop]

  return " ".join(tokens)

if __name__ == "__main__":
  nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
  source = Path(__file__).parent.parent / "output" / "articles.parquet"

  df = pd.read_parquet(source)
  tqdm.pandas()

  start = time.perf_counter()
  df["lemmas"] = df["text"].progress_apply(lambda t: preprocess(t, nlp))
  elapsed = time.perf_counter() - start
  print(f"{elapsed:.1f} s")

  df["n_tokens"] = df["lemmas"].str.split().str.len()
  filtered = df[df["n_tokens"] >= 50]
  print(f"deleted {len(df) - len(filtered)}")

  out_dir = Path(__file__).parent.parent / "output"
  filtered.to_parquet(out_dir / "articles_processed.parquet", index=False)