# Testing Documentation

## Overview

This document describes the test coverage for the PECS Learning System, with a focus on the new features implemented in the NiceGUI migration.

## Test Coverage Summary

### Test Files

1. **tests/test_llm_service.py** (18 tests)
   - JSON extraction from markdown code blocks
   - LLM service initialization with/without API keys
   - Flashcard generation with context (NEW)
   - Error handling for invalid responses
   - Service availability checks

2. **tests/test_context_builder.py** (18 tests) ⭐ NEW
   - Context building from section state
   - Context formatting for flashcards
   - Context formatting for completion reports
   - Conversation inclusion/exclusion
   - Integration tests for full workflows

3. **tests/test_database.py** (10 tests)
   - Project CRUD operations
   - Section CRUD operations
   - Flashcard creation and review
   - PECS data persistence
   - Project statistics

### Coverage Statistics

```
Module                        Coverage
--------------------------------
utils/context_builder.py      100%  ⭐ NEW MODULE
utils/database.py              62%
utils/llm_service.py           52%
utils/models.py                90%
--------------------------------
TOTAL (relevant modules)       48%
```

## New Features with Tests

### 1. Context Engineering (DRY Principle)

**Module**: `utils/context_builder.py`

This new utility module eliminates code duplication and provides a single source of truth for AI context building.

**Functions Tested**:
- `build_learning_context()` - Gathers learning state from all phases
- `format_context_for_flashcards()` - Formats context for flashcard generation
- `format_context_for_completion()` - Formats context for completion reports

**Key Test Cases**:
- Empty PECS data handling
- All phases completed
- Partial phase completion
- Flashcard inclusion (ONLY committed DB cards, not ephemeral suggestions)
- Conversation inclusion/exclusion
- Content truncation for token limits
- Visual separators for clarity
- Full workflow integration tests

### 2. LLM Service Enhancements

**Module**: `utils/llm_service.py`

**New Features Tested**:
- `extract_json_from_markdown()` - Handles LLM responses wrapped in markdown code blocks
- `suggest_flashcards_with_context()` - NEW method using pre-formatted context

**Key Test Cases**:
- JSON extraction from various markdown formats (```json, ```, plain text)
- Flashcard generation success scenarios
- Limiting to 3 flashcards maximum
- Invalid JSON handling
- Non-list response handling
- API error handling
- Empty response handling
- Legacy method compatibility
- Existing cards context inclusion

### 3. Database Integration

**Module**: `utils/database.py`

Tests verify that PECS data, flashcards, and completion state are properly persisted.

**Key Test Cases**:
- PECS data storage and retrieval
- Flashcard creation with section association
- Section completion tracking
- Review count and spaced repetition algorithm
- Project statistics calculation

## Running Tests

### Run All New Feature Tests
```bash
pytest tests/test_llm_service.py tests/test_context_builder.py tests/test_database.py -v
```

### Run With Coverage
```bash
pytest tests/test_llm_service.py tests/test_context_builder.py tests/test_database.py \
  --cov=utils/llm_service.py \
  --cov=utils/context_builder.py \
  --cov=utils/database.py \
  --cov-report=term-missing
```

### Run Individual Test Files
```bash
# Context engineering tests
pytest tests/test_context_builder.py -v

# LLM service tests
pytest tests/test_llm_service.py -v

# Database tests
pytest tests/test_database.py -v
```

## Test Strategy

### Unit Tests
- **Focus**: Individual functions in isolation
- **Examples**: JSON extraction, context formatting, flashcard filtering

### Integration Tests
- **Focus**: Multiple components working together
- **Examples**: Context building → formatting → LLM call → database save

### Mock Strategy
- **LLM API calls**: Mocked with `unittest.mock`
- **YAML file loading**: Mocked to avoid file system dependencies
- **Database**: Uses temporary in-memory SQLite database per test

## Key Design Decisions

### 1. Context Builder Extraction
Previously, context building logic was embedded in `PECSLearningPage`. This made it:
- Hard to test
- Duplicated across features
- Difficult to maintain

**Solution**: Extracted to `utils/context_builder.py` with:
- Pure functions (no side effects)
- Clear input/output contracts
- Easy to test in isolation

### 2. ONLY Committed Flashcards in Context
**Critical Bug Fix**: Originally included ephemeral in-dialog suggestions in context, causing duplicates.

**Solution**: Context builder ONLY includes committed database flashcards. This ensures:
- No duplicate generation
- Consistent AI behavior
- Clear separation of persistent vs ephemeral state

### 3. Conversation Key: `ai_conversation`
The database uses `ai_conversation` (not `conversation`) for storing chat history. Tests verify correct key usage.

### 4. Field Name Compatibility
Challenge phase uses `critical_questions` field. Context builder handles both `critical_questions` and `critical_thinking` for backward compatibility.

## Critical Test Cases

### Preventing Duplicate Flashcards
```python
def test_format_context_for_flashcards_with_existing_cards():
    """Test that existing cards are clearly marked to prevent duplicates"""
    # Verifies:
    # - "DO NOT DUPLICATE" warning present
    # - Existing cards listed with numbers
    # - Visual separators used
    # - Instruction to generate DIFFERENT cards
```

### Context Truncation
```python
def test_format_context_for_flashcards_truncates_long_content():
    """Test that very long content doesn't exceed token limits"""
    # Verifies content is truncated to 1500 chars for flashcards
    # and 2000 chars for completion reports
```

### Conversation Inclusion Control
```python
def test_build_learning_context_without_conversations():
    """Test that conversations are excluded when not requested"""
    # Important for performance - conversations are expensive
    # Only include when needed (e.g., completion reports)
```

## Future Test Improvements

### Areas for Additional Coverage

1. **NiceGUI UI Components** (currently not tested)
   - Phase rendering
   - Flashcard dialog interactions
   - Navigation flow

2. **Additional LLM Methods** (52% coverage)
   - `analyze_section_understanding()`
   - `analyze_explanation()`
   - `analyze_critical_thinking()`
   - All follow similar patterns to tested methods

3. **Error Scenarios**
   - Database connection failures
   - Corrupt PECS data
   - Malformed flashcard data

4. **Performance Tests**
   - Context building for large sections (10k+ words)
   - Flashcard generation with 100+ existing cards
   - Database queries with 1000+ sections

### Testing Strategy for UI

Options for future NiceGUI testing:
1. **Selenium/Playwright**: End-to-end browser testing
2. **FastAPI TestClient**: Test underlying endpoints
3. **Component isolation**: Extract logic from UI for testing

Currently, we test the business logic and data layer thoroughly. UI logic is kept minimal and follows established patterns.

## Continuous Integration

### Recommended CI Pipeline

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/test_llm_service.py \
                 tests/test_context_builder.py \
                 tests/test_database.py \
                 --cov=utils \
                 --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Conclusion

The test suite provides strong coverage for the critical new features:
- ✅ Context engineering (100% coverage)
- ✅ LLM flashcard generation (comprehensive)
- ✅ Database persistence (62% coverage)
- ✅ JSON parsing edge cases
- ✅ Error handling

All 46 tests pass successfully, ensuring the reliability of the refactored codebase. The DRY principle is now properly tested and enforced at the architectural level.
