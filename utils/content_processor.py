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
    Detect if content contains markdown headers.
    Returns True if markdown headers are found.
    """
    md_header_pattern = r"^#{1,6}\s+.+$"
    lines = text.split("\n")
    header_count = sum(1 for line in lines if re.match(md_header_pattern, line.strip()))
    return header_count >= 2


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
