"""RAG orchestration module combining retrieval with answer generation."""

from __future__ import annotations

from typing import Any
import os
import sys

from gspace_chat.config import get_settings
from gspace_chat.retriever import retrieve_chunks

FALLBACK_ANSWER = "I don’t know from the Gilmour Space website."
SYSTEM_PROMPT = (
    "You are a grounded website knowledge assistant for Gilmour Space. "
    "Answer only using the provided website excerpts. Do not use outside knowledge. "
    "If the answer is not supported by the excerpts, say exactly: "
    "I don’t know from the Gilmour Space website."
)


def _load_dotenv_if_available() -> None:
    """Load environment variables from .env when python-dotenv is installed."""

    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return

    load_dotenv()


def _format_context(chunks: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        lines.append(f"[Chunk {i}]")
        lines.append(f"URL: {chunk.get('url', '')}")
        lines.append(f"Title: {chunk.get('title', '')}")
        lines.append(f"Text: {chunk.get('text', '')}")
        lines.append("")
    return "\n".join(lines)


def _sources_from_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    sources: list[dict[str, str]] = []
    for chunk in chunks:
        url = str(chunk.get("url", "")).strip()
        if not url or url in seen:
            continue
        seen.add(url)
        sources.append({"url": url, "title": str(chunk.get("title", "")).strip()})
    return sources


def generate_answer(question: str, top_k: int = 5) -> dict[str, Any]:
    """Generate a grounded answer from retrieved context."""

    cleaned_question = question.strip()
    if not cleaned_question:
        raise ValueError("Question cannot be empty.")

    _load_dotenv_if_available()
    settings = get_settings()
    api_key = os.getenv("OPENAI_API_KEY", "").strip() or settings.openai_api_key.strip()
    if not api_key:
        return {
            "answer": "Error: OPENAI_API_KEY is not set. Add it to your environment or .env file.",
            "sources": [],
            "used_chunks": [],
        }

    chunks = retrieve_chunks(cleaned_question, top_k=top_k)
    used_chunks = [
        {
            "chunk_id": chunk.get("chunk_id", ""),
            "url": chunk.get("url", ""),
            "title": chunk.get("title", ""),
            "text": chunk.get("text", ""),
            "distance": chunk.get("distance", None),
        }
        for chunk in chunks
    ]

    if not chunks:
        return {"answer": FALLBACK_ANSWER, "sources": [], "used_chunks": used_chunks}

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    user_prompt = (
        f"Question: {cleaned_question}\n\n"
        "Website excerpts:\n"
        f"{_format_context(chunks)}\n"
        "Instructions: Answer only using the excerpts. "
        f"If they do not provide enough evidence, reply exactly: {FALLBACK_ANSWER}"
    )

    response = client.chat.completions.create(
        model=settings.openai_chat_model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    answer = (response.choices[0].message.content or "").strip()
    sources = _sources_from_chunks(chunks)

    if answer == FALLBACK_ANSWER:
        return {"answer": answer, "sources": [], "used_chunks": used_chunks}

    if not answer:
        answer = FALLBACK_ANSWER
        return {"answer": answer, "sources": [], "used_chunks": used_chunks}

    if sources:
        source_lines = ["Sources:"] + [f"- {item['url']}" for item in sources]
        answer = f"{answer}\n\n" + "\n".join(source_lines)

    return {"answer": answer, "sources": sources, "used_chunks": used_chunks}


def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        print('Usage: python -m gspace_chat.rag "<question>"')
        return 1

    question = " ".join(argv[1:])

    try:
        result = generate_answer(question)
    except Exception as exc:
        print(f"RAG error: {exc}")
        return 1

    print(result["answer"])
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
