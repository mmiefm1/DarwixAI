from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from langchain_cohere import CohereEmbeddings
from pinecone import Pinecone
from logger import logger
import os

router = APIRouter()


class RetrievalTestRequest(BaseModel):
    query: str
    top_k: int = 3


@router.post("/query_test/")
async def query_test(req: RetrievalTestRequest):
    try:
        pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
        index = pc.Index(os.environ.get("PINECONE_INDEX_NAME", "medicalindex"))
        embed_model = CohereEmbeddings(
            cohere_api_key=os.environ["COHERE_API_KEY"],
            model="embed-english-light-v3.0"
        )
        embedded_query = embed_model.embed_query(req.query)
        res = index.query(vector=embedded_query, top_k=req.top_k, include_metadata=True)

        records = []
        for match in res.get("matches", []):
            meta = match.get("metadata", {})
            records.append({
                "record_id": match.get("id"),
                "title": meta.get("title", "untitled"),
                "content": meta.get("text", "")[:500],
                "category": meta.get("category", "unknown"),
                "source": meta.get("source", "unknown"),
                "version": meta.get("version", "unknown"),
                "pii": meta.get("pii", False),
                "relevance_score": round(match.get("score", 0), 4),
            })

        return {"query": req.query, "total_results": len(records), "records": records}
    except Exception as e:
        logger.exception("Error in query_test")
        return JSONResponse(status_code=500, content={"error": str(e)})