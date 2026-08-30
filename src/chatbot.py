import os
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from rag_pipeline import query_vector_store

load_dotenv()

logger = logging.getLogger(__name__)

# ── Module-level singletons ─────────────────────────────────────────────────
_llm    = None
_prompt = None


def load_llm() -> ChatGroq:
    global _llm
    if _llm is not None:
        return _llm
    logger.info("Loading LLM…")
    _llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="groq/compound-mini",
        temperature=0.3,
    )
    logger.info("LLM loaded")
    return _llm


def build_prompt() -> ChatPromptTemplate:
    global _prompt
    if _prompt is not None:
        return _prompt
    template = """Tu es un assistant de support client pour Vala, une entreprise d'hébergement web marocaine.
Réponds à la question du client en utilisant uniquement le contexte ci-dessous.
Si la réponse ne se trouve pas dans le contexte, dis: "Je n'ai pas trouvé d'information sur ce sujet. Veuillez contacter le support Vala directement."
Réponds toujours dans la même langue que la question.
Sois concis, amical et clair.

Contexte:
{context}

Question: {question}

Réponse:"""
    _prompt = ChatPromptTemplate.from_template(template)
    return _prompt


def ask(question: str) -> dict:
    logger.info("Searching knowledge base for: %.80s…", question)
    results = query_vector_store(question, k=5)

    if not results:
        logger.info("No relevant chunks found for question")
        return {
            "answer": "Je n'ai pas trouvé d'information sur ce sujet. Veuillez contacter le support Vala directement.",
            "sources": [],
        }

    context_parts: list[str] = []
    sources: list[dict] = []

    for doc in results:
        context_parts.append(doc.page_content)
        source = {"title": doc.metadata["title"], "url": doc.metadata["url"]}
        if source not in sources:
            sources.append(source)

    context = "\n\n---\n\n".join(context_parts)

    prompt = build_prompt()
    llm    = load_llm()

    chain = prompt | llm
    response = chain.invoke({
        "context": context, 
        "question": question
    })
    logger.info("Answer generated (%d sources)", len(sources))

    return {
        "answer": response.content,
        "sources": sources
    }
# ── Script entry-point (manual testing) ────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    test_questions = [
        "Comment créer une adresse email?",
        "Comment réinitialiser mon mot de passe FTP?",
        "C'est quoi le CDN?"
    ]

    for question in test_questions:
        print(f"\n❓ Question: {question}")
        print("-" * 40)
        result = ask(question)
        print(f"💬 Answer:\n{result['answer']}")
        print("Sources:")
        for src in result["sources"]:
            print(f"   - {src['title']}")
            print(f"     {src['url']}")
        print("=" * 40)