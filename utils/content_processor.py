from typing import List, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_text_from_input(pasted_text: Optional[str] = None, uploaded_file=None) -> str:
    """Load text from either pasted text or uploaded file."""
    if pasted_text:
        return pasted_text.strip()

    if uploaded_file is not None:
        return uploaded_file.getvalue().decode("utf-8").strip()

    return ""


def chunk_text_content(
    text: str, chunk_size: int = 1500, chunk_overlap: int = 100
) -> List[str]:
    """Split text into chunks using LangChain's RecursiveCharacterTextSplitter."""
    if not text:
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )

    return text_splitter.split_text(text)
