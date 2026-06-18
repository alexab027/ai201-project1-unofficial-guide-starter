"""
Ingestion and chunking pipeline for the MIT CS Unofficial Guide.

Reads local .txt files from documents/blogs/ and documents/forums/.
See FILE FORMAT section below for how to structure each file.

FILE FORMAT — blogs (documents/blogs/*.txt)
-------------------------------------------
TITLE: Every Class I've Ever Taken
SOURCE: https://mitadmissions.org/blogs/entry/every-class-ive-ever-taken/

## Section Heading

Paste paragraph text here. Multiple paragraphs separated by blank lines.

Another paragraph here.

## Another Section Heading

More text...

FILE FORMAT — forums (documents/forums/*.txt)
----------------------------------------------
TITLE: The workload for computer science students?
SOURCE: https://www.reddit.com/r/mit/comments/10gk3zf/...

POST:
Paste the original post body here. Leave blank if none.

COMMENT:
Paste first top-level comment text here.

REPLY:
A short reply that gets merged into the comment above if under 75 words.

COMMENT:
Second comment text here.

REPLY:
A longer reply that becomes its own chunk.

---
Chunking behavior:
  - 4 sentences per chunk
  - 1 sentence overlap between chunks
  - Sub-comments under 75 words are merged into their parent comment
"""

import re
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORD_LIMIT_MAX = 700
SENTENCES_PER_CHUNK = 4
OVERLAP_SENTENCES = 1
SUBCOMMENT_MERGE_LIMIT = 75

DOCUMENTS_DIR = Path("documents")
BLOGS_DIR = DOCUMENTS_DIR / "blogs"
FORUMS_DIR = DOCUMENTS_DIR / "forums"

# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def word_count(text: str) -> int:
    return len(text.split())


def clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = text.strip()
    return text


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences while avoiding common false splits:
    - MIT course numbers like 6.1210 or 18.06
    - abbreviations like Prof., Dr., e.g., i.e.
    - URLs
    """
    text = clean_text(text)

    # Protect URLs first because they contain periods and slashes.
    url_map = {}

    def protect_url(match):
        key = f"<URL{len(url_map)}>"
        url_map[key] = match.group(0)
        return key

    text = re.sub(r"https?://\S+", protect_url, text)

    # Protect common abbreviations.
    protected = {
        "Prof.": "Prof<DOT>",
        "Dr.": "Dr<DOT>",
        "Mr.": "Mr<DOT>",
        "Ms.": "Ms<DOT>",
        "Mrs.": "Mrs<DOT>",
        "e.g.": "e<DOT>g<DOT>",
        "i.e.": "i<DOT>e<DOT>",
        "etc.": "etc<DOT>",
        "vs.": "vs<DOT>",
    }

    for original, replacement in protected.items():
        text = text.replace(original, replacement)

    # Protect course numbers and decimals like 6.1210, 18.06, 14.01.
    text = re.sub(r"(\d+)\.(\d+)", r"\1<DOT>\2", text)

    # Split after sentence-ending punctuation followed by whitespace.
    parts = re.split(r"(?<=[.!?])\s+", text)

    sentences = []
    for part in parts:
        part = part.replace("<DOT>", ".").strip()

        for key, url in url_map.items():
            part = part.replace(key, url)

        if part:
            sentences.append(part)

    return sentences


def chunk_text(
    text: str,
    sentences_per_chunk: int = SENTENCES_PER_CHUNK,
    overlap_sentences: int = OVERLAP_SENTENCES,
) -> list[str]:
    """
    Create chunks of 4 sentences with 1 sentence overlap.

    Example:
      Chunk 1 = sentences 1, 2, 3, 4
      Chunk 2 = sentences 4, 5, 6, 7
      Chunk 3 = sentences 7, 8, 9, 10

    This prevents chunks from ending with dangling half-sentences.
    """
    sentences = split_into_sentences(text)

    if not sentences:
        return []

    if sentences_per_chunk <= overlap_sentences:
        raise ValueError("sentences_per_chunk must be greater than overlap_sentences")

    chunks = []
    step = sentences_per_chunk - overlap_sentences

    for start in range(0, len(sentences), step):
        chunk_sentences = sentences[start:start + sentences_per_chunk]

        if not chunk_sentences:
            continue

        chunk = " ".join(chunk_sentences).strip()

        if chunk:
            chunks.append(chunk)

        if start + sentences_per_chunk >= len(sentences):
            break

    return chunks


# ---------------------------------------------------------------------------
# File parsing
# ---------------------------------------------------------------------------

def parse_header(lines: list[str]) -> tuple[str, str, int]:
    """
    Read TITLE: and SOURCE: lines at the top of a file.
    Returns (title, source_url, index_of_first_content_line).
    """
    title = ""
    source = ""
    i = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.upper().startswith("TITLE:"):
            title = stripped[6:].strip()
        elif stripped.upper().startswith("SOURCE:"):
            source = stripped[7:].strip()
        elif stripped == "" and (title or source):
            continue
        elif title and source:
            break

    return title, source, i


def parse_blog_file(path: Path) -> dict:
    """
    Parse a blog txt file into {title, source, type, sections}.
    Sections are split on ## headings.
    Paragraphs are separated by blank lines.
    """
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    title, source, _ = parse_header(lines)

    if not title:
        title = path.stem.replace("_", " ").title()

    if not source:
        source = path.name

    sections: list[dict] = []
    current_heading = title
    current_paragraphs: list[str] = []
    current_block: list[str] = []

    def flush_block():
        block_text = " ".join(current_block).strip()
        if block_text:
            current_paragraphs.append(block_text)
        current_block.clear()

    def flush_section():
        nonlocal current_heading

        flush_block()

        if current_paragraphs:
            sections.append({
                "heading": current_heading,
                "text": clean_text("\n\n".join(current_paragraphs)),
            })
            current_paragraphs.clear()

    in_header = True

    for line in lines:
        stripped = line.strip()

        # Skip TITLE:/SOURCE: header area.
        if in_header:
            if stripped.upper().startswith("TITLE:") or stripped.upper().startswith("SOURCE:"):
                continue
            elif stripped == "":
                continue
            else:
                in_header = False

        if stripped.startswith("## ") or stripped.startswith("# "):
            flush_section()
            current_heading = stripped.lstrip("#").strip()
        elif stripped == "":
            flush_block()
        else:
            current_block.append(stripped)

    flush_section()

    return {
        "path": str(path),
        "title": title,
        "source": source,
        "type": "blog",
        "sections": sections,
    }


def parse_forum_file(path: Path) -> dict:
    """
    Parse a forum txt file into {title, source, type, comments}.
    POST: block is the original post body.
    COMMENT: blocks are top-level comments.
    REPLY: blocks are sub-comments.
    """
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    title, source, _ = parse_header(lines)

    if not title:
        title = path.stem.replace("_", " ").title()

    if not source:
        source = path.name

    selftext = ""
    comments: list[dict] = []

    current_type = None
    current_lines: list[str] = []
    current_comment_idx = -1

    def flush_block():
        nonlocal selftext, current_comment_idx

        text = clean_text(" ".join(current_lines))

        if not text:
            return

        if current_type == "post":
            selftext = text

        elif current_type == "comment":
            comments.append({
                "id": str(len(comments)),
                "parent_id": None,
                "depth": 0,
                "text": text,
            })
            current_comment_idx = len(comments) - 1

        elif current_type == "reply":
            parent_id = str(current_comment_idx) if current_comment_idx >= 0 else None
            comments.append({
                "id": str(len(comments)),
                "parent_id": parent_id,
                "depth": 1,
                "text": text,
            })

    in_header = True

    for line in lines:
        stripped = line.strip()

        # Skip TITLE:/SOURCE: header area.
        if in_header:
            if stripped.upper().startswith("TITLE:") or stripped.upper().startswith("SOURCE:"):
                continue
            elif stripped == "":
                continue
            else:
                in_header = False

        marker = stripped.upper().rstrip(":")

        if marker in ("POST", "COMMENT", "REPLY"):
            flush_block()
            current_lines.clear()
            current_type = marker.lower()
        elif stripped == "":
            current_lines.append("")
        else:
            current_lines.append(stripped)

    flush_block()

    return {
        "path": str(path),
        "title": title,
        "source": source,
        "selftext": selftext,
        "type": "forum",
        "comments": comments,
    }


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_blog(doc: dict) -> list[dict]:
    """
    Split blog sections into 4-sentence chunks with 1-sentence overlap.
    """
    chunks: list[dict] = []

    for section in doc["sections"]:
        heading = section["heading"]
        text = section["text"]

        if not text:
            continue

        for piece in chunk_text(text):
            chunks.append(_make_chunk(piece, doc, heading, "blog"))

    return chunks


def chunk_forum(doc: dict) -> list[dict]:
    """
    Split forum threads into 4-sentence chunks with 1-sentence overlap.
    Sub-comments under 75 words are merged into their parent comment.
    """
    chunks: list[dict] = []

    def emit(text: str, label: str):
        text = clean_text(text)

        if not text or word_count(text) < 10:
            return

        for piece in chunk_text(text):
            chunks.append(_make_chunk(piece, doc, label, "forum"))

    if doc.get("selftext"):
        emit(f"{doc['title']}\n\n{doc['selftext']}", "post")

    processed: set[str] = set()

    for comment in doc["comments"]:
        if comment["depth"] != 0:
            continue

        body = comment["text"]
        children = [c for c in doc["comments"] if c["parent_id"] == comment["id"]]

        for child in children:
            processed.add(child["id"])

            if word_count(child["text"]) < SUBCOMMENT_MERGE_LIMIT:
                body += "\n\n> " + child["text"]
            else:
                emit(child["text"], "reply")

        emit(body, "comment")
        processed.add(comment["id"])

    for comment in doc["comments"]:
        if comment["id"] not in processed:
            emit(comment["text"], "nested reply")

    return chunks


def _make_chunk(text: str, doc: dict, section: str, doc_type: str) -> dict:
    return {
        "text": text,
        "source": doc["source"],
        "title": doc["title"],
        "section": section,
        "type": doc_type,
        "word_count": word_count(text),
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline() -> list[dict]:
    all_chunks: list[dict] = []

    # Blogs
    blog_files = sorted(BLOGS_DIR.glob("*.txt")) if BLOGS_DIR.exists() else []
    print(f"=== Ingesting blogs ({len(blog_files)} files) ===")

    for path in blog_files:
        print(f"  {path.name}")
        doc = parse_blog_file(path)
        chunks = chunk_blog(doc)
        all_chunks.extend(chunks)
        print(f"    -> {len(doc['sections'])} sections -> {len(chunks)} chunks")

    # Forums
    forum_files = sorted(FORUMS_DIR.glob("*.txt")) if FORUMS_DIR.exists() else []
    print(f"\n=== Ingesting forums ({len(forum_files)} files) ===")

    for path in forum_files:
        print(f"  {path.name}")
        doc = parse_forum_file(path)
        chunks = chunk_forum(doc)
        all_chunks.extend(chunks)
        print(f"    -> {len(doc['comments'])} comments -> {len(chunks)} chunks")

    if not blog_files and not forum_files:
        print("No files found. Add .txt files to documents/blogs/ and documents/forums/")
        return all_chunks

    print(f"\n=== Total chunks: {len(all_chunks)} ===")

    wcs = [c["word_count"] for c in all_chunks]

    if wcs:
        print(f"  min: {min(wcs)}  max: {max(wcs)}  avg: {sum(wcs)//len(wcs)} words")

        over = [c for c in all_chunks if c["word_count"] > WORD_LIMIT_MAX]

        if over:
            print(f"  WARNING: {len(over)} chunks exceed {WORD_LIMIT_MAX} words")

    return all_chunks


if __name__ == "__main__":
    chunks = run_pipeline()

    out_path = DOCUMENTS_DIR / "chunks.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {out_path}")