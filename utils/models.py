"""
Database models for the P.E.C.S. Learning System using SQLAlchemy ORM.
"""

from datetime import UTC, datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

# Use timezone-aware UTC for Python 3.11+, fallback for older versions
try:
    UTC_TZ = UTC
except AttributeError:
    UTC_TZ = timezone.utc

Base = declarative_base()


class Project(Base):
    """Represents a study project (e.g., a book or course material)."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC_TZ))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC_TZ),
        onupdate=lambda: datetime.now(UTC_TZ),
    )

    # Relationships
    sections = relationship(
        "Section",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Section.order_index",
    )
    flashcards = relationship(
        "Flashcard", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class Section(Base):
    """Represents a section/chapter within a project."""

    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(
        String(300), nullable=True
    )  # Optional title like "Chapter 1: Introduction"
    content = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False)  # For maintaining order

    # PECS data stored as flexible JSON
    pecs_data = Column(JSON, default={})

    # Completion tracking
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="sections")
    flashcards = relationship(
        "Flashcard", back_populates="section", cascade="all, delete-orphan"
    )

    # Index for efficient queries
    __table_args__ = (Index("idx_project_order", "project_id", "order_index"),)

    def __repr__(self):
        return f"<Section(id={self.id}, project_id={self.project_id}, title='{self.title}', order={self.order_index})>"


class Flashcard(Base):
    """Represents a flashcard for spaced repetition."""

    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    section_id = Column(
        Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=True
    )  # Optional: can be global

    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    # Spaced repetition tracking
    last_reviewed = Column(DateTime, nullable=True)
    review_count = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)  # SM-2 algorithm parameter
    interval_days = Column(Integer, default=1)
    next_review = Column(DateTime, nullable=True)

    # Self-grading results
    is_mastered = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC_TZ))

    # Relationships
    project = relationship("Project", back_populates="flashcards")
    section = relationship("Section", back_populates="flashcards")

    # Index for efficient queries
    __table_args__ = (
        Index("idx_project_section", "project_id", "section_id"),
        Index("idx_next_review", "next_review"),
    )

    def __repr__(self):
        return f"<Flashcard(id={self.id}, project_id={self.project_id}, question='{self.question[:50]}...')>"
