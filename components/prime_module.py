import streamlit as st
from utils.llm_service import LLMService

def render_prime_phase(chunk_text: str, chunk_idx: int):
    """
    Render the Prime & Preview phase UI and handle user interactions.
    
    Args:
        chunk_text (str): The text content of the current chunk
        chunk_idx (int): The index of the current chunk
    """
    st.header("P - Prime & Preview")
    st.markdown("""
    Take a moment to skim through this section and prepare for deeper reading.
    """)
    
    # Display the chunk text in a read-only text area
    st.text_area(
        "Material to Review:",
        value=chunk_text,
        height=200,
        disabled=True
    )
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Section understanding
    st.markdown("#### What is this section generally about?")
    section_understanding = st.text_area(
        "Share your initial understanding",
        key=f"prime_section_{chunk_idx}",
        height=100
    )
    
    # Add AI feedback button for section understanding
    if section_understanding and st.button("Get AI Feedback on Understanding", key=f"ai_section_{chunk_idx}"):
        with st.spinner("Analyzing your understanding..."):
            feedback = llm_service.analyze_section_understanding(chunk_text, section_understanding)
            if feedback:
                st.info("AI Feedback:")
                st.write(feedback)
    
    # Prior knowledge
    st.markdown("#### What do I already know (or think I know) about this topic?")
    prior_knowledge = st.text_area(
        "Share your prior knowledge",
        key=f"prime_knowledge_{chunk_idx}",
        height=100
    )
    
    # Questions
    st.markdown("#### What questions do I have, or what do I hope to understand by the end?")
    questions = st.text_area(
        "Share your questions",
        key=f"prime_questions_{chunk_idx}",
        height=100
    )
    
    # Add AI feedback button for questions
    if questions and st.button("Get AI Feedback on Questions", key=f"ai_questions_{chunk_idx}"):
        with st.spinner("Analyzing your questions..."):
            feedback = llm_service.analyze_questions(chunk_text, questions)
            if feedback:
                st.info("AI Feedback:")
                st.write(feedback)
    
    # Save button
    if st.button("Save Priming & Proceed to Engage"):
        # Save the data to session state
        if chunk_idx not in st.session_state.chunk_data:
            st.session_state.chunk_data[chunk_idx] = {}
        
        st.session_state.chunk_data[chunk_idx]['prime_preview'] = {
            'initial_thoughts': section_understanding,
            'prior_knowledge': prior_knowledge,
            'questions': questions
        }
        
        # Update the current phase
        st.session_state.current_pecs_phase = 'engage'
        st.rerun() 