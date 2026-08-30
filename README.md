# Vala Customer Support Chatbot

A RAG-powered chatbot that answers customer questions using the Vala knowledgebase.

## Live Demo
Ask questions like:
- "Comment créer une adresse email?"
- "Comment réinitialiser mon mot de passe FTP?"
- "C'est quoi le CDN?"

## Architecture
User Question
│
▼
React Frontend (UI)
│ HTTP POST
▼
FastAPI Backend (API)
│
▼
RAG Pipeline
├── ChromaDB (finds relevant articles)
└── Groq LLM (generates the answer)
│
▼
Answer + Sources

## Tech Stack
| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI + Uvicorn |
| Scraping | BeautifulSoup + Requests |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB |
| LLM | Groq (Llama / GPT-OSS) |
| Data | 220 articles scraped from myvala.com/knowledgebase |

## Project Structure
vala-chatbot/
├── src/
│ ├── scraper.py # Scrapes Vala knowledgebase
│ ├── rag_pipeline.py # Builds and queries ChromaDB
│ ├── chatbot.py # LLM answer generation
│ └── api.py # FastAPI backend
├── frontend/ # React chat UI
├── scraped_data.json # 220 scraped articles
├── chroma_db/ # Vector database (local)
├── .env # API keys (not committed)
└── requirements.txt # Python dependencies

## Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/aabirid/vala-chatbot.git
cd vala-chatbot
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file:
GROQ_API_KEY=your_groq_key_here

### 5. Build the RAG pipeline (first time only)
```bash
python src/rag_pipeline.py
```

### 6. Start the backend
```bash
uvicorn src.api:app --reload --port 8000
```

### 7. Start the frontend
```bash
cd frontend
npm install
npm run dev
```

### 8. Open the app
Go to http://localhost:5173

## How It Works

1. **Scraping** — BeautifulSoup scrapes 220 articles from the Vala knowledgebase
2. **Chunking** — Articles are split into 1000-character chunks with 200-char overlap
3. **Embedding** — Each chunk is converted to a vector using sentence-transformers
4. **Storage** — Vectors are stored in ChromaDB locally
5. **Query** — User question is embedded and matched against stored vectors
6. **Generation** — Top matching chunks are sent to Groq LLM as context
7. **Answer** — LLM generates a grounded answer based only on Vala's docs

## GitHub
https://github.com/aabirid/vala-chatbot