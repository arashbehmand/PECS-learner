import json
import streamlit as st
from typing import Dict, Any, Optional

def export_session_to_json() -> str:
    """
    Export relevant session state data to a JSON string.
    
    Returns:
        str: JSON string containing the session data
    """
    # Define the keys we want to export
    export_keys = [
        'raw_material',
        'chunks',
        'chunk_data',
        'all_recall_prompts',
        'current_chunk_index',
        'current_pecs_phase'
    ]
    
    # Create export dictionary
    export_data = {}
    for key in export_keys:
        if key in st.session_state:
            export_data[key] = st.session_state[key]
    
    # Convert to JSON string
    return json.dumps(export_data, indent=2)

def import_session_from_json(json_str: str) -> bool:
    """
    Import session data from a JSON string.
    
    Args:
        json_str (str): JSON string containing the session data
        
    Returns:
        bool: True if import was successful, False otherwise
    """
    try:
        # Parse JSON string
        import_data = json.loads(json_str)
        
        # Validate required keys
        required_keys = ['raw_material', 'chunks', 'chunk_data']
        if not all(key in import_data for key in required_keys):
            st.error("Invalid session data: missing required fields")
            return False
        
        # Update session state
        for key, value in import_data.items():
            st.session_state[key] = value
        
        # Ensure material is marked as loaded
        st.session_state.material_loaded = True
        
        return True
        
    except json.JSONDecodeError:
        st.error("Invalid JSON format")
        return False
    except Exception as e:
        st.error(f"Error importing session: {str(e)}")
        return False

def get_session_summary() -> Dict[str, Any]:
    """
    Get a summary of the current session state.
    
    Returns:
        Dict[str, Any]: Dictionary containing session summary
    """
    return {
        'total_chunks': len(st.session_state.chunks),
        'completed_chunks': sum(1 for chunk_idx in st.session_state.chunk_data 
                              if st.session_state.chunk_data[chunk_idx].get('completed', False)),
        'total_flashcards': len(st.session_state.all_recall_prompts),
        'current_phase': st.session_state.current_pecs_phase,
        'current_chunk': st.session_state.current_chunk_index + 1
    } 