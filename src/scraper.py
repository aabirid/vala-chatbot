import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.myvala.com"
KNOWLEDGE_BASE_URL = "https://www.myvala.com/knowledgebase"
OUTPUT_FILE = "scraped_data.json"

def get_article_links():
    print("Fetching knowledge base index page...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(KNOWLEDGE_BASE_URL, headers=headers)

    print(f"Status code: {response.status_code}")
    print(f"Final URL after redirects: {response.url}")

    if response.status_code != 200:
        print(f"Failed to fetch the knowledge base index page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if "/knowledgebase/" in href and "/knowledge-base/" not in href:
            full_url = href if href.startswith("http") else BASE_URL + href
            if full_url not in links:
                links.append(full_url)

    print(f"Found {len(links)} article links.")
    for link in links:
        print(f"   🔗 {link}")
    return links

def scrape_article(url):
    print(f"Scraping article: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch the article page: {url}. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title = ""
    title_tag = soup.find('h1')
    if title_tag:
        title = title_tag.get_text(strip=True)

    content = ""
    article_body = soup.find('article') or soup.find('main') or soup.find('div', class_=lambda x: x and 'content' in x.lower())
    if article_body:
        content = article_body.get_text(separator="\n", strip=True)
    else:
        paragraphs = soup.find_all('p')
        content = "\n".join(p.get_text(strip=True) for p in paragraphs)

    return {
        "url": url,
        "title": title,
        "content": content        
    }

def main():
    print("Starting Vala knowledgebase scraper...")

    links = get_article_links()
    if not links:
        print("No article links found. Exiting.")
        return
    
    articles = []

    for i, url in enumerate(links):
        print(f"Scraping article {i + 1}/{len(links)}: {url}")
        article = scrape_article(url)

        if article and article['content']:
            articles.append(article)
            print(f"Successfully scraped: {article['title']} - {len(article['content'])} characters")
        else:
            print(f"No content found for: {url}")    

        time.sleep(1)  # Be polite and avoid overwhelming the server

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"Scraping completed. Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()