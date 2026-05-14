"""Retrieval module for selecting relevant chunks for a user query."""

from __future__ import annotations

from pathlib import Path
import sys

import chromadb

CHROMA_DB_DIR = Path("chroma_db")
COLLECTION_NAME = "gspace_site"


def retrieve_chunks(query: str, top_k: int = 5) -> list[dict[str, object]]:
    """Retrieve relevant chunks for a question from the ChromaDB index."""

    cleaned_query = query.strip()
    if not cleaned_query:
        raise ValueError("Query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than 0.")

    if not CHROMA_DB_DIR.exists():
        raise RuntimeError(
            f"ChromaDB directory '{CHROMA_DB_DIR}' does not exist. "
            "Build the index before running retrieval."
        )

    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))

    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as exc:  # pragma: no cover - defensive for backend errors
        raise RuntimeError(
            f"Collection '{COLLECTION_NAME}' was not found in '{CHROMA_DB_DIR}'. "
            "Build or load the index before querying."
        ) from exc

    if collection.count() == 0:
        raise RuntimeError(
            f"Collection '{COLLECTION_NAME}' is empty. "
            "Index content before running retrieval."
        )

    results = collection.query(
        query_texts=[cleaned_query],
        n_results=top_k,
        include=["metadatas", "documents", "distances"],
    )

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    chunks: list[dict[str, object]] = []
    for idx, chunk_id in enumerate(ids):
        metadata = metadatas[idx] if idx < len(metadatas) and metadatas[idx] else {}
        text = documents[idx] if idx < len(documents) else ""
        distance = distances[idx] if idx < len(distances) else None

        chunks.append(
            {
                "chunk_id": chunk_id,
                "text": text,
                "url": metadata.get("url", ""),
                "title": metadata.get("title", ""),
                "source_type": metadata.get("source_type", ""),
                "distance": distance,
            }
        )

    return chunks


def _preview(text: str, max_len: int = 180) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_len:
        return compact
    return f"{compact[: max_len - 3]}..."


def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        print('Usage: python -m gspace_chat.retriever "<query>"')
        return 1

    query = " ".join(argv[1:])

    try:
        chunks = retrieve_chunks(query)
    except Exception as exc:
        print(f"Retrieval error: {exc}")
        return 1

    if not chunks:
        print("No matching chunks found.")
        return 0

    for i, chunk in enumerate(chunks, start=1):
        print(f"\n[{i}] {chunk['title'] or '(untitled)'}")
        print(f"URL: {chunk['url'] or '(no url)'}")
        print(f"Distance: {chunk['distance']}")
        print(f"Preview: {_preview(str(chunk['text']))}")

    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
