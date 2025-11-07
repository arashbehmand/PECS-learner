import streamlit as st
from utils.llm_service import LLMService

def render_engage_phase(chunk_text: str, chunk_idx: int):
    """
    Render the Engage & Explain phase UI and handle user interactions.
    
    Args:
        chunk_text (str): The text content of the current chunk
        chunk_idx (int): The index of the current chunk
    """
    st.header("E - Engage & Explain")
    st.markdown("""
    Now, read through the material carefully. Try to understand the core concepts
    and explain them in your own words. Focus on clarity and simplicity.
    """)
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Initialize show_material in session state if not present
    if 'show_engage_material' not in st.session_state:
        st.session_state.show_engage_material = True
    
    # Toggle button for showing/hiding material
    if st.button("Hide/Show Material Chunk"):
        st.session_state.show_engage_material = not st.session_state.show_engage_material
    
    # Display the chunk text if it should be shown
    if st.session_state.show_engage_material:
        st.text_area(
            "Material to Review:",
            value=chunk_text,
            height=200,
            disabled=True
        )
    
    # Get existing explanation if any
    existing_data = st.session_state.chunk_data.get(chunk_idx, {}).get('engage_explain', {})
    
    # Explanation text area
    explanation = st.text_area(
        "Explain the core concepts in your own words...",
        value=existing_data.get('explanation', ''),
        height=200
    )
    
    # Add AI feedback button for explanation
    if explanation and st.button("Get AI Feedback on Explanation", key=f"ai_explanation_{chunk_idx}"):
        with st.spinner("Analyzing your explanation..."):
            feedback = llm_service.analyze_explanation(chunk_text, explanation)
            if feedback:
                st.info("AI Feedback:")
                st.write(feedback)
    
    # Self-correction prompts
    st.markdown("""
    **Self-Correction Prompts:**
    - Can you simplify this further?
    - Are you using any jargon that could be explained more clearly?
    - Have you captured the main ideas?
    - Could someone new to this topic understand your explanation?
    """)
    
    # Optional analogy input
    analogy = st.text_area(
        "Optional: Create an analogy to help understand this concept",
        value=existing_data.get('analogy', ''),
        height=100
    )
    
    # Add AI feedback button for analogy
    if analogy and st.button("Get AI Feedback on Analogy", key=f"ai_analogy_{chunk_idx}"):
        with st.spinner("Analyzing your analogy..."):
            feedback = llm_service.analyze_analogy(chunk_text, analogy)
            if feedback:
                st.info("AI Feedback:")
                st.write(feedback)
    
    # Save button
    if st.button("Save Explanation & Proceed to Challenge"):
        # Save the data to session state
        if chunk_idx not in st.session_state.chunk_data:
            st.session_state.chunk_data[chunk_idx] = {}
        
        st.session_state.chunk_data[chunk_idx]['engage_explain'] = {
            'explanation': explanation,
            'analogy': analogy
        }
        
        # Update the current phase
        st.session_state.current_pecs_phase = 'challenge'
        st.rerun() 