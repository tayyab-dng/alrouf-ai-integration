import os
from dotenv import load_dotenv
import chromadb
import google.generativeai as genai
from pathlib import Path

# Load environment variables from .env in project root
BASE_DIR = Path(__file__).parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Setup ChromaDB persistent client pointing to /rag/db
DB_DIR = Path(__file__).parent / "db"
chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
collection = chroma_client.get_collection("alrouf_knowledge")

# Setup Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment or .env file.")
genai.configure(api_key=api_key)

def generate_bilingual_response(query: str) -> dict:
    """
    Retrieves relevant document chunks from ChromaDB and uses Gemini 3.1 Flash Lite
    to generate an answer in the same language as the query (English or Arabic).
    """
    # a) Search ChromaDB for top 3 relevant chunks
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    # Retrieve documents and metadatas
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    
    # b) Construct prompt with Context
    context_str = "\n\n".join(documents)
    
    prompt = f"""You are a helpful customer support and technical assistant for AL ROUF LED.
You are given the following Context containing product specifications and policies.
Use ONLY the provided Context to answer the user's Query. If the answer cannot be found in the Context, state that you do not know the answer based on the available documentation. Do not make up facts.

You must automatically detect the language of the Query (English or Arabic) and reply in that EXACT same language.

Context:
---
{context_str}
---

Query: {query}

Answer:"""

    # c) Initialize Gemini model (Gemini 3.1 Flash Lite)
    # The exact string is models/gemini-3.1-flash-lite or gemini-3.1-flash-lite
    model = genai.GenerativeModel("gemini-3.1-flash-lite")
    
    # Generate content
    response = model.generate_content(prompt)
    
    # Format and return dict
    source_docs = [
        {"text": doc, "source": meta.get("source", "unknown")}
        for doc, meta in zip(documents, metadatas)
    ]
    
    return {
        "query": query,
        "response": response.text.strip(),
        "sources": source_docs
    }

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    # Test queries
    en_query = "What is the warranty on the solar street light?"
    ar_query = "ما هي أبعاد اللوحة الذكية؟"

    print("--- Testing English Query ---")
    print(f"Query: {en_query}")
    en_result = generate_bilingual_response(en_query)
    print(f"Response:\n{en_result['response']}\n")
    print("Sources:")
    for src in en_result["sources"]:
        print(f"- {src['source']}")

    print("\n--- Testing Arabic Query ---")
    print(f"Query: {ar_query}")
    ar_result = generate_bilingual_response(ar_query)
    print(f"Response:\n{ar_result['response']}\n")
    print("Sources:")
    for src in ar_result["sources"]:
        print(f"- {src['source']}")
