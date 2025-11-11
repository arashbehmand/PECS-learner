"""
Unit tests for file format converters.
"""

from unittest.mock import MagicMock, patch

import pytest

from utils.file_converters import (
    convert_file_to_text,
    get_file_type_description,
    is_supported_file_type,
)


class MockUploadedFile:
    """Mock UploadedFile-like object."""

    def __init__(self, name, content):
        self.name = name
        self._content = content

    def getvalue(self):
        return self._content


def test_is_supported_file_type():
    """Test file type detection."""
    assert is_supported_file_type("test.txt") is True
    assert is_supported_file_type("test.md") is True
    assert is_supported_file_type("test.epub") is True
    assert is_supported_file_type("test.pdf") is True
    assert is_supported_file_type("test.docx") is True
    assert is_supported_file_type("test.doc") is True
    assert is_supported_file_type("test.xyz") is False
    assert is_supported_file_type("test.TXT") is True  # Case insensitive
    assert is_supported_file_type("test.PDF") is True


def test_get_file_type_description():
    """Test file type description."""
    desc = get_file_type_description()
    assert "Text" in desc
    assert "EPUB" in desc
    assert "PDF" in desc


@patch("utils.file_converters.MarkItDown")
def test_convert_file_to_text_string_result(mock_markitdown):
    """Test conversion when markitdown returns a string."""
    uploaded_file = MockUploadedFile("test.pdf", b"fake pdf content")

    # Mock markitdown to return a string
    mock_converter = MagicMock()
    mock_converter.convert.return_value = "Converted text content"
    mock_markitdown.return_value = mock_converter

    with (
        patch("tempfile.NamedTemporaryFile") as mock_temp,
        patch("os.path.exists", return_value=True),
        patch("os.unlink"),
    ):
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.pdf"
        result = convert_file_to_text(uploaded_file)

        assert result == "Converted text content"
        mock_converter.convert.assert_called_once()


@patch("utils.file_converters.MarkItDown")
def test_convert_file_to_text_object_result(mock_markitdown):
    """Test conversion when markitdown returns an object with text_content."""
    uploaded_file = MockUploadedFile("test.epub", b"fake epub content")

    # Mock markitdown to return an object
    mock_result = MagicMock()
    mock_result.text_content = "Object text content"

    mock_converter = MagicMock()
    mock_converter.convert.return_value = mock_result
    mock_markitdown.return_value = mock_converter

    with (
        patch("tempfile.NamedTemporaryFile") as mock_temp,
        patch("os.path.exists", return_value=True),
        patch("os.unlink"),
    ):
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.epub"
        result = convert_file_to_text(uploaded_file)

        assert result == "Object text content"


@patch("utils.file_converters.MarkItDown")
def test_convert_file_to_text_empty_result(mock_markitdown):
    """Test conversion when result is empty."""
    uploaded_file = MockUploadedFile("test.pdf", b"fake pdf content")

    mock_converter = MagicMock()
    mock_converter.convert.return_value = (
        "   "  # Whitespace that becomes empty after strip
    )
    mock_markitdown.return_value = mock_converter

    with (
        patch("tempfile.NamedTemporaryFile") as mock_temp,
        patch("os.path.exists", return_value=True),
        patch("os.unlink"),
    ):
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.pdf"
        with pytest.raises(ValueError):
            convert_file_to_text(uploaded_file)


@patch("utils.file_converters.MarkItDown")
def test_convert_file_to_text_exception(mock_markitdown):
    """Test conversion error handling."""
    uploaded_file = MockUploadedFile("test.pdf", b"fake pdf content")

    mock_converter = MagicMock()
    mock_converter.convert.side_effect = Exception("Conversion failed")
    mock_markitdown.return_value = mock_converter

    with (
        patch("tempfile.NamedTemporaryFile") as mock_temp,
        patch("os.path.exists", return_value=True),
        patch("os.unlink"),
    ):
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.pdf"
        with pytest.raises(Exception):
            convert_file_to_text(uploaded_file)


@patch("utils.file_converters.MarkItDown")
def test_convert_file_to_text_text_attribute(mock_markitdown):
    """Test conversion with .text attribute."""
    uploaded_file = MockUploadedFile("test.docx", b"fake docx content")

    # Create a mock result with only .text attribute
    mock_result = MagicMock(spec=["text"])
    mock_result.text = "Text attribute content"

    mock_converter = MagicMock()
    mock_converter.convert.return_value = mock_result
    mock_markitdown.return_value = mock_converter

    with (
        patch("tempfile.NamedTemporaryFile") as mock_temp,
        patch("os.path.exists", return_value=True),
        patch("os.unlink"),
    ):
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.docx"
        result = convert_file_to_text(uploaded_file)
        assert result == "Text attribute content"


@patch("utils.file_converters.MarkItDown")
def test_convert_file_to_text_markdown_attribute(mock_markitdown):
    """Test conversion with .markdown attribute."""
    uploaded_file = MockUploadedFile("test.docx", b"fake docx content")

    # Create a mock result with only .markdown attribute
    mock_result = MagicMock(spec=["markdown"])
    mock_result.markdown = "Markdown attribute content"

    mock_converter = MagicMock()
    mock_converter.convert.return_value = mock_result
    mock_markitdown.return_value = mock_converter

    with (
        patch("tempfile.NamedTemporaryFile") as mock_temp,
        patch("os.path.exists", return_value=True),
        patch("os.unlink"),
    ):
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.docx"
        result = convert_file_to_text(uploaded_file)
        assert result == "Markdown attribute content"


@patch("utils.file_converters.MarkItDown")
def test_convert_file_to_text_content_attribute(mock_markitdown):
    """Test conversion with .content attribute."""
    uploaded_file = MockUploadedFile("test.docx", b"fake docx content")

    # Create a mock result with only .content attribute
    mock_result = MagicMock(spec=["content"])
    mock_result.content = "Content attribute"

    mock_converter = MagicMock()
    mock_converter.convert.return_value = mock_result
    mock_markitdown.return_value = mock_converter

    with (
        patch("tempfile.NamedTemporaryFile") as mock_temp,
        patch("os.path.exists", return_value=True),
        patch("os.unlink"),
    ):
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.docx"
        result = convert_file_to_text(uploaded_file)
        assert result == "Content attribute"
