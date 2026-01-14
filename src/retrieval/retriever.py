
from src.vectorstore.pgvector_store import vector_store


def retrieve_relevant_chunks(
    query: str,
    k: int = 8,
    similarity_threshold: float = 0.40
):
    """
    Retrieve chunks and filter by semantic similarity >= threshold
    """
    results = vector_store.similarity_search_with_score(
        query=query,
        k=k
    )

    filtered_chunks = []

    for doc, score in results:
        semantic_score = 1 - score  # distance → similarity
        if semantic_score >= similarity_threshold:
            # print(semantic_score)
            filtered_chunks.append((doc, semantic_score))

    return filtered_chunks

