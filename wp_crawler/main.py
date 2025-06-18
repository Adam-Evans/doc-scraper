import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse

START_URL = "https://www.my-site.co.uk/"
DOMAIN = "my-site.co.uk"
OUTPUT_DIR = "crawled_json"

visited = set()
pages = []

# Use sitemap if available for efficiency
SITEMAP_URL = urljoin(START_URL, "/sitemap.xml")

def get_links(soup, base_url):
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        url = urljoin(base_url, href)
        parsed = urlparse(url)
        if DOMAIN in parsed.netloc:
            links.add(url.split("#")[0])
    return links

def extract_content(soup):
    # Try common WP selectors
    main = soup.find("main")
    if not main:
        main = soup.find(class_="entry-content")
    if not main:
        main = soup.body
    title = soup.title.string.strip() if soup.title else ""
    content = main.get_text(separator="\n", strip=True) if main else ""
    return title, content

def crawl(url):
    if url in visited:
        return
    print(f"Crawling: {url}")
    visited.add(url)
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200 or "text/html" not in resp.headers.get("Content-Type", ""):
            return
        soup = BeautifulSoup(resp.text, "html.parser")
        title, content = extract_content(soup)
        pages.append({"url": url, "title": title, "content": content})
        for link in get_links(soup, url):
            if link not in visited:
                crawl(link)
    except Exception as e:
        print(f"Failed to crawl {url}: {e}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    crawl(START_URL)
    with open(os.path.join(OUTPUT_DIR, "pages.json"), "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    print(f"Crawled {len(pages)} pages. Output in {OUTPUT_DIR}/pages.json")

if __name__ == "__main__":
    main()
