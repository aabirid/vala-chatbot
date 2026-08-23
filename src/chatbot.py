import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from rag_pipeline import query_vector_store

load_dotenv()

def load_llm():
    print("Loading LLM...")
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="groq/compound-mini",
        temperature=0.3,
    )
    print("LLM loaded")
    return llm

def build_prompt():
    template = """Tu es un assistant de support client pour Vala, une entreprise d'hébergement web marocaine.
Réponds à la question du client en utilisant uniquement le contexte ci-dessous.
Si la réponse ne se trouve pas dans le contexte, dis: "Je n'ai pas trouvé d'information sur ce sujet. Veuillez contacter le support Vala directement."
Réponds toujours dans la même langue que la question.
Sois concis, amical et clair.

Contexte:
{context}

Question: {question}

Réponse:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    return prompt

def ask(question):
    print("Searching knowledge base...")
    results = query_vector_store(question, k=5)

    if not results:
        return {
            "answer": "Je n'ai pas trouvé d'information sur ce sujet. Veuillez contacter le support Vala directement.",
            "sources": []
        }

    context_parts = []
    sources = []

    for doc in results:
        context_parts.append(doc.page_content)
        source = {
            "title": doc.metadata["title"],
            "url": doc.metadata["url"]
        }
        if source not in sources:
            sources.append(source)

    context = "\n\n---\n\n".join(context_parts)

    prompt = build_prompt()
    llm = load_llm()

    chain = prompt | llm
    response = chain.invoke({
        "context": context, 
        "question": question
    })

    return {
        "answer": response.content,
        "sources": sources
    }

if __name__ == "__main__":
    print("🤖 Vala Customer Support Chatbot")
    print("=" * 40)

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
        print(f"\n📚 Sources:")
        for source in result['sources']:
            print(f"   - {source['title']}")
            print(f"     {source['url']}")
        print("=" * 40)