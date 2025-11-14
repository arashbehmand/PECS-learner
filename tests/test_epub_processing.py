"""
Test EPUB processing with real public domain book.
Uses Pride and Prejudice from Project Gutenberg as a standard test case.
"""

import os
import tempfile
from urllib.request import urlretrieve

from utils.file_converters import convert_file_to_text
from utils.hierarchical_processor import HierarchicalContentProcessor


def test_epub_basic_processing():
    """Test that a real EPUB file can be converted and processed."""
    # Download Pride and Prejudice from Project Gutenberg
    epub_url = "https://www.gutenberg.org/ebooks/1342.epub.noimages"

    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as tmp:
        epub_path = tmp.name

    try:
        # Download the book
        urlretrieve(epub_url, epub_path)

        # Convert EPUB to text
        text = convert_file_to_text(epub_path)

        # Basic sanity checks
        assert len(text) > 100000, "EPUB should produce substantial text"
        assert "Pride" in text or "Prejudice" in text, "Should contain book title"

        # Process into sections
        processor = HierarchicalContentProcessor()
        sections = processor.split_into_sections(
            text, min_section_size=2000, max_section_size=20000, overlap=200
        )

        # Verify processing quality
        assert len(sections) > 10, "Should create multiple sections"
        assert len(sections) < 200, "Should not over-segment"

        # Calculate coverage
        total_chars = sum(len(content) for content, _ in sections)
        coverage = (total_chars / len(text)) * 100

        assert coverage > 90, f"Should cover most of the book, got {coverage:.1f}%"

        # Check for clean titles (no citation artifacts)
        for content, title in sections:
            if title:
                assert (
                    "http" not in title
                ), f"Title should not contain URLs: {title[:100]}"
                assert (
                    len(title) < 200
                ), f"Title should be reasonable length: {title[:100]}"

    finally:
        # Cleanup
        if os.path.exists(epub_path):
            os.unlink(epub_path)


def test_epub_with_local_file():
    """Test with a local EPUB file if available (for faster testing)."""
    # Use a local test file if it exists
    local_test_file = "test_epubs/pride_prejudice.epub"

    if not os.path.exists(local_test_file):
        # Skip if test file doesn't exist
        return

    text = convert_file_to_text(local_test_file)
    processor = HierarchicalContentProcessor()
    sections = processor.split_into_sections(
        text, min_section_size=2000, max_section_size=20000, overlap=200
    )

    # Verify results
    assert len(sections) > 10
    total_chars = sum(len(content) for content, _ in sections)
    coverage = (total_chars / len(text)) * 100
    assert coverage > 90

    # Check no citation titles
    citation_count = sum(
        1 for _, title in sections if title and ("http" in title or len(title) > 150)
    )
    assert (
        citation_count == 0
    ), f"Found {citation_count} sections with citation-like titles"


def test_epub_link_style_detection():
    """Test EPUB-style chapter link detection."""
    # Simulate EPUB-style content (like Stolen Focus)
    test_text = """
[Introduction Walking in Memphis](ch07com.xhtml#fm02_ch_001)

When he was nine years old, my godson developed a brief but intense obsession.

[Chapter One: The Problem](ch08com.xhtml#ch01_ch_001)

This is the first chapter with substantial content about the problem.
Multiple paragraphs of real content here.

[Acknowledgements](ch24com.xhtml#em01_bem_001)

Thanks to everyone who helped with this book.
"""

    processor = HierarchicalContentProcessor()
    sections = processor.split_into_sections(
        test_text, min_section_size=50, max_section_size=500, overlap=20
    )

    # Should detect 3 chapters
    assert len(sections) >= 3, f"Expected at least 3 sections, got {len(sections)}"

    # Check titles are clean
    titles = [title for _, title in sections if title]
    assert "Introduction Walking in Memphis" in titles or "Walking in Memphis" in titles
    assert any("Chapter One" in t or "The Problem" in t for t in titles)
    assert "Acknowledgements" in titles


def test_markdown_vs_epub_detection():
    """Test that both markdown headers and EPUB links are detected."""
    processor = HierarchicalContentProcessor()

    # Markdown-style content
    md_text = """
# Chapter One

This is markdown chapter one.

## Section 1.1

More content here.

# Chapter Two

Another chapter.
"""

    assert processor.is_markdown_content(md_text) is True

    # EPUB-link style content (no markdown headers)
    epub_text = """
[Chapter One](ch01.xhtml)

This is EPUB chapter one.

[Chapter Two](ch02.xhtml)

Another chapter.
"""

    assert processor.is_markdown_content(epub_text) is False

    # Both should be processable
    md_sections = processor.split_into_sections(
        md_text, min_section_size=10, max_section_size=500
    )
    epub_sections = processor.split_into_sections(
        epub_text, min_section_size=10, max_section_size=500
    )

    assert len(md_sections) > 0
    assert len(epub_sections) > 0
