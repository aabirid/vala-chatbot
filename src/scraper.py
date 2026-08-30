import logging
import time
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

BASE_URL           = "https://www.myvala.com"
KNOWLEDGE_BASE_URL = "https://www.myvala.com/knowledgebase"
OUTPUT_FILE        = Path(__file__).resolve().parent.parent / "scraped_data.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def safe_get(url: str, retries: int = 3) -> requests.Response | None:
    """Fetch *url* with up to *retries* attempts. Returns None on total failure."""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            return response
        except Exception as e:
            wait = (attempt + 1) * 5
            logger.warning("Attempt %d failed for %s: %s", attempt + 1, url, type(e).__name__)
            if attempt < retries - 1:
                logger.info("Retrying in %ds…", wait)
                time.sleep(wait)
            else:
                logger.error("All %d attempts failed for %s. Skipping.", retries, url)
                return None


def get_category_links() -> list[str]:
    logger.info("Fetching main knowledgebase page…")
    response = safe_get(KNOWLEDGE_BASE_URL)

    if response is None or response.status_code != 200:
        code = response.status_code if response is not None else "N/A"
        logger.error("Failed to fetch knowledgebase page. Status: %s", code)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    categories: list[str] = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/knowledgebase/" in href and href.rstrip("/") != "/knowledgebase":
            full_url = href if href.startswith("http") else BASE_URL + href
            if full_url not in categories:
                categories.append(full_url)

    logger.info("Found %d category links", len(categories))
    return categories


def get_article_links(category_url: str) -> list[str]:
    response = safe_get(category_url)

    if response is None or response.status_code != 200:
        code = response.status_code if response is not None else "N/A"
        logger.warning("Failed to fetch category %s. Status: %s", category_url, code)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles: list[str] = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/info/" in href:
            full_url = href if href.startswith("http") else BASE_URL + href
            if full_url not in articles:
                articles.append(full_url)

    return articles


def scrape_article(url: str) -> dict | None:
    logger.info("Scraping: %s", url)
    response = safe_get(url)

    if response is None or response.status_code != 200:
        code = response.status_code if response is not None else "N/A"
        logger.warning("Failed to fetch article %s. Status: %s", url, code)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title = ""
    title_tag = soup.find("h4", class_="bbbaslik2")
    if title_tag:
        title = title_tag.get_text(strip=True)

    content = ""
    main_container = soup.find("div", class_="sayfacontent")
    if main_container:
        content_parts: list[str] = []

        for element in main_container.find_all(["p", "li", "h4", "h5", "h3"], recursive=True):
            parent = element.find_parent(["li", "ul", "ol"])
            if parent and element.name == "p":
                continue

            text = element.get_text(separator=" ", strip=True)

            if not text or text == title or len(text) < 3:
                continue

            if element.find_parent("div", class_="sidebar"):
                continue

            if element.name == "li":
                text = f"• {text}"
            if element.name in ["h3", "h4", "h5"]:
                text = f"\n{text}\n"

            content_parts.append(text)

        # Deduplicate consecutive identical lines
        cleaned: list[str] = []
        for part in content_parts:
            if not cleaned or part != cleaned[-1]:
                cleaned.append(part)

        content = "\n".join(cleaned)

    if not content or len(content) < 50:
        paragraphs = soup.find_all("p")
        content = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    if not title and not content:
        logger.warning("No title or content found for: %s", url)
        return None

    return {"url": url, "title": title, "content": content}


def main() -> None:
    logger.info("Starting Vala knowledgebase scraper…")

    categories = get_category_links()
    if not categories:
        logger.error("No category links found. Exiting.")
        return

    all_article_links: list[str] = []
    for cat_url in categories:
        logger.info("Fetching articles from: %s", cat_url)
        all_article_links.extend(get_article_links(cat_url))
        time.sleep(1)

    all_article_links = list(set(all_article_links))
    logger.info("Total unique article links: %d", len(all_article_links))

    if not all_article_links:
        logger.error("No article links found. Exiting.")
        return

    articles: list[dict] = []
    for i, url in enumerate(all_article_links, start=1):
        logger.info("Scraping %d/%d: %s", i, len(all_article_links), url)
        article = scrape_article(url)

        if article:
            articles.append(article)
            logger.info("OK — '%s' (%d chars)", article["title"], len(article["content"]))
        else:
            logger.warning("No content for: %s", url)

        time.sleep(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    logger.info("Done! Scraped %d articles → %s", len(articles), OUTPUT_FILE)


if __name__ == "__main__":
    main()