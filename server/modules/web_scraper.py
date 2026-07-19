import requests
from bs4 import BeautifulSoup
from logger import logger


def scrape_url(url: str, timeout: int = 10) -> dict:
    """
    Fetch a webpage and strip it down to the main readable content,
    removing nav/header/footer/script noise. Returns a dict compatible
    with the same shape PDF loading produces (text + source).
    """
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "header", "footer", "form", "svg", "noscript", "aside"]):
            tag.decompose()

        main = soup.find("main") or soup.find("article") or soup.body
        text = main.get_text(separator="\n", strip=True) if main else soup.get_text(separator="\n", strip=True)

        if not text.strip():
            logger.warning(f"No content extracted from {url}")
            return {"source": url, "text": "", "status": "failed", "error": "empty after cleaning"}

        return {"source": url, "text": text, "status": "ok", "error": None}
    except Exception as e:
        logger.exception(f"Failed to scrape {url}")
        return {"source": url, "text": "", "status": "failed", "error": str(e)}


def scrape_urls(urls: list[str]) -> list[dict]:
    return [scrape_url(u) for u in urls]
