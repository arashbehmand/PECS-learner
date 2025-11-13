"""
Hierarchical content processor for large texts.
Processes text into logical sections (chapters, user-defined sections) instead of flat chunks.
Supports markdown-aware splitting for better context preservation.
"""

import re
from typing import List, Optional, Tuple

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    MarkdownTextSplitter,
)


def _clean_title(title: str) -> Optional[str]:
    """
    Clean up a title by removing markdown/HTML artifacts and links.
    Returns None if the title appears to be a citation/reference rather than a real section title.

    Args:
        title: Raw title string that may contain markdown/HTML

    Returns:
        Cleaned title string, or None if this looks like a citation
    """
    if not title:
        return None

    # Check if this looks like a citation/reference (before cleaning)
    # Citations typically start with "here" or "see" in academic texts
    if title.lower().strip().startswith(("here ", "see ", "cf. ", "e.g. ", "i.e. ")):
        return None

    # Remove markdown links: [text](url) -> text
    title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)

    # Remove standalone URLs in angle brackets: <url>
    title = re.sub(r'<https?://[^>]+>', '', title)

    # Remove standalone URLs
    title = re.sub(r'https?://\S+', '', title)

    # Remove HTML tags
    title = re.sub(r'<[^>]+>', '', title)

    # Remove markdown formatting (bold, italic, etc.)
    title = re.sub(r'[*_`]+', '', title)

    # Remove multiple spaces and trim
    title = re.sub(r'\s+', ' ', title).strip()

    # If title is too long (likely not a real title), it's probably a citation
    if len(title) > 200:
        return None

    # If title is empty after cleaning
    if not title:
        return None

    # If title contains too many citation markers (colons, semicolons)
    # Real chapter titles rarely have multiple colons/semicolons
    citation_markers = title.count(':') + title.count(';')
    if citation_markers > 2:
        return None

    return title


class HierarchicalContentProcessor:
    """Processes large texts into hierarchical sections."""

    def __init__(self):
        self.section_patterns = [
            # Chapter patterns
            r"^(?:Chapter\s+\d+|CHAPTER\s+\d+|Chapter\s+[IVXLC]+)\s*[:-]?\s*(.+)$",
            r"^#+\s*(?:Chapter\s+\d+|Chapter\s+[IVXLC]+)\s*[:-]?\s*(.+)$",
            # Numbered sections
            r"^\d+\.\s+\d+\.\s+(.+)$",  # 1.1 Section Title
            r"^Section\s+\d+\s*[:-]?\s*(.+)$",
            # Roman numerals
            r"^[IVXLC]+\.\s+(.+)$",
            # Common book section markers
            r"^(?:Part\s+\d+|PART\s+\d+)\s*[:-]?\s*(.+)$",
            # Custom markers (user-defined)
            r"^---+\s*(.+?)\s*---+$",  # --- Section Title ---
        ]

        # Markdown header splitter configuration
        self.md_headers_to_split = [
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
        ]

    def _is_markdown_content(self, text: str) -> bool:
        """
        Detect if content contains meaningful markdown headers (not just citations).
        Returns True if real markdown section headers are found.
        """
        # Check for markdown headers (# Header, ## Header, etc.)
        md_header_pattern = r"^#{1,6}\s+(.+)$"
        lines = text.split("\n")

        # Count only headers that look like real section headers
        real_header_count = 0
        for line in lines:
            match = re.match(md_header_pattern, line.strip())
            if match:
                header_text = match.group(1)
                # Skip headers that are likely citations/references/URLs
                # Real headers are typically:
                # - Not starting with "here" (references like "here some text:")
                # - Not mostly URLs
                # - Not too long (> 150 chars is likely a citation)
                # - Contains actual words, not just punctuation
                if (
                    not header_text.lower().startswith("here ")
                    and "http" not in header_text.lower()
                    and len(header_text) < 150
                    and re.search(r'\w{3,}', header_text)  # At least one 3+ char word
                ):
                    real_header_count += 1

        # Require at least 3 real headers to consider it structured markdown
        return real_header_count >= 3

    def _process_markdown_sections(
        self,
        text: str,
        min_section_size: int = 2000,
        max_section_size: int = 20000,
        overlap: int = 200,
    ) -> List[Tuple[str, Optional[str]]]:
        """
        Process markdown content using markdown-aware splitters.
        Respects headers, paragraphs, lists, and tables.

        Args:
            text: The markdown text to process
            min_section_size: Minimum characters per section
            max_section_size: Maximum characters per section
            overlap: Character overlap between sections

        Returns:
            List of tuples: (section_content, section_title)
        """
        # Step 1: Split by headers to preserve document structure
        header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.md_headers_to_split,
            strip_headers=False,  # Keep headers in content for context
        )

        try:
            header_sections = header_splitter.split_text(text)
        except Exception:
            # If markdown splitting fails, fall back to regex-based detection
            return self.split_into_sections(
                text, min_section_size, max_section_size, overlap
            )

        # Step 2: Process each header section
        sections = []
        md_splitter = MarkdownTextSplitter(
            chunk_size=max_section_size,
            chunk_overlap=overlap,
        )

        # Buffer for front-matter citations before first real chapter
        front_matter_buffer = []

        for doc in header_sections:
            content = doc.page_content

            # Extract title from metadata if available
            title = None
            is_citation_section = False
            if hasattr(doc, "metadata") and doc.metadata:
                # Combine all header levels for a hierarchical title
                title_parts = []
                for key in ["h1", "h2", "h3"]:
                    if key in doc.metadata and doc.metadata[key]:
                        cleaned = _clean_title(doc.metadata[key])
                        if cleaned:  # Only add non-empty cleaned titles
                            title_parts.append(cleaned)
                        elif doc.metadata[key]:  # Had a title but cleaning returned None (citation)
                            is_citation_section = True
                title = " > ".join(title_parts) if title_parts else None

            # Handle citation sections (references, footnotes, etc.)
            if is_citation_section and not title:
                if not sections:
                    # Front-matter citations before first real chapter - buffer them
                    front_matter_buffer.append(content)
                else:
                    # Merge with previous section if it exists
                    prev_content, prev_title = sections[-1]
                    sections[-1] = (prev_content + "\n\n" + content, prev_title)
                continue

            # If this is the first real section, prepend buffered front-matter
            if front_matter_buffer and not sections:
                content = "\n\n".join(front_matter_buffer) + "\n\n" + content
                front_matter_buffer = []

            # Skip very small sections (merge with previous)
            if len(content) < min_section_size and sections:
                prev_content, prev_title = sections[-1]
                merged_title = prev_title or title
                sections[-1] = (prev_content + "\n\n" + content, merged_title)
                continue

            # If section is too large, split it further using markdown-aware splitter
            if len(content) > max_section_size:
                chunks = md_splitter.split_text(content)
                for i, chunk in enumerate(chunks):
                    chunk_title = f"{title} (Part {i + 1})" if title else None
                    sections.append((chunk, chunk_title))
            else:
                sections.append((content, title))

        # Filter out empty sections
        return [(content, title) for content, title in sections if content.strip()]

    def detect_sections(self, text: str) -> List[Tuple[int, str, Optional[str]]]:
        """
        Detect logical sections in the text.

        Returns:
            List of tuples: (line_number, section_title, section_start_index)
            where section_title can be None if no title is found
        """
        lines = text.split("\n")
        sections = []

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Try each pattern
            for pattern in self.section_patterns:
                match = re.match(pattern, line_stripped, re.IGNORECASE)
                if match:
                    title = match.group(1).strip() if match.groups() else None
                    if not title:
                        title = match.group(0).strip()

                    # Find the actual start position in the text
                    start_pos = text.find(line)
                    sections.append((i, title, start_pos))
                    break

        # If no sections found, create a single section
        if not sections:
            sections.append((0, None, 0))

        return sections

    def split_into_sections(
        self,
        text: str,
        min_section_size: int = 2000,
        max_section_size: int = 20000,
        overlap: int = 200,
    ) -> List[Tuple[str, Optional[str]]]:
        """
        Split text into logical sections with optional titles.
        Uses markdown-aware splitting when markdown headers are detected.

        Args:
            text: The full text to process
            min_section_size: Minimum characters per section (will merge small sections)
            max_section_size: Maximum characters per section (will split large sections)
            overlap: Character overlap between split sections

        Returns:
            List of tuples: (section_content, section_title)
        """
        # Check if content is markdown and use appropriate processing
        if self._is_markdown_content(text):
            return self._process_markdown_sections(
                text, min_section_size, max_section_size, overlap
            )

        # Fall back to regex-based section detection for non-markdown content
        detected_sections = self.detect_sections(text)

        if len(detected_sections) == 1 and detected_sections[0][1] is None:
            # No sections detected, use chunking strategy
            return self._chunk_without_sections(text, max_section_size, overlap)

        # Process detected sections
        sections = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_section_size, chunk_overlap=overlap, length_function=len
        )

        for i, (_line_num, title, start_pos) in enumerate(detected_sections):
            # Determine end position
            if i + 1 < len(detected_sections):
                end_pos = detected_sections[i + 1][2]
            else:
                end_pos = len(text)

            # Extract section content
            section_content = text[start_pos:end_pos].strip()

            # Skip if too short (will be merged with previous)
            if len(section_content) < min_section_size and sections:
                # Merge with previous section
                if sections:
                    prev_content, prev_title = sections[-1]
                    sections[-1] = (
                        prev_content + "\n\n" + section_content,
                        prev_title or title,
                    )
                    continue

            # If section is too large, split it further
            if len(section_content) > max_section_size:
                chunks = text_splitter.split_text(section_content)
                for j, chunk in enumerate(chunks):
                    chunk_title = f"{title} (Part {j + 1})" if title else None
                    sections.append((chunk, chunk_title))
            else:
                sections.append((section_content, title))

        # Filter out empty sections
        return [(content, title) for content, title in sections if content.strip()]

    def _chunk_without_sections(
        self, text: str, chunk_size: int, overlap: int
    ) -> List[Tuple[str, Optional[str]]]:
        """Fallback: chunk text without section detection."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=overlap, length_function=len
        )
        chunks = text_splitter.split_text(text)
        return [(chunk, None) for chunk in chunks]

    def process_for_user(
        self,
        text: str,
        use_custom_markers: bool = False,
        custom_markers: Optional[List[str]] = None,
        min_section_size: int = 2000,
        max_section_size: int = 20000,
        overlap: int = 200,
    ) -> List[Tuple[str, Optional[str]]]:
        """
        Main entry point for processing text.

        Args:
            text: Input text to process
            use_custom_markers: Whether to use custom section markers
            custom_markers: List of custom regex patterns for section detection
            min_section_size: Minimum section size
            max_section_size: Maximum section size
            overlap: Overlap between sections

        Returns:
            List of (content, title) tuples
        """
        if use_custom_markers and custom_markers:
            # Temporarily add custom patterns
            original_patterns = self.section_patterns.copy()
            self.section_patterns.extend(custom_markers)
            try:
                result = self.split_into_sections(
                    text, min_section_size, max_section_size, overlap
                )
            finally:
                self.section_patterns = original_patterns
            return result

        return self.split_into_sections(
            text, min_section_size, max_section_size, overlap
        )


def create_sections_from_text(
    text: str,
    min_section_size: int = 2000,
    max_section_size: int = 20000,
    overlap: int = 200,
) -> List[Tuple[str, Optional[str]]]:
    """
    Convenience function to process text into sections.

    Returns:
        List of (content, title) tuples ready for database insertion
    """
    processor = HierarchicalContentProcessor()
    return processor.process_for_user(
        text,
        min_section_size=min_section_size,
        max_section_size=max_section_size,
        overlap=overlap,
    )
