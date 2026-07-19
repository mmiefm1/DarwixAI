from fastapi import APIRouter, Request
from langchain_cohere import CohereEmbeddings
from pinecone import Pinecone
from logger import logger
import os

router = APIRouter()

RELEVANCE_THRESHOLD = 0.35


def _search(query: str) -> str:
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = pc.Index(os.environ.get("PINECONE_INDEX_NAME", "medicalindex"))
    embed_model = CohereEmbeddings(
        cohere_api_key=os.environ["COHERE_API_KEY"],
        model="embed-english-light-v3.0"
    )
    embedded_query = embed_model.embed_query(query)
    res = index.query(vector=embedded_query, top_k=3, include_metadata=True)

    matches = res.get("matches", [])
    usable = [m for m in matches if m.get("score", 0) >= RELEVANCE_THRESHOLD]

    if not usable:
        return "No information available on this topic. Offer to escalate to a human instead of guessing."

    parts = [
        f"(source: {m['metadata'].get('source', 'unknown')}) {m['metadata'].get('text', '').replace(chr(10), ' ')}"
        for m in usable
    ]
    return " || ".join(parts)


@router.post("/voice/search_kb")
async def search_kb(request: Request):
    body = await request.json()
    tool_calls = body.get("message", {}).get("toolCallList", [])

    results = []
    for call in tool_calls:
        call_id = call.get("id")
        args = call.get("arguments", {})
        query = args.get("query", "") if isinstance(args, dict) else ""

        try:
            result_text = _search(query) if query else "No query provided."
        except Exception:
            logger.exception("Error in voice search_kb")
            result_text = "Knowledge base lookup failed. Offer to escalate to a human."

        results.append({"toolCallId": call_id, "result": result_text})

    return {"results": results}