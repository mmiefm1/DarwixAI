from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from modules.load_vectorstore import load_raw_text
from logger import logger

router = APIRouter()


class AddContentRequest(BaseModel):
    title: str
    content: str
    category: str = "general"
    version: str = "1.0"


@router.post("/add_content/")
async def add_content(req: AddContentRequest):
    try:
        result = load_raw_text(req.title, req.content, req.category, version=req.version)
        return {"message": "Content indexed", "title": req.title, "category": req.category, **result}
    except Exception as e:
        logger.exception("Error adding manual content")
        return JSONResponse(status_code=500, content={"error": str(e)})