# Wikipedia Article Recommender

A content-based recommender for Wikipedia articles, built as an Information Retrieval course project.
Given a list of visited articles, it returns other articles the user is likely to find interesting, each with a relevance score.
Every score can also be explained: it is broken down into the contributions of individual words.

The corpus covers **psychiatry and neurology** (1,081 articles crawled from 9 seed articles such as ADHD, Schizophrenia and Epilepsy).

## How it works

| Step | What happens | Code |
|---|---|---|
| 1. Crawling & scraping | Breadth-first crawl from 9 seed articles with Playwright (headless Chromium), ~1,100 articles | `crawler.py`, `scraper.py` |
| 2. Preprocessing | spaCy lemmatization, stop-word removal, filtering of articles shorter than 50 lemmas, saved as Parquet | `preprocessing.py` |
| 3. Recommendation | TF-IDF vectors; user profile = mean vector of visited articles; score = cosine similarity | `recommender.py` |
| 4. Explanation | The cosine score decomposed into per-word contributions, shown as bar charts | `recommender.py`, report |

The full description, corpus statistics and example recommendations are in the report notebook: [`api/notebooks/report.ipynb`](api/notebooks/report.ipynb).

### Example

Visited: *Attention deficit hyperactivity disorder*

| # | Recommendation | Score |
|---|---|---|
| 1 | Adult attention deficit hyperactivity disorder | 0.838 |
| 2 | ADHD Rating Scale | 0.741 |
| 3 | Vanderbilt ADHD Diagnostic Rating Scale | 0.580 |
| 4 | Keith Conners | 0.454 |
| 5 | Conners Comprehensive Behaviour Rating Scale | 0.435 |

Why #1? The word *adhd* alone contributes 0.67 of the 0.84 score, followed by *symptom*, *diagnosis* and *adult*.

## Setup

Requires **Python 3.12**. Newer Python versions may not have prebuilt wheels for spaCy's dependencies.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r api/requirements.txt
python -m spacy download en_core_web_sm
playwright install chromium     # only needed for crawling
```

Notes:
- `preshed` is pinned to `3.0.13`: version `3.0.14` breaks `spacy.load` with an `OverflowError`.
- If `spacy download` fails with an SSL certificate error, install the model wheel directly:
  `pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl`
- `api/check_env.py` prints library versions and checks that spaCy and Playwright work.

## Usage

The scraped and preprocessed data are already included in `api/output/`, so you can skip straight to the recommender.

```powershell
# optional: rebuild the data (crawling takes a while)
python api/wiki_recommender/crawler.py         # -> api/output/articles.parquet
python api/wiki_recommender/preprocessing.py   # -> api/output/articles_processed.parquet

# recommendations + score breakdown for an example article
python api/wiki_recommender/recommender.py
```

From Python:

```python
import pandas as pd
from wiki_recommender.recommender import WikiRecommender   # run from the api/ folder

df = pd.read_parquet("output/articles_processed.parquet")
rec = WikiRecommender(df)

rec.recommend(["Attention deficit hyperactivity disorder", "Autism"], k=10)
rec.explain(["Attention deficit hyperactivity disorder"], "ADHD Rating Scale", top_n=10)
```

Article titles must match Wikipedia titles exactly (e.g. `"Attention deficit hyperactivity disorder"`, not `"ADHD"`).

## Project structure

```
api/
├── wiki_recommender/
│   ├── scraper.py          # scrape a single article (title, text, links)
│   ├── crawler.py          # BFS crawler -> articles.parquet
│   ├── preprocessing.py    # spaCy lemmatization -> articles_processed.parquet
│   └── recommender.py      # WikiRecommender: recommend() and explain()
├── notebooks/
│   └── report.ipynb        # report: methods, statistics, examples, breakdowns
├── output/                 # Parquet data
├── check_env.py
└── requirements.txt
```

## Limitations

- **Topic drift:** BFS follows every link, so about 21% of the articles are off-topic (e.g. *Santa Claus*, *Cat*).
- **Keyword dominance:** with linear term frequency, one frequent word (e.g. *adhd*) can decide most of the score.
- **Multi-topic profiles:** the mean profile leans towards the topic that has more similar articles in the corpus.
- **Lemmatization** does not merge derived words (*autism* / *autistic* stay separate terms).
- The interactive t-SNE map in the report uses Plotly, which is not rendered in GitHub's notebook preview. Open the notebook locally to see it.
