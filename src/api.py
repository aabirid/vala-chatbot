import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import ask

app = FastAPI(
    title="Vala Chatbot API",
    description="RAG-powered chatbot API for Vala knowledgebase",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class  ChatRequest(BaseModel):
    question: str

class Source(BaseModel):
    title: str
    url: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Vala Chatbot API is running"
    }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=400, 
            detail="Question cannot be empty"
        )

    try:
        result = ask(request.question)
        return ChatResponse(
            answer=result["answer"],
            sources=[Source(**s) for s in result["sources"]]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )