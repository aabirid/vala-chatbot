import requests
from bs4 import BeautifulSoup
import json
import time
import random

BASE_URL = "https://www.myvala.com"
KNOWLEDGE_BASE_URL = "https://www.myvala.com/knowledgebase"
OUTPUT_FILE = "scraped_data.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def safe_get(url,  retries=3):
    """
    Try to fetch a URL up to `retries` times.
    If it fails, wait a bit longer and try again.
    Returns the response, or None if all retries fail.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            return response
        except Exception as e:
            wait = (attempt + 1) * 5  # Wait 5s, then 10s, then 15s
            print(f"⚠️ Attempt {attempt+1} failed: {type(e).__name__}")
            if attempt < retries - 1:
                print(f"⏳ Waiting {wait}s before retrying...")
                time.sleep(wait)
            else:
                print(f"❌ All {retries} attempts failed. Skipping.")
                return None

def get_category_links():
    print("Fetching main knowledgebase page...")
    response = safe_get(KNOWLEDGE_BASE_URL)

    if response.status_code != 200:
            print(f"Failed. Status code: {response.status_code}")
            return []

    soup = BeautifulSoup(response.text, "html.parser")
    
    categories = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if "/knowledgebase/" in href and href.rstrip("/") != "/knowledgebase":
            full_url = href if href.startswith("http") else BASE_URL + href
            if full_url not in categories:
                categories.append(full_url)

    print(f"Found {len(categories)} category links.")
    return categories


def get_article_links(category_url):
    response = safe_get(category_url)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if "/info/" in href:
            full_url = href if href.startswith("http") else BASE_URL + href
            if full_url not in articles:
                articles.append(full_url)

    return articles

def scrape_article(url):
    print(f"Scraping article: {url}")

    response = safe_get(url)

    if response.status_code != 200:
        print(f"Failed to fetch the article page: {url}. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title = ""
    title_tag = soup.find("h4", class_="bbbaslik2")
    if title_tag:
        title = title_tag.get_text(strip=True)

    content = ""
    main_container = soup.find("div", class_="sayfacontent")
    if main_container:
        content_parts = []

        for element in main_container.find_all(["p", "li", "h4", "h5", "h3"], recursive=True):
            parent = element.find_parent(["li", "ul", "ol"])
            if parent and element.name == "p":
                continue

            text = element.get_text(separator=" ", strip=True)

            if not text or text == title:
                continue

            if len(text) < 3:
                continue

            if element.find_parent("div", class_="sidebar"):
                continue

            if element.name == "li":
                text = f"• {text}"

            if element.name in ["h3", "h4", "h5"]:
                text = f"\n{text}\n"

            content_parts.append(text)

        cleaned_parts = []
        for part in content_parts:
            if not cleaned_parts or part != cleaned_parts[-1]:
                cleaned_parts.append(part)

        content = "\n".join(cleaned_parts)

    if not content or len(content) < 50:
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

    if not title and not content:
        print(f"No title or content found for: {url}")
        return None
    
    return {
        "url": url,
        "title": title,
        "content": content        
    }

def main():
    print("Starting Vala knowledgebase scraper...")

    categories = get_category_links()
    if not categories:
        print("No category links found. Exiting.")
        return
    
    all_article_links = []
    for cat_url in categories:
        print(f"Fetching articles from category: {cat_url}")
        article_links = get_article_links(cat_url)
        all_article_links.extend(article_links)
        time.sleep(1)  # Be polite and avoid overwhelming the server

    all_article_links = list(set(all_article_links))
    print(f"Total unique article links found: {len(all_article_links)}")
    
    if not all_article_links:
        print("No article links found. Exiting.")
        return

    
    articles = []
    for i, url in enumerate(all_article_links):
        print(f"Scraping article {i + 1}/{len(all_article_links)}: {url}")
        article = scrape_article(url)

        if article:
            articles.append(article)
            print(f"Successfully scraped: {article['title']} - {len(article['content'])} characters")
        else:
            print(f"No content found for: {url}")    

        time.sleep(1)  # Be polite and avoid overwhelming the server

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"\n Done! Scraped {len(articles)} articles")
    print(f"Scraping completed. Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()