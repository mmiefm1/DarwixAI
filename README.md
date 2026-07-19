# AI Engineer Assessment Submission

## Overview
This project implements:
- **Q1:** A knowledge-grounded voice agent for health insurance lead qualification
- **Q2:** A production knowledge base pipeline (parsing, cleaning, chunking, embedding, retrieval)
- **Q3:** Localized voice bots for the Philippines (life insurance/bancassurance) and Indonesia (multifinance)
- **Q4:** Real-time call analysis and nudge generation *(in progress / see Q4 section below)*

All voice agents share one backend and Pinecone index, with per-market content
separated via a `category` field, so the same retrieval infrastructure serves
all three assistants without cross-contamination.

## Architecture

```text
                                  USER
                        (Phone / Web Widget)
                                       │
                                       │ Voice Query
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            VAPI VOICE PLATFORM                             │
│─────────────────────────────────────────────────────────────────────────────│
│ • Speech-to-Text (Deepgram)                                                │
│ • Conversation Orchestration                                               │
│ • GPT-4o generates tool calls when knowledge retrieval is required          │
│ • Text-to-Speech for final response                                        │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                │ Tool Call
                                │ POST /voice/search_kb?category=<market>
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND                                  │
│─────────────────────────────────────────────────────────────────────────────│
│ • Receives tool call from Vapi                                             │
│ • Extracts user's search query                                             │
│ • Reads category from query parameters                                     │
│ • Handles errors and logging                                               │
│ • Formats retrieved knowledge for the LLM                                  │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                │ User Query
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     COHERE EMBEDDINGS                                      │
│─────────────────────────────────────────────────────────────────────────────│
│ Model: embed-english-light-v3.0                                            │
│                                                                             │
│ Converts the natural language query into a dense semantic vector            │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                │ Query Embedding
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PINECONE VECTOR DATABASE                               │
│─────────────────────────────────────────────────────────────────────────────│
│ Shared Vector Index                                                        │
│ Metadata Filtering                                                         │
│    • category                                                              │
│    • source                                                                │
│                                                                             │
│ Performs Similarity Search                                                 │
│    • top_k = 3                                                             │
│    • Metadata Filter                                                       │
│    • Relevance Threshold = 0.28                                            │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                │ Most Relevant Knowledge Chunks
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                                    │
│─────────────────────────────────────────────────────────────────────────────│
│ • Removes irrelevant matches                                               │
│ • Formats retrieved chunks                                                 │
│ • Returns structured tool response                                         │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                │ Tool Response
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            GPT-4o (inside Vapi)                            │
│─────────────────────────────────────────────────────────────────────────────│
│ • Uses retrieved knowledge as context                                      │
│ • Generates a grounded response                                            │
│ • Avoids hallucinations                                                    │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
                      Vapi Text-to-Speech
                                │
                                ▼
                           Final Voice Response
                                │
                                ▼
                               USER
```

### Key design decisions
- **No hardcoded FAQs/policies in system prompts.** Every factual claim is
  retrieved live from the knowledge base via a tool call. If retrieval
  confidence falls below a relevance threshold, the agent explicitly says
  it doesn't know rather than guessing.
- **One shared index, filtered by category.** Rather than separate indexes
  per market, all content lives in one Pinecone index tagged with a
  `category` field (`health_insurance`, `ph_insurance`, `id_multifinance`).
  Each assistant's tool queries with its own category filter, keeping
  markets isolated while reusing the same infrastructure.
- **Retrieval-only tool, generation stays with Vapi's model.** The backend
  tool returns raw retrieved context (with citations), not a generated
  answer — Vapi's LLM does the final response generation, guided by the
  system prompt's grounding rules. This keeps the integration simple and
  auditable.


## 📁 Project Structure

```text
Medical-AI-Assistant-main/
│
├── client/                              # Frontend application
│   ├── components/
│   │   ├── chatUI.py                    # Chat interface
│   │   ├── history_download.py          # Chat history download
│   │   └── upload.py                    # PDF upload UI
│   │
│   ├── utils/
│   │   ├── api.py                       # Backend API calls
│   │   ├── app.py                       # Client entry point
│   │   └── config.py                    # Client configuration
│   │
│   └── requirements.txt
│
├── server/                              # Backend application
│   │
│   ├── middlewares/
│   │   └── exception_handlers.py        # Global exception handling
│   │
│   ├── modules/
│   │   ├── cleaning.py                  # Data preprocessing
│   │   ├── llm.py                       # LLM integration
│   │   ├── load_vectorstore.py          # Vector database loader
│   │   ├── pdf_handlers.py              # PDF processing
│   │   ├── query_handlers.py            # Query processing
│   │   └── web_scraper.py               # Website scraping
│   │
│   ├── routes/
│   │   ├── add_content.py               # Add custom knowledge
│   │   ├── ask_question.py              # Chat endpoint
│   │   ├── query_test.py                # Query testing
│   │   ├── scrape_url.py                # URL scraping endpoint
│   │   ├── upload_pdfs.py               # PDF upload endpoint
│   │   └── voice_respond.py             # Voice response endpoint
│   │
│   ├── uploaded_docs/                   # Uploaded PDF storage
│   ├── .env                             # Environment variables
│   ├── logger.py                        # Logging configuration
│   ├── main.py                          # FastAPI application entry point
│   ├── requirements.txt
│   └── test.py
│
├── tests/                               # Automated tests
│   ├── test_live_endpoint.py
│   └── test_voice_endpoint.py
│
├── multilingual/                        # Multilingual voice configurations
│   ├── vapi_id_config.txt
│   ├── vapi_ph_config.txt
│   ├── web_call_id.html
│   └── web_call_ph.html
│
├── voice-agent/                         # Voice AI integration
│   ├── vapi_en_config.txt
│   └── web-calling-interface.html
│
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── venv/
```


## 📂 Directory Overview

| Folder/File | Description |
|-------------|-------------|
| **client/** | Frontend application |
| **server/** | FastAPI backend services |
| **server/routes/** | API endpoints |
| **server/modules/** | Business logic (LLM, PDF, Vector DB, Scraping) |
| **server/middlewares/** | Exception handling middleware |
| **tests/** | API and integration tests |
| **multilingual/** | Language-specific voice configurations |
| **voice-agent/** | Vapi voice assistant integration |
| **uploaded_docs/** | Uploaded PDFs |
| **main.py** | Application entry point |
| **requirements.txt** | Python dependencies |
| **pyproject.toml** | Project configuration |
| **README.md** | Project documentation |


## Setup Instructions

### 1. Install dependencies
```bash
cd server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables
Create `.env` in `server/` and fill in:
PINECONE_API_KEY=
PINECONE_INDEX_NAME=medicalinsurance
PINECONE_ENV=us-east-1
COHERE_API_KEY=
GROQ_API_KEY=

### 3. Run the backend
```bash
uvicorn main:app --reload --port 8000
```
Verify at `http://127.0.0.1:8000/docs`.

### 4. Expose it publicly
Development used **ngrok** for tunneling:
```bash
ngrok http 8000
```
Note: free-tier ngrok URLs change on every restart. To re-run this project
live, update the `server.url` in each Vapi tool config to your current
ngrok URL (see files in `voice_agent/` and `multilingual/`).

### 5. Populate the knowledge base
Via `/docs`:
- `POST /upload_pdfs/` — PDF documents
- `POST /scrape_urls/` — web pages (specify `category`)
- `POST /add_content/` — direct text content (specify `category`)

### 6. Configure Vapi
Recreate each assistant/tool in the Vapi dashboard using the exact prompts
and settings documented in `voice_agent/*.txt` and `multilingual/*.txt`.

### 7. Test
- `POST /query_test/` — verify retrieval directly, see `docs/retrieval_test_report.md`
- Open the relevant `web_call_*.html` file (after filling in your Vapi
  public key + assistant ID) to place a live test call

## Q1 — Health Insurance Voice Agent
- **Use case:** Health insurance lead qualification
- **Web calling interface:** `voice_agent/web_calling_interface.html`
- **Test call recordings/transcripts:** `docs/transcripts/q1_*.txt`
- **Test coverage:** cooperative customer, objection, incomplete/conflicting
  details, out-of-scope question, human-assistance request 
- **Grounded fallback confirmed:** agent explicitly states when information
  is unavailable rather than inventing an answer 

## Q2 — Knowledge Base
- **Schema:** `record_id, title, content, category, source, version, pii`
- **Chunking:** token-aware splitting via LangChain's RecursiveCharacterTextSplitter
- **Retrieval:** Pinecone cosine similarity, category-filtered, relevance
  threshold of 0.28 (tuned against observed score distribution from real
  scraped content — see limitations)
- **Retrieval test report:** `docs/retrieval_test_report.md` — 7 queries
  covering product, qualification, policy, objection, FAQ, and a negative
  (unanswerable) test case
- **PII handling:** regex-based detection/masking for web-scraped and
  manually-added content (see limitations for PDF gap)

## Q3 — Multilingual Bots
- **Philippines:** life insurance/bancassurance, Taglish support, Deepgram
  nova-3 (language: tl), config in `multilingual/vapi_ph_config.txt`
- **Indonesia:** multifinance, Bahasa Indonesia, Deepgram nova-3 (language: id),
  config in `multilingual/vapi_id_config.txt`
- **Localization evidence:** `docs/localization_notes.md`
- **Test call recordings/transcripts:** `docs/transcripts/q3_ph_*.txt`, `q3_id_*.txt`

## Q4 — Real-Time Nudges
*[To be completed — will document streaming pipeline, latency measurements,
and nudge examples here once built]*

## Known Limitations
- PDF ingestion does not run PII detection (web-scraped/manual content does).
- PII regex can false-positive on numeric content (prices, step numbers).
- Multilingual test calls used pronunciation references rather than a
  fluent native speaker — see `docs/localization_notes.md`.
- Relevance threshold (0.28) was empirically tuned, not formally validated.
- ngrok tunnel is not permanent; a production deployment would need a
  stable hosted URL.
- Discovered and fixed a Vapi payload-parsing bug during development
  (tool arguments are nested under `function.arguments`, not top-level) —
  documented as a specific debugging example of API contract mismatches.

## Production Improvement Plan
- Deploy backend to Render/Railway for a permanent webhook URL.
- Add PII detection to the PDF ingestion path.
- Tighten phone-number regex to reduce false positives.
- Native-speaker validation pass for PH/Indonesia scripts and pronunciation.
- Add automated retrieval regression tests.
- Add proper logging/monitoring for tool-call failures in production.