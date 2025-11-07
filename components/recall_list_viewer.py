import streamlit as st
from typing import List, Dict, Any
import json

def render_recall_list_viewer():
    """
    Render the recall list viewer interface for displaying and managing flashcards.
    """
    st.header("My Recall List")
    
    if not st.session_state.all_recall_prompts:
        st.info("No flashcards created yet. Complete some P.E.C.S. cycles to create flashcards!")
        return
    
    # Add filtering options
    st.subheader("Filter Flashcards")
    col1, col2 = st.columns(2)
    
    with col1:
        # Filter by chunk
        chunk_options = ["All Chunks"] + [f"Chunk {i+1}" for i in range(len(st.session_state.chunks))]
        selected_chunk = st.selectbox("Filter by Chunk:", chunk_options)
    
    with col2:
        # Search functionality
        search_query = st.text_input("Search in questions and answers:", "")
    
    # Filter flashcards
    filtered_cards = st.session_state.all_recall_prompts
    
    if selected_chunk != "All Chunks":
        chunk_idx = int(selected_chunk.split()[-1]) - 1
        filtered_cards = [card for card in filtered_cards if card.get('chunk_idx') == chunk_idx]
    
    if search_query:
        search_query = search_query.lower()
        filtered_cards = [
            card for card in filtered_cards
            if search_query in card['question'].lower() or search_query in card['answer'].lower()
        ]
    
    # Display filtered cards
    st.subheader(f"Found {len(filtered_cards)} flashcards")
    
    # Group cards by chunk for better organization
    chunk_groups = {}
    for card in filtered_cards:
        chunk_idx = card.get('chunk_idx', 0)
        if chunk_idx not in chunk_groups:
            chunk_groups[chunk_idx] = []
        chunk_groups[chunk_idx].append(card)
    
    # Display cards by chunk
    for chunk_idx, cards in sorted(chunk_groups.items()):
        with st.expander(f"Chunk {chunk_idx + 1} ({len(cards)} cards)"):
            for i, card in enumerate(cards):
                with st.expander(f"Card {i+1}: {card['question']}"):
                    st.text_area(
                        "Answer:",
                        value=card['answer'],
                        height=100,
                        disabled=True
                    )
                    
                    # Add a delete button for each card
                    if st.button(f"Delete Card {i+1}", key=f"delete_{chunk_idx}_{i}"):
                        st.session_state.all_recall_prompts.remove(card)
                        st.rerun()
    
    # Add export option
    st.markdown("---")
    st.subheader("Export Options")
    if st.button("Export Flashcards to JSON"):
        json_data = json.dumps(st.session_state.all_recall_prompts, indent=2)
        st.download_button(
            label="Download Flashcards",
            data=json_data,
            file_name="pecs_flashcards.json",
            mime="application/json"
        ) 