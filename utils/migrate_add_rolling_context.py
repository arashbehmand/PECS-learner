"""
Database Migration: Add Rolling Context and Study Notes Fields

This migration adds the new rolling_summary and study_notes columns to the
sections table for existing databases.

For new databases, these columns are automatically created by SQLAlchemy
from the models.py definition.
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database(db_path: str = "data/pecs.db"):
    """
    Add rolling_summary and study_notes columns to sections table.

    Args:
        db_path: Path to SQLite database file
    """
    db_file = Path(db_path)

    if not db_file.exists():
        logger.info(f"Database {db_path} does not exist. No migration needed.")
        return

    logger.info(f"Migrating database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(sections)")
        columns = [row[1] for row in cursor.fetchall()]

        migrations_applied = []

        # Add rolling_summary column if it doesn't exist
        if "rolling_summary" not in columns:
            logger.info("Adding rolling_summary column...")
            cursor.execute(
                """
                ALTER TABLE sections
                ADD COLUMN rolling_summary TEXT
                """
            )
            migrations_applied.append("rolling_summary")
        else:
            logger.info("rolling_summary column already exists")

        # Add study_notes column if it doesn't exist
        if "study_notes" not in columns:
            logger.info("Adding study_notes column...")
            cursor.execute(
                """
                ALTER TABLE sections
                ADD COLUMN study_notes TEXT
                """
            )
            migrations_applied.append("study_notes")
        else:
            logger.info("study_notes column already exists")

        conn.commit()

        if migrations_applied:
            logger.info(f"✓ Migration complete. Added columns: {', '.join(migrations_applied)}")
        else:
            logger.info("✓ No migration needed. All columns exist.")

    except sqlite3.Error as e:
        logger.error(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/pecs.db"
    migrate_database(db_path)
