"""
Hierarchical content processor for large texts.
Processes text into logical sections (chapters, user-defined sections) instead of flat chunks.
"""

import re
from typing import List, Optional, Tuple

from langchain.text_splitter import RecursiveCharacterTextSplitter


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
        min_section_size: int = 500,
        max_section_size: int = 5000,
        overlap: int = 100,
    ) -> List[Tuple[str, Optional[str]]]:
        """
        Split text into logical sections with optional titles.

        Args:
            text: The full text to process
            min_section_size: Minimum characters per section (will merge small sections)
            max_section_size: Maximum characters per section (will split large sections)
            overlap: Character overlap between split sections

        Returns:
            List of tuples: (section_content, section_title)
        """
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
        min_section_size: int = 500,
        max_section_size: int = 5000,
        overlap: int = 100,
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
    min_section_size: int = 500,
    max_section_size: int = 5000,
    overlap: int = 100,
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
