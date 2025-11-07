import streamlit as st
from utils.llm_service import LLMService

def render_challenge_phase(chunk_text: str, chunk_idx: int):
    """
    Render the Challenge & Connect phase UI and handle user interactions.
    
    Args:
        chunk_text (str): The text content of the current chunk
        chunk_idx (int): The index of the current chunk
    """
    st.header("C - Challenge & Connect")
    st.markdown("""
    Now it's time to think critically about what you've learned and connect it
    to other knowledge and experiences. Challenge your understanding and make
    meaningful connections.
    """)
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Get existing data
    existing_data = st.session_state.chunk_data.get(chunk_idx, {}).get('challenge_connect', {})
    
    # Display the user's explanation from the Engage phase
    engage_data = st.session_state.chunk_data.get(chunk_idx, {}).get('engage_explain', {})
    if engage_data and 'explanation' in engage_data:
        st.subheader("Your Explanation:")
        st.text_area(
            "From the Engage phase:",
            value=engage_data['explanation'],
            height=150,
            disabled=True
        )
    
    # Critical thinking
    st.subheader("Critical Thinking")
    st.markdown("""
    Consider these prompts while analyzing the material:
    - Why is this true?
    - What are the underlying assumptions?
    - Are there any exceptions or limitations?
    - How could this be applied differently?
    """)
    
    critical_analysis = st.text_area(
        "My Challenges & Critical Questions",
        key=f"challenge_analysis_{chunk_idx}",
        height=150
    )
    
    # Add AI feedback button for critical analysis
    if critical_analysis and st.button("Get AI Feedback on Critical Analysis", key=f"ai_critical_{chunk_idx}"):
        with st.spinner("Analyzing your critical thinking..."):
            feedback = llm_service.analyze_critical_thinking(chunk_text, critical_analysis)
            if feedback:
                st.info("AI Feedback:")
                st.write(feedback)
    
    # Connection prompts
    st.subheader("Making Connections")
    st.markdown("""
    Consider how this material relates to:
    - Other topics you've learned
    - Real-world applications
    - Your personal experiences
    - Broader concepts or theories
    """)
    
    connections = st.text_area(
        "How does this relate to other topics/experiences?",
        key=f"challenge_connections_{chunk_idx}",
        height=150
    )
    
    # Add AI feedback button for connections
    if connections and st.button("Get AI Feedback on Connections", key=f"ai_connections_{chunk_idx}"):
        with st.spinner("Analyzing your connections..."):
            feedback = llm_service.analyze_connections(chunk_text, connections)
            if feedback:
                st.info("AI Feedback:")
                st.write(feedback)
    
    # New analogies
    st.subheader("New Analogies or Mental Models")
    new_analogies = st.text_area(
        "What new analogies or mental models help understand this?",
        key=f"challenge_analogies_{chunk_idx}",
        height=100
    )
    
    # Save button
    if st.button("Save Challenges & Proceed to Solidify"):
        # Save the data to session state
        if chunk_idx not in st.session_state.chunk_data:
            st.session_state.chunk_data[chunk_idx] = {}
        
        st.session_state.chunk_data[chunk_idx]['challenge_connect'] = {
            'critical_questions': critical_analysis,
            'connections': connections,
            'new_analogies': new_analogies
        }
        
        # Update the current phase
        st.session_state.current_pecs_phase = 'solidify'
        st.rerun() 