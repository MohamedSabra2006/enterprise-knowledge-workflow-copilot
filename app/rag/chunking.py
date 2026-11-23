from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    source_name: str
    text: str
    chunk_index: int
    # Access-control metadata copied from the document header.
    classification: str = "internal"
    department: str = ""
    allowed_roles: tuple[str, ...] = ()


# Roles allowed when a document has no "Allowed roles" line.
# Unlabeled documents default to "internal" (see 05_data_classification.md).
DEFAULT_ROLES_BY_CLASSIFICATION = {
    "public": ("employee", "manager", "ceo"),
    "internal": ("employee", "manager", "ceo"),
    "business-confidential": ("manager", "ceo"),
    "restricted": ("explicit-grant-only",),
}


def parse_metadata(text: str) -> dict:
    """Read the '**Key:** value' header lines at the top of a document."""

    fields = {}

    for line in text.splitlines():
        # The header ends at the first '## ' section heading.
        if line.startswith("## "):
            break

        match = re.match(r"^\*\*(.+?):\*\*\s*(.+?)\s*$", line)

        if match:
            fields[match.group(1).strip().lower()] = match.group(2).strip()

    classification = fields.get("classification", "internal").lower()

    if "allowed roles" in fields:
        roles = tuple(
            role.strip().lower()
            for role in fields["allowed roles"].split(",")
            if role.strip()
        )
    else:
        roles = DEFAULT_ROLES_BY_CLASSIFICATION.get(
            classification,
            ("explicit-grant-only",),  # unknown label: fail closed
        )

    return {
        "classification": classification,
        "department": fields.get("department", ""),
        "allowed_roles": roles,
    }


def normalize_text(text: str) -> str:
    """Normalize whitespace without merging separate words."""

    # Normalize line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Normalize spaces and tabs, but preserve newlines.
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_markdown_blocks(
    text: str,
) -> list[tuple[str, str]]:
    """Split Markdown into headings, lists, and paragraphs."""

    blocks = []
    paragraph_lines = []

    def flush_paragraph():
        if paragraph_lines:
            block = "\n".join(paragraph_lines).strip()

            if block:
                blocks.append(("paragraph", block))

            paragraph_lines.clear()

    for line in text.splitlines():
        line = line.rstrip()

        if not line.strip():
            flush_paragraph()
            continue

        # Markdown headings: # Heading, ## Heading, etc.
        if re.match(r"^#{1,6}\s+", line):
            flush_paragraph()
            blocks.append(("heading", line.strip()))

        # Markdown unordered and ordered list items.
        elif re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line):
            flush_paragraph()
            blocks.append(("list", line.strip()))

        else:
            paragraph_lines.append(line.strip())

    flush_paragraph()

    return blocks


def split_into_sentences(text: str) -> list[str]:
    """Split paragraphs into sentence-sized units."""

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def split_oversized_text(
    text: str,
    chunk_size: int,
) -> list[str]:
    """Split oversized text at word boundaries."""

    words = text.split()

    return [
        " ".join(words[start:start + chunk_size])
        for start in range(0, len(words), chunk_size)
    ]


def render_units(
    units: list[tuple[str, str]],
) -> str:
    """Render semantic units with safe Markdown spacing."""

    rendered = []
    previous_type = None

    for unit_type, text in units:

        if not rendered:
            rendered.append(text)

        elif unit_type == "heading":
            rendered.append("\n\n" + text)

        elif unit_type == "list":
            rendered.append("\n" + text)

        elif previous_type == "heading":
            rendered.append("\n\n" + text)

        else:
            rendered.append("\n\n" + text)

        previous_type = unit_type

    return "".join(rendered).strip()


def chunk_markdown(
    path: Path,
    chunk_size: int = 180,
    overlap: int = 35,
) -> list[DocumentChunk]:
    """
    Chunk Markdown while prioritizing semantic and structural integrity.

    Headings and list items are preserved where possible.
    Sentence boundaries are preferred over arbitrary word boundaries.
    Overlap is not strictly enforced.
    """

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero"
        )

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and < chunk_size"
        )

    # Step 1: Read and normalize the document.
    text = normalize_text(
        path.read_text(encoding="utf-8")
    )

    if not text:
        return []

    # Read access-control metadata from the document header.
    metadata = parse_metadata(text)

    # Step 2: Split the document into Markdown blocks.
    blocks = split_markdown_blocks(text)

    # Step 3: Convert blocks into semantic units.
    units: list[tuple[str, str]] = []

    for block_type, block_text in blocks:

        if block_type == "heading":
            units.append(("heading", block_text))

        elif block_type == "list":

            if len(block_text.split()) <= chunk_size:
                units.append(("list", block_text))

            else:
                units.extend(
                    ("list", piece)
                    for piece in split_oversized_text(
                        block_text,
                        chunk_size,
                    )
                )

        else:
            sentences = split_into_sentences(block_text)

            for sentence in sentences:

                if len(sentence.split()) <= chunk_size:
                    units.append(("paragraph", sentence))

                else:
                    units.extend(
                        ("paragraph", piece)
                        for piece in split_oversized_text(
                            sentence,
                            chunk_size,
                        )
                    )

    # Step 4: Build chunks while preserving Markdown structure.
    chunks_text: list[str] = []

    current_units: list[tuple[str, str]] = []
    current_words = 0

    latest_heading: str | None = None

    for unit_type, unit_text in units:

        unit_words = len(unit_text.split())

        if unit_type == "heading":
            latest_heading = unit_text

        # If the next unit exceeds the chunk limit, close the chunk.
        if (
            current_units
            and current_words + unit_words > chunk_size
        ):

            chunks_text.append(
                render_units(current_units)
            )

            current_units = []
            current_words = 0

            # Repeat the latest heading when a list continues
            # into the next chunk, if it fits.
            if unit_type == "list" and latest_heading:

                heading_words = len(
                    latest_heading.split()
                )

                if (
                    heading_words + unit_words
                    <= chunk_size
                ):
                    current_units.append(
                        ("heading", latest_heading)
                    )

                    current_words += heading_words

        # Ensure that no individual unit exceeds the limit.
        if current_words + unit_words > chunk_size:

            raise ValueError(
                f"Unit has {unit_words} words and cannot "
                f"fit within the {chunk_size}-word limit."
            )

        current_units.append(
            (unit_type, unit_text)
        )

        current_words += unit_words

    # Step 5: Add the final chunk.
    if current_units:

        chunks_text.append(
            render_units(current_units)
        )

    # Step 6: Create DocumentChunk objects.
    result: list[DocumentChunk] = []

    for index, chunk_text in enumerate(chunks_text):

        if not chunk_text.strip():
            continue

        word_count = len(chunk_text.split())

        if word_count > chunk_size:

            raise ValueError(
                f"Chunk {index} contains {word_count} words; "
                f"maximum allowed is {chunk_size}."
            )

        result.append(
            DocumentChunk(
                chunk_id=f"{path.stem}-{index:04d}",
                source_name=path.name,
                text=chunk_text,
                chunk_index=index,
                classification=metadata["classification"],
                department=metadata["department"],
                allowed_roles=metadata["allowed_roles"],
            )
        )

    return result