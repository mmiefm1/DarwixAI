from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from modules.web_scraper import scrape_urls
from modules.load_vectorstore import load_web_content
from logger import logger

router = APIRouter()


class ScrapeRequest(BaseModel):
    urls: list[str]
    category: str = "website"


@router.post("/scrape_urls/")
async def scrape_and_index(req: ScrapeRequest):
    try:
        logger.info(f"Scraping {len(req.urls)} URLs")
        scraped = scrape_urls(req.urls)

        failed = [d for d in scraped if d["status"] != "ok"]
        if failed:
            logger.warning(f"{len(failed)} URLs failed to scrape: {[d['source'] for d in failed]}")

        result = load_web_content(scraped, category=req.category)
        return {
            "message": "Scraping and indexing complete",
            "total_urls": len(req.urls),
            "failed_urls": [{"source": d["source"], "error": d["error"]} for d in failed],
            **result,
        }
    except Exception as e:
        logger.exception("Error during URL scraping/indexing")
        return JSONResponse(status_code=500, content={"error": str(e)})
