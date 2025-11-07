import streamlit as st
from utils.content_processor import load_text_from_input, chunk_text_content

def render_content_upload():
    """Render the content upload and chunking interface."""
    st.header("Import Your Learning Material")
    
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
            height=200,
            help="Paste the text you want to learn from."
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload a text file:",
            type=['txt'],
            help="Upload a .txt file containing your learning material."
        )
        if uploaded_file is not None:
            try:
                text_content = load_text_from_input(uploaded_file=uploaded_file)
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                return
    
    # Chunking configuration
    st.subheader("Configure Text Chunking")
    col1, col2 = st.columns(2)
    
    with col1:
        chunk_size = st.slider(
            "Chunk Size (characters):",
            min_value=500,
            max_value=5000,
            value=1500,
            step=100,
            help="Size of each text chunk in characters."
        )
    
    with col2:
        chunk_overlap = st.slider(
            "Chunk Overlap (characters):",
            min_value=0,
            max_value=500,
            value=100,
            step=50,
            help="Number of characters to overlap between chunks."
        )
    
    # Process button
    if st.button("Process & Chunk Material", disabled=not text_content):
        if not text_content.strip():
            st.error("Please provide some text content to process.")
            return
            
        with st.spinner("Processing your material..."):
            try:
                # Load and chunk the text
                raw_text = load_text_from_input(pasted_text=text_content)
                chunks = chunk_text_content(raw_text, chunk_size, chunk_overlap)
                
                if not chunks:
                    st.error("No valid chunks could be created from the provided text.")
                    return
                
                # Update session state
                st.session_state.raw_material = raw_text
                st.session_state.chunks = chunks
                st.session_state.material_loaded = True
                st.session_state.current_pecs_phase = "prime"
                st.session_state.current_chunk_index = 0
                
                st.success(f"Material processed into {len(chunks)} chunks!")
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred while processing the text: {str(e)}") 