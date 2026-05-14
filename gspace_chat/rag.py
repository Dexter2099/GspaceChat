"""RAG orchestration module combining retrieval with answer generation."""


def generate_answer(question: str, context_chunks: list[dict[str, str]]) -> str:
    """Generate a grounded answer from retrieved context.

    TODO: Call a chat model with retrieval context and prompt template.
    """

    _ = (question, context_chunks)
    return "RAG pipeline not implemented yet."
