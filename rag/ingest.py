import chromadb
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "db"

def chunk_text(text: str, chunk_size: int = 500) -> list:
    """
    Splits text into paragraphs to maintain structural markdown context.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        # If adding this paragraph exceeds chunk size, save current chunk and start a new one
        if len(current_chunk) + len(paragraph) + 2 > chunk_size:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = paragraph
        else:
            current_chunk = f"{current_chunk}\n\n{paragraph}" if current_chunk else paragraph
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def ingest_documents():
    # 1. Initialize persistent chromadb client
    DB_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(DB_DIR))
    
    # 2. Get or create collection (uses default ONNX MiniLM embedding function)
    collection = client.get_or_create_collection(
        name="alrouf_knowledge"
    )
    
    # 3. Read markdown files
    md_files = list(DATA_DIR.glob("*.md"))
    if not md_files:
        print("No documents found in /rag/data")
        return
        
    all_documents = []
    all_metadatas = []
    all_ids = []
    
    chunk_counter = 0
    for md_file in md_files:
        print(f"Reading file: {md_file.name}")
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Chunk text
        chunks = chunk_text(content)
        for i, chunk in enumerate(chunks):
            chunk_counter += 1
            all_documents.append(chunk)
            all_metadatas.append({"source": md_file.name, "chunk_index": i})
            all_ids.append(f"chunk_{chunk_counter}")
            
    # 4. Store in ChromaDB collection
    if all_documents:
        print(f"Ingesting {len(all_documents)} chunks into ChromaDB collection 'alrouf_knowledge'...")
        collection.add(
            documents=all_documents,
            metadatas=all_metadatas,
            ids=all_ids
        )
        print("Ingestion completed successfully!")
    else:
        print("No chunks generated.")

if __name__ == "__main__":
    ingest_documents()
