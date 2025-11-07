"""
File format converters for EPUB and PDF files.
Performs pure data conversion using markitdown when available.
"""
import tempfile
import os
from typing import Optional

try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False


def convert_file_to_text(uploaded_file) -> str:
    """
    Convert uploaded file (file-like object or filesystem path) to plain text using markitdown.

    Args:
        uploaded_file: Either a path (str) to a file on disk or an object with
                       attributes `name` and `getvalue()` returning bytes (e.g. uploaded file).

    Returns:
        str: Converted and stripped text content.

    Raises:
        ImportError: if markitdown is not installed.
        ValueError: if the conversion produced no usable text.
        Exception: any error raised by the underlying conversion library is propagated.
    """
    if not MARKITDOWN_AVAILABLE:
        raise ImportError("markitdown library is not installed. Install with: pip install markitdown")

    owns_tmp = False
    tmp_path = None

    try:
        # Accept either a path string or an uploaded-file-like object
        if isinstance(uploaded_file, str):
            tmp_path = uploaded_file
        else:
            # write uploaded bytes to a temporary file so markitdown can read it
            file_ext = os.path.splitext(getattr(uploaded_file, "name", ""))[1] or ""
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                # uploaded_file.getvalue() should return bytes
                content = uploaded_file.getvalue()
                if isinstance(content, str):
                    content = content.encode("utf-8")
                tmp_file.write(content)
                tmp_path = tmp_file.name
            owns_tmp = True

        # Use markitdown to convert the file to text/markdown
        md = MarkItDown()
        result = md.convert(tmp_path)

        # Extract text from result - markitdown can return different shapes
        text_content = None

        if isinstance(result, str):
            text_content = result
        elif hasattr(result, "text_content"):
            text_content = result.text_content
        elif hasattr(result, "text"):
            text_content = result.text
        elif hasattr(result, "markdown"):
            text_content = result.markdown
        elif hasattr(result, "content"):
            text_content = result.content

        if text_content is None:
            raise ValueError("Could not extract text from file. The file format might not be supported.")

        # Normalize and return
        text_content = text_content.strip()
        if not text_content:
            raise ValueError("Converted content is empty.")

        return text_content

    finally:
        # Cleanup temporary file if we created one
        if owns_tmp and tmp_path:
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception:
                # Best-effort cleanup; ignore failures
                pass


def is_supported_file_type(filename: str) -> bool:
    """
    Check if file type is supported for conversion.
    
    Args:
        filename: Name of the file
        
    Returns:
        bool: True if file type is supported
    """
    supported_extensions = ['.txt', '.md', '.epub', '.pdf', '.docx', '.doc']
    return any(filename.lower().endswith(ext) for ext in supported_extensions)


def get_file_type_description() -> str:
    """Get description of supported file types."""
    return "Supported formats: Text (.txt), Markdown (.md), EPUB (.epub), PDF (.pdf), Word (.docx, .doc)"

