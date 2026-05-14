"""Indexing module for building a vector/search index from chunks."""


def build_index(chunks: list[dict[str, str]]) -> None:
    """Build and persist an index from chunks.

    TODO: Generate embeddings and store them in a retrieval backend.
    """

    _ = chunks
