"""
Unit tests for database repository layer.
"""

import os
import tempfile

import pytest

from utils.database import DatabaseRepository


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseRepository(db_path=path)
    yield db
    # Close all database connections
    db.engine.dispose()
    # Small delay to ensure file handles are released (Windows issue)
    import time

    time.sleep(0.1)
    try:
        os.unlink(path)
    except PermissionError:
        # On Windows, sometimes the file is still locked
        # This is acceptable for tests - the file will be cleaned up by tempfile
        pass


def test_create_project(temp_db):
    """Test project creation."""
    project = temp_db.create_project("Test Project")
    assert project is not None
    assert project.name == "Test Project"
    assert project.id is not None


def test_duplicate_project_name(temp_db):
    """Test that duplicate project names are rejected."""
    temp_db.create_project("Test Project")
    project2 = temp_db.create_project("Test Project")
    assert project2 is None


def test_get_project(temp_db):
    """Test retrieving a project."""
    project = temp_db.create_project("Test Project")
    retrieved = temp_db.get_project(project.id)
    assert retrieved is not None
    assert retrieved.name == "Test Project"


def test_create_section(temp_db):
    """Test section creation."""
    project = temp_db.create_project("Test Project")
    section = temp_db.create_section(
        project_id=project.id,
        content="Test content",
        title="Test Section",
        order_index=0,
    )
    assert section is not None
    assert section.content == "Test content"
    assert section.title == "Test Section"


def test_get_sections_by_project(temp_db):
    """Test retrieving sections for a project."""
    project = temp_db.create_project("Test Project")
    temp_db.create_section(project.id, "Content 1", "Section 1", 0)
    temp_db.create_section(project.id, "Content 2", "Section 2", 1)

    sections = temp_db.get_sections_by_project(project.id)
    assert len(sections) == 2
    assert sections[0].order_index == 0
    assert sections[1].order_index == 1


def test_update_section_pecs_data(temp_db):
    """Test updating PECS data."""
    project = temp_db.create_project("Test Project")
    section = temp_db.create_section(project.id, "Test content", "Section 1", 0)

    pecs_data = {
        "initial_thoughts": "Test thoughts",
        "prior_knowledge": "Test knowledge",
    }
    result = temp_db.update_section_pecs_data(section.id, "prime_preview", pecs_data)
    assert result is True

    updated_section = temp_db.get_section(section.id)
    # Check that the PECS data exists and matches
    assert updated_section.pecs_data is not None
    assert "prime_preview" in updated_section.pecs_data
    assert updated_section.pecs_data["prime_preview"] == pecs_data


def test_create_flashcard(temp_db):
    """Test flashcard creation."""
    project = temp_db.create_project("Test Project")
    flashcard = temp_db.create_flashcard(
        project_id=project.id, question="Test question?", answer="Test answer"
    )
    assert flashcard is not None
    assert flashcard.question == "Test question?"
    assert flashcard.answer == "Test answer"


def test_mark_section_completed(temp_db):
    """Test marking section as completed."""
    project = temp_db.create_project("Test Project")
    section = temp_db.create_section(project.id, "Test content", "Section 1", 0)

    result = temp_db.mark_section_completed(section.id, completed=True)
    assert result is True

    updated_section = temp_db.get_section(section.id)
    assert updated_section.is_completed is True


def test_get_project_stats(temp_db):
    """Test getting project statistics."""
    project = temp_db.create_project("Test Project")
    section = temp_db.create_section(project.id, "Test content", "Section 1", 0)
    temp_db.create_flashcard(project.id, "Q?", "A")
    temp_db.mark_section_completed(section.id, completed=True)

    stats = temp_db.get_project_stats(project.id)
    assert stats["total_sections"] == 1
    assert stats["completed_sections"] == 1
    assert stats["total_flashcards"] == 1


def test_update_flashcard_review(temp_db):
    """Test flashcard review update."""
    project = temp_db.create_project("Test Project")
    flashcard = temp_db.create_flashcard(project.id, "Q?", "A")

    # First review - knew it
    result = temp_db.update_flashcard_review(flashcard.id, knew_it=True)
    assert result is True

    updated = temp_db.get_flashcard(flashcard.id)
    assert updated.review_count == 1
    assert updated.interval_days > 0

    # Second review - didn't know it
    result = temp_db.update_flashcard_review(flashcard.id, knew_it=False)
    assert result is True

    updated = temp_db.get_flashcard(flashcard.id)
    assert updated.review_count == 2
    assert updated.interval_days == 1  # Reset


def test_delete_section(temp_db):
    """Test deleting a section."""
    project = temp_db.create_project("Test Project")
    section1 = temp_db.create_section(project.id, "Section 1 content", "Section 1", 0)
    section2 = temp_db.create_section(project.id, "Section 2 content", "Section 2", 1)

    # Delete section 1
    result = temp_db.delete_section(section1.id)
    assert result is True

    # Verify section 1 is deleted
    deleted_section = temp_db.get_section(section1.id)
    assert deleted_section is None

    # Verify section 2 still exists
    remaining_section = temp_db.get_section(section2.id)
    assert remaining_section is not None
    assert remaining_section.title == "Section 2"

    # Test deleting non-existent section
    result = temp_db.delete_section(999)
    assert result is False


def test_delete_section_cascades_flashcards(temp_db):
    """Test that deleting a section also deletes associated flashcards."""
    project = temp_db.create_project("Test Project")
    section = temp_db.create_section(project.id, "Test content", "Section 1", 0)

    # Create flashcards for this section
    flashcard1 = temp_db.create_flashcard(
        project.id, "Question 1?", "Answer 1", section_id=section.id
    )
    flashcard2 = temp_db.create_flashcard(
        project.id, "Question 2?", "Answer 2", section_id=section.id
    )
    # Create a flashcard for the project but not this section
    flashcard3 = temp_db.create_flashcard(project.id, "Question 3?", "Answer 3")

    # Verify flashcards exist
    section_flashcards = temp_db.get_flashcards_by_project(
        project.id, section_id=section.id
    )
    assert len(section_flashcards) == 2

    # Delete the section
    result = temp_db.delete_section(section.id)
    assert result is True

    # Verify section flashcards are deleted
    deleted_flashcard1 = temp_db.get_flashcard(flashcard1.id)
    deleted_flashcard2 = temp_db.get_flashcard(flashcard2.id)
    assert deleted_flashcard1 is None
    assert deleted_flashcard2 is None

    # Verify project-level flashcard still exists
    remaining_flashcard = temp_db.get_flashcard(flashcard3.id)
    assert remaining_flashcard is not None
    assert remaining_flashcard.question == "Question 3?"
