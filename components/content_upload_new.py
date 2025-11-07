"""
Content upload component for creating new projects with hierarchical content processing.
"""
import os
import streamlit as st
from utils.content_processor import load_text_from_input
from utils.hierarchical_processor import create_sections_from_text
from utils.database import DatabaseRepository
from utils.file_converters import convert_file_to_text, is_supported_file_type, get_file_type_description


def render_content_upload(db: DatabaseRepository, project_id: int):
    """
    Render the content upload interface for a project.
    
    Args:
        db: DatabaseRepository instance
        project_id: ID of the project to add content to
    """
    st.header("📥 Import Learning Material")
    st.markdown("""
    Upload or paste your learning material. The system will automatically detect chapters
    and sections, or you can configure how the content is organized.
    """)
    
    # Check if project already has sections
    existing_sections = db.get_sections_by_project(project_id)
    if existing_sections:
        st.warning(f"⚠️ This project already has {len(existing_sections)} sections. Adding new content will append to the project.")
        if st.button("Clear Existing Sections", key="clear_sections"):
            # Note: This would require a delete_sections method
            st.info("Feature coming soon. For now, delete and recreate the project.")
    
    # Text input options
    input_method = st.radio(
        "Choose input method:",
        ["Paste Text", "Upload File"],
        horizontal=True
    )
    
    text_content = ""
    if input_method == "Paste Text":
        text_content = st.text_area(
            "Paste your learning material here:",
            height=300,
            help="Paste the text you want to learn from. The system will detect chapters and sections automatically."
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload a file:",
            type=['txt', 'md', 'epub', 'pdf', 'docx', 'doc'],
            help=get_file_type_description()
        )
        if uploaded_file is not None:
            try:
                # Check file extension
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                
                if file_ext in ['.txt', '.md']:
                    # Simple text files - decode directly
                    if file_ext == '.md':
                        text_content = uploaded_file.getvalue().decode('utf-8')
                    else:
                        text_content = load_text_from_input(uploaded_file=uploaded_file)
                elif file_ext in ['.epub', '.pdf', '.docx', '.doc']:
                    # Use markitdown for complex formats
                    st.info(f"📄 Converting {file_ext[1:].upper()} file to text... This may take a moment for large files.")
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        text_content = convert_file_to_text(uploaded_file)
                        if not text_content:
                            return  # Error already displayed by converter
                        st.success(f"✅ Successfully converted {uploaded_file.name} ({len(text_content):,} characters)")
                else:
                    st.error(f"Unsupported file type: {file_ext}")
                    return
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                import traceback
                st.debug(traceback.format_exc())
                return
    
    # Processing configuration
    st.subheader("⚙️ Processing Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        min_section_size = st.slider(
            "Minimum Section Size (characters):",
            min_value=200,
            max_value=2000,
            value=500,
            step=100,
            help="Minimum size for a section. Smaller sections will be merged."
        )
        
        max_section_size = st.slider(
            "Maximum Section Size (characters):",
            min_value=1000,
            max_value=10000,
            value=5000,
            step=500,
            help="Maximum size for a section. Larger sections will be split."
        )
    
    with col2:
        overlap = st.slider(
            "Overlap Between Sections (characters):",
            min_value=0,
            max_value=500,
            value=100,
            step=50,
            help="Character overlap when splitting large sections."
        )
        
        # Advanced options
        st.markdown("**Advanced Options:**")
        use_hierarchical = st.checkbox(
            "Enable hierarchical section detection",
            value=True,
            help="Automatically detect chapters, sections, and headings."
        )
    
    # Process button
    if st.button("🚀 Process & Create Sections", disabled=not text_content, type="primary"):
        if not text_content.strip():
            st.error("Please provide some text content to process.")
            return
        
        with st.spinner("Processing your material and detecting sections..."):
            try:
                # Process text into hierarchical sections
                sections = create_sections_from_text(
                    text_content,
                    min_section_size=min_section_size,
                    max_section_size=max_section_size,
                    overlap=overlap
                )
                
                if not sections:
                    st.error("No valid sections could be created from the provided text.")
                    return
                
                # Save sections to database
                created_count = 0
                start_index = len(existing_sections)  # Continue from existing sections
                
                for order_idx, (content, title) in enumerate(sections):
                    section = db.create_section(
                        project_id=project_id,
                        content=content,
                        title=title,
                        order_index=start_index + order_idx
                    )
                    if section:
                        created_count += 1
                
                if created_count > 0:
                    st.success(f"✅ Successfully created {created_count} sections!")
                    
                    # Show preview
                    with st.expander("📋 Section Preview", expanded=True):
                        preview_sections = db.get_sections_by_project(project_id)
                        for i, section in enumerate(preview_sections[-created_count:], 1):
                            preview_title = section.title or f"Section {section.order_index + 1}"
                            st.markdown(f"**{preview_title}** ({len(section.content)} chars)")
                    
                    st.info(f"🎯 You can now navigate to any section and start your P.E.C.S. learning cycle!")
                    st.rerun()
                else:
                    st.error("Failed to create sections. Please try again.")
                    
            except Exception as e:
                st.error(f"An error occurred while processing the text: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

