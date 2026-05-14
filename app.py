"""Streamlit entrypoint for the Gspace Chat project scaffold."""

import streamlit as st


def main() -> None:
    """Render a minimal homepage for the project."""
    st.set_page_config(page_title="Gspace Chat", page_icon="🚀")

    st.title("Gspace Chat")
    st.subheader(
        "A grounded AI assistant over public Gilmour Space website data."
    )

    st.markdown("### Example prompts")
    st.markdown("- What launch vehicles does Gilmour Space currently offer?")
    st.markdown("- Summarize recent company updates from the website.")
    st.markdown("- What does Gilmour Space say about launch timelines?")

    st.info("Scaffold mode: scraping, indexing, retrieval, and generation are TODO.")


if __name__ == "__main__":
    main()
