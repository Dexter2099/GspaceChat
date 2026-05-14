"""Document cleaning module for normalizing raw scraped content."""

from __future__ import annotations

import json
import re
from pathlib import Path


RAW_PATH = Path("data/raw/pages.jsonl")
CLEAN_PATH = Path("data/processed/clean_pages.jsonl")

BOILERPLATE_LINES = {
    "top of page",
    "bottom of page",
    "HOME",
    "ABOUT",
    "TEAM",
    "LAUNCH",
    "SATELLITES",
    "CAREER",
    "Space & STEM",
    "UPDATES",
    "ASMN",
    "Missions",
    "Contact",
    "More...",
    "Use tab to navigate through the menu items.",
    "JOIN OUR MAILING LIST",
    "SUBSCRIBE",
    "Message sent!",
    "CONTACT US",
    "SEND A MESSAGE:",
    "Send",
}

def _fix_mojibake(text: str) -> str:
    """Fix common UTF-8 text decoded as Windows-1252."""
    try:
        text = text.encode("latin1").decode("utf-8")
    except UnicodeError:
        pass

    text = text.replace("Â®", "®")
    text = text.replace("Â©", "©")
    text = text.replace("â€”", "—")
    text = text.replace("â€‹", "")
    text = text.replace("â€‹".encode("utf-8").decode("cp1252"), "")
    text = text.replace("\ufeff", "")
    text = text.replace("Â", "")
    text = re.sub(r"â€‹+", "", text)
    return text


def _remove_boilerplate_lines(text: str) -> str:
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if stripped_line in BOILERPLATE_LINES:
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def _normalize_whitespace_preserve_paragraphs(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\t", " ")

    normalized_lines: list[str] = []
    for line in text.split("\n"):
        line = re.sub(r"[ \u00a0]+", " ", line).strip()
        normalized_lines.append(line)

    text = "\n".join(normalized_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _clean_text(text: str) -> str:
    text = _fix_mojibake(text)
    text = _remove_boilerplate_lines(text)
    text = _normalize_whitespace_preserve_paragraphs(text)
    return text


def clean_documents(documents: list[dict[str, str]]) -> list[dict[str, str]]:
    """Clean scraped documents before chunking."""

    cleaned_documents: list[dict[str, str]] = []
    for record in documents:
        if record.get("status") != "ok":
            continue

        cleaned_documents.append(
            {
                "url": record.get("url", ""),
                "title": record.get("title", ""),
                "fetched_at": record.get("fetched_at", ""),
                "status": record.get("status", ""),
                "text": _clean_text(record.get("text", "")),
            }
        )

    return cleaned_documents


def _load_jsonl(path: Path) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            documents.append(json.loads(line))
    return documents


def _write_jsonl(path: Path, documents: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")


def main() -> None:
    documents = _load_jsonl(RAW_PATH)
    cleaned = clean_documents(documents)
    _write_jsonl(CLEAN_PATH, cleaned)

    avg_len = 0.0
    if cleaned:
        avg_len = sum(len(doc.get("text", "")) for doc in cleaned) / len(cleaned)

    print(f"documents loaded: {len(documents)}")
    print(f"documents written: {len(cleaned)}")
    print(f"average cleaned text length: {avg_len:.2f}")


if __name__ == "__main__":
    main()
