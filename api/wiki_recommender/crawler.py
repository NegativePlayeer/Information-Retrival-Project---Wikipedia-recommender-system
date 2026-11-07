from collections import deque
from scraper import scrape_article
from playwright.sync_api import sync_playwright
import pandas as pd
import time
import random
from pathlib import Path

START_URLS = [
    "https://en.wikipedia.org/wiki/Attention_deficit_hyperactivity_disorder",
    "https://en.wikipedia.org/wiki/Major_depressive_disorder",
    "https://en.wikipedia.org/wiki/Bipolar_disorder",
    "https://en.wikipedia.org/wiki/Schizophrenia",
    "https://en.wikipedia.org/wiki/Autism",
    "https://en.wikipedia.org/wiki/Generalized_anxiety_disorder",
    "https://en.wikipedia.org/wiki/Post-traumatic_stress_disorder",
    "https://en.wikipedia.org/wiki/Alzheimer%27s_disease",
    "https://en.wikipedia.org/wiki/Epilepsy",
]


def crawl(page, start_urls, limit=1100):
  queue = deque(start_urls)
  visited = set(start_urls)
  articles = []
  seen_titles = set()

  while queue and len(articles) < limit:
    link = queue.popleft()
    time.sleep(random.uniform(0.5, 1.5))
    try:
      article = scrape_article(page, link)

    except Exception as e:
      print(f"Skipping {link}: {str(e).splitlines()[0]}")
      continue

    if article['title'] in seen_titles:
      continue
          
    seen_titles.add(article["title"])
    articles.append(article)
    print(f"[{len(articles)}/{limit}] scraped, {article['title']}")
          
    for wiki_link in article["links"]:
      if wiki_link not in visited:
        visited.add(wiki_link)
        queue.append(wiki_link)

  return articles

if __name__ == "__main__":
  with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    articles = crawl(page, START_URLS)

    browser.close()

  df = pd.DataFrame(articles)
  print(df.shape)

  out_dir = Path(__file__).parent.parent / "output"
  out_dir.mkdir(exist_ok=True)
  df.to_parquet(out_dir / "articles.parquet")