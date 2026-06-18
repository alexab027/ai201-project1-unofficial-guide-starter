import json
import shutil
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


CHUNKS_PATH = Path("documents/chunks.json")
CHROMA_PATH = Path("chroma_db")
COLLECTION_NAME = "mit_unofficial_guide"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks(path: Path = CHUNKS_PATH) -> list[dict]:
    """Load chunks created by ingest.py."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def reset_chroma_db():
    """
    Delete the old ChromaDB folder so the database is rebuilt from scratch.

    Run this whenever chunking logic changes so stale embeddings don't persist.
    """
    if CHROMA_PATH.exists():
        shutil.rmtree(CHROMA_PATH)


def build_vector_store(reset: bool = True):
    """
    Embed all chunks and store them in ChromaDB.

    collection.add() stores four parallel lists:
    - ids:        unique string IDs, one per chunk
    - documents:  raw chunk text (Chroma keeps this alongside the embedding)
    - embeddings: float vectors from the sentence-transformer model
    - metadatas:  dicts of source info returned alongside results at query time
    """
    if reset:
        reset_chroma_db()

    chunks = load_chunks()

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(f"chunk_{i}")
        documents.append(chunk["text"])
        metadatas.append({
            "chunk_index": i,
            "source": chunk.get("source", ""),
            "title": chunk.get("title", ""),
            "section": chunk.get("section", ""),
            "type": chunk.get("type", ""),
            "word_count": chunk.get("word_count", 0),
        })

    print(f"Embedding {len(documents)} chunks...")
    embeddings = model.encode(documents).tolist()

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"Saved {len(documents)} chunks to ChromaDB collection: {COLLECTION_NAME}")

    return collection, model


def load_vector_store():
    """
    Load the existing ChromaDB collection and embedding model without rebuilding.
    Call this after build_vector_store() has already been run once.
    """
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    return collection, model


def retrieve(query: str, k: int = 8) -> list[dict]:
    """
    Retrieve the top-k most relevant chunks for a query.

    collection.query() takes an embedded query vector and returns the k nearest
    chunks by cosine distance. Lower distance = more similar to the query.

    k defaults to 8 per the planning spec (target: 8-10 chunks per query).
    """
    collection, model = load_vector_store()

    query_embedding = model.encode([query]).tolist()[0]

    # n_results controls how many chunks come back.
    # include defaults to ["documents", "metadatas", "distances"] so we get
    # text, metadata, and similarity scores in one call.
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
    )

    retrieved = []

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append({
            "text": text,
            "metadata": metadata,
            "distance": distance,
        })

    return retrieved


def print_results(query: str, results: list[dict]):
    print("=" * 100)
    print(f"QUERY: {query}")
    print("=" * 100)

    for i, result in enumerate(results, start=1):
        metadata = result["metadata"]

        print(f"\nRESULT {i}")
        print(f"Distance: {result['distance']:.4f}")
        print(f"Title:    {metadata.get('title')}")
        print(f"Source:   {metadata.get('source')}")
        print(f"Section:  {metadata.get('section')}")
        print(f"Type:     {metadata.get('type')}")
        print()
        print(result["text"])
        print("-" * 100)


if __name__ == "__main__":
    build_vector_store(reset=True)

    test_queries = [
        "How do I choose between 6-3 and 6-4?",
        "Should I take 6.1210 and 6.1010 at the same time?",
        "I am struggling to feel like I fit in as a course 6.",
        "How do course sixes find balance?",
        "I don't know what courses to take next semester after 6.100A and 6.1200.",
    ]

    for query in test_queries:
        results = retrieve(query, k=8)
        print_results(query, results)
