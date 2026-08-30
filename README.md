# Vala Customer Support Chatbot

An AI-powered customer support chatbot that answers questions using the Vala knowledgebase, built with a RAG (Retrieval-Augmented Generation) architecture.

## What It Does
Ask questions in French or English and get accurate answers based on Vala's official documentation:
- "Comment créer une adresse email?"
- "Comment réinitialiser mon mot de passe FTP?"
- "C'est quoi le CDN?"

## Architecture

    User Question
          │
          ▼
    React Frontend
          │ HTTP POST /chat
          ▼
    FastAPI Backend
          │
          ▼
    RAG Pipeline
      ├── ChromaDB ──→ finds relevant articles
      └── Groq LLM ──→ generates the answer
          │
          ▼
    Answer + Sources

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI + Uvicorn |
| Scraping | BeautifulSoup + Requests |
| Embeddings | sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2) |
| Vector DB | ChromaDB |
| LLM | Groq |
| Data | 220 articles from myvala.com/knowledgebase |

## Project Structure

    vala-chatbot/
    ├── src/
    │   ├── scraper.py         → scrapes the Vala knowledgebase
    │   ├── rag_pipeline.py    → builds and queries ChromaDB
    │   ├── chatbot.py         → LLM answer generation
    │   └── api.py             → FastAPI backend
    ├── frontend/              → React chat UI
    ├── scraped_data.json      → 220 scraped articles
    ├── chroma_db/             → vector database (local)
    ├── .env                   → API keys (not committed)
    └── requirements.txt       → Python dependencies

## Setup & Installation

### 1. Clone the repo
    git clone https://github.com/aabirid/vala-chatbot.git
    cd vala-chatbot

### 2. Create virtual environment
    python -m venv venv
    venv\Scripts\activate

### 3. Install Python dependencies
    pip install -r requirements.txt

### 4. Set up environment variables
Create a `.env` file in the root folder:
    GROQ_API_KEY=your_groq_key_here
    ALLOWED_ORIGINS=http://localhost:5173

### 5. Build the RAG pipeline (first time only)
    python src/rag_pipeline.py

### 6. Start the backend
    uvicorn src.api:app --reload --port 8000

### 7. Start the frontend
    cd frontend
    npm install
    npm run dev

### 8. Open the app
    http://localhost:5173

## How It Works

1. **Scraping** — BeautifulSoup scrapes 220 articles from the Vala knowledgebase
2. **Chunking** — Articles split into 1000-character chunks with 150-char overlap
3. **Embedding** — Each chunk converted to a vector using sentence-transformers
4. **Storage** — Vectors stored locally in ChromaDB
5. **Query** — User question embedded and matched against stored vectors
6. **Generation** — Top matching chunks sent to Groq LLM as context
7. **Answer** — LLM generates a grounded answer based only on Vala's docs