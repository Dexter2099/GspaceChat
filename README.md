# Gspace Chat

A retrieval-augmented AI assistant that turns Gilmour Space’s public website into a searchable knowledge interface with grounded answers and source citations.

## 1. Project overview

Gspace Chat is a Python Streamlit application that answers user questions using selected public pages from the Gilmour Space website. The application uses a local retrieval pipeline: it scrapes website content, cleans and chunks the text, builds a local ChromaDB vector index, retrieves relevant chunks for each question, and generates answers grounded only in retrieved content.

## 2. Why this project exists

Public website information is often spread across multiple pages and can be time-consuming to search manually. This project provides a focused, query-based interface over that website content, while keeping answers tied to source material and reducing unsupported responses.

## 3. Current MVP features

- Streamlit-based chat interface
- Scraping of selected public Gilmour Space website pages
- Text cleaning for scraped website content
- Chunking pipeline for retrieval-ready documents
- Local ChromaDB vector index generation
- Retrieval of relevant chunks at question time
- OpenAI chat model response generation grounded in retrieved content
- Source links shown under answers
- Fallback response when evidence is missing: `I don’t know from the Gilmour Space website.`
- Streamlit sidebar admin control to rebuild the local index

## 4. Architecture

```text
Gilmour Space website pages
        ↓
Scraper
        ↓
Cleaner
        ↓
Chunker
        ↓
ChromaDB vector index
        ↓
Retriever
        ↓
OpenAI grounded answer generation
        ↓
Streamlit UI with citations
```

## 5. Tech stack

- Python
- Streamlit
- ChromaDB
- OpenAI API (chat + embeddings)

## 6. Setup

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

## 7. Environment variables

Set these values in `.env`:

```env
OPENAI_API_KEY=
OPENAI_CHAT_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

## 8. Build the local knowledge base

Run the pipeline steps in order:

```bash
python -m gspace_chat.scraper
python -m gspace_chat.cleaner
python -m gspace_chat.chunker
python -m gspace_chat.indexer
```

You can also rebuild the local index from the Streamlit sidebar admin button.

## 9. Run the app

```bash
streamlit run app.py
```

## 10. Example questions

- What is Gilmour Space’s Eris rocket?
- What launch services are described on the website?
- Where is Gilmour Space’s launch site located?
- What does the website say about current mission or launch updates?

## 11. Hallucination control

The assistant is designed to answer from retrieved website chunks only. If relevant evidence is not found in retrieved content, it returns:

`I don’t know from the Gilmour Space website.`

This behavior is intended to reduce unsupported claims.

## 12. Repository safety / secrets

- Do not commit `.env`.
- `.env`, `data/`, `chroma_db/`, `__pycache__/`, and `.venv` are gitignored.
- `data/` and `chroma_db/` are local generated folders and are not committed.

## 13. Known limitations

- This is an MVP, not a production system.
- Retrieval quality depends on page selection and chunking strategy.
- Answers are limited to scraped website content and may miss information not present in indexed pages.
- Content freshness depends on when the scraping and indexing pipeline was last run.

## 14. Future improvements

- Expand and manage source page coverage.
- Improve chunking and retrieval tuning for better precision and recall.
- Add stronger admin controls for index lifecycle and content refresh.
- Add evaluation workflows for answer quality and citation quality.
- Add production-oriented concerns such as observability, authentication, and deployment hardening.
