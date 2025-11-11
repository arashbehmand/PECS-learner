"""
Migration utility to import old JSON session files into the new SQLite database.
"""

import json
import logging
from typing import Tuple

from utils.database import DatabaseRepository

logger = logging.getLogger(__name__)


def migrate_json_to_database(
    json_str: str, db: DatabaseRepository, project_name: str = "Migrated Project"
) -> Tuple[bool, str]:
    """
    Migrate data from old JSON format to new database.

    Args:
        json_str: JSON string from old export format
        db: DatabaseRepository instance
        project_name: Name for the new project

    Returns:
        Tuple[bool, str]: (success, message)
            - success: True if migration successful, False otherwise
            - message: Success or error message
    """
    try:
        # Parse JSON
        data = json.loads(json_str)

        # Validate required fields
        if "raw_material" not in data or "chunks" not in data:
            return (
                False,
                "Invalid JSON format: missing required fields (raw_material, chunks)",
            )

        # Create new project
        project = db.create_project(project_name)
        if not project:
            return (
                False,
                f"Failed to create project '{project_name}'. It may already exist.",
            )

        # Migrate chunks to sections
        chunks = data.get("chunks", [])
        chunk_data = data.get("chunk_data", {})

        sections_created = 0
        warnings = []

        for idx, chunk_content in enumerate(chunks):
            # Create section from chunk
            section = db.create_section(
                project_id=project.id,
                content=chunk_content,
                title=f"Section {idx + 1}",
                order_index=idx,
            )

            if not section:
                warnings.append(f"Failed to create section {idx + 1}")
                continue

            sections_created += 1

            # Store section ID immediately (section object may be from closed session)
            section_id = section.id

            # Migrate PECS data if available
            if idx in chunk_data:
                chunk_pecs = chunk_data[idx]

                # Process completed flag first (before PECS data updates)
                if "completed" in chunk_pecs and chunk_pecs["completed"]:
                    db.mark_section_completed(section_id, completed=True)

                # Migrate each phase (skip 'completed' as it's handled above)
                for phase, phase_data in chunk_pecs.items():
                    if phase == "completed":
                        continue  # Already handled above

                    # Save PECS phase data - use section_id to ensure correct reference
                    success = db.update_section_pecs_data(section_id, phase, phase_data)
                    if not success:
                        warnings.append(
                            f"Failed to migrate {phase} data for section {idx + 1}"
                        )

            # Migrate flashcards if available
            all_flashcards = data.get("all_recall_prompts", [])
            for flashcard in all_flashcards:
                if flashcard.get("chunk_idx") == idx:
                    db.create_flashcard(
                        project_id=project.id,
                        question=flashcard.get("question", ""),
                        answer=flashcard.get("answer", ""),
                        section_id=section.id,
                    )

        success_msg = f"Migration complete! Created project '{project_name}' with {sections_created} sections."
        if warnings:
            success_msg += f"\nWarnings: {'; '.join(warnings)}"

        logger.info(success_msg)
        return True, success_msg

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Migration error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg
