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
    
    prompt = f"""You are a technical assistant for AL ROUF LED. If the provided context does not contain the exact information needed to answer the user's query, you must cleanly refuse by replying EXACTLY with: "I am sorry, but I can only answer questions based on the provided AL ROUF LED documentation." Translate this refusal into Arabic if the user's query is in Arabic. Do not attempt to guess or provide outside information.

You must automatically detect the language of the Query (English or Arabic) and reply in that EXACT same language.

Context:
---
{context_str}
---

Query: {query}

Answer:"""

    # c) Initialize Gemini model (Gemini 3.1 Flash Lite)
    model = genai.GenerativeModel("gemini-3.1-flash-lite")
    
    # Generate content
    response = model.generate_content(prompt)
    
    # Format and return dict with citations
    unique_citations = list(set(meta.get("source", "unknown") for meta in metadatas))
    source_docs = [
        {"text": doc, "source": meta.get("source", "unknown")}
        for doc, meta in zip(documents, metadatas)
    ]
    
    return {
        "query": query,
        "response": response.text.strip(),
        "citations": unique_citations,
        "sources": source_docs
    }

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    
    # Test queries
    en_query = "What is the warranty on the solar street light?"
    ar_query = "ما هي أبعاد اللوحة الذكية؟"
    out_of_scope_query = "What is the recipe for biryani?"

    print("--- Testing English Query ---")
    print(f"Query: {en_query}")
    en_result = generate_bilingual_response(en_query)
    print(f"Response:\n{en_result['response']}\n")
    print(f"Citations: {en_result['citations']}")

    print("\n--- Testing Arabic Query ---")
    print(f"Query: {ar_query}")
    ar_result = generate_bilingual_response(ar_query)
    print(f"Response:\n{ar_result['response']}\n")
    print(f"Citations: {ar_result['citations']}")

    print("\n--- Testing Out-of-Scope Query ---")
    print(f"Query: {out_of_scope_query}")
    oos_result = generate_bilingual_response(out_of_scope_query)
    print(f"Response:\n{oos_result['response']}\n")
    print(f"Citations: {oos_result['citations']}")
