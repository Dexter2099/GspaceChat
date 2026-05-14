"""Chunking module for splitting cleaned text into retrieval units."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

CLEAN_PATH = Path("data/processed/clean_pages.jsonl")
CHUNKS_PATH = Path("data/processed/chunks.jsonl")
TARGET_CHUNK_WORDS = 700
OVERLAP_WORDS = 100
MIN_CHUNK_WORDS = 80
SOURCE_TYPE = "gilmour_website"


def _load_jsonl(path: Path) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            documents.append(json.loads(line))
    return documents


def _write_jsonl(path: Path, records: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _split_units(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", normalized) if p.strip()]
    if len(paragraphs) <= 1:
        return [line.strip() for line in normalized.split("\n") if line.strip()]
    return paragraphs


def _deterministic_chunk_id(url: str, chunk_index: int) -> str:
    digest = hashlib.sha1(f"{url}|{chunk_index}".encode("utf-8")).hexdigest()
    return f"chunk_{digest[:16]}"


def chunk_documents(documents: list[dict[str, str]]) -> list[dict[str, str]]:
    """Split cleaned documents into overlapping text chunks."""

    chunked: list[dict[str, str]] = []

    for doc in documents:
        url = doc.get("url", "")
        title = doc.get("title", "")
        text = doc.get("text", "")

        all_words = text.split()
        if not all_words:
            continue

        # Keep a short page as one chunk, even if below the minimum chunk threshold.
        if len(all_words) < MIN_CHUNK_WORDS:
            chunked.append(
                {
                    "chunk_id": _deterministic_chunk_id(url, 0),
                    "url": url,
                    "title": title,
                    "text": " ".join(all_words),
                    "source_type": SOURCE_TYPE,
                }
            )
            continue

        units = _split_units(text)
        unit_words: list[list[str]] = [u.split() for u in units if u.split()]
        if not unit_words:
            continue

        i = 0
        chunk_index = 0
        while i < len(unit_words):
            current_words: list[str] = []
            j = i

            while j < len(unit_words):
                candidate = unit_words[j]
                if not current_words:
                    current_words.extend(candidate)
                    j += 1
                    continue

                if len(current_words) + len(candidate) > TARGET_CHUNK_WORDS:
                    break

                current_words.extend(candidate)
                j += 1

            # Unit larger than target, hard-split by words.
            if len(current_words) > TARGET_CHUNK_WORDS:
                current_words = current_words[:TARGET_CHUNK_WORDS]

            if len(current_words) >= MIN_CHUNK_WORDS:
                chunked.append(
                    {
                        "chunk_id": _deterministic_chunk_id(url, chunk_index),
                        "url": url,
                        "title": title,
                        "text": " ".join(current_words),
                        "source_type": SOURCE_TYPE,
                    }
                )
                chunk_index += 1

            if j >= len(unit_words):
                break

            # Move next start forward with overlap measured in words.
            backtrack_words = OVERLAP_WORDS
            next_i = j
            while next_i > i and backtrack_words > 0:
                next_i -= 1
                backtrack_words -= len(unit_words[next_i])
            i = max(i + 1, next_i)

    return chunked


def main() -> None:
    documents = _load_jsonl(CLEAN_PATH)
    chunks = chunk_documents(documents)
    _write_jsonl(CHUNKS_PATH, chunks)

    avg_word_count = 0.0
    if chunks:
        avg_word_count = sum(len(chunk.get("text", "").split()) for chunk in chunks) / len(chunks)

    print(f"documents loaded: {len(documents)}")
    print(f"chunks written: {len(chunks)}")
    print(f"average chunk word count: {avg_word_count:.2f}")


if __name__ == "__main__":
    main()
