
from pathlib import Path

from app.rag.chunking import chunk_markdown


documents_dir = Path("documents")

for path in sorted(documents_dir.glob("*.md")):
    if path.name.lower() == "test_questions.md":
        continue

    chunks = chunk_markdown(path)

    print(f"\n{path.name}: {len(chunks)} chunks")

    for chunk in chunks:
        word_count = len(chunk.text.split())

        print(
            f"  {chunk.chunk_id} | "
            f"{word_count} words | "
            f"{chunk.text[:100]}..."
        )

        assert word_count <= 180, (
            f"Chunk too large: {chunk.chunk_id}"
        )
