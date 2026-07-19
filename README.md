# 🏥 Medical AI Assistant — RAG-powered Document Chatbot

---

## 🧠 Overview

**Medical AI Assistant** is an intelligent chatbot that lets users upload medical documents and ask health-related questions. Built on **Retrieval-Augmented Generation (RAG)**, the system retrieves the most relevant content from uploaded PDFs before generating accurate, context-aware responses — reducing hallucinations common in general-purpose LLMs.

---

## 🎓 Why RAG?

Standard LLMs generate answers from training data alone, which can be outdated or inaccurate for specialized domains like medicine. RAG solves this by grounding every response in **your actual documents** — making answers both reliable and traceable.

---

## 🔄 How It Works

```
User uploads PDF
      ↓
Text extracted → split into chunks → embedded → stored in Pinecone
      ↓
User asks a question
      ↓
Question embedded → similar chunks retrieved from Pinecone
      ↓
Retrieved context + question → LLaMA 3.1 via Groq
      ↓
Accurate, document-grounded answer
```

---

## ✨ Features

- Upload one or more medical PDFs
- Automatic text extraction and semantic chunking
- Vector embeddings stored in Pinecone
- LLaMA 3.1 8B served via Groq for fast inference
- FastAPI backend with clean REST endpoints
- Streamlit frontend for easy interaction
- Downloadable chat history

---

## 🌐 Tech Stack

| Layer | Technology |
|---|---|
| LLM | LLaMA 3.1 8B (Groq) |
| Embeddings | Cohere embed-english-light-v3.0 |
| Vector DB | Pinecone |
| Orchestration | LangChain |
| Backend | FastAPI, Python |
| Frontend | Streamlit |
| Deployment | Render |

---

## 📡 API Endpoints

```http
POST /upload_pdfs/   — Upload one or more PDF files
POST /ask/           — Ask a question (form field: question)
```

---

## 📁 Project Structure

```
Medical-AI-Assistant/
├── client/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── components/
│   │   ├── chatUI.py
│   │   ├── upload.py
│   │   └── history_download.py
│   └── utils/
│       └── api.py
│
└── server/
    ├── main.py
    ├── logger.py
    ├── requirements.txt
    ├── modules/
    │   ├── llm.py
    │   ├── load_vectorstore.py
    │   ├── pdf_handlers.py
    │   └── query_handlers.py
    ├── routes/
    │   ├── upload_pdfs.py
    │   └── ask_question.py
    └── middlewares/
        └── exception_handlers.py
```

---

## 🚀 Deployment

- **Frontend:** [Try it here](https://medical-ai-assistant-chatbot-rag.streamlit.app/)
- **Backend:** Hosted on Render
