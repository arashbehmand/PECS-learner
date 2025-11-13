import re
from typing import List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownTextSplitter


def load_text_from_input(pasted_text: Optional[str] = None, uploaded_file=None) -> str:
    """Load text from either pasted text or uploaded file."""
    if pasted_text:
        return pasted_text.strip()

    if uploaded_file is not None:
        return uploaded_file.getvalue().decode("utf-8").strip()

    return ""


def _is_markdown_content(text: str) -> bool:
    """
    Detect if content contains meaningful markdown headers (not just citations).
    Returns True if real markdown section headers are found.
    """
    md_header_pattern = r"^#{1,6}\s+(.+)$"
    lines = text.split("\n")

    # Count only headers that look like real section headers
    real_header_count = 0
    for line in lines:
        match = re.match(md_header_pattern, line.strip())
        if match:
            header_text = match.group(1)
            # Skip headers that are likely citations/references/URLs
            if (
                not header_text.lower().startswith("here ")
                and "http" not in header_text.lower()
                and len(header_text) < 150
                and re.search(r'\w{3,}', header_text)
            ):
                real_header_count += 1

    return real_header_count >= 3


def chunk_text_content(
    text: str, chunk_size: int = 1500, chunk_overlap: int = 100
) -> List[str]:
    """
    Split text into chunks using markdown-aware or recursive splitting.
    Automatically detects markdown content and uses appropriate splitter.
    """
    if not text:
        return []

    # Use markdown-aware splitter for markdown content
    if _is_markdown_content(text):
        text_splitter = MarkdownTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    else:
        # Fall back to recursive splitter for non-markdown content
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    return text_splitter.split_text(text)
