
from pathlib import Path

from app.rag.chunking import chunk_markdown

documents_dir = Path("documents")

for path in sorted(documents_dir.glob("*.md")):
    if path.name.lower() == "test_questions.md":
        continue

    chunks = chunk_markdown(path)
    word_count = len(path.read_text(encoding="utf-8").split())

    print(
        f"{path.name:35} "
        f"Words: {word_count:5} | "
        f"Chunks: {len(chunks)}"
    )
