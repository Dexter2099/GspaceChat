"""Indexing module for building a ChromaDB index from processed chunks."""

from __future__ import annotations

import json
from pathlib import Path

import chromadb


CHUNKS_PATH = Path("data/processed/chunks.jsonl")
CHROMA_PATH = Path("chroma_db")
COLLECTION_NAME = "gspace_site"


def load_chunks(chunks_path: Path = CHUNKS_PATH) -> list[dict[str, str]]:
    """Load chunk records from a JSONL file."""
    chunks: list[dict[str, str]] = []
    with chunks_path.open("r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            chunks.append(json.loads(line))
    return chunks


def build_index(chunks: list[dict[str, str]]) -> None:
    """Build and persist a ChromaDB collection from chunk records."""
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    existing_collections = {collection.name for collection in client.list_collections()}
    if COLLECTION_NAME in existing_collections:
        client.delete_collection(name=COLLECTION_NAME)

    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [
        {
            "url": chunk["url"],
            "title": chunk["title"],
            "source_type": chunk["source_type"],
        }
        for chunk in chunks
    ]

    if chunks:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)

    print(f"chunks loaded: {len(chunks)}")
    print(f"chunks indexed: {len(chunks)}")
    print(f"collection name: {COLLECTION_NAME}")
    print(f"database path: {CHROMA_PATH}")


def main() -> None:
    """CLI entrypoint for rebuilding the ChromaDB index."""
    chunks = load_chunks()
    build_index(chunks)


if __name__ == "__main__":
    main()
