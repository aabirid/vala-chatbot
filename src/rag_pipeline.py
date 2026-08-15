import os
import json
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

SCRAPED_DATA_FILE = "scraped_data.json"
CHROMA_DB_PATH = "chroma_db"
COLLECTION_NAME = "vala_knowledgebase"

def load_articles():
    print("Loading scraped articles...")
    with open(SCRAPED_DATA_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)
    print(f"Loaded {len(articles)} articles")
    return articles

def split_articles(articles):
    print("Splitting articles into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = []
    metadatas = []
    
    for article in articles:
        full_text = f"Title: {article['title']}\n\n{article['content']}"
        article_chunks = text_splitter.split_text(full_text)

        for chunk in article_chunks:
            chunks.append(chunk)
            metadatas.append({
                "title": article["title"],
                "url": article["url"]
            })
    print(f"Created {len(chunks)} chunks from {len(articles)} articles")
    return chunks, metadatas

def load_embedding_model():
    print("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}        )
    print("Embedding model loaded")
    return embeddings

def build_vector_store(chunks, metadatas, embeddings):
    print("Building ChromaDB vector store...")
    print(f"   Processing {len(chunks)} chunks — please wait...")
    vector_store = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=CHROMA_DB_PATH,
        collection_name=COLLECTION_NAME
    )
    print(f"Vector store saved to {CHROMA_DB_PATH}/")
    return vector_store

def load_vector_store(embeddings):
    print("Loading ChromaDB vector store...")
    vector_store = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    print("Vector store loaded")
    return vector_store

def query_vector_store(question,k=3):
    embeddings = load_embedding_model()
    vector_store = load_vector_store(embeddings)
    results = vector_store.similarity_search(question, k=k)
    return results

if __name__ == "__main__":
    print("Building RAG pipeline...")
    articles = load_articles()
    chunks, metadatas = split_articles(articles)
    embeddings = load_embedding_model()
    build_vector_store(chunks, metadatas, embeddings)
    print("RAG pipeline built successfully")

    # Test query
    print("\n🔍 Testing with a sample query...")
    results = query_vector_store("Comment créer une adresse email?")

    print(f"\nTop 3 results:")
    for i, doc in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Title: {doc.metadata['title']}")
        print(f"URL:   {doc.metadata['url']}")
        print(f"Text:  {doc.page_content[:150]}...")