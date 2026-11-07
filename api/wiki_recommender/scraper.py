from playwright.sync_api import sync_playwright
import re

def scrape_article(page, url):
    page.goto(url)
    title = page.locator("#firstHeading").inner_text()
    paragraphs = page.locator(".mw-parser-output > section > p").all_inner_texts()

    paragraphs = filter(str.strip, paragraphs)
    text = "\n".join(paragraphs)
    clean_text = re.sub(r"\[[^\]]*\]", "", text)

    return {
        "title": title,
        "url": url,
        "text": clean_text
    }
    
if __name__ == "__main__":
    urls = ["https://en.wikipedia.org/wiki/Information_retrieval", "https://en.wikipedia.org/wiki/Python_(programming_language)", "https://en.wikipedia.org/wiki/Kraków"]
    results = []

    with sync_playwright() as p:
      browser = p.chromium.launch()
      page = browser.new_page()
      for url in urls:
        results.append(scrape_article(page, url))
      browser.close()

    for article in results:
      print(f"title: {article['title']}\nlength: {len(article['text'])}\ntext: {article['text'][:300]}\n\n")
