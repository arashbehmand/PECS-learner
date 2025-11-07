"""
Project Dashboard component for viewing and managing study projects.
"""
import streamlit as st
from utils.database import DatabaseRepository
from utils.models import Project


def render_project_dashboard(db: DatabaseRepository):
    """
    Render the project dashboard where users can view, create, and select projects.
    
    Args:
        db: DatabaseRepository instance
    """
    st.header("📚 My Study Projects")
    st.markdown("---")
    
    # Get all projects
    projects = db.get_all_projects()
    
    # Create new project section
    with st.expander("➕ Create New Project", expanded=False):
        new_project_name = st.text_input("Project Name:", key="new_project_name")
        if st.button("Create Project", key="create_project_btn"):
            if new_project_name.strip():
                project = db.create_project(new_project_name.strip())
                if project:
                    st.success(f"Project '{project.name}' created successfully!")
                    st.rerun()
                else:
                    st.error("A project with this name already exists. Please choose a different name.")
            else:
                st.warning("Please enter a project name.")
    
    st.markdown("---")
    
    # Display existing projects
    if not projects:
        st.info("""
        👋 **Welcome to P.E.C.S. Learning System!**
        
        You don't have any projects yet. Create your first project above to get started.
        
        **What is P.E.C.S.?**
        - **P**rime & Preview: Skim and prepare
        - **E**ngage & Explain: Deep reading and understanding
        - **C**hallenge & Connect: Critical thinking and connections
        - **S**olidify & Space: Review and spaced repetition
        """)
        return
    
    st.subheader(f"Your Projects ({len(projects)})")
    
    # Display projects in a grid
    cols_per_row = 2
    project_cols = st.columns(cols_per_row)
    
    for idx, project in enumerate(projects):
        col_idx = idx % cols_per_row
        with project_cols[col_idx]:
            with st.container():
                # Get project statistics
                stats = db.get_project_stats(project.id)
                sections = db.get_sections_by_project(project.id)
                
                # Project card
                st.markdown(f"### 📖 {project.name}")
                
                # Project metadata
                st.caption(f"Created: {project.created_at.strftime('%Y-%m-%d') if project.created_at else 'N/A'}")
                
                # Statistics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Sections", f"{stats.get('total_sections', len(sections))}")
                    st.metric("Completed", f"{stats.get('completed_sections', 0)}")
                
                with col2:
                    st.metric("Flashcards", f"{stats.get('total_flashcards', 0)}")
                    due_review = stats.get('cards_due_for_review', 0)
                    if due_review > 0:
                        st.metric("Due for Review", due_review, delta=None)
                
                # Action buttons
                button_col1, button_col2 = st.columns(2)
                with button_col1:
                    if st.button("📖 Open Project", key=f"open_{project.id}", use_container_width=True):
                        st.session_state.current_project_id = project.id
                        st.session_state.show_dashboard = False
                        st.rerun()
                
                with button_col2:
                    if st.button("🗑️ Delete", key=f"delete_{project.id}", use_container_width=True):
                        if db.delete_project(project.id):
                            st.success(f"Project '{project.name}' deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to delete project.")
                
                st.markdown("---")
    
    # If we have an odd number of projects, fill the last column
    # (Already handled by the loop, no additional action needed)

