"""
Section navigator component for browsing sections within a project.
"""
import streamlit as st
from utils.database import DatabaseRepository
from utils.models import Section


def render_section_navigator(db: DatabaseRepository, project_id: int, current_section_id: int = None):
    """
    Render the section navigation sidebar.
    
    Args:
        db: DatabaseRepository instance
        project_id: ID of the current project
        current_section_id: ID of the currently selected section
    """
    st.sidebar.header("📑 Sections")
    
    # Get all sections
    sections = db.get_sections_by_project(project_id)
    
    if not sections:
        st.sidebar.info("No sections yet. Upload content to get started.")
        return
    
    # Search functionality
    search_query = st.sidebar.text_input("🔍 Search sections...", key="section_search")
    
    # Filter sections based on search
    filtered_sections = sections
    if search_query:
        search_lower = search_query.lower()
        filtered_sections = [
            s for s in sections
            if search_lower in (s.title or "").lower() or search_lower in s.content.lower()[:200]
        ]
    
    # Pagination for large number of sections
    sections_per_page = 20
    if len(filtered_sections) > sections_per_page:
        page_num = st.sidebar.number_input(
            "Page:",
            min_value=1,
            max_value=(len(filtered_sections) - 1) // sections_per_page + 1,
            value=1,
            key="section_page"
        )
        start_idx = (page_num - 1) * sections_per_page
        end_idx = start_idx + sections_per_page
        display_sections = filtered_sections[start_idx:end_idx]
    else:
        display_sections = filtered_sections
    
    # Display sections
    st.sidebar.markdown(f"**{len(filtered_sections)} sections**")
    
    for section in display_sections:
        # Create section label
        section_label = section.title or f"Section {section.order_index + 1}"
        
        # Add completion indicator
        if section.is_completed:
            section_label = f"✓ {section_label}"
        
        # Display section with selection
        if section.id == current_section_id:
            st.sidebar.markdown(f"**▶ {section_label}**")
        else:
            if st.sidebar.button(
                section_label,
                key=f"section_{section.id}",
                use_container_width=True
            ):
                st.session_state.current_section_id = section.id
                st.rerun()
        
        # Show preview of section content
        if section.id == current_section_id:
            preview = section.content[:100] + "..." if len(section.content) > 100 else section.content
            st.sidebar.caption(preview)

