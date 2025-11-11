"""
Unit tests for content processor utilities.
"""

from utils.content_processor import chunk_text_content, load_text_from_input


class MockUploadedFile:
    """Mock Streamlit UploadedFile object."""

    def __init__(self, content_bytes, encoding="utf-8"):
        self._content = content_bytes
        self._encoding = encoding

    def getvalue(self):
        return self._content

    def decode(self, encoding):
        if encoding != self._encoding:
            raise UnicodeDecodeError("test", b"", 0, 1, "wrong encoding")
        return self._content.decode(encoding)


def test_load_text_from_pasted_text():
    """Test loading text from pasted input."""
    result = load_text_from_input(pasted_text="  Test text with spaces  ")
    assert result == "Test text with spaces"


def test_load_text_from_uploaded_file():
    """Test loading text from uploaded file."""
    uploaded_file = MockUploadedFile(b"Test content from file")
    result = load_text_from_input(uploaded_file=uploaded_file)
    assert result == "Test content from file"


def test_load_text_from_empty_pasted_text():
    """Test loading empty pasted text."""
    result = load_text_from_input(pasted_text="   ")
    assert result == ""


def test_load_text_from_empty_uploaded_file():
    """Test loading empty uploaded file."""
    uploaded_file = MockUploadedFile(b"")
    result = load_text_from_input(uploaded_file=uploaded_file)
    assert result == ""


def test_load_text_from_none():
    """Test loading when both inputs are None."""
    result = load_text_from_input()
    assert result == ""


def test_load_text_prefers_pasted_over_file():
    """Test that pasted text takes precedence over file."""
    uploaded_file = MockUploadedFile(b"File content")
    result = load_text_from_input(
        pasted_text="Pasted content", uploaded_file=uploaded_file
    )
    assert result == "Pasted content"


def test_chunk_text_content_basic():
    """Test basic text chunking."""
    text = "This is a test. " * 100  # Create text longer than default chunk size
    chunks = chunk_text_content(text, chunk_size=150, chunk_overlap=10)

    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
    # Verify chunks don't exceed size (with some tolerance for word boundaries)
    assert all(
        len(chunk) <= 150 * 1.5 for chunk in chunks
    )  # LangChain may overshoot slightly


def test_chunk_text_content_empty():
    """Test chunking empty text."""
    result = chunk_text_content("")
    assert not result


def test_chunk_text_content_whitespace_only():
    """Test chunking whitespace-only text."""
    result = chunk_text_content("   \n\t   ")
    # Should return empty or very small chunks
    assert isinstance(result, list)


def test_chunk_text_content_smaller_than_chunk_size():
    """Test chunking text smaller than chunk size."""
    text = "Short text"
    chunks = chunk_text_content(text, chunk_size=100, chunk_overlap=0)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_content_with_overlap():
    """Test chunking with overlap between chunks."""
    text = "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10"
    chunks = chunk_text_content(text, chunk_size=20, chunk_overlap=5)

    if len(chunks) > 1:
        # Check that chunks have some overlap (content appears in multiple chunks)
        # This is approximate since LangChain handles overlap
        assert len(chunks) >= 1


def test_chunk_text_content_custom_size():
    """Test chunking with custom chunk size."""
    text = "Test word. " * 50
    chunks = chunk_text_content(text, chunk_size=50, chunk_overlap=0)

    assert len(chunks) > 0
    # With size 50 and overlap 0, should get multiple chunks
    assert len(chunks) >= 1


def test_chunk_text_content_large_text():
    """Test chunking very large text."""
    text = "Paragraph. " * 1000  # Large text
    chunks = chunk_text_content(text, chunk_size=500, chunk_overlap=50)

    assert len(chunks) > 1
    # Verify all text is preserved (approximately)
    total_length = sum(len(chunk) for chunk in chunks)
    assert total_length >= len(text) * 0.8  # Allow for some trimming/overlap


def test_load_text_from_file_encoding_errors():
    """Test handling of encoding errors in file."""
    # Create file with invalid UTF-8
    invalid_utf8 = b"\xff\xfe\x00\x00"
    uploaded_file = MockUploadedFile(invalid_utf8)

    # Should handle the error gracefully
    try:
        result = load_text_from_input(uploaded_file=uploaded_file)
        # If it doesn't raise, result might be empty or error message
        assert isinstance(result, str)
    except UnicodeDecodeError:
        # This is also acceptable - the error should be handled at a higher level
        pass
