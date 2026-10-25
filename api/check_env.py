import sys
import numpy as np
from playwright.sync_api import sync_playwright
import pandas as pd
import matplotlib
import pyarrow as pa
import spacy
import sklearn
import fastapi
import seaborn as sns

print(f"System version: {sys.version}")
print(f"System virtual environment: {sys.prefix}")
print("--------------------------")
print("numpy", np.__version__)
print("pandas", pd.__version__)
print("pyarrow", pa.__version__)
print("sklearn", sklearn.__version__)
print("fastapi", fastapi.__version__)
print("matplotlib", matplotlib.__version__)
print("seaborn", sns.__version__)
print("spacy", spacy.__version__)
print("--------------------------")
nlp = spacy.load("en_core_web_sm")
doc = nlp("To be or not to be.")
for token in doc:
  print(token.text, token.lemma_, token.is_stop)
print("--------------------------")
with sync_playwright() as p:
  browser = p.chromium.launch()
  page = browser.new_page()
  page.goto("https://www.wikipedia.org/")
  print(page.title())
  browser.close()