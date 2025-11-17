# CLAUDE.md - AI Assistant Guide to PECS Learning System

**Last Updated**: November 2025
**Version**: 2.0 (NiceGUI Architecture)
**Purpose**: This document provides AI assistants with comprehensive guidance for working with the PECS Learning System codebase.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Key Architectural Decisions](#key-architectural-decisions)
4. [Development Workflows](#development-workflows)
5. [Coding Conventions](#coding-conventions)
6. [Testing Strategy](#testing-strategy)
7. [Common Tasks](#common-tasks)
8. [AI Context Engineering](#ai-context-engineering)
9. [Database Operations](#database-operations)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

---

## Project Overview

### What is PECS?

P.E.C.S. (Prime → Engage → Challenge → Solidify) is an AI-powered learning platform that implements a scientifically-backed active learning methodology. It transforms reading materials (books, articles, PDFs) into structured learning experiences with AI feedback and spaced repetition.

### Technology Stack

- **Frontend**: NiceGUI 1.4+ (Pure Python web framework, PWA-enabled)
- **Backend**: Python 3.11+, FastAPI/Uvicorn (via NiceGUI)
- **Database**: SQLite with SQLAlchemy ORM
- **AI**: LiteLLM (supports 100+ providers: OpenAI, Anthropic, Google, etc.)
- **Observability**: Langfuse (optional)
- **Testing**: pytest (56 tests, targeting 100% coverage on critical modules)
- **Containerization**: Docker & Docker Compose

### Core Features

1. **Multi-format content import** (Text, Markdown, EPUB, PDF, Word)
2. **Hierarchical content processing** (auto-detects chapters/sections)
3. **Guided 4-phase learning workflow** (Prime → Engage → Challenge → Solidify)
4. **AI-powered feedback and flashcard generation**
5. **Voice input** (speech-to-text via Whisper API + Web Speech API)
6. **Text-to-speech** (hear AI feedback read aloud with natural voices)
7. **Rolling context** for book-length materials
8. **SM-2 spaced repetition** algorithm
9. **Anki export** (API and file-based)
10. **PWA support** (installable, offline-capable)

---

## Codebase Structure

### Directory Layout

```
PECS-learner/
├── nicegui_app/              # Main NiceGUI application
│   ├── main.py               # Entry point, PWA setup, routing
│   ├── config.py             # Configuration management
│   ├── pages/                # Page implementations
│   │   ├── dashboard.py      # Project management
│   │   ├── content_upload.py # File upload & processing
│   │   ├── project_view.py   # Section list & study notes
│   │   ├── pecs_learning.py  # Core learning interface ⭐
│   │   └── study_mode.py     # Flashcard spaced repetition
│   ├── static/               # PWA assets (manifest, service worker)
│   ├── auth/                 # Future authentication (placeholder)
│   ├── components/           # Reusable UI components (placeholder)
│   └── utils/                # App-specific utilities (placeholder)
│
├── utils/                    # Shared business logic
│   ├── models.py             # SQLAlchemy ORM models
│   ├── database.py           # Repository layer (all DB operations)
│   ├── context_builder.py   # DRY AI context engineering ⭐
│   ├── llm_service.py        # LiteLLM integration
│   ├── rolling_context_service.py  # Rolling context & study notes
│   ├── hierarchical_processor.py   # Document structure detection
│   ├── file_converters.py    # EPUB, PDF, DOCX → text
│   ├── anki_export.py        # Anki export (API + file)
│   ├── voice_service.py      # Voice input & TTS ⭐
│   ├── content_processor.py  # Legacy content processing
│   └── prompts.yaml          # AI prompt templates
│
├── tests/                    # Comprehensive test suite
│   ├── test_context_builder.py     # 100% coverage ⭐
│   ├── test_database.py
│   ├── test_llm_service.py
│   ├── test_file_converters.py
│   ├── test_hierarchical_processor.py
│   ├── test_rolling_context_service.py
│   └── conftest.py           # Shared test fixtures
│
├── data/                     # Runtime data (auto-created)
│   ├── pecs.db               # SQLite database
│   └── nicegui_storage/      # NiceGUI session storage
│
├── logs/                     # Application logs (auto-created)
│
├── .env.example              # Environment configuration template
├── requirements.txt          # Python dependencies
├── Dockerfile                # Production container
├── docker-compose.yml        # Local development stack
├── pytest.ini                # Test configuration
├── .pylintrc                 # Linting rules
├── README.md                 # User-facing documentation
├── BLUEPRINT.md              # Technical architecture (ESSENTIAL READ)
└── CLAUDE.md                 # This file
```

### Critical Files to Understand

**MUST READ FIRST:**
1. `BLUEPRINT.md` - Complete technical architecture and design decisions
2. `nicegui_app/pages/pecs_learning.py` - Core learning interface (heart of the system)
3. `utils/context_builder.py` - AI context engineering (100% tested, DRY principle)
4. `utils/database.py` - All database operations (repository pattern)

**IMPORTANT:**
5. `utils/models.py` - Database schema
6. `utils/llm_service.py` - LLM integration with LiteLLM
7. `utils/rolling_context_service.py` - Rolling context for book-length materials
8. `nicegui_app/main.py` - Application entry point and PWA setup

---

## Key Architectural Decisions

### 1. DRY (Don't Repeat Yourself) Principle

**CRITICAL**: The codebase follows strict DRY principles to prevent bugs (especially duplicate flashcard generation).

**Context Building - Single Source of Truth:**
```python
# ✅ CORRECT: Use context_builder.py for ALL AI context needs
from utils.context_builder import build_learning_context, format_context_for_flashcards

context = build_learning_context(
    section_content=section.content,
    pecs_data=section.pecs_data,
    flashcards=existing_flashcards,  # ONLY committed DB flashcards!
    include_conversations=False
)
formatted = format_context_for_flashcards(context)

# ❌ WRONG: Building context manually in UI code
# This leads to inconsistencies and duplicate flashcards!
```

**Phase Rendering - Generic System:**
```python
# ✅ CORRECT: Use phase_config dictionary + generic renderer
self.phase_config = {...}  # Configuration-driven
self._render_learning_phase('prime_preview')  # Generic method

# ❌ WRONG: Copy-pasting similar code for each phase
```

### 2. Database-First Design

All state persists in SQLite immediately. No in-memory state that could be lost.

```python
# ✅ CORRECT: Use DatabaseRepository for all operations
from utils.database import DatabaseRepository
db = DatabaseRepository()
db.update_section_pecs_data(section_id, 'prime_preview', {'understanding': text})

# ❌ WRONG: Managing state in session/memory without DB persistence
```

### 3. Repository Pattern

All database operations go through `DatabaseRepository` class in `utils/database.py`. Never use SQLAlchemy sessions directly in UI code.

### 4. NiceGUI Architecture (Not Streamlit!)

- **URL-based routing**: Each page has a dedicated route (`/`, `/project/{id}`, etc.)
- **No page reloads**: UI updates are reactive via NiceGUI's binding system
- **Async/await**: Use `asyncio.to_thread()` for blocking LLM calls
- **PWA support**: Service worker + manifest for installable app

### 5. Testing-Driven Development

- Write tests BEFORE implementing features (or immediately after)
- Target 100% coverage on critical modules (context_builder, database)
- Mock external dependencies (LLM API, file I/O)
- Use fixtures for common test data

---

## Development Workflows

### Setting Up Development Environment

```bash
# Clone repository
git clone <repo-url>
cd PECS-learner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add at least one LLM API key

# Run tests to verify setup
pytest

# Start development server
python nicegui_app/main.py
# Access at http://localhost:8080
```

### Git Workflow

```bash
# Create feature branch from claude/* branch
git checkout -b claude/claude-md-<session-id>-<feature-name>

# Make changes with clear commits
git add .
git commit -m "feat: add new feature X

- Detailed description of changes
- Reference to any issues
"

# Push to remote
git push -u origin claude/claude-md-<session-id>-<feature-name>

# Create PR to main branch
```

**Commit Message Convention:**
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `test:` - Adding/updating tests
- `docs:` - Documentation updates
- `chore:` - Maintenance tasks

### Making Changes

**ALWAYS:**
1. Read `BLUEPRINT.md` first to understand architecture
2. Check existing tests for patterns
3. Update tests when changing functionality
4. Update `BLUEPRINT.md` if architecture changes
5. Test locally before committing

**NEVER:**
- Modify database schema without migration plan
- Break DRY principles (especially context building)
- Skip writing tests for new features
- Use Streamlit patterns (this is NiceGUI!)
- Hardcode configuration (use `config.py` + `.env`)

---

## Coding Conventions

### Python Style

- **Type hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions/classes
- **Naming**:
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`
- **Line length**: 88 characters (Black default)
- **Imports**: Standard library → Third-party → Local (separated by blank lines)

### Example

```python
"""Module description."""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from nicegui import ui
from sqlalchemy.orm import Session

from utils.database import DatabaseRepository
from utils.models import Section


def process_section(
    section: Section,
    db: DatabaseRepository,
    *,
    include_context: bool = False
) -> Dict[str, any]:
    """Process a section and return structured data.

    Args:
        section: The section to process
        db: Database repository instance
        include_context: Whether to include full context (default: False)

    Returns:
        Dictionary containing processed section data

    Raises:
        ValueError: If section is invalid
    """
    if not section.content:
        raise ValueError("Section has no content")

    # Implementation...
    return {"status": "success"}
```

### NiceGUI Patterns

**Component Structure:**
```python
class MyPage:
    """Page description."""

    def __init__(self, project_id: int):
        """Initialize page with project ID."""
        self.project_id = project_id
        self.db = DatabaseRepository()

    def render(self) -> None:
        """Render the page UI."""
        with ui.card():
            ui.label('Title').classes('text-2xl')
            self._render_content()

    def _render_content(self) -> None:
        """Render content section (private method)."""
        # Implementation...
```

**Async LLM Calls:**
```python
async def generate_flashcards(self):
    """Generate flashcards asynchronously."""
    # Show loading indicator
    self.loading = True
    ui.notify('Generating flashcards...')

    try:
        # Run LLM call in thread pool to avoid blocking
        result = await asyncio.to_thread(
            self.llm_service.suggest_flashcards_with_context,
            formatted_context
        )

        # Process results
        self._display_flashcards(result)

    except Exception as e:
        ui.notify(f'Error: {str(e)}', type='negative')
    finally:
        self.loading = False
```

### Error Handling

```python
# Always log errors
import logging
logger = logging.getLogger(__name__)

try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    ui.notify(f"Error: {str(e)}", type='negative')
    return None
```

---

## Testing Strategy

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=utils --cov=nicegui_app --cov-report=term-missing

# Run specific test file
pytest tests/test_context_builder.py -v

# Run specific test
pytest tests/test_context_builder.py::test_build_learning_context -v

# Run fast tests only (skip slow integration tests)
pytest -m "not slow"
```

### Writing Tests

**Location**: `tests/test_<module_name>.py`

**Structure:**
```python
"""Tests for module_name."""

import pytest
from unittest.mock import Mock, patch

from utils.module_name import function_to_test


class TestFunctionName:
    """Tests for function_to_test."""

    def test_basic_case(self):
        """Test basic functionality."""
        result = function_to_test(arg='value')
        assert result == expected_value

    def test_edge_case(self):
        """Test edge case behavior."""
        result = function_to_test(arg=None)
        assert result is None

    def test_error_handling(self):
        """Test error is raised for invalid input."""
        with pytest.raises(ValueError):
            function_to_test(arg='invalid')
```

**Fixtures** (`tests/conftest.py`):
```python
@pytest.fixture
def db():
    """Provide a test database."""
    # Setup
    db = DatabaseRepository()
    db.create_tables()

    yield db

    # Teardown
    db.close()
```

**Mocking LLM Calls:**
```python
@patch('utils.llm_service.completion')
def test_flashcard_generation(mock_completion):
    """Test flashcard generation."""
    mock_completion.return_value = {
        'choices': [{'message': {'content': '{"flashcards": [...]}'}}]
    }

    result = generate_flashcards(context)
    assert len(result) > 0
```

### Test Coverage Goals

- **Critical modules** (context_builder, database): 100%
- **Business logic** (llm_service, processors): >80%
- **UI code** (pages): >50% (focus on logic, not rendering)

---

## Common Tasks

### Adding a New PECS Phase

1. **Update models** (`utils/models.py`):
   - Add phase key to `pecs_data` JSON schema documentation

2. **Update context builder** (`utils/context_builder.py`):
   - Add phase to `build_learning_context()`
   - Update formatting functions

3. **Add prompts** (`utils/prompts.yaml`):
   - Create prompt templates for new phase

4. **Update UI** (`nicegui_app/pages/pecs_learning.py`):
   - Add phase configuration to `self.phase_config`
   - Generic renderer should handle it automatically

5. **Add tests**:
   - Test context building with new phase
   - Test UI rendering (if special behavior)

6. **Update docs**:
   - Update `BLUEPRINT.md` with new phase description
   - Update `README.md` user documentation

### Adding a New LLM Provider

1. **Check LiteLLM support**: https://docs.litellm.ai/docs/providers

2. **Update `.env.example`**:
   - Add API key documentation
   - Add example model configurations

3. **Update `config.py`** (if needed):
   - Add provider-specific configuration

4. **Test integration**:
   - Add test case in `test_llm_service.py`
   - Test with real API key locally

5. **Update docs**:
   - Add to README.md provider list
   - Document in BLUEPRINT.md

### Adding a New Export Format

1. **Create converter** in `utils/`:
   - Follow pattern from `anki_export.py`
   - Use repository pattern for data access

2. **Add UI controls** in `nicegui_app/pages/project_view.py`:
   - Export button with modal/dialog
   - Progress indicator for large exports

3. **Add tests**:
   - Test conversion logic
   - Test error handling

4. **Update docs**:
   - README.md user guide
   - BLUEPRINT.md architecture

### Modifying Database Schema

**IMPORTANT**: Schema changes require careful migration!

1. **Update models** (`utils/models.py`):
   - Modify SQLAlchemy model definitions

2. **Create migration function**:
   - In `utils/migration.py` or similar
   - Handle both upgrade and downgrade

3. **Test migration**:
   - Test on fresh database
   - Test on database with existing data

4. **Update database.py**:
   - Update repository methods as needed

5. **Update all dependent code**:
   - Search codebase for references to changed fields

6. **Update tests**:
   - Update fixtures with new schema
   - Test migration function

7. **Document**:
   - BLUEPRINT.md schema changes
   - CHANGELOG.md migration notes

---

## AI Context Engineering

### Core Principle: DRY (Don't Repeat Yourself)

**ALWAYS use `context_builder.py`** - it's the single source of truth for AI context.

### Key Functions

**1. `build_learning_context()`**

Gathers all relevant context from a section's state.

```python
from utils.context_builder import build_learning_context

context = build_learning_context(
    section_content=section.content,
    pecs_data=section.pecs_data,
    flashcards=existing_flashcards,  # ONLY committed DB flashcards!
    include_conversations=True  # Optional, for completion reports
)
```

**Returns:**
```python
{
    'content': str,
    'understanding': str,
    'questions': str,
    'explanation': str,
    'critical_thinking': str,
    'flashcards': List[Dict],  # Only committed flashcards from DB
    'conversations': Dict  # Optional
}
```

**2. `format_context_for_flashcards()`**

Formats context specifically for flashcard generation with duplicate prevention.

```python
from utils.context_builder import format_context_for_flashcards

formatted = format_context_for_flashcards(context)
# Returns: Formatted string with clear separators and "DO NOT DUPLICATE" warnings
```

**3. `format_context_for_completion()`**

Formats context for completion reports (includes conversations).

```python
from utils.context_builder import format_context_for_completion

formatted = format_context_for_completion(context)
# Returns: Full learning journey including conversations
```

### Why This Matters

**Problem**: Duplicate flashcards were being generated because different parts of the code built context differently.

**Solution**: One function (`build_learning_context()`) that:
- ONLY includes flashcards committed to database
- Has 100% test coverage
- Is used everywhere consistently

**❌ NEVER DO THIS:**
```python
# Building context manually
flashcards = session_state.get('pending_flashcards', [])  # WRONG!
# This includes uncommitted cards, causing duplicates
```

**✅ ALWAYS DO THIS:**
```python
# Using repository to get only committed cards
flashcards = db.get_flashcards_by_section(section_id)
context = build_learning_context(..., flashcards=flashcards, ...)
```

---

## Database Operations

### Repository Pattern

All database operations go through `utils/database.py`:

```python
from utils.database import DatabaseRepository

db = DatabaseRepository()
```

### Common Operations

**Projects:**
```python
# Create
project = db.create_project(name="My Book")

# List all
projects = db.get_all_projects()

# Get one
project = db.get_project_by_id(project_id)

# Get stats
stats = db.get_project_stats(project_id)
# Returns: {'total_sections': 10, 'completed_sections': 5, ...}

# Delete
db.delete_project(project_id)
```

**Sections:**
```python
# Create
section = db.create_section(
    project_id=project_id,
    content="Section text...",
    title="Chapter 1",
    order_index=0
)

# Get all in project
sections = db.get_sections_by_project(project_id)

# Get one
section = db.get_section_by_id(section_id)

# Update PECS data
db.update_section_pecs_data(
    section_id=section_id,
    phase_key='prime_preview',
    phase_data={'understanding': 'My thoughts...'}
)

# Mark complete
db.mark_section_complete(section_id, is_completed=True)

# Delete
db.delete_section(section_id)
```

**Flashcards:**
```python
# Create
flashcard = db.create_flashcard(
    project_id=project_id,
    section_id=section_id,  # Optional
    question="What is X?",
    answer="X is..."
)

# Get by section
flashcards = db.get_flashcards_by_section(section_id)

# Get by project
flashcards = db.get_flashcards_by_project(project_id)

# Get due for review
due_cards = db.get_due_flashcards(project_id)

# Update after review (SM-2 algorithm)
db.update_flashcard_review(
    flashcard_id=flashcard_id,
    knew_it=True  # or False
)

# Delete
db.delete_flashcard(flashcard_id)
```

### PECS Data Structure

Sections store phase data in a JSON blob (`pecs_data` field):

```python
{
    "prime_preview": {
        "understanding": "My initial thoughts...",
        "questions": "What is X? Why Y?",
        "conversations": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ],
        "completed_at": "2025-11-17T12:00:00"
    },
    "engage_explain": {
        "explanation": "In my own words...",
        "conversations": [...],
        "completed_at": "2025-11-17T12:30:00"
    },
    "challenge_connect": {
        "critical_thinking": "This connects to...",
        "conversations": [...],
        "completed_at": "2025-11-17T13:00:00"
    },
    "solidify_space": {
        "completion_report": "Great work! You created 5 flashcards...",
        "completed_at": "2025-11-17T13:30:00"
    }
}
```

**Accessing PECS Data:**
```python
section = db.get_section_by_id(section_id)
pecs_data = section.pecs_data or {}
understanding = pecs_data.get('prime_preview', {}).get('understanding', '')
```

---

## Deployment

### Local Development

```bash
python nicegui_app/main.py
# Access at http://localhost:8080
```

### Docker (Recommended)

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Production Platforms

**Railway** (Recommended - Free tier):
```bash
railway login
railway init
railway up
```

**Render** (Free tier with sleep):
- Connect GitHub repository
- Set environment variables (API keys)
- Auto-deploy on push

**Environment Variables for Production:**
```bash
# Required
OPENAI_API_KEY=sk-...  # Or other LLM provider

# Recommended
PORT=8080
HOST=0.0.0.0
NICEGUI_STORAGE_PATH=/app/data/nicegui_storage

# Optional
LLM_MODEL_FAST=gpt-5-mini
LLM_MODEL_QUALITY=gpt-5.1
LANGFUSE_PUBLIC_KEY=pk-...  # For observability
```

### PWA Configuration

PWA assets are in `nicegui_app/static/`:
- `manifest.json` - App metadata, icons, theme
- `service-worker.js` - Offline support

**Updating PWA:**
1. Edit `manifest.json` for app name, colors, icons
2. Update `service-worker.js` for caching strategy
3. Increment version in `config.py` to force update

---

## Troubleshooting

### Common Issues

**1. Database locked errors**
- Cause: Concurrent writes to SQLite
- Solution: Use `DatabaseRepository` methods (they handle transactions)
- Check: Not using multiple `db` instances

**2. Duplicate flashcards**
- Cause: Not using `context_builder.py` consistently
- Solution: Always use `build_learning_context()` and fetch flashcards from DB
- Check: Not using session state for flashcards

**3. LLM API errors**
- Check: API key is set in `.env`
- Check: Model name is correct for provider (see LiteLLM docs)
- Enable: `LITELLM_VERBOSE=true` for debugging
- Check: Langfuse credentials if using observability

**4. PWA not installing**
- Check: Accessing via HTTPS (required for PWA)
- Check: `manifest.json` is valid JSON
- Check: Service worker is registered (browser console)
- Clear: Browser cache and re-register

**5. Tests failing**
- Run: `pytest -v` for verbose output
- Check: Mock patches are correct
- Check: Fixtures are properly set up
- Clear: Test database before running (`rm tests/test.db`)

### Debugging Tips

**1. Enable verbose logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**2. Use NiceGUI dev mode:**
```python
# In main.py
ui.run(reload=True)  # Auto-reloads on code changes
```

**3. Check database contents:**
```bash
sqlite3 data/pecs.db
.tables
SELECT * FROM projects;
SELECT * FROM sections LIMIT 5;
.quit
```

**4. Test LLM integration:**
```python
from utils.llm_service import LLMService
llm = LLMService()
result = llm.suggest_flashcards_with_context("Test context")
print(result)
```

**5. Monitor Langfuse (if configured):**
- Visit https://cloud.langfuse.com
- Check traces for LLM calls
- Review token usage and costs

---

## Best Practices for AI Assistants

### When Reading Code

1. **Start with BLUEPRINT.md** - Understand architecture first
2. **Check tests** - They document expected behavior
3. **Look for patterns** - This codebase uses consistent patterns
4. **Respect DRY principle** - Don't duplicate logic

### When Writing Code

1. **Follow existing patterns** - Consistency is key
2. **Write tests first** - Or immediately after implementation
3. **Update documentation** - BLUEPRINT.md for architecture changes
4. **Use type hints** - Makes code self-documenting
5. **Log errors** - Future you will thank you

### When Refactoring

1. **Run tests before** - Establish baseline
2. **Make small changes** - Easier to debug
3. **Run tests after** - Verify nothing broke
4. **Update tests** - If behavior changed intentionally
5. **Update docs** - Keep BLUEPRINT.md current

### When Adding Features

1. **Check if similar exists** - Don't reinvent the wheel
2. **Design for reusability** - Follow DRY principle
3. **Consider testability** - Mock external dependencies
4. **Think about UX** - NiceGUI allows smooth interactions
5. **Document thoroughly** - Code, tests, and BLUEPRINT.md

### Code Review Checklist

- [ ] Follows coding conventions (type hints, docstrings)
- [ ] Uses existing patterns (repository, DRY, etc.)
- [ ] Has tests with good coverage
- [ ] Handles errors gracefully
- [ ] Logs appropriately
- [ ] Updates documentation (BLUEPRINT.md if needed)
- [ ] No breaking changes (or documented migration)
- [ ] Works with Docker deployment
- [ ] PWA still functions (if UI changes)

---

## Voice Input & Text-to-Speech

### Overview

Voice features enable users to speak their thoughts (speech-to-text) and hear AI feedback aloud (text-to-speech). This is crucial for learning - speaking is often more natural than writing.

### Key Components

**1. Voice Service (`utils/voice_service.py`)**

Core service handling both STT and TTS:

```python
from utils.voice_service import get_voice_service

voice_service = get_voice_service()

# Check availability
if voice_service.is_available():
    # Transcribe audio
    transcript = voice_service.transcribe_audio("/path/to/audio.webm")

    # Contextual transcription (better accuracy)
    transcript = voice_service.transcribe_with_context(
        "/path/to/audio.webm",
        section_content="Learning material",
        phase="engage"
    )

    # Generate speech
    audio_path = voice_service.text_to_speech("Hello, world!")

    # Cleanup
    voice_service.cleanup_temp_file(audio_path)
```

**2. Voice Input Component (`nicegui_app/components/voice_input.py`)**

Reusable UI component for adding voice input to textareas:

```python
from nicegui import ui
from nicegui_app.components.voice_input import add_voice_input_buttons

textarea = ui.textarea(label="Your response")

# Add both high-quality and real-time voice buttons
add_voice_input_buttons(
    textarea,
    section_content=section.content,  # Optional context
    phase="engage",  # Optional phase
    on_transcribe=lambda text: save_to_db(text)  # Optional callback
)
```

**3. Integration in PECS Learning (`nicegui_app/pages/pecs_learning.py`)**

Voice input buttons appear automatically in all learning phases. TTS "Read Aloud" buttons appear on all AI feedback.

### Two Voice Input Modes

**Mode 1: High-Quality Recording (Whisper API)**
- Professional transcription (90%+ accuracy)
- Works in all browsers
- Context-aware (uses section content)
- Cost: $0.006/minute

**Mode 2: Real-Time (Web Speech API)**
- Instant transcription
- FREE (no API costs)
- Chrome/Safari only
- Great for quick notes

### Text-to-Speech

- Click "🔊 Read Aloud" on any AI response
- Natural voices (6 options: alloy, echo, fable, onyx, nova, shimmer)
- Cost: $15 per 1M characters
- High-quality MP3 audio

### Configuration

Add to `.env`:

```bash
# Required for voice features
OPENAI_API_KEY=sk-...

# Optional customization
TTS_VOICE=nova  # alloy, echo, fable, onyx, nova, shimmer
TTS_MODEL=tts-1  # tts-1 or tts-1-hd
WHISPER_MODEL=whisper-1
```

### Testing

```bash
pytest tests/test_voice_service.py -v
```

Tests cover:
- Transcription success/failure
- TTS generation
- Context-aware transcription
- Error handling
- Temp file cleanup

### Cost Estimates

**Individual User (~10 recordings/week, 3 min each):**
- Voice input: ~$1.80/month
- TTS (10 reads/week): ~$1.80/month
- **Total: ~$3-5/month**

**100 Active Users:**
- Voice input: ~$18/month
- TTS: ~$45/month
- **Total: ~$63/month**

### Important Notes

- **Context-aware transcription**: Voice service uses section content and phase to build prompts, improving accuracy for technical terms
- **Auto-save**: Transcriptions automatically save to database after completion
- **Privacy**: Audio sent to OpenAI for processing, immediately deleted. No permanent storage.
- **Browser compat**: Whisper works everywhere. Web Speech API works in Chrome/Safari only.

### Common Tasks

**Adding voice input to a new textarea:**

```python
# 1. Import
from nicegui_app.components.voice_input import add_voice_input_buttons

# 2. Create textarea
textarea = ui.textarea(label="Input")

# 3. Add voice buttons
add_voice_input_buttons(textarea)
```

**Adding TTS to AI responses:**

```python
# Use the _render_tts_button helper from pecs_learning.py
def _render_tts_button(self, text: str, unique_id: str):
    """Render text-to-speech button for reading text aloud"""
    # See pecs_learning.py:325-379 for implementation
```

**Customizing voice settings:**

```python
from utils.voice_service import VoiceService

service = VoiceService(
    tts_voice="alloy",  # Choose voice
    tts_model="tts-1-hd",  # Higher quality
)
```

### Troubleshooting

**"Voice features require OpenAI API key"**
- Add `OPENAI_API_KEY` to `.env`
- Restart application

**Transcription fails**
- Check audio file format (webm, mp3, wav supported)
- Verify API key has credits
- Check file size (<25MB)

**TTS not playing**
- Check browser audio permissions
- Verify API key
- Check browser console for errors

### Documentation

- **User guide**: `VOICE_FEATURES.md` - Complete user documentation
- **Code examples**: `tests/test_voice_service.py`
- **Integration**: `nicegui_app/components/voice_input.py`

---

## Additional Resources

### Essential Documentation

1. **BLUEPRINT.md** - Complete technical architecture (READ THIS FIRST!)
2. **README.md** - User-facing documentation
3. **tests/** - Living documentation via test cases
4. **.env.example** - Configuration options

### External Documentation

1. **NiceGUI**: https://nicegui.io/documentation
2. **LiteLLM**: https://docs.litellm.ai/docs/
3. **SQLAlchemy**: https://docs.sqlalchemy.org/
4. **Langfuse**: https://langfuse.com/docs
5. **pytest**: https://docs.pytest.org/

### Getting Help

- Check `BLUEPRINT.md` for architectural questions
- Check tests for usage examples
- Check GitHub issues for known problems
- Enable verbose logging (`LITELLM_VERBOSE=true`)

---

## Conclusion

This codebase is well-structured, thoroughly tested, and follows strong architectural principles. The key to working effectively with it is:

1. **Understand the architecture** (read BLUEPRINT.md)
2. **Follow DRY principle** (use context_builder.py)
3. **Use repository pattern** (database.py for all DB ops)
4. **Write tests** (maintain high coverage)
5. **Document changes** (keep BLUEPRINT.md current)

When in doubt, look at existing code for patterns, check tests for examples, and consult BLUEPRINT.md for architectural guidance.

Happy coding! 🚀
