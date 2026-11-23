from pathlib import Path
import uuid

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from app.rag.chunking import chunk_markdown


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
QDRANT_PATH = PROJECT_ROOT / "data" / "qdrant"

COLLECTION_NAME = "enterprise_knowledge"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 64

# 384-dimensional embeddings for this model.
EMBEDDING_DIMENSION = 384


def ingest_documents() -> int:
    if not DOCUMENTS_DIR.exists():
        raise FileNotFoundError(
            f"Documents directory not found: {DOCUMENTS_DIR}"
        )

    files = sorted(
        path
        for path in DOCUMENTS_DIR.glob("*.md")
        if path.name.lower() != "test_questions.md"
    )

    if not files:
        raise ValueError(
            f"No Markdown documents found in {DOCUMENTS_DIR}"
        )

    chunks = []

    for path in files:
        chunks.extend(chunk_markdown(path))

    if not chunks:
        raise ValueError("No non-empty chunks were produced")

    # Load the embedding model.
    model = SentenceTransformer(MODEL_NAME)

    # Ensure the local Qdrant storage directory exists.
    QDRANT_PATH.mkdir(parents=True, exist_ok=True)

    client = QdrantClient(path=str(QDRANT_PATH))

    try:
        existing = client.collection_exists(COLLECTION_NAME)

        if existing:
            # Baseline behavior: rebuild the entire collection.
            client.delete_collection(COLLECTION_NAME)

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=models.Distance.COSINE,
            ),
        )

        for start in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[start:start + BATCH_SIZE]

            vectors = model.encode(
                [chunk.text for chunk in batch],
                normalize_embeddings=True,
                convert_to_numpy=True,
            )

            points = []

            for chunk, vector in zip(batch, vectors):

                point_id = str(
                    uuid.uuid5(
                        uuid.NAMESPACE_URL,
                        f"enterprise-knowledge:"
                        f"{chunk.source_name}:"
                        f"{chunk.chunk_index}",
                    )
                )

                points.append(
                    models.PointStruct(
                        id=point_id,
                        vector=vector.tolist(),
                        payload={
                            "chunk_id": chunk.chunk_id,
                            "source_name": chunk.source_name,
                            "chunk_index": chunk.chunk_index,
                            "classification": chunk.classification,
                            "department": chunk.department,
                            "allowed_roles": list(chunk.allowed_roles),
                            "text": chunk.text,
                        },
                    )
                )

            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
                wait=True,
            )

        print(f"Documents processed: {len(files)}")
        print(f"Chunks indexed: {len(chunks)}")

        return len(chunks)

    finally:
        client.close()


if __name__ == "__main__":
    ingest_documents()