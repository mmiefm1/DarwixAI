from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.exception_handlers import catch_exception_middleware
from routes.upload_pdfs import router as upload_router
from routes.ask_question import router as ask_router
from routes.scrape_url import router as scrape_router
from routes.voice_respond import router as voice_router
from routes.add_content import router as add_content_router
from routes.query_test import router as query_test_router

app=FastAPI(title="Medical Assistant API",description="API for AI Medical Assistant Chatbot")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.middleware("http")(catch_exception_middleware)


# 1. upload pdfs documents
app.include_router(upload_router)
# 2. asking query
app.include_router(ask_router)
# 3. scraping websites
app.include_router(scrape_router)
# 4. voice agent connection point (Vapi tool-call target)
app.include_router(voice_router)
app.include_router(add_content_router)
app.include_router(query_test_router)