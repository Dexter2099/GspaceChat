"""Retrieval module for selecting relevant chunks for a user query."""


def retrieve_chunks(query: str, top_k: int = 5) -> list[dict[str, str]]:
    """Retrieve relevant chunks for a question.

    TODO: Execute vector similarity search over the built index.
    """

    _ = (query, top_k)
    return []
