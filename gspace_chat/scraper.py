"""Website scraping module for Gilmour Space source content."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from gspace_chat.config import SEED_URLS

RAW_PAGES_PATH = Path("data/raw/pages.jsonl")
REMOVED_TAGS = ("script", "style", "noscript", "svg")


def scrape_site() -> list[dict[str, str]]:
    """Fetch pages from configured seed URLs and save raw content to JSONL."""

    RAW_PAGES_PATH.parent.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, str]] = []
    attempted = len(SEED_URLS)
    saved = 0
    failed = 0

    with RAW_PAGES_PATH.open("w", encoding="utf-8") as output_file:
        for url in SEED_URLS:
            fetched_at = datetime.now(timezone.utc).isoformat()
            record: dict[str, str] = {
                "url": url,
                "title": "",
                "text": "",
                "fetched_at": fetched_at,
                "status": "ok",
            }

            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                for tag in soup.find_all(REMOVED_TAGS):
                    tag.decompose()

                title = soup.title.string.strip() if soup.title and soup.title.string else ""
                text = soup.get_text(separator="\n", strip=True)

                record["title"] = title
                record["text"] = text
                saved += 1
            except Exception:
                record["status"] = "error"
                failed += 1

            output_file.write(json.dumps(record, ensure_ascii=False) + "\n")
            records.append(record)

    print(f"pages attempted: {attempted}")
    print(f"pages saved: {saved}")
    print(f"pages failed: {failed}")

    return records


def main() -> None:
    """Run scraper from the command line."""

    scrape_site()


if __name__ == "__main__":
    main()
