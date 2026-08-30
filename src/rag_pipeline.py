import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ── Paths resolved relative to this file, not the CWD ──────────────────────
_SRC_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _SRC_DIR.parent

SCRAPED_DATA_FILE = _ROOT_DIR / "scraped_data.json"
CHROMA_DB_PATH    = str(_ROOT_DIR / "chroma_db")
COLLECTION_NAME   = "vala_knowledgebase"

# Multilingual model — better than all-MiniLM-L6-v2 for French/Arabic content
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Minimum relevance score (0–1) for a chunk to be included in results
RELEVANCE_THRESHOLD = 0.45

# ── Module-level singletons ─────────────────────────────────────────────────
_embedding_model = None
_vector_store    = None


def load_embedding_model() -> HuggingFaceEmbeddings:
    global _embedding_model
    if _embedding_model is not None:
        return _embedding_model
    logger.info("Loading embedding model (first time only)…")
    _embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    logger.info("Embedding model loaded: %s", EMBEDDING_MODEL_NAME)
    return _embedding_model


def load_vector_store(embeddings: HuggingFaceEmbeddings) -> Chroma:
    global _vector_store
    if _vector_store is not None:
        return _vector_store
    logger.info("Loading ChromaDB vector store from %s…", CHROMA_DB_PATH)
    _vector_store = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )
    logger.info("Vector store loaded")
    return _vector_store


# ── Data helpers (used only when rebuilding the vector store) ───────────────

def load_articles() -> list[dict]:
    logger.info("Loading scraped articles from %s…", SCRAPED_DATA_FILE)
    with open(SCRAPED_DATA_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)
    logger.info("Loaded %d articles", len(articles))
    return articles


def split_articles(articles: list[dict]) -> tuple[list[str], list[dict]]:
    logger.info("Splitting articles into chunks…")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks: list[str] = []
    metadatas: list[dict] = []

    for article in articles:
        full_text = f"Title: {article['title']}\n\n{article['content']}"
        article_chunks = text_splitter.split_text(full_text)

        for chunk in article_chunks:
            if len(chunk.strip()) < 100:
                continue
            chunks.append(chunk)
            metadatas.append({"title": article["title"], "url": article["url"]})

    logger.info("Created %d chunks from %d articles", len(chunks), len(articles))
    return chunks, metadatas


def build_vector_store(chunks: list[str], metadatas: list[dict], embeddings: HuggingFaceEmbeddings) -> Chroma:
    global _vector_store
    logger.info("Building ChromaDB vector store (%d chunks)…", len(chunks))
    _vector_store = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=CHROMA_DB_PATH,
        collection_name=COLLECTION_NAME,
    )
    logger.info("Vector store saved to %s/", CHROMA_DB_PATH)
    return _vector_store


# ── Public query function ───────────────────────────────────────────────────

def query_vector_store(question: str, k: int = 5) -> list:
    """Return up to *k* relevant document chunks for *question*.

    Only chunks that score at or above RELEVANCE_THRESHOLD are returned.
    Falls back gracefully to the raw results if the store does not support
    relevance scores.
    """
    embeddings = load_embedding_model()
    store = load_vector_store(embeddings)

    try:
        raw = store.similarity_search_with_relevance_scores(question, k=k * 3)
        filtered = [
            doc for doc, score in raw
            if score >= RELEVANCE_THRESHOLD and len(doc.page_content.strip()) > 100
        ]
        logger.info(
            "Query returned %d/%d chunks above threshold %.2f",
            len(filtered), len(raw), RELEVANCE_THRESHOLD,
        )
        return filtered[:k]
    except Exception:
        # Fallback: store may not implement relevance scores
        logger.warning("Relevance-score search failed, falling back to plain similarity search")
        raw_docs = store.similarity_search(question, k=k * 3)
        return [doc for doc in raw_docs if len(doc.page_content.strip()) > 100][:k]


# ── Script entry-point (rebuild the index) ─────────────────────────────────

if __name__ == "__main__":
    logger.info("Building RAG pipeline…")
    articles = load_articles()
    chunks, metadatas = split_articles(articles)
    embeddings = load_embedding_model()
    build_vector_store(chunks, metadatas, embeddings)
    logger.info("RAG pipeline built successfully")

    logger.info("Testing with a sample query…")
    results = query_vector_store("Comment créer une adresse email?")
    for i, doc in enumerate(results):
        logger.info(
            "Result %d — %s | %s | %.150s…",
            i + 1, doc.metadata["title"], doc.metadata["url"], doc.page_content,
        )