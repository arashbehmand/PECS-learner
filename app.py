"""
P.E.C.S. Learning System - Main Application
Refactored to use SQLite database and hierarchical content processing.
"""
import streamlit as st
from utils.database import DatabaseRepository
from components.project_dashboard import render_project_dashboard
from components.content_upload_new import render_content_upload as render_content_upload_new
from components.section_navigator import render_section_navigator
from components.pecs_tabs import render_pecs_phases
from components.study_mode import render_study_mode
from utils.migration import create_migration_ui

# Page configuration
st.set_page_config(
    page_title="P.E.C.S. Learning System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database connection
@st.cache_resource
def get_database():
    """Get cached database repository instance."""
    return DatabaseRepository()

db = get_database()

# Initialize session state
if 'show_dashboard' not in st.session_state:
    st.session_state.show_dashboard = True
if 'current_project_id' not in st.session_state:
    st.session_state.current_project_id = None
if 'current_section_id' not in st.session_state:
    st.session_state.current_section_id = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'study'  # 'study' or 'pecs'

# Sidebar navigation
st.sidebar.title("📚 P.E.C.S. Learning System")
st.sidebar.markdown("---")

# Main navigation
if st.session_state.current_project_id:
    project = db.get_project(st.session_state.current_project_id)
    if project:
        st.sidebar.markdown(f"**Current Project:** {project.name}")
        
        # Navigation options
        nav_option = st.sidebar.radio(
            "Navigate to:",
            ["Study Section", "Study Mode", "Migration", "Project Dashboard"],
            key="main_nav"
        )
        
        if nav_option == "Project Dashboard":
            if st.sidebar.button("← Back to Dashboard"):
                st.session_state.show_dashboard = True
                st.session_state.current_project_id = None
                st.rerun()
        elif nav_option == "Study Section":
            st.session_state.view_mode = 'pecs'
        elif nav_option == "Study Mode":
            st.session_state.view_mode = 'study'
        elif nav_option == "Migration":
            st.session_state.view_mode = 'migration'
        
        st.sidebar.markdown("---")
        
        # Project stats
        stats = db.get_project_stats(st.session_state.current_project_id)
        st.sidebar.subheader("📊 Project Statistics")
        st.sidebar.metric("Sections", f"{stats.get('total_sections', 0)}")
        st.sidebar.metric("Completed", f"{stats.get('completed_sections', 0)}")
        st.sidebar.metric("Flashcards", f"{stats.get('total_flashcards', 0)}")
        
        if stats.get('cards_due_for_review', 0) > 0:
            st.sidebar.metric("📅 Due for Review", stats.get('cards_due_for_review', 0))
        
        st.sidebar.markdown("---")
else:
    if st.sidebar.button("📚 Project Dashboard"):
        st.session_state.show_dashboard = True
        st.rerun()

# Main content area
if st.session_state.show_dashboard or not st.session_state.current_project_id:
    # Show project dashboard
    render_project_dashboard(db)
    
    # Check if a project was selected
    if st.session_state.current_project_id:
        project = db.get_project(st.session_state.current_project_id)
        if project:
            sections = db.get_sections_by_project(st.session_state.current_project_id)
            
            if not sections:
                # No sections - show content upload
                st.session_state.show_dashboard = False
                st.header(f"📖 {project.name}")
                render_content_upload_new(db, st.session_state.current_project_id)
            else:
                st.session_state.show_dashboard = False
                st.rerun()

else:
    # We have a project selected
    project = db.get_project(st.session_state.current_project_id)
    if not project:
        st.error("Project not found. Returning to dashboard.")
        st.session_state.current_project_id = None
        st.session_state.show_dashboard = True
        st.rerun()
    
    # Check for migration mode first (doesn't require sections)
    if st.session_state.view_mode == 'migration':
        st.header("🔄 Data Migration")
        create_migration_ui(db)
    else:
        sections = db.get_sections_by_project(st.session_state.current_project_id)
        
        if not sections:
            # No sections yet - show upload interface
            st.header(f"📖 {project.name}")
            st.info("No sections yet. Upload your learning material to get started!")
            render_content_upload_new(db, st.session_state.current_project_id)
        
        else:
            # We have sections - show main interface
            if st.session_state.view_mode == 'study':
                # Study mode
                render_study_mode(db, st.session_state.current_project_id)
            
            elif st.session_state.view_mode == 'pecs':
                # PECS learning mode
                
                # Section navigator in sidebar
                render_section_navigator(
                    db, 
                    st.session_state.current_project_id,
                    st.session_state.current_section_id
                )
                
                # Get current section
                if st.session_state.current_section_id:
                    current_section = db.get_section(st.session_state.current_section_id)
                else:
                    # Default to first section
                    current_section = sections[0]
                    st.session_state.current_section_id = current_section.id
                
                if current_section:
                    # Render PECS tabs
                    render_pecs_phases(db, current_section)
                else:
                    st.error("Section not found. Please select a different section.")
        
        # Additional options
        st.sidebar.markdown("---")
        st.sidebar.subheader("Project Actions")
        
        if st.sidebar.button("➕ Add More Content"):
            render_content_upload(db, st.session_state.current_project_id)
        
        if st.sidebar.button("📊 View Statistics"):
            stats = db.get_project_stats(st.session_state.current_project_id)
            st.sidebar.json(stats)

