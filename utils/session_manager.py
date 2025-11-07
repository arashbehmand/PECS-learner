from typing import Dict, List, Optional, Any
import streamlit as st

def initialize_session_state():
    """Initialize all session state variables with default values."""
    if 'raw_material' not in st.session_state:
        st.session_state.raw_material = None
    
    if 'chunks' not in st.session_state:
        st.session_state.chunks = []
    
    if 'current_chunk_index' not in st.session_state:
        st.session_state.current_chunk_index = 0
    
    if 'chunk_data' not in st.session_state:
        st.session_state.chunk_data = {}
    
    if 'all_recall_prompts' not in st.session_state:
        st.session_state.all_recall_prompts = []
    
    if 'material_loaded' not in st.session_state:
        st.session_state.material_loaded = False
    
    if 'current_pecs_phase' not in st.session_state:
        st.session_state.current_pecs_phase = "import"

def save_chunk_progress(chunk_idx: int, phase: str, data: Dict[str, Any]):
    """Save progress data for a specific chunk and phase."""
    if chunk_idx not in st.session_state.chunk_data:
        st.session_state.chunk_data[chunk_idx] = {}
    
    st.session_state.chunk_data[chunk_idx][phase] = data 