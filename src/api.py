import os
import sys
import logging
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, Field
from chatbot import ask, load_llm
from rag_pipeline import load_embedding_model, load_vector_store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Rate limiter ────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── App Lifespan (Pre-warm models on server boot) ───────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("⚡ Warming up embedding model, vector store, and LLM...")
    try:
        embeddings = load_embedding_model()
        load_vector_store(embeddings)
        load_llm()
        logger.info("✅ All models warmed up and ready to serve requests!")
    except Exception:
        logger.exception("⚠️ Warmup failed, models will load on first request")
    yield


app = FastAPI(
    title="Vala Chatbot API",
    description="RAG-powered chatbot API for Vala knowledgebase",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — restrict to known origins via env var, default to localhost for dev
_allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [o.strip() for o in _allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# ── Models ──────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class Source(BaseModel):
    title: str
    url: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "online", "message": "Vala Chatbot API is running"}


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
def chat(request: Request, body: ChatRequest):
    logger.info("Received question: %.80s…", body.question)
    try:
        result = ask(body.question)
        return ChatResponse(
            answer=result["answer"],
            sources=[Source(**s) for s in result["sources"]],
        )
    except Exception as e:
        logger.exception("Error processing question")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")