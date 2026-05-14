"""Streamlit entrypoint for the Gspace Chat project scaffold."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from gspace_chat.cleaner import CLEAN_PATH, _load_jsonl as load_raw_jsonl, _write_jsonl as write_clean_jsonl, clean_documents
from gspace_chat.chunker import CHUNKS_PATH, _load_jsonl as load_clean_jsonl, _write_jsonl as write_chunks_jsonl, chunk_documents
from gspace_chat.indexer import build_index, load_chunks
from gspace_chat.rag import generate_answer
from gspace_chat.scraper import scrape_site

EXAMPLE_PROMPTS = [
    "What does Gilmour Space do?",
    "What is Eris?",
    "Where is Bowen Orbital Spaceport?",
    "What services does Gilmour Space offer?",
    "What happened with TestFlight1?",
]


def rebuild_local_index() -> tuple[bool, str]:
    """Run scrape -> clean -> chunk -> index in order and persist outputs."""

    try:
        scraped_records = scrape_site()

        raw_documents = load_raw_jsonl(Path("data/raw/pages.jsonl"))
        cleaned_documents = clean_documents(raw_documents)
        write_clean_jsonl(CLEAN_PATH, cleaned_documents)

        clean_records = load_clean_jsonl(CLEAN_PATH)
        chunks = chunk_documents(clean_records)
        write_chunks_jsonl(CHUNKS_PATH, chunks)

        chunk_records = load_chunks(CHUNKS_PATH)
        build_index(chunk_records)

        return (
            True,
            (
                "Rebuild complete: "
                f"scraped={len(scraped_records)}, "
                f"cleaned={len(cleaned_documents)}, "
                f"chunks={len(chunks)}, "
                f"indexed={len(chunk_records)}"
            ),
        )
    except Exception as exc:
        return False, f"Rebuild failed: {exc}"


def main() -> None:
    """Render the Streamlit app with RAG query and admin index controls."""
    st.set_page_config(page_title="Gspace Chat", page_icon="🚀")

    st.title("Gspace Chat")
    st.subheader(
        "A grounded AI assistant over public Gilmour Space website data."
    )

    st.markdown("### Example prompts")
    prompt_columns = st.columns(2)
    for idx, prompt in enumerate(EXAMPLE_PROMPTS):
        if prompt_columns[idx % 2].button(prompt, key=f"example_{idx}"):
            st.session_state["question"] = prompt

    question = st.text_input("Ask a question", key="question")

    if st.button("Submit question", type="primary"):
        cleaned_question = question.strip()
        if not cleaned_question:
            st.warning("Please enter a question.")
        else:
            try:
                result = generate_answer(cleaned_question)
                answer = str(result.get("answer", "")).strip()
                sources = result.get("sources", [])

                if answer.lower().startswith("error:"):
                    st.error(answer)
                else:
                    st.markdown("### Answer")
                    st.write(answer)

                    st.markdown("### Sources")
                    if sources:
                        for source in sources:
                            url = str(source.get("url", "")).strip()
                            title = str(source.get("title", "")).strip() or url
                            if url:
                                st.markdown(f"- [{title}]({url})")
                    else:
                        st.caption("No sources returned.")
            except Exception as exc:
                st.error(f"Unable to generate answer: {exc}")

    with st.sidebar:
        st.markdown("## Admin")
        if st.button("Rebuild local index"):
            with st.spinner("Rebuilding local index..."):
                ok, message = rebuild_local_index()
            if ok:
                st.success(message)
            else:
                st.error(message)


if __name__ == "__main__":
    main()
