"""
Interactive study mode for spaced repetition flashcard practice.
"""
import streamlit as st
from utils.database import DatabaseRepository
from utils.models import Flashcard, Project
from datetime import datetime


def render_study_mode(db: DatabaseRepository, project_id: int):
    """
    Render interactive study mode for flashcards.
    
    Args:
        db: DatabaseRepository instance
        project_id: ID of the project to study
    """
    st.header("📚 Study Mode - Spaced Repetition")
    
    # Initialize session state for study mode
    if 'study_mode_initialized' not in st.session_state:
        st.session_state.study_mode_initialized = True
        st.session_state.current_card_index = 0
        st.session_state.show_answer = False
        st.session_state.study_flashcards = []
    
    # Get flashcards for review
    flashcards_due = db.get_flashcards_for_review(project_id)
    all_flashcards = db.get_flashcards_by_project(project_id)
    
    # Study mode options
    col1, col2 = st.columns(2)
    with col1:
        study_mode = st.radio(
            "Study:",
            ["Cards Due for Review", "All Cards", "Mastered Cards"],
            key="study_mode_select"
        )
    with col2:
        shuffle = st.checkbox("Shuffle cards", value=False, key="shuffle_cards")
    
    # Select flashcards based on mode
    if study_mode == "Cards Due for Review":
        study_cards = flashcards_due
        st.info(f"📅 {len(study_cards)} cards due for review")
    elif study_mode == "All Cards":
        study_cards = all_flashcards
        st.info(f"📚 {len(study_cards)} total cards")
    else:
        study_cards = [f for f in all_flashcards if f.is_mastered]
        st.info(f"✅ {len(study_cards)} mastered cards")
    
    # Shuffle if requested
    if shuffle and study_cards:
        import random
        random.seed(42)  # For reproducibility
        study_cards = random.sample(study_cards, len(study_cards))
    
    # Update study flashcards if mode changed
    if st.session_state.study_flashcards != study_cards:
        st.session_state.study_flashcards = study_cards
        st.session_state.current_card_index = 0
        st.session_state.show_answer = False
    
    # Display current card
    if not study_cards:
        st.warning("No flashcards available for this study mode. Create some flashcards first!")
        return
    
    # Get current card
    current_index = st.session_state.current_card_index % len(study_cards) if study_cards else 0
    current_card = study_cards[current_index]
    
    # Progress indicator
    progress = (current_index + 1) / len(study_cards)
    st.progress(progress)
    st.caption(f"Card {current_index + 1} of {len(study_cards)}")
    
    # Card display
    st.markdown("---")
    
    # Question
    st.markdown(f"### ❓ Question")
    with st.container():
        st.markdown(f"**{current_card.question}**")
    
    # Answer reveal
    if not st.session_state.show_answer:
        if st.button("🔓 Reveal Answer", key="reveal_answer", type="primary"):
            st.session_state.show_answer = True
            st.rerun()
    else:
        st.markdown("---")
        st.markdown(f"### ✅ Answer")
        with st.container():
            st.markdown(f"{current_card.answer}")
        
        # Self-grading buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👍 I Knew It", key="knew_it", type="primary", use_container_width=True):
                db.update_flashcard_review(current_card.id, knew_it=True)
                st.session_state.show_answer = False
                st.session_state.current_card_index += 1
                if st.session_state.current_card_index >= len(study_cards):
                    st.balloons()
                    st.success("🎉 You've completed all cards!")
                    st.session_state.current_card_index = 0
                st.rerun()
        
        with col2:
            if st.button("👎 Review Again", key="review_again", type="secondary", use_container_width=True):
                db.update_flashcard_review(current_card.id, knew_it=False)
                st.session_state.show_answer = False
                # Move to next card but keep this one in rotation
                st.session_state.current_card_index += 1
                if st.session_state.current_card_index >= len(study_cards):
                    st.session_state.current_card_index = 0
                st.rerun()
    
    # Navigation
    st.markdown("---")
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    with nav_col1:
        if st.button("⏮️ Previous", key="prev_card"):
            st.session_state.current_card_index = max(0, st.session_state.current_card_index - 1)
            st.session_state.show_answer = False
            st.rerun()
    
    with nav_col2:
        if st.button("🔄 Reset Session", key="reset_session"):
            st.session_state.current_card_index = 0
            st.session_state.show_answer = False
            st.rerun()
    
    with nav_col3:
        if st.button("⏭️ Next", key="next_card"):
            st.session_state.current_card_index = (st.session_state.current_card_index + 1) % len(study_cards)
            st.session_state.show_answer = False
            st.rerun()
    
    # Statistics sidebar
    with st.sidebar:
        st.subheader("📊 Study Statistics")
        project = db.get_project(project_id)
        if project:
            stats = db.get_project_stats(project_id)
            st.metric("Total Cards", stats.get('total_flashcards', 0))
            st.metric("Mastered", stats.get('mastered_flashcards', 0))
            st.metric("Due for Review", stats.get('cards_due_for_review', 0))
            
            # Show next review date for current card
            if current_card.next_review:
                days_until = (current_card.next_review - datetime.utcnow()).days
                if days_until > 0:
                    st.caption(f"Next review in {days_until} days")
                elif days_until == 0:
                    st.caption("Due today!")
                else:
                    st.caption("Overdue!")
            
            st.caption(f"Review count: {current_card.review_count}")
            st.caption(f"Ease factor: {current_card.ease_factor:.2f}")

