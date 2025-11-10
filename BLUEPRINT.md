# P.E.C.S. Learning System - Technical Blueprint

**Version**: 2.0 (NiceGUI Architecture)
**Status**: Pre-Alpha
**Last Updated**: November 2025

## System Overview

The P.E.C.S. Learning System is a production-grade, PWA-enabled web application built with NiceGUI that implements a structured active learning methodology. The system has been architectured for scalability, persistence, and mobile-first experience, handling book-length materials with comprehensive testing and AI integration.

## Core Technologies

- **Frontend Framework**: NiceGUI 1.4+ (Pure Python, no Streamlit)
- **UI Architecture**: URL-based routing, reactive components
- **PWA Support**: Installable, offline-capable, app-like experience
- **State Management**: NiceGUI storage + SQLite database
- **Text Processing**: LangChain + Custom hierarchical processor
- **AI Integration**: OpenAI API (Optional, with Langfuse observability)
- **Data Persistence**: SQLite with SQLAlchemy ORM
- **Prompt Management**: YAML files
- **Testing**: pytest (56 tests, 100% coverage on critical modules)
- **Containerization**: Docker & Docker Compose

## Key Architectural Decisions

### 1. NiceGUI Migration (Complete)
**Problem**: Streamlit's page-reload model was limiting UX and mobile experience
**Solution**: Full migration to NiceGUI for SPA-like experience
**Benefits**:
- No page reloads - instant UI updates
- URL-based routing - bookmarkable links
- Better mobile responsiveness
- PWA capabilities (installable app)
- Cleaner async/await patterns
- Multi-user ready architecture

### 2. Vertical Accordion Flow
**Problem**: Tabs allowed jumping around phases too easily, reducing learning engagement
**Solution**: Vertical accordion with sequential unlocking
**Benefits**:
- Forces engagement with each phase in order
- Better focus on current phase
- Progress feels more natural and guided
- Collapsible completed phases save space

### 3. DRY Context Engineering
**Problem**: Context building for AI was duplicated across features, causing bugs (duplicate flashcards)
**Solution**: Single source of truth via `context_builder.py` module
**Benefits**:
- One place to manage AI context
- Prevents duplicate flashcard generation
- Reusable across all AI features
- 100% test coverage on critical logic
- Clear separation of concerns

### 4. Database-First Design
**Problem**: In-memory state limited scalability
**Solution**: SQLite with SQLAlchemy ORM for all persistence
**Benefits**:
- Handles book-length materials (100s of sections)
- Automatic persistence across sessions
- Multi-project support
- Efficient indexed queries
- Easy backup and migration

### 5. Comprehensive Testing
**Problem**: Lack of tests made refactoring risky
**Solution**: Full test suite with 56 tests
**Benefits**:
- Confidence in refactoring
- Prevents regression
- Documents expected behavior
- 100% coverage on context builder

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User's Device                          │
│  ┌───────────────────────────────────────────────────────┐ │
│  │          Browser / PWA Shell                          │ │
│  │  ┌─────────────────────────────────────────────────┐ │ │
│  │  │          NiceGUI Client (JavaScript)            │ │ │
│  │  │  • Reactive UI updates                          │ │ │
│  │  │  • Service Worker (offline support)             │ │ │
│  │  │  • PWA manifest                                 │ │ │
│  │  └─────────────────────────────────────────────────┘ │ │
│  └────────────────────┬────────────────────────────────── │
│                       │ WebSocket                          │
└───────────────────────┼────────────────────────────────────┘
                        │
┌───────────────────────┼────────────────────────────────────┐
│                       │  Server (Python)                   │
│  ┌────────────────────▼──────────────────────────────────┐ │
│  │         NiceGUI Application (FastAPI/Uvicorn)        │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  nicegui_app/main.py                           │ │ │
│  │  │  • PWA setup                                   │ │ │
│  │  │  • Routing                                     │ │ │
│  │  │  • Database initialization                     │ │ │
│  │  │  • Logging setup                               │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  │                                                       │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  nicegui_app/pages/                            │ │ │
│  │  │  • dashboard.py (Project list)                 │ │ │
│  │  │  • content_upload.py (File processing)         │ │ │
│  │  │  • project_view.py (Section list)              │ │ │
│  │  │  • pecs_learning.py (Core learning interface)  │ │ │
│  │  │  • study_mode.py (Flashcard practice)          │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Business Logic Layer (utils/)                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │  │
│  │  │ database.py  │  │context_builder│  │llm_service│ │
│  │  │ (Repository) │  │ (DRY AI ctx)  │  │ (OpenAI) │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │  │
│  │  │ models.py    │  │hierarchical_  │  │file_conv.│  │  │
│  │  │ (SQLAlchemy) │  │ processor     │  │(markitdown│ │  │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Data Layer                                          │  │
│  │  ┌───────────────────────────────────────────────┐  │  │
│  │  │  SQLite Database (data/pecs.db)               │  │  │
│  │  │  • projects                                    │  │  │
│  │  │  • sections (with pecs_data JSON blob)         │  │  │
│  │  │  • flashcards                                  │  │  │
│  │  └───────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  External Services (Optional)                        │  │
│  │  ┌─────────────┐  ┌──────────────────────────────┐  │  │
│  │  │ OpenAI API  │  │ Langfuse (LLM observability) │  │  │
│  │  └─────────────┘  └──────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Application Entry Point

**File**: `nicegui_app/main.py`

**Responsibilities**:
- Initialize logging (console + file: `logs/pecs_learning.log`)
- Setup PWA configuration (manifest, service worker, meta tags)
- Register routes and pages
- Initialize database singleton
- Configure mobile-friendly CSS

**Key Functions**:
- `setup_logging()` - Configures dual-output logging
- `setup_pwa()` - Creates PWA assets and configuration
- `get_database()` - Singleton pattern for DB connection

### 2. Page Components

#### Dashboard (`nicegui_app/pages/dashboard.py`)
**Purpose**: Project management interface
**Features**:
- Create new projects
- View all projects with statistics (sections, flashcards, completion %)
- Delete projects (with confirmation)
- Navigate to project view
- Responsive grid layout (1-3 columns based on screen size)

**UI Pattern**: Card-based grid with statistics and actions

#### Content Upload (`nicegui_app/pages/content_upload.py`)
**Purpose**: Import and process learning material
**Features**:
- Paste text or upload files (.txt, .md, .epub, .pdf, .docx)
- Automatic format conversion (markitdown)
- Hierarchical section detection
- Configurable processing parameters
- Preview before final creation
- Direct database persistence

**Processing Flow**:
1. File upload → markitdown conversion (if needed)
2. Hierarchical processor detects structure
3. Creates sections in database
4. Navigates to project view

#### Project View (`nicegui_app/pages/project_view.py`)
**Purpose**: Section navigation and management
**Features**:
- List all sections in project
- Show completion status
- Navigate to learning interface
- Access study mode
- Project statistics

**UI Pattern**: List view with completion indicators

#### PECS Learning Interface (`nicegui_app/pages/pecs_learning.py`)
**Purpose**: Core learning interface - THE HEART OF THE SYSTEM
**Architecture**: Vertical accordion flow with sequential unlocking

**Key Innovation - DRY Refactoring**:
```python
# Phase configuration (lines 26-77)
self.phase_config = {
    'prime_preview': {
        'index': 0,
        'name': 'Phase 1: Prime & Preview',
        'description': 'First Impressions...',
        'field': 'understanding',
        # ... all phase-specific settings
    },
    # ... other phases
}

# Generic phase renderer (lines 220-289)
def _render_learning_phase(self, phase_key: str):
    """One method handles all 3 learning phases"""
    config = self.phase_config[phase_key]
    # ... renders phase based on config
```

**Phases**:

1. **Phase 1: Prime & Preview**
   - Collapsible content display
   - Understanding text area
   - Save button
   - AI feedback button (opens conversation dialog)
   - Completes when user saves their thoughts

2. **Phase 2: Engage & Explain**
   - Explanation text area
   - Save and AI feedback options
   - Unlocks after Phase 1 completion

3. **Phase 3: Challenge & Connect**
   - Critical thinking text area
   - Save and AI feedback options
   - Unlocks after Phase 2 completion

4. **Phase 4: Solidify Space** (separate section)
   - Manual flashcard creation
   - AI flashcard suggestions (with "Generate More")
   - Completion report (persistent, not dialog)
   - Next section navigation
   - Unlocks after Phase 3 completion

**AI Conversation Pattern**:
- Opens in modal dialog
- Persistent conversation history
- "Continue Conversation" button
- All conversations saved to database

**Context Engineering** (lines 519-611):
```python
def _build_learning_context(include_flashcards=True, include_conversations=False):
    """Single source of truth for AI context"""
    return {
        'content': section.content,
        'understanding': prime_phase_data,
        'explanation': engage_phase_data,
        'critical_thinking': challenge_phase_data,
        'flashcards': [...],  # ONLY committed DB cards!
        'conversations': {...}  # Optional, for completion report
    }

def _format_context_for_flashcards(context):
    """Format specifically for flashcard generation"""
    # Clear visual separators
    # Existing cards with "DO NOT DUPLICATE" warning
    # Student's learning journey
    return formatted_string
```

**Flashcard Dialog** (lines 661-772):
- Shows multiple suggestions
- "Add to deck" for each card (turns green when added)
- "Generate More" button (uses fresh DB context)
- Dialog stays open (no more wasteful regeneration!)
- Uses closure pattern for button handlers

#### Study Mode (`nicegui_app/pages/study_mode.py`)
**Purpose**: Spaced repetition flashcard practice
**Features**:
- One card at a time presentation
- Show question → reveal answer
- Self-grading: "I Knew It" / "Review Again"
- SM-2 algorithm for scheduling
- Progress tracking
- Filter by review status

**Algorithm**: SM-2 (SuperMemo 2)
- Initial interval: 1 day
- Ease factor adjusts based on performance
- Calculates next review date automatically

### 3. Utility Modules

#### Database Layer (`utils/database.py`)
**Purpose**: Repository pattern for all data operations
**Key Classes**:
- `DatabaseRepository` - Main interface for all DB operations

**Key Methods**:
- `create_project(name)` → Project
- `get_all_projects()` → List[Project]
- `create_section(...)` → Section
- `get_sections_by_project(project_id)` → List[Section]
- `update_section_pecs_data(section_id, phase, data)` → bool
- `create_flashcard(...)` → Flashcard
- `update_flashcard_review(flashcard_id, knew_it)` → bool (SM-2 algorithm)
- `get_project_stats(project_id)` → Dict (completion %, flashcard count, etc.)

**Features**:
- Transaction management
- Automatic session handling
- Error logging
- JSON field support for PECS data

#### Models (`utils/models.py`)
**Purpose**: SQLAlchemy ORM models
**Tables**:

1. **Project**
   - `id` (primary key)
   - `name` (unique)
   - `created_at`
   - Relationships: sections, flashcards

2. **Section**
   - `id` (primary key)
   - `project_id` (foreign key)
   - `content` (text)
   - `title` (optional)
   - `order_index` (for sorting)
   - `pecs_data` (JSON blob - stores all phase data)
   - `is_completed` (boolean)
   - `created_at`

3. **Flashcard**
   - `id` (primary key)
   - `project_id` (foreign key)
   - `section_id` (optional foreign key)
   - `question`
   - `answer`
   - `review_count`
   - `ease_factor` (SM-2)
   - `interval_days` (SM-2)
   - `next_review_date`
   - `created_at`
   - `last_reviewed_at`

#### Context Builder (`utils/context_builder.py`) ⭐ NEW
**Purpose**: DRY principle - single source of truth for AI context
**Key Functions**:

1. `build_learning_context(section_content, pecs_data, flashcards, include_conversations)`
   - Gathers all relevant context from section state
   - ONLY includes committed DB flashcards (prevents duplicates)
   - Optionally includes conversation history
   - Returns structured dictionary

2. `format_context_for_flashcards(context)`
   - Formats with clear visual separators
   - Shows existing flashcards with "DO NOT DUPLICATE" warning
   - Includes student's learning journey
   - Returns formatted string for LLM

3. `format_context_for_completion(context)`
   - Includes conversations for full context
   - Shows all phases and flashcards created
   - Returns formatted string for completion report

**Test Coverage**: 100% (18 tests)

#### LLM Service (`utils/llm_service.py`)
**Purpose**: OpenAI API integration with Langfuse observability
**Key Features**:
- Optional Langfuse integration (graceful fallback if not configured)
- YAML-based prompt management
- JSON parsing from markdown code blocks
- Comprehensive error handling

**Key Methods**:
- `suggest_flashcards_with_context(formatted_context)` - NEW preferred method
- `suggest_flashcards(...)` - Legacy method (still supported)
- `analyze_section_understanding(...)`
- `analyze_explanation(...)`
- `analyze_critical_thinking(...)`

**JSON Extraction**:
```python
def extract_json_from_markdown(content: str) -> str:
    """Handles LLMs wrapping JSON in ```json blocks"""
    # Extracts JSON from various markdown patterns
    # Prevents JSON parsing errors
```

#### Hierarchical Processor (`utils/hierarchical_processor.py`)
**Purpose**: Intelligent document structure detection
**Features**:
- Detects chapters, sections, headings (Markdown ## markers)
- Custom section markers support (`--- Section N ---`)
- Fallback to chunking if no structure detected
- Configurable size limits and overlap
- LangChain integration for text splitting

**Processing Logic**:
1. Try hierarchy detection (headings, markers)
2. If no structure, fall back to semantic chunking
3. Create sections maintaining document order
4. Generate titles from content or position

#### File Converters (`utils/file_converters.py`)
**Purpose**: Convert various formats to text
**Supported Formats**:
- Text (.txt, .md) - Direct read
- EPUB (.epub) - markitdown conversion
- PDF (.pdf) - markitdown conversion
- Word (.docx, .doc) - markitdown conversion

**Key Function**:
```python
def convert_file_to_text(uploaded_file) -> str:
    """Convert any supported format to plain text"""
    # Uses markitdown library
    # Handles various result object shapes
    # Returns clean text content
```

**Test Coverage**: 87% (10 tests)

## Data Flow

### Learning Flow
```
1. User uploads content
   ↓
2. File converted to text (if needed)
   ↓
3. Hierarchical processor detects structure
   ↓
4. Sections created in database
   ↓
5. User navigates to section
   ↓
6. PECS learning interface loads:
   - Prime: User records first impressions
   - Engage: User explains in own words
   - Challenge: User thinks critically
   - Solidify: User creates flashcards
   ↓
7. All data auto-saved to section.pecs_data (JSON)
   ↓
8. Section marked complete
   ↓
9. Move to next section
```

### AI Interaction Flow
```
1. User clicks "AI Feedback" or "Generate Flashcards"
   ↓
2. System calls _build_learning_context()
   - Gathers: content, understanding, explanation, critical thinking
   - Fetches: ONLY committed flashcards from database
   - Optionally: conversation history
   ↓
3. Context formatted for specific use case
   - format_context_for_flashcards(): Clear separators, duplicate warnings
   - format_context_for_completion(): Include conversations
   ↓
4. LLM API call (via llm_service)
   - Langfuse tracks call (if configured)
   - JSON response parsed (handles markdown wrappers)
   ↓
5. Response processed and displayed
   - Feedback: Shown in dialog
   - Flashcards: Shown in persistent dialog
   - Completion: Saved to database, always visible
   ↓
6. User interaction saved to database
   - Conversations: Appended to phase data
   - Flashcards: Created in database
   - Completion: Stored in solidify_space
```

### Flashcard Study Flow
```
1. User enters study mode
   ↓
2. System fetches flashcards (filtered by due date if chosen)
   ↓
3. Present one card at a time:
   - Show question
   - User thinks/recalls
   - Reveal answer
   ↓
4. User self-grades: "I Knew It" / "Review Again"
   ↓
5. SM-2 algorithm updates card:
   - Adjust ease_factor
   - Calculate next interval
   - Update next_review_date
   ↓
6. Save to database
   ↓
7. Move to next card
```

## Key Design Patterns

### 1. Repository Pattern
All database operations go through `DatabaseRepository` - no direct SQLAlchemy session management in UI code.

### 2. DRY (Don't Repeat Yourself)
- **Context Building**: One function (`build_learning_context()`) used everywhere
- **Phase Rendering**: Generic `_render_learning_phase()` handles all 3 phases
- **Format Functions**: Separate formatters for different AI use cases

### 3. Closure Pattern
Used in flashcard dialog for button handlers:
```python
def make_add_handler(idx, suggestion):
    def handler():
        # Has access to idx and suggestion
        db.create_flashcard(...)
        added_indices.add(idx)
        render_suggestions()  # Re-render UI
    return handler
```

### 4. Configuration over Code
- Phase configuration in dictionary (not hardcoded)
- YAML files for AI prompts
- Environment variables for API keys

### 5. Async/Await for LLM Calls
```python
async def generate_flashcards():
    # Run LLM call in thread pool
    result = await asyncio.to_thread(
        llm_service.suggest_flashcards_with_context,
        formatted_context
    )
    # UI remains responsive
```

## Testing Strategy

### Test Coverage
- **Total Tests**: 56
- **Passing**: 100%
- **Coverage Highlights**:
  - `context_builder.py`: 100%
  - `file_converters.py`: 87%
  - `database.py`: 62%
  - `llm_service.py`: 52%

### Test Files
1. `test_context_builder.py` (18 tests) - Context engineering
2. `test_llm_service.py` (18 tests) - AI integration
3. `test_database.py` (10 tests) - Data persistence
4. `test_file_converters.py` (10 tests) - Format conversion

### Mock Strategy
- LLM API calls: Mocked with `unittest.mock`
- File I/O: Mocked to avoid file system dependencies
- Database: Temporary in-memory SQLite per test

See `TESTING.md` for comprehensive documentation.

## Security Considerations

### API Key Management
- Keys stored in `.env` file (never committed)
- Environment variable fallback
- Optional Langfuse keys

### Data Privacy
- All data stored locally in SQLite
- No external data transmission (except LLM API calls)
- User has full control over data

### Input Validation
- File size limits (handled by markitdown)
- SQL injection protection (SQLAlchemy ORM)
- JSON schema validation for PECS data

## Performance Optimizations

### Database
- Indexed columns (project_id, section_id, next_review_date)
- Batch operations where possible
- Lazy loading of relationships

### UI
- Dynamic rendering (only visible components)
- Collapsible sections to reduce DOM size
- Pagination for large section lists

### LLM Calls
- Non-blocking async calls
- Loading indicators
- Error recovery with user feedback

## Deployment

### Docker
- Single Dockerfile for production
- docker-compose.yml for local development
- Health checks included
- Volume mounting for database persistence

### Supported Platforms
- Railway (recommended, free tier)
- Render (free tier with sleep)
- DigitalOcean ($5/month)
- Self-hosted VPS ($5/month)
- Google Cloud Run (pay-per-use)

### PWA Features
- Installable on all devices
- Offline-capable (service worker)
- App-like experience (no browser UI)
- Manifest.json with icons

## Future Enhancements

### Planned (High Priority)
- [ ] Export flashcards to Anki format
- [ ] Backup/restore functionality
- [ ] Advanced analytics dashboard
- [ ] Multiple LLM providers (Anthropic, local models)

### Considered (Medium Priority)
- [ ] User authentication (NiceGUI supports OAuth)
- [ ] Collaborative study groups
- [ ] Custom prompt editor
- [ ] Image support in flashcards
- [ ] Audio recording for explanations

### Long-term
- [ ] Mobile native apps (React Native with same backend)
- [ ] Browser extension for quick captures
- [ ] Integration with note-taking apps (Obsidian, Notion)
- [ ] AI tutor mode with active questioning

## Known Issues & Limitations

### Current Limitations
- Single-user (no authentication yet)
- No real-time collaboration
- Large files (>100MB) process slowly
- Limited markdown rendering in content areas

### Pre-Alpha Status
- No backward compatibility guarantees
- Database schema may change
- Breaking changes possible

## Contributing

### Development Setup
1. Clone repository
2. Create `.env` with API keys
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests: `pytest`
5. Start app: `python nicegui_app/main.py`

### Code Standards
- Type hints required
- Docstrings (Google style)
- Tests for new features
- Update BLUEPRINT.md for architecture changes
- Follow DRY principles

### Testing Requirements
- Add tests for new features
- Maintain >80% coverage on new code
- Use mocks for external services
- Follow existing test patterns

## Documentation

- **README.md**: User-facing documentation and quick start
- **BLUEPRINT.md**: This file - technical architecture
- **TESTING.md**: Test coverage and strategies
- **Code Comments**: Inline documentation for complex logic
- **Docstrings**: All public functions and classes

---

**Document Maintenance**: Update this blueprint whenever:
- Architecture changes significantly
- New major features added
- Design patterns change
- Database schema modified
- External dependencies added/removed

**Last Review**: November 2025 (NiceGUI migration complete)
