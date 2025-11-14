"""
Database repository layer for P.E.C.S. Learning System.
Provides a clean interface for all database operations.
"""

import os
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from utils.models import Base, Flashcard, Project, Section

# Database file path - stored in data/ directory
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "pecs.db")


class DatabaseRepository:
    """Repository class for database operations."""

    def __init__(self, db_path: str = None):
        """
        Initialize the database connection.

        Args:
            db_path: Path to SQLite database file. Defaults to data/pecs.db
        """
        if db_path is None:
            db_path = DB_PATH

        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create engine and session factory
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.session_local = sessionmaker(bind=self.engine)

        # Create tables
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.session_local()

    # Project operations
    def create_project(self, name: str) -> Optional[Project]:
        """Create a new project."""
        session = self.get_session()
        try:
            # Check if project with same name exists
            existing = session.query(Project).filter(Project.name == name).first()
            if existing:
                return None

            project = Project(name=name)
            session.add(project)
            session.commit()
            session.refresh(project)
            return project
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a project by ID."""
        session = self.get_session()
        try:
            return session.query(Project).filter(Project.id == project_id).first()
        finally:
            session.close()

    def get_all_projects(self) -> List[Project]:
        """Get all projects."""
        session = self.get_session()
        try:
            return session.query(Project).order_by(Project.created_at.desc()).all()
        finally:
            session.close()

    def update_project(self, project_id: int, **kwargs) -> bool:
        """Update project fields."""
        session = self.get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False

            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)

            project.updated_at = datetime.now(UTC)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all its sections/flashcards."""
        session = self.get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False

            session.delete(project)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # Section operations
    def create_section(
        self, project_id: int, content: str, title: str = None, order_index: int = 0
    ) -> Optional[Section]:
        """Create a new section."""
        session = self.get_session()
        try:
            section = Section(
                project_id=project_id,
                content=content,
                title=title,
                order_index=order_index,
                pecs_data={},
            )
            session.add(section)
            session.commit()
            session.refresh(section)
            return section
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_section(self, section_id: int) -> Optional[Section]:
        """Get a section by ID."""
        session = self.get_session()
        try:
            return session.query(Section).filter(Section.id == section_id).first()
        finally:
            session.close()

    def get_sections_by_project(self, project_id: int) -> List[Section]:
        """Get all sections for a project, ordered by order_index."""
        session = self.get_session()
        try:
            return (
                session.query(Section)
                .filter(Section.project_id == project_id)
                .order_by(Section.order_index)
                .all()
            )
        finally:
            session.close()

    def update_section(self, section_id: int, **kwargs) -> bool:
        """Update section fields."""
        session = self.get_session()
        try:
            section = session.query(Section).filter(Section.id == section_id).first()
            if not section:
                return False

            for key, value in kwargs.items():
                if hasattr(section, key):
                    setattr(section, key, value)

            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_section_pecs_data(
        self, section_id: int, phase: str, data: Dict[str, Any]
    ) -> bool:
        """Update PECS data for a specific phase, auto-saving in real-time."""
        session = self.get_session()
        try:
            section = session.query(Section).filter(Section.id == section_id).first()
            if not section:
                return False

            # Merge PECS data - create a new dict to ensure SQLAlchemy detects the change
            if section.pecs_data is None:
                section.pecs_data = {}
            else:
                # Create a copy to ensure change detection
                section.pecs_data = dict(section.pecs_data)

            section.pecs_data[phase] = data
            # Explicitly mark as modified for SQLAlchemy JSON column
            from sqlalchemy.orm.attributes import flag_modified

            flag_modified(section, "pecs_data")
            session.commit()
            session.refresh(section)  # Refresh to ensure data is persisted
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def mark_section_completed(self, section_id: int, completed: bool = True) -> bool:
        """Mark a section as completed or not completed."""
        session = self.get_session()
        try:
            section = session.query(Section).filter(Section.id == section_id).first()
            if not section:
                return False

            section.is_completed = completed
            if completed:
                section.completed_at = datetime.now(UTC)
            else:
                section.completed_at = None

            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_section(self, section_id: int) -> bool:
        """
        Delete a section and all associated flashcards.

        Args:
            section_id: ID of section to delete

        Returns:
            True if deletion successful, False if section not found
        """
        session = self.get_session()
        try:
            section = session.query(Section).filter(Section.id == section_id).first()
            if not section:
                return False

            # Delete section (cascades to flashcards automatically)
            session.delete(section)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # Flashcard operations
    def create_flashcard(
        self,
        project_id: int,
        question: str,
        answer: str,
        section_id: Optional[int] = None,
    ) -> Optional[Flashcard]:
        """Create a new flashcard."""
        session = self.get_session()
        try:
            flashcard = Flashcard(
                project_id=project_id,
                section_id=section_id,
                question=question,
                answer=answer,
                next_review=datetime.now(UTC),  # Start with immediate review
            )
            session.add(flashcard)
            session.commit()
            session.refresh(flashcard)
            return flashcard
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_flashcard(self, flashcard_id: int) -> Optional[Flashcard]:
        """Get a flashcard by ID."""
        session = self.get_session()
        try:
            return session.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
        finally:
            session.close()

    def get_flashcards_by_project(
        self, project_id: int, section_id: Optional[int] = None
    ) -> List[Flashcard]:
        """Get flashcards for a project, optionally filtered by section."""
        session = self.get_session()
        try:
            query = session.query(Flashcard).filter(Flashcard.project_id == project_id)
            if section_id is not None:
                query = query.filter(Flashcard.section_id == section_id)
            return query.order_by(Flashcard.created_at.desc()).all()
        finally:
            session.close()

    def get_flashcards_for_review(self, project_id: int) -> List[Flashcard]:
        """Get flashcards that are due for review."""
        session = self.get_session()
        try:
            now = datetime.now(UTC)
            return (
                session.query(Flashcard)
                .filter(
                    Flashcard.project_id == project_id,
                    Flashcard.next_review <= now,
                    not Flashcard.is_mastered,
                )
                .order_by(Flashcard.next_review)
                .all()
            )
        finally:
            session.close()

    def update_flashcard_review(self, flashcard_id: int, knew_it: bool) -> bool:
        """
        Update flashcard after review using SM-2 algorithm.

        Args:
            flashcard_id: ID of the flashcard
            knew_it: True if user knew the answer, False if they need to review again
        """
        session = self.get_session()
        try:
            flashcard = (
                session.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
            )
            if not flashcard:
                return False

            # Update review tracking
            flashcard.last_reviewed = datetime.now(UTC)
            flashcard.review_count += 1

            if knew_it:
                # User knew it - increase interval
                if flashcard.interval_days == 0:
                    flashcard.interval_days = 1
                else:
                    flashcard.interval_days = int(
                        flashcard.interval_days * flashcard.ease_factor
                    )

                flashcard.ease_factor = min(2.5, flashcard.ease_factor + 0.1)

                # Mark as mastered after multiple successful reviews
                if flashcard.review_count >= 5 and flashcard.interval_days >= 30:
                    flashcard.is_mastered = True
            else:
                # User needs to review again - reset interval
                flashcard.interval_days = 1
                flashcard.ease_factor = max(1.3, flashcard.ease_factor - 0.2)

            flashcard.next_review = datetime.now(UTC) + timedelta(
                days=flashcard.interval_days
            )

            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_flashcard(self, flashcard_id: int) -> bool:
        """Delete a flashcard."""
        session = self.get_session()
        try:
            flashcard = (
                session.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
            )
            if not flashcard:
                return False

            session.delete(flashcard)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_project_stats(self, project_id: int) -> Dict[str, Any]:
        """Get statistics for a project."""
        session = self.get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return {}

            sections = self.get_sections_by_project(project_id)
            flashcards = self.get_flashcards_by_project(project_id)

            return {
                "total_sections": len(sections),
                "completed_sections": sum(1 for s in sections if s.is_completed),
                "total_flashcards": len(flashcards),
                "mastered_flashcards": sum(1 for f in flashcards if f.is_mastered),
                "cards_due_for_review": len(self.get_flashcards_for_review(project_id)),
            }
        finally:
            session.close()
