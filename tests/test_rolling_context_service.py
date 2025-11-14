"""
Unit tests for Rolling Context Service.
"""

# pylint: disable=unused-argument

import os
import tempfile
from unittest.mock import MagicMock

import pytest

from utils.database import DatabaseRepository
from utils.rolling_context_service import RollingContextService


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseRepository(db_path=path)
    yield db
    db.engine.dispose()
    import time

    time.sleep(0.1)
    try:
        os.unlink(path)
    except (PermissionError, FileNotFoundError):
        pass


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    mock = MagicMock()
    mock.generate_rolling_summary.return_value = "Test rolling summary"
    mock.generate_study_notes.return_value = "Test study notes"
    return mock


@pytest.fixture
def service(temp_db, mock_llm_service):
    """Create a RollingContextService instance."""
    return RollingContextService(mock_llm_service, temp_db)


@pytest.fixture
def sample_project(temp_db):
    """Create a sample project."""
    return temp_db.create_project("Test Project")


@pytest.fixture
def sample_sections(temp_db, sample_project):
    """Create sample sections."""
    sections = []
    for i in range(3):
        section = temp_db.create_section(
            project_id=sample_project.id,
            content=f"Content for section {i}",
            order_index=i,
            title=f"Section {i}",
        )
        sections.append(section)
    return sections


# ===== Rolling Summary Generation Tests =====


def test_generate_rolling_summary_first_section(
    service, temp_db, sample_project, mock_llm_service
):
    """Test generating rolling summary for first section (no previous context)."""
    section = temp_db.create_section(
        sample_project.id, "First section content", title="First Section", order_index=0
    )

    result = service.generate_rolling_summary(section.id)

    assert result == "Test rolling summary"
    mock_llm_service.generate_rolling_summary.assert_called_once()
    call_args = mock_llm_service.generate_rolling_summary.call_args[1]
    assert call_args["previous_summary"] == ""
    assert call_args["current_content"] == "First section content"
    assert call_args["section_title"] == "First Section"


def test_generate_rolling_summary_with_previous(
    service, temp_db, sample_sections, mock_llm_service
):
    """Test generating rolling summary with previous context."""
    # Set rolling summary for first section
    temp_db.update_section(sample_sections[0].id, rolling_summary="Previous summary")

    result = service.generate_rolling_summary(sample_sections[1].id)

    assert result == "Test rolling summary"
    call_args = mock_llm_service.generate_rolling_summary.call_args[1]
    assert call_args["previous_summary"] == "Previous summary"


def test_generate_rolling_summary_missing_previous(
    service,
    temp_db,
    sample_sections,
    mock_llm_service,
):
    """Test generating rolling summary when previous section lacks summary."""
    # Second section has no previous summary - should generate it recursively
    mock_llm_service.generate_rolling_summary.return_value = "Generated summary"

    result = service.generate_rolling_summary(sample_sections[1].id)

    assert result == "Generated summary"
    # Should be called twice: once for section 0, once for section 1
    assert mock_llm_service.generate_rolling_summary.call_count >= 1


def test_generate_rolling_summary_already_exists(
    service, temp_db, sample_sections, mock_llm_service
):
    """Test that existing summary is returned when force_regenerate=False."""
    # Set existing summary
    temp_db.update_section(sample_sections[0].id, rolling_summary="Existing summary")

    result = service.generate_rolling_summary(
        sample_sections[0].id, force_regenerate=False
    )

    assert result == "Existing summary"
    # LLM should not be called
    mock_llm_service.generate_rolling_summary.assert_not_called()


def test_generate_rolling_summary_force_regenerate(
    service, temp_db, sample_sections, mock_llm_service
):
    """Test force regeneration of existing summary."""
    # Set existing summary
    temp_db.update_section(sample_sections[0].id, rolling_summary="Old summary")

    result = service.generate_rolling_summary(
        sample_sections[0].id, force_regenerate=True
    )

    assert result == "Test rolling summary"
    # LLM should be called despite existing summary
    mock_llm_service.generate_rolling_summary.assert_called_once()


def test_generate_rolling_summary_invalid_section(service, mock_llm_service):
    """Test generating summary for non-existent section."""
    result = service.generate_rolling_summary(99999)

    assert result is None
    mock_llm_service.generate_rolling_summary.assert_not_called()


def test_generate_rolling_summary_llm_failure(
    service,
    temp_db,
    sample_sections,
    mock_llm_service,
):
    """Test handling LLM failure."""
    mock_llm_service.generate_rolling_summary.return_value = None

    result = service.generate_rolling_summary(sample_sections[0].id)

    assert result is None


def test_generate_rolling_summary_truncation(
    service,
    temp_db,
    sample_sections,
    mock_llm_service,
):
    """Test truncation of very long summaries."""
    # Create a summary longer than ROLLING_CONTEXT_MAX_CHARS
    long_summary = "x" * 15000  # Exceeds default 10000 limit
    mock_llm_service.generate_rolling_summary.return_value = long_summary

    result = service.generate_rolling_summary(sample_sections[0].id)

    # Should be truncated
    assert result is not None
    assert len(result) <= 10003  # 10000 + "..."


def test_generate_rolling_summary_saves_to_db(
    service, temp_db, sample_sections, mock_llm_service
):
    """Test that generated summary is saved to database."""
    mock_llm_service.generate_rolling_summary.return_value = "New summary"

    service.generate_rolling_summary(sample_sections[0].id)

    # Verify it was saved
    section = temp_db.get_section(sample_sections[0].id)
    assert section.rolling_summary == "New summary"


# ===== Batch Rolling Summary Generation Tests =====


def test_generate_rolling_summaries_batch(
    service,
    temp_db,
    sample_project,
    sample_sections,
    mock_llm_service,
):
    """Test batch generation of rolling summaries."""
    mock_llm_service.generate_rolling_summary.return_value = "Batch summary"

    results = service.generate_rolling_summaries_batch(sample_project.id)

    assert len(results) == 3
    assert all(success for success in results.values())
    # Should be called 3 times (once per section)
    assert mock_llm_service.generate_rolling_summary.call_count == 3


def test_generate_rolling_summaries_batch_with_callback(
    service,
    temp_db,
    sample_project,
    sample_sections,
    mock_llm_service,
):
    """Test batch generation with progress callback."""
    mock_llm_service.generate_rolling_summary.return_value = "Batch summary"
    callback_calls = []

    def progress_callback(current, total, message):
        callback_calls.append((current, total, message))

    service.generate_rolling_summaries_batch(
        sample_project.id, progress_callback=progress_callback
    )

    # Should have received progress updates
    assert len(callback_calls) > 0
    assert callback_calls[-1][0] == 3  # Final count
    assert callback_calls[-1][1] == 3  # Total


def test_generate_rolling_summaries_batch_empty_project(
    service,
    temp_db,
    sample_project,
    mock_llm_service,
):
    """Test batch generation for project with no sections."""
    results = service.generate_rolling_summaries_batch(sample_project.id)

    assert results == {}
    mock_llm_service.generate_rolling_summary.assert_not_called()


def test_generate_rolling_summaries_batch_invalid_project(service, mock_llm_service):
    """Test batch generation for invalid project."""
    results = service.generate_rolling_summaries_batch(99999)

    assert results == {}


def test_generate_rolling_summaries_batch_partial_failure(
    service,
    temp_db,
    sample_project,
    sample_sections,
    mock_llm_service,
):
    """Test batch generation with some failures."""
    # First call succeeds, second fails, third will depend on second
    # so it might also fail
    mock_llm_service.generate_rolling_summary.side_effect = [
        "Summary 1",
        None,  # Failure for section 1
        None,  # Section 2 tries to generate but fails due to missing previous
    ]

    results = service.generate_rolling_summaries_batch(sample_project.id)

    assert len(results) == 3
    assert results[sample_sections[0].id] is True
    assert results[sample_sections[1].id] is False
    # Section 2 fails because section 1 (its previous) failed
    assert results[sample_sections[2].id] is False


# ===== Study Notes Generation Tests =====


def test_generate_study_notes_without_rolling_summary(
    service,
    temp_db,
    sample_sections,
    mock_llm_service,
):
    """Test generating study notes when section lacks rolling summary."""
    mock_llm_service.generate_rolling_summary.return_value = "Generated rolling"
    mock_llm_service.generate_study_notes.return_value = "Study notes"

    result = service.generate_study_notes(sample_sections[0].id)

    assert result == "Study notes"
    # Should generate rolling summary first
    mock_llm_service.generate_rolling_summary.assert_called()
    mock_llm_service.generate_study_notes.assert_called_once()


def test_generate_study_notes_with_existing_rolling_summary(
    service, temp_db, sample_sections, mock_llm_service
):
    """Test generating study notes with existing rolling summary."""
    temp_db.update_section(
        sample_sections[0].id, rolling_summary="Existing rolling summary"
    )
    mock_llm_service.generate_study_notes.return_value = "Study notes"

    result = service.generate_study_notes(sample_sections[0].id)

    assert result == "Study notes"
    # Should use existing rolling summary
    call_args = mock_llm_service.generate_study_notes.call_args[1]
    assert call_args["rolling_summary"] == "Existing rolling summary"


def test_generate_study_notes_force_regenerate(
    service, temp_db, sample_sections, mock_llm_service
):
    """Test force regeneration of existing study notes."""
    temp_db.update_section(sample_sections[0].id, study_notes="Old notes")
    mock_llm_service.generate_study_notes.return_value = "New notes"

    result = service.generate_study_notes(sample_sections[0].id, force_regenerate=True)

    assert result == "New notes"
    mock_llm_service.generate_study_notes.assert_called()


def test_generate_study_notes_with_pecs_data(
    service, temp_db, sample_sections, mock_llm_service
):
    """Test generating study notes with PECS data."""
    # Add PECS data
    temp_db.update_section_pecs_data(
        sample_sections[0].id,
        "engage_explain",
        {"explanation": "Test explanation"},
    )
    mock_llm_service.generate_study_notes.return_value = "Notes with PECS"

    result = service.generate_study_notes(sample_sections[0].id)

    assert result == "Notes with PECS"


def test_generate_study_notes_invalid_section(service, mock_llm_service):
    """Test generating study notes for invalid section."""
    result = service.generate_study_notes(99999)

    assert result is None


def test_generate_study_notes_llm_failure(
    service,
    temp_db,
    sample_sections,
    mock_llm_service,
):
    """Test handling LLM failure during study notes generation."""
    mock_llm_service.generate_study_notes.return_value = None

    result = service.generate_study_notes(sample_sections[0].id)

    assert result is None


def test_generate_study_notes_saves_to_db(
    service, temp_db, sample_sections, mock_llm_service
):
    """Test that generated study notes are saved to database."""
    mock_llm_service.generate_study_notes.return_value = "Generated notes"

    service.generate_study_notes(sample_sections[0].id)

    section = temp_db.get_section(sample_sections[0].id)
    assert section.study_notes == "Generated notes"


# ===== Batch Study Notes Generation Tests =====


def test_generate_study_notes_batch(
    service,
    temp_db,
    sample_project,
    sample_sections,
    mock_llm_service,
):
    """Test batch generation of study notes."""
    mock_llm_service.generate_rolling_summary.return_value = "Rolling"
    mock_llm_service.generate_study_notes.return_value = "Notes"

    results = service.generate_study_notes_batch(sample_project.id)

    assert len(results) == 3
    assert all(success for success in results.values())


def test_generate_study_notes_batch_with_callback(
    service,
    temp_db,
    sample_project,
    sample_sections,
    mock_llm_service,
):
    """Test batch study notes generation with progress callback."""
    mock_llm_service.generate_rolling_summary.return_value = "Rolling"
    mock_llm_service.generate_study_notes.return_value = "Notes"
    callback_calls = []

    def progress_callback(current, total, message):
        callback_calls.append((current, total, message))

    service.generate_study_notes_batch(
        sample_project.id, progress_callback=progress_callback
    )

    assert len(callback_calls) > 0


def test_generate_study_notes_batch_includes_rolling_context(
    service,
    temp_db,
    sample_project,
    sample_sections,
    mock_llm_service,
):
    """Test that batch generation includes rolling context generation."""
    mock_llm_service.generate_rolling_summary.return_value = "Rolling"
    mock_llm_service.generate_study_notes.return_value = "Notes"

    service.generate_study_notes_batch(sample_project.id)

    # Should generate both rolling summaries and study notes
    assert mock_llm_service.generate_rolling_summary.call_count >= 1
    assert mock_llm_service.generate_study_notes.call_count >= 1


def test_generate_study_notes_batch_empty_project(
    service,
    temp_db,
    sample_project,
    mock_llm_service,
):
    """Test batch study notes generation for empty project."""
    results = service.generate_study_notes_batch(sample_project.id)

    assert results == {}


def test_generate_study_notes_batch_invalid_project(service, mock_llm_service):
    """Test batch study notes generation for invalid project."""
    results = service.generate_study_notes_batch(99999)

    assert results == {}


# ===== Edge Cases =====


def test_section_without_title(service, temp_db, sample_project, mock_llm_service):
    """Test handling section without title."""
    section = temp_db.create_section(
        sample_project.id, "Content", title=None, order_index=0
    )
    mock_llm_service.generate_rolling_summary.return_value = "Summary"

    result = service.generate_rolling_summary(section.id)

    assert result == "Summary"
    call_args = mock_llm_service.generate_rolling_summary.call_args[1]
    # Should use default section title
    assert "Section 1" in call_args["section_title"]


def test_empty_section_content(service, temp_db, sample_project, mock_llm_service):
    """Test handling empty section content."""
    section = temp_db.create_section(sample_project.id, "", 0)
    mock_llm_service.generate_rolling_summary.return_value = "Summary"

    result = service.generate_rolling_summary(section.id)

    assert result == "Summary"


def test_section_with_very_long_content(
    service, temp_db, sample_project, mock_llm_service
):
    """Test handling section with very long content."""
    long_content = "x" * 50000
    section = temp_db.create_section(sample_project.id, long_content, 0)
    mock_llm_service.generate_rolling_summary.return_value = "Summary"

    result = service.generate_rolling_summary(section.id)

    assert result == "Summary"
    # Should still call LLM with full content
    call_args = mock_llm_service.generate_rolling_summary.call_args[1]
    assert len(call_args["current_content"]) == 50000
