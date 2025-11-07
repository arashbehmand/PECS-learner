"""
Migration utility to import old JSON session files into the new SQLite database.
"""
import json
import streamlit as st
from utils.database import DatabaseRepository
from utils.hierarchical_processor import create_sections_from_text
from typing import Dict, Any


def migrate_json_to_database(json_str: str, db: DatabaseRepository, project_name: str = "Migrated Project") -> bool:
    """
    Migrate data from old JSON format to new database.
    
    Args:
        json_str: JSON string from old export format
        db: DatabaseRepository instance
        project_name: Name for the new project
    
    Returns:
        bool: True if migration successful, False otherwise
    """
    try:
        # Parse JSON
        data = json.loads(json_str)
        
        # Validate required fields
        if 'raw_material' not in data or 'chunks' not in data:
            st.error("Invalid JSON format: missing required fields (raw_material, chunks)")
            return False
        
        # Create new project
        project = db.create_project(project_name)
        if not project:
            st.error(f"Failed to create project '{project_name}'. It may already exist.")
            return False
        
        # Migrate chunks to sections
        chunks = data.get('chunks', [])
        chunk_data = data.get('chunk_data', {})
        
        for idx, chunk_content in enumerate(chunks):
            # Create section from chunk
            section = db.create_section(
                project_id=project.id,
                content=chunk_content,
                title=f"Section {idx + 1}",
                order_index=idx
            )
            
            if not section:
                st.warning(f"Failed to create section {idx + 1}")
                continue
            
            # Store section ID immediately (section object may be from closed session)
            section_id = section.id
            
            # Migrate PECS data if available
            if idx in chunk_data:
                chunk_pecs = chunk_data[idx]
                
                # Process completed flag first (before PECS data updates)
                if 'completed' in chunk_pecs and chunk_pecs['completed']:
                    db.mark_section_completed(section_id, completed=True)
                
                # Migrate each phase (skip 'completed' as it's handled above)
                for phase, phase_data in chunk_pecs.items():
                    if phase == 'completed':
                        continue  # Already handled above
                    
                    # Save PECS phase data - use section_id to ensure correct reference
                    success = db.update_section_pecs_data(section_id, phase, phase_data)
                    if not success:
                        st.warning(f"Failed to migrate {phase} data for section {idx + 1}")
            
            # Migrate flashcards if available
            all_flashcards = data.get('all_recall_prompts', [])
            for flashcard in all_flashcards:
                if flashcard.get('chunk_idx') == idx:
                    db.create_flashcard(
                        project_id=project.id,
                        question=flashcard.get('question', ''),
                        answer=flashcard.get('answer', ''),
                        section_id=section.id
                    )
        
        st.success(f"✅ Migration complete! Created project '{project_name}' with {len(chunks)} sections.")
        return True
        
    except json.JSONDecodeError:
        st.error("Invalid JSON format")
        return False
    except Exception as e:
        st.error(f"Migration error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return False


def create_migration_ui(db: DatabaseRepository):
    """
    Create UI for importing old JSON sessions.
    """
    st.subheader("📥 Import Old Session (JSON)")
    st.markdown("""
    Import a previously exported session from the old JSON format into the new database format.
    """)
    
    uploaded_file = st.file_uploader("Upload JSON session file", type=['json'])
    
    if uploaded_file is not None:
        project_name = st.text_input(
            "Project Name:",
            value="Migrated Session",
            key="migration_project_name"
        )
        
        if st.button("Import Session", key="migrate_btn"):
            json_str = uploaded_file.getvalue().decode('utf-8')
            if migrate_json_to_database(json_str, db, project_name):
                st.balloons()
                st.rerun()

