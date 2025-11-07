import streamlit as st
from utils.llm_service import LLMService
from typing import Dict, Any, List

def render_solidify_phase(chunk_text: str, chunk_idx: int):
    """
    Render the Solidify & Space phase UI and handle user interactions.
    
    Args:
        chunk_text (str): The text content of the current chunk
        chunk_idx (int): The index of the current chunk
    """
    st.header("S - Solidify & Space")
    st.markdown("""
    Now it's time to reinforce your learning and create tools for spaced repetition.
    Create flashcards and think about how you can apply this knowledge.
    """)
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Get existing data
    existing_data = st.session_state.chunk_data.get(chunk_idx, {}).get('solidify_space', {})
    
    # Show previous notes in an expander
    with st.expander("View Previous Notes"):
        # Show explanation from Engage phase
        engage_data = st.session_state.chunk_data.get(chunk_idx, {}).get('engage_explain', {})
        if engage_data and 'explanation' in engage_data:
            st.subheader("Your Explanation:")
            st.text(engage_data['explanation'])
        
        # Show challenges from Challenge phase
        challenge_data = st.session_state.chunk_data.get(chunk_idx, {}).get('challenge_connect', {})
        if challenge_data and 'critical_questions' in challenge_data:
            st.subheader("Your Challenges:")
            st.text(challenge_data['critical_questions'])
    
    # Option to show original material
    show_original = st.checkbox("Show original material for targeted review")
    if show_original:
        st.text_area(
            "Original Material:",
            value=chunk_text,
            height=200,
            disabled=True
        )
    
    # Flashcard creation interface
    st.subheader("Create Flashcards")
    
    # Initialize flashcard list in session state if not present
    if 'current_flashcards' not in st.session_state:
        st.session_state.current_flashcards = existing_data.get('recall_prompts', [])
    
    # AI Flashcard Suggestions
    if engage_data and 'explanation' in engage_data:
        st.markdown("---")
        st.markdown("### AI Flashcard Assistant")
        st.markdown("""
        Get AI suggestions for flashcards based on your explanation and challenges.
        You can use these as inspiration for your own flashcards.
        """)
        
        if st.button("Suggest Flashcard Q/A (AI)"):
            if llm_service.is_available():
                with st.spinner("Generating flashcard suggestions..."):
                    suggestions = llm_service.suggest_flashcards(
                        chunk_text=chunk_text,
                        user_explanation=engage_data['explanation'],
                        user_challenges=challenge_data.get('critical_questions', '') if challenge_data else ''
                    )
                    
                    if suggestions:
                        st.info("**AI Suggestions:**")
                        for i, suggestion in enumerate(suggestions, 1):
                            with st.expander(f"Suggestion {i}"):
                                st.markdown(f"**Q:** {suggestion['question']}")
                                st.markdown(f"**A:** {suggestion['answer']}")
                                
                                # Add a button to use this suggestion
                                if st.button(f"Use Suggestion {i}", key=f"use_suggestion_{i}"):
                                    st.session_state.suggested_question = suggestion['question']
                                    st.session_state.suggested_answer = suggestion['answer']
                                    st.rerun()
                    else:
                        st.warning("Unable to generate flashcard suggestions at this time.")
            else:
                st.warning("AI flashcard suggestions are currently unavailable. Please create your own flashcards.")
    
    # Flashcard input fields
    question = st.text_input(
        "Question/Prompt:",
        value=st.session_state.get('suggested_question', '')
    )
    answer = st.text_area(
        "Answer/Key Idea:",
        value=st.session_state.get('suggested_answer', ''),
        height=100
    )
    
    # Clear suggested values after displaying them
    if 'suggested_question' in st.session_state:
        del st.session_state.suggested_question
    if 'suggested_answer' in st.session_state:
        del st.session_state.suggested_answer
    
    # Add flashcard button
    if st.button("Add to My Recall List"):
        if question and answer:  # Only add if both fields are filled
            new_card = {
                'question': question,
                'answer': answer,
                'chunk_idx': chunk_idx
            }
            st.session_state.current_flashcards.append(new_card)
            
            # Also add to global recall list
            if 'all_recall_prompts' not in st.session_state:
                st.session_state.all_recall_prompts = []
            st.session_state.all_recall_prompts.append(new_card)
            
            st.success("Flashcard added!")
            st.rerun()
    
    # Display current chunk's flashcards
    if st.session_state.current_flashcards:
        st.subheader("Your Flashcards for This Chunk:")
        for i, card in enumerate(st.session_state.current_flashcards):
            with st.expander(f"Card {i+1}: {card['question']}"):
                st.text(card['answer'])
    
    # Add AI feedback button for flashcards
    if st.session_state.current_flashcards and st.button("Get AI Feedback on Flashcards", key=f"ai_flashcards_{chunk_idx}"):
        with st.spinner("Analyzing your flashcards..."):
            feedback = llm_service.analyze_flashcards(chunk_text, st.session_state.current_flashcards)
            if feedback:
                st.info("AI Feedback:")
                st.write(feedback)
    
    # Application of knowledge
    st.subheader("Application")
    application = st.text_area(
        "How can you apply this knowledge?",
        value=existing_data.get('application', ''),
        height=100
    )
    
    # Add AI feedback button for application
    if application and st.button("Get AI Feedback on Application", key=f"ai_application_{chunk_idx}"):
        with st.spinner("Analyzing your application ideas..."):
            feedback = llm_service.analyze_application(chunk_text, application)
            if feedback:
                st.info("AI Feedback:")
                st.write(feedback)
    
    # Spaced repetition information
    st.markdown("""
    **About Spaced Repetition:**
    - Review these flashcards at increasing intervals
    - Start with daily review, then every few days, then weekly
    - Focus on understanding, not just memorization
    - Use the questions to test your recall and understanding
    """)
    
    # Complete button
    if st.button("Chunk Cycle Complete!"):
        # Save the data to session state
        if chunk_idx not in st.session_state.chunk_data:
            st.session_state.chunk_data[chunk_idx] = {}
        
        st.session_state.chunk_data[chunk_idx]['solidify_space'] = {
            'recall_prompts': st.session_state.current_flashcards,
            'application': application
        }
        
        # Mark chunk as completed
        st.session_state.chunk_data[chunk_idx]['completed'] = True
        
        # Show celebration
        st.balloons()
        st.success("Congratulations! You've completed this chunk's P.E.C.S. cycle!")
        
        # Offer to proceed to next chunk or review recall list
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Proceed to Next Chunk"):
                if chunk_idx < len(st.session_state.chunks) - 1:
                    # Reset phase and move to next chunk
                    st.session_state.current_chunk_index = chunk_idx + 1
                    st.session_state.current_pecs_phase = 'prime'
                    # Clear current flashcards for the new chunk
                    if 'current_flashcards' in st.session_state:
                        del st.session_state.current_flashcards
                    st.rerun()
                else:
                    st.info("This was the last chunk!")
        
        with col2:
            if st.button("Review My Recall List"):
                st.session_state.show_recall_list = True
                st.rerun() 