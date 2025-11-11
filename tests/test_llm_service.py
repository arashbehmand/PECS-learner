"""
Unit tests for LLM service functionality.
Tests cover JSON extraction, flashcard generation, and context-based methods.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from utils.llm_service import LLMService, extract_json_from_markdown

# ===== JSON EXTRACTION TESTS =====


def test_extract_json_from_markdown_with_json_fence():
    """Test extracting JSON from ```json fence."""
    content = """```json
{
  "question": "What is Python?",
  "answer": "A programming language"
}
```"""
    result = extract_json_from_markdown(content)
    expected = """{
  "question": "What is Python?",
  "answer": "A programming language"
}"""
    assert result == expected


def test_extract_json_from_markdown_with_plain_fence():
    """Test extracting JSON from ``` fence without language."""
    content = """```
[{"question": "Q1", "answer": "A1"}]
```"""
    result = extract_json_from_markdown(content)
    assert result == '[{"question": "Q1", "answer": "A1"}]'


def test_extract_json_from_markdown_no_fence():
    """Test that plain JSON without fence is returned as-is."""
    content = '[{"question": "Q1", "answer": "A1"}]'
    result = extract_json_from_markdown(content)
    assert result == content


def test_extract_json_from_markdown_with_surrounding_text():
    """Test extraction when JSON is embedded in other text."""
    content = """Here are some flashcards:

```json
[{"question": "Q1", "answer": "A1"}]
```

Hope this helps!"""
    result = extract_json_from_markdown(content)
    assert result == '[{"question": "Q1", "answer": "A1"}]'


def test_extract_json_from_markdown_multiline_json():
    """Test extraction of multiline JSON with nested objects."""
    content = """```json
[
  {
    "question": "What is the capital of France?",
    "answer": "Paris is the capital and most populous city of France."
  },
  {
    "question": "What is 2+2?",
    "answer": "4"
  }
]
```"""
    result = extract_json_from_markdown(content)
    # Verify it's valid JSON
    parsed = json.loads(result)
    assert len(parsed) == 2
    assert parsed[0]["question"] == "What is the capital of France?"


# ===== LLM SERVICE INITIALIZATION TESTS =====


@patch("utils.llm_service.OpenAI")
@patch("yaml.safe_load")
@patch("builtins.open")
@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
def test_llm_service_initialization_with_api_key(_mock_open, mock_yaml, _mock_openai):
    """Test LLM service initializes with API key."""
    # Mock the YAML file content
    mock_yaml.return_value = {
        "prime_module": {
            "section_analysis": {
                "system": "Test system prompt",
                "user": "Test user prompt",
            }
        }
    }

    llm = LLMService()
    assert llm.is_available() is True
    assert llm.api_key == "test-key"


@patch("yaml.safe_load")
@patch("builtins.open")
@patch.dict("os.environ", {}, clear=True)
def test_llm_service_initialization_without_api_key(_mock_open, mock_yaml):
    """Test LLM service handles missing API key gracefully."""
    # Mock the YAML file content
    mock_yaml.return_value = {
        "prime_module": {"section_analysis": {"system": "Test", "user": "Test"}}
    }

    llm = LLMService()
    assert llm.is_available() is False
    assert llm.client is None


# ===== FLASHCARD GENERATION TESTS =====


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service with necessary attributes."""
    with patch("yaml.safe_load") as mock_yaml, patch("builtins.open"):
        # Mock the YAML file content
        mock_yaml.return_value = {
            "prime_module": {"section_analysis": {"system": "Test", "user": "Test"}},
            "solidify_module": {
                "flashcard_analysis": {
                    "system": "Flashcard analysis",
                    "user": "Analyze: {chunk_text} {student_flashcards}",
                }
            },
        }

        llm = LLMService()
        # Mock the client
        llm.client = MagicMock()
        llm.api_key = "test-key"
        return llm


def test_suggest_flashcards_with_context_success(mock_llm_service):
    """Test successful flashcard generation with formatted context."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[
        0
    ].message.content = """```json
[
  {
    "question": "What is Python?",
    "answer": "A high-level programming language"
  },
  {
    "question": "What is a variable?",
    "answer": "A named storage location in memory"
  }
]
```"""

    mock_llm_service.client.chat.completions.create.return_value = mock_response

    formatted_context = """Learning Material:
Python is a programming language...

Student's Initial Understanding:
Python seems powerful and easy to learn.

EXISTING FLASHCARDS (2 cards - DO NOT DUPLICATE):
1. Q: What is syntax?
   A: The rules of a language
"""

    result = mock_llm_service.suggest_flashcards_with_context(formatted_context)

    assert result is not None
    assert len(result) == 2
    assert result[0]["question"] == "What is Python?"
    assert result[1]["answer"] == "A named storage location in memory"


def test_suggest_flashcards_with_context_limits_to_three(mock_llm_service):
    """Test that flashcard suggestions are limited to 3."""
    # Mock response with 5 flashcards
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(
        [{"question": f"Q{i}", "answer": f"A{i}"} for i in range(1, 6)]
    )

    mock_llm_service.client.chat.completions.create.return_value = mock_response

    result = mock_llm_service.suggest_flashcards_with_context("Test context")

    assert result is not None
    assert len(result) == 3  # Should limit to 3


def test_suggest_flashcards_with_context_invalid_json(mock_llm_service):
    """Test handling of invalid JSON response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is not valid JSON"

    mock_llm_service.client.chat.completions.create.return_value = mock_response

    result = mock_llm_service.suggest_flashcards_with_context("Test context")

    assert result is None  # Should return None on parse error


def test_suggest_flashcards_with_context_not_a_list(mock_llm_service):
    """Test handling of JSON that's not a list."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(
        {"question": "Single question", "answer": "Single answer"}
    )

    mock_llm_service.client.chat.completions.create.return_value = mock_response

    result = mock_llm_service.suggest_flashcards_with_context("Test context")

    assert result is None  # Should return None if not a list


def test_suggest_flashcards_with_context_api_error(mock_llm_service):
    """Test handling of API errors."""
    mock_llm_service.client.chat.completions.create.side_effect = Exception("API Error")

    result = mock_llm_service.suggest_flashcards_with_context("Test context")

    assert result is None  # Should return None on exception


def test_suggest_flashcards_with_context_empty_response(mock_llm_service):
    """Test handling of empty array response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "[]"

    mock_llm_service.client.chat.completions.create.return_value = mock_response

    result = mock_llm_service.suggest_flashcards_with_context("Test context")

    assert result == []  # Empty list is valid


# ===== LEGACY METHOD TESTS =====


def test_suggest_flashcards_legacy_method(mock_llm_service):
    """Test the legacy suggest_flashcards method still works."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(
        [{"question": "Q1", "answer": "A1"}]
    )

    mock_llm_service.client.chat.completions.create.return_value = mock_response

    result = mock_llm_service.suggest_flashcards(
        chunk_text="Test content",
        user_explanation="Test explanation",
        user_challenges="Test challenges",
    )

    assert result is not None
    assert len(result) == 1


def test_suggest_flashcards_with_existing_cards(mock_llm_service):
    """Test that existing cards are included in context."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(
        [{"question": "New Q", "answer": "New A"}]
    )

    mock_llm_service.client.chat.completions.create.return_value = mock_response

    existing_cards = [
        {"question": "Old Q1", "answer": "Old A1"},
        {"question": "Old Q2", "answer": "Old A2"},
    ]

    mock_llm_service.suggest_flashcards(
        chunk_text="Test content",
        user_explanation="Test explanation",
        user_challenges="Test challenges",
        existing_cards=existing_cards,
    )

    # Verify the API was called
    assert mock_llm_service.client.chat.completions.create.called

    # Verify the prompt included existing cards context
    call_args = mock_llm_service.client.chat.completions.create.call_args
    prompt = call_args[1]["messages"][1]["content"]
    assert "Old Q1" in prompt
    assert "Old Q2" in prompt
    assert "DO NOT duplicate" in prompt


# ===== SERVICE AVAILABILITY TESTS =====


@patch("yaml.safe_load")
@patch("builtins.open")
def test_is_available_without_client(_mock_open, mock_yaml):
    """Test is_available returns False when client is None."""
    mock_yaml.return_value = {"prime_module": {"test": {}}}
    llm = LLMService()
    llm.client = None
    llm.prompts = {"test": "data"}
    assert llm.is_available() is False


@patch("yaml.safe_load")
@patch("builtins.open")
def test_is_available_without_prompts(_mock_open, mock_yaml):
    """Test is_available returns False when prompts is None."""
    mock_yaml.return_value = {"prime_module": {"test": {}}}
    llm = LLMService()
    llm.client = MagicMock()
    llm.prompts = None
    assert llm.is_available() is False


@patch("yaml.safe_load")
@patch("builtins.open")
def test_is_available_with_both(_mock_open, mock_yaml):
    """Test is_available returns True when both client and prompts exist."""
    mock_yaml.return_value = {"prime_module": {"test": {}}}
    llm = LLMService()
    llm.client = MagicMock()
    assert llm.is_available() is True
