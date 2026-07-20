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

## 📁 Project Structure

```text
Medical-AI-Assistant-main/
│
├── client/                                 # Frontend application
│   ├── components/
│   │   ├── chatUI.py                       # Chat interface
│   │   ├── history_download.py             # Chat history download
│   │   └── upload.py                       # PDF upload UI
│   │
│   ├── utils/
│   │   ├── api.py                          # Backend API communication
│   │   ├── app.py                          # Streamlit entry point
│   │   └── config.py                       # Client configuration
│   │
│   └── requirements.txt
│
├── docs/                                   # Project documentation
│   ├── Audio/                              # Recorded voice call samples
│   ├── transcripts/                        # Conversation transcripts
│   ├── retrieval_test_report.md            # RAG retrieval evaluation (Q2)
│   └── localization_notes.md               # Localization & ASR evaluation (Q3)
│
├── server/                                 # FastAPI backend
│   ├── middlewares/
│   │   └── exception_handlers.py           # Global exception handling
│   │
│   ├── modules/
│   │   ├── cleaning.py                     # Data preprocessing
│   │   ├── llm.py                          # LLM integration
│   │   ├── load_vectorstore.py             # Vector database loader
│   │   ├── pdf_handlers.py                 # PDF processing
│   │   ├── query_handlers.py               # Query processing
│   │   └── web_scraper.py                  # Website scraping
│   │
│   ├── routes/
│   │   ├── add_content.py                  # Add custom knowledge
│   │   ├── ask_question.py                 # Chat endpoint
│   │   ├── query_test.py                   # Retrieval testing endpoint
│   │   ├── scrape_url.py                   # Website ingestion endpoint
│   │   ├── upload_pdfs.py                  # PDF upload endpoint
│   │   └── voice_respond.py                # Voice assistant endpoint
│   │
│   ├── uploaded_docs/                      # Uploaded PDF storage
│   ├── .env                                # Environment variables
│   ├── logger.py                           # Logging configuration
│   ├── main.py                             # FastAPI application entry point
│   ├── requirements.txt
│   └── test.py
│
├── tests/                                  # Automated tests
│   ├── test_live_endpoint.py
│   └── test_voice_endpoint.py
│
├── multilingual/                           # Multilingual voice configurations
│   ├── vapi_id_config.txt
│   ├── vapi_ph_config.txt
│   ├── web_call_id.html
│   └── web_call_ph.html
│
├── voice-agent/                            # Voice assistant configuration
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
| **client/** | Streamlit frontend application |
| **server/** | FastAPI backend and Retrieval-Augmented Generation (RAG) pipeline |
| **tests/** | Automated API and integration tests |
| **docs/** | Project documentation, evaluation reports, multilingual transcripts, and audio recordings |
| **multilingual/** | Language-specific voice assistant configurations |
| **voice-agent/** | Vapi voice assistant integration |
| **.env** | Environment variables *(excluded from version control)* |
| **pyproject.toml** | Python project configuration |
| **requirements.txt** | Project dependencies |
| **README.md** | Project documentation and setup guide |

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
- **Test call recordings/transcripts:** `docs/transcripts/Ques1_*.txt`
- **Sample voice call audio:** [`docs/Audio/Ques1_voice_agent_english.wav`](docs/Audio/Ques1_voice_agent_english.wav)
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
- **Retrieval test report:** `docs/Ques2_retrieval_test_report.md` — 5 queries
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


## 📊 Retrieval Evaluation Summary

You can refer to detailed version of outputs in "docs/retrieval_test_report.md"

The retrieval pipeline was evaluated using **five representative queries** covering key user intents: **Product**, **Policy**, **Qualification**, **FAQ**, and **Objection Handling**. For each query, the vector database returned the **top-3 most relevant chunks** based on semantic similarity. A **minimum relevance threshold of 0.35** was used by the voice assistant to determine whether the retrieved context was sufficiently reliable for response generation.

### Evaluation Results

| Category | Top Score | Verdict | Summary |
|----------|:---------:|:-------:|---------|
| 🏥 Product | **0.3235** | ❌ Rejected | No relevant knowledge existed in the knowledge base. The retrieval system returned loosely related health policy benefits, but the confidence score remained below the threshold, preventing an incorrect response. |
| 📋 Policy | **0.6265** | ✅ Correct | Successfully retrieved eligibility information directly related to the user's question, supported by multiple relevant documents. |
| 💼 Qualification | **0.3668** | ⚠️ Incorrect Retrieval | Retrieved documents containing similar numeric values (₹50,000) rather than qualification criteria, highlighting a knowledge base coverage gap. |
| ❓ FAQ | **0.4390** | ⚠️ Ambiguous | Retrieved multiple valid processing timelines (claim settlement, cashless approval, and application processing). The query requires clarification before generating a final answer. |
| 💬 Objection Handling | **0.4230** | ✅ Correct | Successfully retrieved objection-handling guidance along with supporting policy information, producing a grounded response. |

### Overall Performance

| Metric | Result |
|---------|:------:|
| Total Queries Evaluated | **5** |
| Correct Retrievals | **2** |
| Partially Correct / Ambiguous | **2** |
| Correctly Rejected (Low Confidence) | **1** |
| Hallucinated Responses | **0** |

### Key Observations

- ✅ The retrieval system performs reliably for **policy-related** and **objection-handling** queries where relevant knowledge exists.
- ✅ The confidence threshold successfully prevents hallucinations by rejecting unsupported queries instead of generating misleading answers.
- ⚠️ Retrieval quality is limited by the coverage of the indexed knowledge base. Missing qualification-related content resulted in a semantically similar but incorrect match.
- ⚠️ Broad or ambiguous questions can retrieve multiple valid contexts, indicating the need for a clarification step before response generation.

> **Conclusion:** The evaluation demonstrates that the retrieval pipeline effectively grounds responses when relevant knowledge is available and safely avoids hallucinations when confidence is low. Future enhancements will focus on improving knowledge base coverage and refining confidence-based retrieval strategies.


## 📞 Sample Voice Conversation

A complete transcript of a real conversation with the voice assistant is available here:

📄 **[Sample Voice Call Transcript](docs/Ques1_sample_call_transcript_english.md)**

The conversation demonstrates:
- Lead qualification flow
- Retrieval-Augmented Generation (RAG)
- Objection handling
- Medical safety guardrails
- Escalation to a licensed agent when required

## 🌎 Localization Support

The voice AI system supports localized conversations for Filipino (Tagalog) and Bahasa Indonesia.

Supported features:
- Multi-language ASR/TTS configuration
- Cultural conversational adaptation
- Local financial and insurance terminology handling
- Objection management and human-agent escalation

Detailed localization testing results are available in:
`docs/localization-evaluation.md`