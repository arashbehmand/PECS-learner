"""
Rolling Context and Study Notes Generation Service

This service implements the "rolling window context" approach from the original
document summarizer, adapted for PECS. It maintains a cumulative summary across
sections and generates study notes with full context.
"""

import logging
from typing import Callable, Dict, Optional

from nicegui_app.config import ROLLING_CONTEXT_MAX_CHARS

logger = logging.getLogger(__name__)


class RollingContextService:
    """Service for managing rolling context and study notes generation."""

    def __init__(self, llm_service, database):
        """
        Initialize the rolling context service.

        Args:
            llm_service: LLMService instance for AI calls
            database: DatabaseRepository instance for data access
        """
        self.llm_service = llm_service
        self.db = database

    def generate_rolling_summary(
        self, section_id: int, force_regenerate: bool = False
    ) -> Optional[str]:
        """
        Generate rolling summary for a section based on all previous sections.

        This is the "summary so far" concept from the original script.
        The summary is based on material sequence (order_index), not user progress.

        Args:
            section_id: ID of section to generate summary for
            force_regenerate: If True, regenerate even if summary exists

        Returns:
            Generated rolling summary, or None if error
        """
        section = self.db.get_section(section_id)
        if not section:
            logger.error(f"Section {section_id} not found")
            return None

        # Check if summary already exists and force_regenerate is False
        if section.rolling_summary and not force_regenerate:
            logger.debug(f"Rolling summary already exists for section {section_id}")
            return section.rolling_summary

        # Get all previous sections in order
        all_sections = self.db.get_sections_by_project(section.project_id)
        previous_sections = [
            s for s in all_sections if s.order_index < section.order_index
        ]

        # Get the previous section's rolling summary (if exists)
        previous_summary = ""
        if previous_sections:
            # Get the most recent previous section's rolling summary
            prev_section = previous_sections[-1]
            if prev_section.rolling_summary:
                previous_summary = prev_section.rolling_summary
            else:
                # If previous section doesn't have a rolling summary, generate it first
                logger.info(
                    f"Previous section {prev_section.id} missing rolling summary, generating it first"
                )
                previous_summary = self.generate_rolling_summary(prev_section.id)
                if not previous_summary:
                    logger.warning("Failed to generate previous section summary")
                    previous_summary = ""

        # Generate rolling summary for current section
        try:
            rolling_summary = self.llm_service.generate_rolling_summary(
                previous_summary=previous_summary,
                current_content=section.content,
                section_title=section.title or f"Section {section.order_index + 1}",
            )

            if not rolling_summary:
                logger.error(
                    f"LLM failed to generate rolling summary for section {section_id}"
                )
                return None

            # Apply safety truncation if needed
            if len(rolling_summary) > ROLLING_CONTEXT_MAX_CHARS:
                logger.warning(
                    f"Rolling summary exceeded max chars ({len(rolling_summary)} > {ROLLING_CONTEXT_MAX_CHARS}), truncating"
                )
                rolling_summary = rolling_summary[:ROLLING_CONTEXT_MAX_CHARS] + "..."

            # Save to database
            self.db.update_section(section_id, rolling_summary=rolling_summary)
            logger.info(
                f"Generated rolling summary for section {section_id} ({len(rolling_summary)} chars)"
            )

            return rolling_summary

        except Exception as e:
            logger.error(f"Error generating rolling summary: {e}", exc_info=True)
            return None

    def generate_rolling_summaries_batch(
        self,
        project_id: int,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[int, bool]:
        """
        Generate rolling summaries for all sections in a project in sequence.

        This is the "1-click generation" mode that processes all sections at once.

        Args:
            project_id: ID of project
            progress_callback: Optional callback(current, total, section_title) for progress updates

        Returns:
            Dictionary mapping section_id to success status
        """
        sections = self.db.get_sections_by_project(project_id)
        if not sections:
            logger.warning(f"No sections found for project {project_id}")
            return {}

        results = {}
        total = len(sections)

        logger.info(f"Starting batch rolling summary generation for {total} sections")

        for idx, section in enumerate(sections):
            if progress_callback:
                progress_callback(
                    idx + 1,
                    total,
                    section.title or f"Section {section.order_index + 1}",
                )

            summary = self.generate_rolling_summary(section.id, force_regenerate=False)
            results[section.id] = summary is not None

            if not summary:
                logger.error(
                    f"Failed to generate rolling summary for section {section.id}"
                )
                # Continue with next section even if one fails

        successful = sum(1 for v in results.values() if v)
        logger.info(
            f"Batch rolling summary generation complete: {successful}/{total} successful"
        )

        return results

    def generate_study_notes(
        self, section_id: int, force_regenerate: bool = False
    ) -> Optional[str]:
        """
        Generate study notes for a section.

        Study notes focus on: diagrams, connections, definitions, key concepts.
        This is NOT a summary - it's active learning notes (Feynman method).

        Args:
            section_id: ID of section to generate notes for
            force_regenerate: If True, regenerate even if notes exist

        Returns:
            Generated study notes, or None if error
        """
        section = self.db.get_section(section_id)
        if not section:
            logger.error(f"Section {section_id} not found")
            return None

        # Check if notes already exist and force_regenerate is False
        if section.study_notes and not force_regenerate:
            logger.debug(f"Study notes already exist for section {section_id}")
            return section.study_notes

        # Ensure rolling summary exists
        if not section.rolling_summary:
            logger.info(f"Generating rolling summary first for section {section_id}")
            self.generate_rolling_summary(section_id)

        # Extract PECS learning summary if available
        pecs_summary = self._extract_pecs_summary(section.pecs_data)

        try:
            study_notes = self.llm_service.generate_study_notes(
                rolling_summary=section.rolling_summary or "",
                section_title=section.title or f"Section {section.order_index + 1}",
                section_content=section.content,
                pecs_summary=pecs_summary,
            )

            if not study_notes:
                logger.error(
                    f"LLM failed to generate study notes for section {section_id}"
                )
                return None

            # Save to database
            self.db.update_section(section_id, study_notes=study_notes)
            logger.info(
                f"Generated study notes for section {section_id} ({len(study_notes)} chars)"
            )

            return study_notes

        except Exception as e:
            logger.error(f"Error generating study notes: {e}", exc_info=True)
            return None

    def generate_study_notes_batch(
        self,
        project_id: int,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[int, bool]:
        """
        Generate study notes for all sections in a project.

        First generates all rolling summaries, then generates study notes.
        This is the "1-click generation" mode.

        Args:
            project_id: ID of project
            progress_callback: Optional callback(current, total, message) for progress updates

        Returns:
            Dictionary mapping section_id to success status
        """
        sections = self.db.get_sections_by_project(project_id)
        if not sections:
            logger.warning(f"No sections found for project {project_id}")
            return {}

        total_steps = len(sections) * 2  # Rolling summaries + study notes
        current_step = 0
        results = {}

        logger.info(
            f"Starting batch study notes generation for {len(sections)} sections"
        )

        # Phase 1: Generate all rolling summaries
        for section in sections:
            current_step += 1
            if progress_callback:
                progress_callback(
                    current_step,
                    total_steps,
                    f"Generating context: {section.title or f'Section {section.order_index + 1}'}",
                )

            summary = self.generate_rolling_summary(section.id, force_regenerate=False)
            if not summary:
                logger.error(
                    f"Failed to generate rolling summary for section {section.id}"
                )
                results[section.id] = False
                continue

        # Phase 2: Generate all study notes
        for section in sections:
            current_step += 1
            if progress_callback:
                progress_callback(
                    current_step,
                    total_steps,
                    f"Generating notes: {section.title or f'Section {section.order_index + 1}'}",
                )

            notes = self.generate_study_notes(section.id, force_regenerate=False)
            results[section.id] = notes is not None

        successful = sum(1 for v in results.values() if v)
        logger.info(
            f"Batch study notes generation complete: {successful}/{len(sections)} successful"
        )

        return results

    def _extract_pecs_summary(self, pecs_data: Dict) -> str:
        """
        Extract a summary of student's learning journey from PECS data.

        Args:
            pecs_data: Section's pecs_data dictionary

        Returns:
            Formatted string summarizing PECS phases
        """
        if not pecs_data:
            return ""

        parts = []

        # Prime phase
        prime_data = pecs_data.get("prime_preview", {})
        if prime_data.get("understanding"):
            parts.append(
                f"Initial Understanding: {prime_data['understanding'][:200]}..."
                if len(prime_data["understanding"]) > 200
                else f"Initial Understanding: {prime_data['understanding']}"
            )

        # Engage phase
        engage_data = pecs_data.get("engage_explain", {})
        if engage_data.get("explanation"):
            parts.append(
                f"Student Explanation: {engage_data['explanation'][:200]}..."
                if len(engage_data["explanation"]) > 200
                else f"Student Explanation: {engage_data['explanation']}"
            )

        # Challenge phase
        challenge_data = pecs_data.get("challenge_connect", {})
        critical_thinking = challenge_data.get(
            "critical_questions"
        ) or challenge_data.get("critical_thinking")
        if critical_thinking:
            parts.append(
                f"Critical Analysis: {critical_thinking[:200]}..."
                if len(critical_thinking) > 200
                else f"Critical Analysis: {critical_thinking}"
            )

        return "\n\n".join(parts) if parts else ""
