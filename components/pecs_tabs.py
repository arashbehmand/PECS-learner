"""
Unified PECS module with tabs for all four phases.
This replaces the individual phase modules with a tabbed interface.
"""
import streamlit as st
from utils.llm_service import LLMService
from utils.database import DatabaseRepository
from utils.models import Section


def render_pecs_phases(db: DatabaseRepository, section: Section):
    """
    Render all PECS phases in a tabbed interface with auto-save.
    
    Args:
        db: DatabaseRepository instance
        section: The Section object to work with
    """
    st.header(f"📖 {section.title or f'Section {section.order_index + 1}'}")
    
    # Initialize PECS data if not present
    if section.pecs_data is None:
        section.pecs_data = {}
    
    # Create tabs for each phase
    tab1, tab2, tab3, tab4 = st.tabs(["P - Prime & Preview", "E - Engage & Explain", "C - Challenge & Connect", "S - Solidify & Space"])
    
    llm_service = LLMService()
    
    # ===== PRIME PHASE =====
    with tab1:
        st.markdown("""
        Take a moment to skim through this section and prepare for deeper reading.
        """)
        
        # Display section content
        st.text_area(
            "Material to Review:",
            value=section.content,
            height=200,
            disabled=True,
            key=f"prime_content_{section.id}"
        )
        
        # Get existing prime data
        prime_data = section.pecs_data.get('prime_preview', {})
        
        # Section understanding
        st.markdown("#### What is this section generally about?")
        section_understanding = st.text_area(
            "Share your initial understanding",
            value=prime_data.get('initial_thoughts', ''),
            height=100,
            key=f"prime_section_{section.id}"
        )
        
        # Auto-save button (triggered on rerun)
        if st.button("💾 Auto-save", key=f"autosave_prime_thoughts_{section.id}"):
            _save_pecs_phase(db, section.id, 'prime_preview', {
                'initial_thoughts': section_understanding,
                'prior_knowledge': prime_data.get('prior_knowledge', ''),
                'questions': prime_data.get('questions', '')
            })
            st.success("Saved!")
        
        # AI feedback button
        if section_understanding and st.button("Get AI Feedback on Understanding", key=f"ai_section_{section.id}"):
            with st.spinner("Analyzing your understanding..."):
                feedback = llm_service.analyze_section_understanding(section.content, section_understanding)
                if feedback:
                    st.info("AI Feedback:")
                    st.write(feedback)
        
        # Prior knowledge
        st.markdown("#### What do I already know (or think I know) about this topic?")
        prior_knowledge = st.text_area(
            "Share your prior knowledge",
            value=prime_data.get('prior_knowledge', ''),
            height=100,
            key=f"prime_knowledge_{section.id}"
        )
        
        if st.button("💾 Auto-save", key=f"autosave_prime_knowledge_{section.id}"):
            _save_pecs_phase(db, section.id, 'prime_preview', {
                'initial_thoughts': prime_data.get('initial_thoughts', ''),
                'prior_knowledge': prior_knowledge,
                'questions': prime_data.get('questions', '')
            })
            st.success("Saved!")
        
        # Questions
        st.markdown("#### What questions do I have, or what do I hope to understand by the end?")
        questions = st.text_area(
            "Share your questions",
            value=prime_data.get('questions', ''),
            height=100,
            key=f"prime_questions_{section.id}"
        )
        
        if st.button("💾 Auto-save", key=f"autosave_prime_questions_{section.id}"):
            _save_pecs_phase(db, section.id, 'prime_preview', {
                'initial_thoughts': prime_data.get('initial_thoughts', ''),
                'prior_knowledge': prime_data.get('prior_knowledge', ''),
                'questions': questions
            })
            st.success("Saved!")
        
        # AI feedback button for questions
        if questions and st.button("Get AI Feedback on Questions", key=f"ai_questions_{section.id}"):
            with st.spinner("Analyzing your questions..."):
                feedback = llm_service.analyze_questions(section.content, questions)
                if feedback:
                    st.info("AI Feedback:")
                    st.write(feedback)
    
    # ===== ENGAGE PHASE =====
    with tab2:
        st.markdown("""
        Now, read through the material carefully. Try to understand the core concepts
        and explain them in your own words. Focus on clarity and simplicity.
        """)
        
        # Toggle for showing material
        if 'show_engage_material' not in st.session_state:
            st.session_state.show_engage_material = True
        
        if st.button("Hide/Show Material"):
            st.session_state.show_engage_material = not st.session_state.show_engage_material
        
        if st.session_state.show_engage_material:
            st.text_area(
                "Material to Review:",
                value=section.content,
                height=200,
                disabled=True,
                key=f"engage_content_{section.id}"
            )
        
        # Get existing engage data
        engage_data = section.pecs_data.get('engage_explain', {})
        
        # Explanation
        explanation = st.text_area(
            "Explain the core concepts in your own words...",
            value=engage_data.get('explanation', ''),
            height=200,
            key=f"engage_explanation_{section.id}"
        )
        
        if st.button("💾 Auto-save", key=f"autosave_engage_explanation_{section.id}"):
            _save_pecs_phase(db, section.id, 'engage_explain', {
                'explanation': explanation,
                'analogy': engage_data.get('analogy', '')
            })
            st.success("Saved!")
        
        # AI feedback
        if explanation and st.button("Get AI Feedback on Explanation", key=f"ai_explanation_{section.id}"):
            with st.spinner("Analyzing your explanation..."):
                feedback = llm_service.analyze_explanation(section.content, explanation)
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
        
        # Analogy
        analogy = st.text_area(
            "Optional: Create an analogy to help understand this concept",
            value=engage_data.get('analogy', ''),
            height=100,
            key=f"engage_analogy_{section.id}"
        )
        
        if st.button("💾 Auto-save", key=f"autosave_engage_analogy_{section.id}"):
            _save_pecs_phase(db, section.id, 'engage_explain', {
                'explanation': engage_data.get('explanation', ''),
                'analogy': analogy
            })
            st.success("Saved!")
        
        # AI feedback for analogy
        if analogy and st.button("Get AI Feedback on Analogy", key=f"ai_analogy_{section.id}"):
            with st.spinner("Analyzing your analogy..."):
                feedback = llm_service.analyze_analogy(section.content, analogy)
                if feedback:
                    st.info("AI Feedback:")
                    st.write(feedback)
    
    # ===== CHALLENGE PHASE =====
    with tab3:
        st.markdown("""
        Now it's time to think critically about what you've learned and connect it
        to other knowledge and experiences. Challenge your understanding and make
        meaningful connections.
        """)
        
        # Show explanation from Engage phase
        engage_data = section.pecs_data.get('engage_explain', {})
        if engage_data and 'explanation' in engage_data:
            st.subheader("Your Explanation:")
            st.text_area(
                "From the Engage phase:",
                value=engage_data['explanation'],
                height=150,
                disabled=True,
                key=f"challenge_prev_explanation_{section.id}"
            )
        
        # Get existing challenge data
        challenge_data = section.pecs_data.get('challenge_connect', {})
        
        # Critical thinking
        st.subheader("Critical Thinking")
        st.markdown("""
        Consider these prompts while analyzing the material:
        - Why is this true?
        - What are the underlying assumptions?
        - Are there any exceptions or limitations?
        - How could this be applied differently?
        """)
        
        critical_questions = st.text_area(
            "My Challenges & Critical Questions",
            value=challenge_data.get('critical_questions', ''),
            height=150,
            key=f"challenge_critical_{section.id}"
        )
        
        if st.button("💾 Auto-save", key=f"autosave_challenge_critical_{section.id}"):
            _save_pecs_phase(db, section.id, 'challenge_connect', {
                'critical_questions': critical_questions,
                'connections': challenge_data.get('connections', ''),
                'new_analogies': challenge_data.get('new_analogies', '')
            })
            st.success("Saved!")
        
        # AI feedback
        if critical_questions and st.button("Get AI Feedback on Critical Analysis", key=f"ai_critical_{section.id}"):
            with st.spinner("Analyzing your critical thinking..."):
                feedback = llm_service.analyze_critical_thinking(section.content, critical_questions)
                if feedback:
                    st.info("AI Feedback:")
                    st.write(feedback)
        
        # Connections
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
            value=challenge_data.get('connections', ''),
            height=150,
            key=f"challenge_connections_{section.id}"
        )
        
        if st.button("💾 Auto-save", key=f"autosave_challenge_connections_{section.id}"):
            _save_pecs_phase(db, section.id, 'challenge_connect', {
                'critical_questions': challenge_data.get('critical_questions', ''),
                'connections': connections,
                'new_analogies': challenge_data.get('new_analogies', '')
            })
            st.success("Saved!")
        
        # AI feedback
        if connections and st.button("Get AI Feedback on Connections", key=f"ai_connections_{section.id}"):
            with st.spinner("Analyzing your connections..."):
                feedback = llm_service.analyze_connections(section.content, connections)
                if feedback:
                    st.info("AI Feedback:")
                    st.write(feedback)
        
        # New analogies
        st.subheader("New Analogies or Mental Models")
        new_analogies = st.text_area(
            "What new analogies or mental models help understand this?",
            value=challenge_data.get('new_analogies', ''),
            height=100,
            key=f"challenge_analogies_{section.id}"
        )
        
        if st.button("💾 Auto-save", key=f"autosave_challenge_analogies_{section.id}"):
            _save_pecs_phase(db, section.id, 'challenge_connect', {
                'critical_questions': challenge_data.get('critical_questions', ''),
                'connections': challenge_data.get('connections', ''),
                'new_analogies': new_analogies
            })
            st.success("Saved!")
    
    # ===== SOLIDIFY PHASE =====
    with tab4:
        st.markdown("""
        Now it's time to reinforce your learning and create tools for spaced repetition.
        Create flashcards and think about how you can apply this knowledge.
        """)
        
        # Show previous notes
        with st.expander("View Previous Notes"):
            if engage_data and 'explanation' in engage_data:
                st.subheader("Your Explanation:")
                st.text(engage_data['explanation'])
            
            challenge_data = section.pecs_data.get('challenge_connect', {})
            if challenge_data and 'critical_questions' in challenge_data:
                st.subheader("Your Challenges:")
                st.text(challenge_data['critical_questions'])
        
        # Show original material option
        show_original = st.checkbox("Show original material for targeted review", key=f"show_original_{section.id}")
        if show_original:
            st.text_area(
                "Original Material:",
                value=section.content,
                height=200,
                disabled=True,
                key=f"solidify_content_{section.id}"
            )
        
        # Get existing solidify data
        solidify_data = section.pecs_data.get('solidify_space', {})
        
        # Flashcard creation
        st.subheader("Create Flashcards")
        
        # Get existing flashcards for this section
        section_flashcards = db.get_flashcards_by_project(section.project_id, section_id=section.id)
        
        # AI Flashcard Suggestions
        if engage_data and 'explanation' in engage_data:
            st.markdown("### AI Flashcard Assistant")
            if st.button("Suggest Flashcard Q/A (AI)", key=f"ai_suggest_flashcards_{section.id}"):
                if llm_service.is_available():
                    with st.spinner("Generating flashcard suggestions..."):
                        suggestions = llm_service.suggest_flashcards(
                            chunk_text=section.content,
                            user_explanation=engage_data['explanation'],
                            user_challenges=challenge_data.get('critical_questions', '') if challenge_data else ''
                        )
                        
                        if suggestions:
                            st.info("**AI Suggestions:**")
                            for i, suggestion in enumerate(suggestions, 1):
                                with st.expander(f"Suggestion {i}"):
                                    st.markdown(f"**Q:** {suggestion['question']}")
                                    st.markdown(f"**A:** {suggestion['answer']}")
                                    
                                    if st.button(f"Use Suggestion {i}", key=f"use_suggestion_{section.id}_{i}"):
                                        db.create_flashcard(
                                            project_id=section.project_id,
                                            question=suggestion['question'],
                                            answer=suggestion['answer'],
                                            section_id=section.id
                                        )
                                        st.success("Flashcard added!")
                                        st.rerun()
        
        # Flashcard input
        question = st.text_input("Question/Prompt:", key=f"flashcard_q_{section.id}")
        answer = st.text_area("Answer/Key Idea:", height=100, key=f"flashcard_a_{section.id}")
        
        if st.button("Add to My Recall List", key=f"add_flashcard_{section.id}"):
            if question and answer:
                flashcard = db.create_flashcard(
                    project_id=section.project_id,
                    question=question,
                    answer=answer,
                    section_id=section.id
                )
                if flashcard:
                    st.success("Flashcard added!")
                    st.rerun()
            else:
                st.warning("Please fill in both question and answer.")
        
        # Display current section's flashcards
        if section_flashcards:
            st.subheader(f"Your Flashcards ({len(section_flashcards)} cards)")
            for i, card in enumerate(section_flashcards, 1):
                with st.expander(f"Card {i}: {card.question}"):
                    st.text(card.answer)
                    if st.button(f"Delete", key=f"delete_card_{card.id}"):
                        db.delete_flashcard(card.id)
                        st.rerun()
        
        # AI feedback for flashcards
        if section_flashcards and st.button("Get AI Feedback on Flashcards", key=f"ai_flashcards_{section.id}"):
            with st.spinner("Analyzing your flashcards..."):
                flashcard_list = [{'question': c.question, 'answer': c.answer} for c in section_flashcards]
                feedback = llm_service.analyze_flashcards(section.content, flashcard_list)
                if feedback:
                    st.info("AI Feedback:")
                    st.write(feedback)
        
        # Application
        st.subheader("Application")
        application = st.text_area(
            "How can you apply this knowledge?",
            value=solidify_data.get('application', ''),
            height=100,
            key=f"solidify_application_{section.id}"
        )
        
        if st.button("💾 Auto-save", key=f"autosave_solidify_application_{section.id}"):
            _save_pecs_phase(db, section.id, 'solidify_space', {
                'application': application
            })
            st.success("Saved!")
        
        # AI feedback for application
        if application and st.button("Get AI Feedback on Application", key=f"ai_application_{section.id}"):
            with st.spinner("Analyzing your application ideas..."):
                feedback = llm_service.analyze_application(section.content, application)
                if feedback:
                    st.info("AI Feedback:")
                    st.write(feedback)
        
        # Spaced repetition info
        st.markdown("""
        **About Spaced Repetition:**
        - Review these flashcards at increasing intervals
        - Start with daily review, then every few days, then weekly
        - Focus on understanding, not just memorization
        """)
        
        # Complete button
        if st.button("✅ Mark Section as Complete", key=f"complete_{section.id}", type="primary"):
            db.mark_section_completed(section.id, completed=True)
            st.balloons()
            st.success("Congratulations! You've completed this section's P.E.C.S. cycle!")
            st.rerun()


def _save_pecs_phase(db: DatabaseRepository, section_id: int, phase: str, data: dict):
    """Helper function to auto-save PECS phase data."""
    db.update_section_pecs_data(section_id, phase, data)



