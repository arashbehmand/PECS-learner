"""
Unit tests for context engineering utilities.
Tests cover context building and formatting for various AI features.
"""
import pytest
from utils.context_builder import (
    build_learning_context,
    format_context_for_flashcards,
    format_context_for_completion
)


# ===== CONTEXT BUILDING TESTS =====

def test_build_learning_context_empty_pecs_data():
    """Test context building with minimal data."""
    context = build_learning_context(
        section_content="Python is a programming language.",
        pecs_data={},
        flashcards=None,
        include_conversations=False
    )

    assert context['content'] == "Python is a programming language."
    assert context['understanding'] is None
    assert context['explanation'] is None
    assert context['critical_thinking'] is None
    assert context['conversations'] == {}
    assert context['flashcards'] == []


def test_build_learning_context_with_all_phases():
    """Test context building with data from all PECS phases."""
    pecs_data = {
        'prime_preview': {
            'understanding': 'Python seems like an easy language to learn.',
            'completed': True
        },
        'engage_explain': {
            'explanation': 'Python is a high-level language with simple syntax.',
            'completed': True
        },
        'challenge_connect': {
            'critical_thinking': 'Python is similar to pseudocode.',
            'completed': True
        }
    }

    context = build_learning_context(
        section_content="Python content",
        pecs_data=pecs_data,
        flashcards=None,
        include_conversations=False
    )

    assert context['understanding'] == 'Python seems like an easy language to learn.'
    assert context['explanation'] == 'Python is a high-level language with simple syntax.'
    assert context['critical_thinking'] == 'Python is similar to pseudocode.'


def test_build_learning_context_with_flashcards():
    """Test context building includes flashcards."""
    flashcards = [
        {'question': 'What is Python?', 'answer': 'A programming language'},
        {'question': 'Is Python compiled?', 'answer': 'No, it is interpreted'}
    ]

    context = build_learning_context(
        section_content="Python content",
        pecs_data={},
        flashcards=flashcards,
        include_conversations=False
    )

    assert len(context['flashcards']) == 2
    assert context['flashcards'][0]['question'] == 'What is Python?'


def test_build_learning_context_with_conversations():
    """Test context building includes conversations when requested."""
    pecs_data = {
        'prime_preview': {
            'understanding': 'Test understanding',
            'ai_conversation': [
                {'role': 'user', 'content': 'What is Python?', 'timestamp': '2024-01-01'},
                {'role': 'assistant', 'content': 'Python is...', 'timestamp': '2024-01-01'}
            ]
        },
        'engage_explain': {
            'explanation': 'Test explanation',
            'ai_conversation': [
                {'role': 'user', 'content': 'How does it work?', 'timestamp': '2024-01-01'}
            ]
        }
    }

    context = build_learning_context(
        section_content="Python content",
        pecs_data=pecs_data,
        flashcards=None,
        include_conversations=True
    )

    assert 'prime_preview' in context['conversations']
    assert 'engage_explain' in context['conversations']
    assert len(context['conversations']['prime_preview']) == 2
    assert len(context['conversations']['engage_explain']) == 1


def test_build_learning_context_without_conversations():
    """Test that conversations are excluded when not requested."""
    pecs_data = {
        'prime_preview': {
            'understanding': 'Test',
            'ai_conversation': [{'role': 'user', 'content': 'Test', 'timestamp': '2024-01-01'}]
        }
    }

    context = build_learning_context(
        section_content="Content",
        pecs_data=pecs_data,
        flashcards=None,
        include_conversations=False
    )

    assert context['conversations'] == {}


def test_build_learning_context_partial_phase_data():
    """Test context building when only some phases are completed."""
    pecs_data = {
        'prime_preview': {
            'understanding': 'Initial thoughts',
            'completed': True
        },
        'engage_explain': {
            # No explanation yet
            'completed': False
        }
    }

    context = build_learning_context(
        section_content="Content",
        pecs_data=pecs_data,
        flashcards=None,
        include_conversations=False
    )

    assert context['understanding'] == 'Initial thoughts'
    assert context['explanation'] is None  # Not completed yet
    assert context['critical_thinking'] is None


# ===== FLASHCARD FORMATTING TESTS =====

def test_format_context_for_flashcards_minimal():
    """Test flashcard formatting with minimal context."""
    context = {
        'content': 'Python is a programming language.',
        'understanding': None,
        'explanation': None,
        'critical_thinking': None,
        'conversations': {},
        'flashcards': []
    }

    formatted = format_context_for_flashcards(context)

    assert 'LEARNING MATERIAL' in formatted
    assert 'Python is a programming language.' in formatted
    assert 'EXISTING FLASHCARDS' not in formatted  # No flashcards


def test_format_context_for_flashcards_with_all_phases():
    """Test flashcard formatting includes all phase data."""
    context = {
        'content': 'Python content',
        'understanding': 'Python seems easy',
        'explanation': 'Python has simple syntax',
        'critical_thinking': 'Python is like pseudocode',
        'conversations': {},
        'flashcards': []
    }

    formatted = format_context_for_flashcards(context)

    assert 'STUDENT\'S INITIAL UNDERSTANDING' in formatted
    assert 'Python seems easy' in formatted
    assert 'STUDENT\'S EXPLANATION' in formatted
    assert 'Python has simple syntax' in formatted
    assert 'STUDENT\'S CRITICAL ANALYSIS' in formatted
    assert 'Python is like pseudocode' in formatted


def test_format_context_for_flashcards_with_existing_cards():
    """Test flashcard formatting includes existing cards with warnings."""
    context = {
        'content': 'Python content',
        'understanding': None,
        'explanation': None,
        'critical_thinking': None,
        'conversations': {},
        'flashcards': [
            {'question': 'What is Python?', 'answer': 'A programming language'},
            {'question': 'Is Python compiled?', 'answer': 'No'}
        ]
    }

    formatted = format_context_for_flashcards(context)

    assert 'EXISTING FLASHCARDS (2 cards - DO NOT DUPLICATE)' in formatted
    assert '1. Q: What is Python?' in formatted
    assert '   A: A programming language' in formatted
    assert '2. Q: Is Python compiled?' in formatted
    assert '   A: No' in formatted
    assert 'DO NOT DUPLICATE' in formatted
    assert 'DIFFERENT flashcards' in formatted


def test_format_context_for_flashcards_truncates_long_content():
    """Test that very long content is truncated."""
    long_content = "x" * 2000

    context = {
        'content': long_content,
        'understanding': None,
        'explanation': None,
        'critical_thinking': None,
        'conversations': {},
        'flashcards': []
    }

    formatted = format_context_for_flashcards(context)

    # Should be truncated to 1500 chars + "..."
    assert len(formatted) < len(long_content)
    assert '...' in formatted


def test_format_context_for_flashcards_visual_separators():
    """Test that visual separators are present for clarity."""
    context = {
        'content': 'Content',
        'understanding': 'Understanding',
        'explanation': None,
        'critical_thinking': None,
        'conversations': {},
        'flashcards': [{'question': 'Q?', 'answer': 'A'}]
    }

    formatted = format_context_for_flashcards(context)

    # Check for separator lines
    separator_count = formatted.count('=' * 60)
    assert separator_count >= 4  # At least for content, understanding, and flashcards


# ===== COMPLETION FORMATTING TESTS =====

def test_format_context_for_completion_with_conversations():
    """Test completion formatting includes conversations."""
    context = {
        'content': 'Python content',
        'understanding': 'Initial thoughts',
        'explanation': 'Detailed explanation',
        'critical_thinking': 'Critical analysis',
        'conversations': {
            'prime_preview': [
                {'role': 'user', 'content': 'What is this?', 'timestamp': '2024-01-01'},
                {'role': 'assistant', 'content': 'This is...', 'timestamp': '2024-01-01'}
            ],
            'engage_explain': [
                {'role': 'user', 'content': 'How does it work?', 'timestamp': '2024-01-01'}
            ]
        },
        'flashcards': []
    }

    formatted = format_context_for_completion(context)

    assert 'PRIME & PREVIEW - Learning Conversation' in formatted
    assert '[USER]: What is this?' in formatted
    assert '[ASSISTANT]: This is...' in formatted
    assert 'ENGAGE & EXPLAIN - Learning Conversation' in formatted
    assert '[USER]: How does it work?' in formatted


def test_format_context_for_completion_with_flashcards():
    """Test completion formatting includes created flashcards."""
    context = {
        'content': 'Content',
        'understanding': None,
        'explanation': None,
        'critical_thinking': None,
        'conversations': {},
        'flashcards': [
            {'question': 'Q1?', 'answer': 'A1'},
            {'question': 'Q2?', 'answer': 'A2'},
            {'question': 'Q3?', 'answer': 'A3'}
        ]
    }

    formatted = format_context_for_completion(context)

    assert 'FLASHCARDS CREATED (3 cards)' in formatted
    assert '1. Q: Q1?' in formatted
    assert '   A: A1' in formatted
    assert '3. Q: Q3?' in formatted


def test_format_context_for_completion_direct_responses():
    """Test completion formatting shows direct responses when no conversations."""
    context = {
        'content': 'Content',
        'understanding': 'Direct understanding',
        'explanation': 'Direct explanation',
        'critical_thinking': 'Direct analysis',
        'conversations': {},
        'flashcards': []
    }

    formatted = format_context_for_completion(context)

    assert 'INITIAL UNDERSTANDING' in formatted
    assert 'Direct understanding' in formatted
    assert 'STUDENT\'S EXPLANATION' in formatted
    assert 'Direct explanation' in formatted
    assert 'CRITICAL ANALYSIS' in formatted
    assert 'Direct analysis' in formatted


def test_format_context_for_completion_truncates_long_content():
    """Test that content is truncated for completion reports."""
    long_content = "x" * 3000

    context = {
        'content': long_content,
        'understanding': None,
        'explanation': None,
        'critical_thinking': None,
        'conversations': {},
        'flashcards': []
    }

    formatted = format_context_for_completion(context)

    # Should be truncated to 2000 chars + "..."
    assert '...' in formatted
    # The formatted string should be much shorter than 3000 chars
    assert len(formatted) < 2500


def test_format_context_for_completion_phase_names():
    """Test that phase names are properly formatted."""
    context = {
        'content': 'Content',
        'understanding': None,
        'explanation': None,
        'critical_thinking': None,
        'conversations': {
            'prime_preview': [{'role': 'user', 'content': 'Test', 'timestamp': '2024-01-01'}],
            'engage_explain': [{'role': 'user', 'content': 'Test', 'timestamp': '2024-01-01'}],
            'challenge_connect': [{'role': 'user', 'content': 'Test', 'timestamp': '2024-01-01'}]
        },
        'flashcards': []
    }

    formatted = format_context_for_completion(context)

    assert 'PRIME & PREVIEW' in formatted
    assert 'ENGAGE & EXPLAIN' in formatted
    assert 'CHALLENGE & CONNECT' in formatted


# ===== INTEGRATION TESTS =====

def test_full_workflow_flashcard_generation():
    """Test complete workflow: build context -> format for flashcards."""
    # Simulate section state
    pecs_data = {
        'prime_preview': {
            'understanding': 'Python seems powerful',
            'completed': True
        },
        'engage_explain': {
            'explanation': 'Python uses indentation for blocks',
            'completed': True
        },
        'challenge_connect': {
            'critical_thinking': 'Python is similar to Ruby',
            'completed': True
        }
    }

    flashcards = [
        {'question': 'What is a variable?', 'answer': 'A named storage'}
    ]

    # Build context
    context = build_learning_context(
        section_content="Python is a versatile programming language.",
        pecs_data=pecs_data,
        flashcards=flashcards,
        include_conversations=False
    )

    # Format for flashcards
    formatted = format_context_for_flashcards(context)

    # Verify all pieces are present
    assert 'Python is a versatile programming language' in formatted
    assert 'Python seems powerful' in formatted
    assert 'Python uses indentation for blocks' in formatted
    assert 'Python is similar to Ruby' in formatted
    assert 'EXISTING FLASHCARDS (1 cards' in formatted
    assert 'What is a variable?' in formatted


def test_full_workflow_completion_report():
    """Test complete workflow: build context -> format for completion."""
    pecs_data = {
        'prime_preview': {
            'understanding': 'Initial thoughts',
            'ai_conversation': [
                {'role': 'user', 'content': 'What is this about?', 'timestamp': '2024-01-01'},
                {'role': 'assistant', 'content': 'This covers...', 'timestamp': '2024-01-01'}
            ],
            'completed': True
        },
        'engage_explain': {
            'explanation': 'Detailed explanation',
            'completed': True
        }
    }

    flashcards = [
        {'question': 'Q1?', 'answer': 'A1'},
        {'question': 'Q2?', 'answer': 'A2'}
    ]

    # Build context with conversations
    context = build_learning_context(
        section_content="Learning material content",
        pecs_data=pecs_data,
        flashcards=flashcards,
        include_conversations=True
    )

    # Format for completion
    formatted = format_context_for_completion(context)

    # Verify comprehensive context
    assert 'Learning material content' in formatted
    assert 'PRIME & PREVIEW - Learning Conversation' in formatted
    assert 'What is this about?' in formatted
    assert 'FLASHCARDS CREATED (2 cards)' in formatted
    assert 'Q1?' in formatted
