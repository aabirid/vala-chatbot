# Vala Customer Support Chatbot

A RAG-powered chatbot that answers customer questions using the Vala knowledgebase.

## Tech Stack
- Python 3.12
- LangChain + ChromaDB (RAG Pipeline)
- OpenAI API (LLM)
- FastAPI (Backend)
- Streamlit (Frontend)

## Setup
1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Add your OpenAI API key to `.env`
6. Run the scraper: `python src/scraper.py`