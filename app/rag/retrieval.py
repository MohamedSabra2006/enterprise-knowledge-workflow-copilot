from pathlib import Path

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from app.rag.ingestion import (
    COLLECTION_NAME,
    EMBEDDING_DIMENSION,
    MODEL_NAME,
    QDRANT_PATH,
)


class RAGRetriever:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.client = QdrantClient(path=str(QDRANT_PATH))

        if not self.client.collection_exists(COLLECTION_NAME):
            raise RuntimeError(
                "Knowledge collection not found. "
                "Run app.rag.ingestion first."
            )

    def search(
        self,
        query: str,
        role: str,
        top_k: int = 5,
        granted_sources: list[str] | None = None,
    ) -> list[dict]:
        """
        Search only the chunks this user is allowed to see.

        `role` and `granted_sources` must come from your verified,
        server-side user record, never from the chat message.
        """

        role = role.strip().lower()

        if not role:
            raise ValueError("A verified role is required")

        query = query.strip()

        if len(query) < 3:
            raise ValueError("Query must contain at least 3 characters")

        if not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20")

        query_vector = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).tolist()

        if len(query_vector) != EMBEDDING_DIMENSION:
            raise RuntimeError("Unexpected embedding dimension")

        # Authorization filter, applied INSIDE the database search so
        # forbidden chunks are never retrieved (see 05_data_classification.md).
        # A chunk is allowed if the user's role is in its allowed_roles,
        # OR the user has an explicit grant for that whole document.
        allowed = [
            models.FieldCondition(
                key="allowed_roles",
                match=models.MatchAny(any=[role]),
            )
        ]

        if granted_sources:
            allowed.append(
                models.FieldCondition(
                    key="source_name",
                    match=models.MatchAny(any=list(granted_sources)),
                )
            )

        response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=models.Filter(should=allowed),
            limit=top_k,
            with_payload=True,
        )

        results = []

        for point in response.points:
            payload = point.payload or {}

            results.append(
                {
                    "citation": (
                        f'{payload.get("source_name", "unknown")} '
                        f'— chunk {payload.get("chunk_index", "?")}'
                    ),
                    "source_name": payload.get("source_name"),
                    "chunk_id": payload.get("chunk_id"),
                    "text": payload.get("text", ""),
                    "score": float(point.score),
                }
            )

        return results

    def close(self):
        self.client.close()


if __name__ == "__main__":
    retriever = RAGRetriever()

    try:
        # Demo only: in a real app the role comes from login, not input().
        demo_role = input("Test as which role (employee/manager/ceo)? ")
        question = input("Ask a company-policy question: ")

        for result in retriever.search(question, role=demo_role, top_k=5):
            print(f"\nSource: {result['citation']}")
            print(f"Score: {result['score']:.4f}")
            print(result["text"])

    finally:
        retriever.close()