import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_cohere import CohereEmbeddings
from modules.cleaning import clean_text

load_dotenv()

PINECONE_ENV = "us-east-1"
PINECONE_INDEX_NAME = "medicalinsurance"

UPLOAD_DIR = "./uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def load_vectorstore(uploaded_files):
    # Initialize Pinecone inside function not at startup
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)
    existing_indexes = [i["name"] for i in pc.list_indexes()]

    if PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=384,
            metric="dotproduct",
            spec=spec
        )
        while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
            time.sleep(1)

    index = pc.Index(PINECONE_INDEX_NAME)

    embed_model = CohereEmbeddings(
    cohere_api_key=os.environ["COHERE_API_KEY"],
    model="embed-english-light-v3.0"
)

    file_paths = []
    for file in uploaded_files:
        save_path = Path(UPLOAD_DIR) / file.filename
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        file_paths.append(str(save_path))

    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        texts = [chunk.page_content for chunk in chunks]
        metadatas = [{"text": chunk.page_content, **chunk.metadata} for chunk in chunks]
        ids = [f"{Path(file_path).stem}-{i}" for i in range(len(chunks))]

        print(f"Embedding {len(texts)} chunks...")
        embeddings = embed_model.embed_documents(texts)

        print("Uploading to Pinecone...")
        with tqdm(total=len(embeddings), desc="Upserting to Pinecone") as progress:
            index.upsert(vectors=zip(ids, embeddings, metadatas))
            progress.update(len(embeddings))

        print(f"Upload complete for {file_path}")


def load_web_content(scraped_docs: list, category: str = "website", version: str = "1.0"):
    """
    scraped_docs: list of {"source": url, "text": raw_text, "status": "ok"/"failed"}
    from web_scraper.scrape_urls(). Cleans, chunks, embeds, and upserts into
    the SAME Pinecone index used for PDFs, so retrieval covers both.
    """
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = pc.Index(PINECONE_INDEX_NAME)
    embed_model = CohereEmbeddings(
        cohere_api_key=os.environ["COHERE_API_KEY"],
        model="embed-english-light-v3.0"
    )
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    total_chunks = 0
    for doc in scraped_docs:
        if doc.get("status") != "ok" or not doc.get("text"):
            print(f"Skipping failed/empty source: {doc.get('source')} - {doc.get('error')}")
            continue

        cleaned = clean_text(doc["text"])
        chunks = splitter.split_text(cleaned["content"])

        texts = chunks
        metadatas = [{
            "text": chunk,
            "source": doc["source"],
            "category": category,
            "version": version,
            "pii": cleaned["pii_detected"],
        } for chunk in chunks]
        ids = [f"web-{hash(doc['source']) & 0xffffffff}-{i}" for i in range(len(chunks))]

        print(f"Embedding {len(texts)} chunks from {doc['source']}...")
        embeddings = embed_model.embed_documents(texts)

        index.upsert(vectors=zip(ids, embeddings, metadatas))
        total_chunks += len(chunks)
        print(f"Upserted {len(chunks)} chunks for {doc['source']}")

    return {"total_chunks_indexed": total_chunks}

def load_raw_text(title: str, text: str, category: str = "general",
                   source: str = "manual_entry", version: str = "1.0"):
    """
    Directly index hand-written content (synthetic policy docs, FAQs you
    write yourself) without needing a PDF or a scrapeable URL. Useful for
    localized content where finding a real source page quickly isn't practical.
    """
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = pc.Index(PINECONE_INDEX_NAME)
    embed_model = CohereEmbeddings(
        cohere_api_key=os.environ["COHERE_API_KEY"],
        model="embed-english-light-v3.0"
    )
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    cleaned = clean_text(text)
    chunks = splitter.split_text(cleaned["content"])

    metadatas = [{
        "text": chunk,
        "title": title,
        "source": source,
        "category": category,
        "version": version,
        "pii": cleaned["pii_detected"],
    } for chunk in chunks]
    ids = [f"manual-{hash(title) & 0xffffffff}-{i}" for i in range(len(chunks))]

    embeddings = embed_model.embed_documents(chunks)
    index.upsert(vectors=zip(ids, embeddings, metadatas))

    return {"total_chunks_indexed": len(chunks)}