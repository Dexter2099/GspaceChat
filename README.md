# Gspace Chat

Gspace Chat is a retrieval-augmented AI assistant over public Gilmour Space website content.

This repository currently contains only the **initial scaffold**:
- a minimal Streamlit homepage,
- placeholder pipeline modules for scraping, cleaning, chunking, indexing, retrieval, and RAG answer generation,
- environment-variable based configuration.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment variables:

```bash
cp .env.example .env
```

4. Fill in your `.env` values (especially `OPENAI_API_KEY`).

## Run

Start the Streamlit app:

```bash
streamlit run app.py
```

The app currently shows a project overview and example prompts while backend RAG components are TODO.
