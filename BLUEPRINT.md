# P.E.C.S. Learning System - Technical Blueprint

## System Architecture

### Overview
The P.E.C.S. Learning System is a production-grade Streamlit-based web application that implements a structured learning methodology through four phases: Prime, Engage, Challenge, and Solidify. The system has been architected for scalability, persistence, and professional use, with the ability to handle book-length materials over extended study periods.

### Core Technologies
- **Frontend Framework**: Streamlit (Python)
- **State Management**: Streamlit Session State (for UI state) + SQLite Database (for persistence)
- **Text Processing**: LangChain + Custom Hierarchical Processor
- **AI Integration**: OpenAI API (Optional)
- **Data Persistence**: SQLite Database (SQLAlchemy ORM)
- **Prompt Management**: YAML
- **Testing**: pytest
- **Containerization**: Docker & Docker Compose

### Key Architectural Decisions

#### Database-Backed Architecture
- **Problem Solved**: The original prototype stored all data in-memory, limiting scalability to small texts
- **Solution**: Full migration to SQLite database with SQLAlchemy ORM
- **Benefits**: 
  - Handles book-length materials (hundreds of sections)
  - Automatic persistence across sessions
  - Multi-project support
  - Efficient queries with indexing

#### Hierarchical Content Processing
- **Problem Solved**: Flat chunking doesn't respect document structure
- **Solution**: Intelligent section detection (chapters, headings, custom markers)
- **Benefits**:
  - Maintains logical document structure
  - Better navigation and organization
  - Respects semantic boundaries

#### Tab-Based PECS Workflow
- **Problem Solved**: Linear phase progression was restrictive
- **Solution**: Tabbed interface allows non-linear navigation between phases
- **Benefits**: 
  - Jump between phases easily
  - Review previous work while writing new content
  - Better UX for iterative learning

### System Components

#### 1. Application Entry Point (`app.py`)
- Main Streamlit application orchestrator
- Manages project selection and navigation
- Routes to dashboard, content upload, PECS learning, or study mode
- Uses `@st.cache_resource` for database connection caching

#### 2. Core Components (`components/`)

##### `project_dashboard.py`
- **Purpose**: Multi-project management interface
- **Features**:
  - Create new projects
  - View all projects with statistics
  - Delete projects
  - Navigate to specific projects
- **UI**: Grid layout with project cards showing metrics

##### `content_upload_new.py`
- **Purpose**: Import learning material with hierarchical processing
- **Features**:
  - Paste text or upload files (.txt, .md, .epub, .pdf, .docx, .doc)
  - Automatic format conversion using markitdown (EPUB, PDF, Word)
  - Configurable section detection
  - Hierarchical processing options
  - Preview of created sections
- **Integration**: Uses `hierarchical_processor.py`, `file_converters.py`, and saves directly to database

##### `pecs_tabs.py`
- **Purpose**: Unified PECS learning interface with tabs
- **Features**:
  - Four tabs for Prime, Engage, Challenge, Solidify phases
  - Auto-save functionality (manual save buttons)
  - AI feedback integration
  - Flashcard creation inline
  - Section completion tracking
- **Key Innovation**: All phases accessible simultaneously via tabs

##### `section_navigator.py`
- **Purpose**: Sidebar navigation for sections within a project
- **Features**:
  - Searchable section list
  - Pagination for large numbers of sections
  - Completion indicators
  - Quick section preview
- **Performance**: Handles hundreds of sections efficiently

##### `study_mode.py`
- **Purpose**: Interactive spaced repetition study session
- **Features**:
  - One-card-at-a-time presentation
  - Self-grading (I Knew It / Review Again)
  - SM-2 algorithm for spaced repetition
  - Progress tracking
  - Filter by review status
- **Algorithm**: Implements SM-2 spaced repetition with ease factors

##### Legacy Components (kept for reference)
- `content_upload.py`: Old flat chunking approach
- `prime_module.py`, `engage_module.py`, `challenge_module.py`, `solidify_module.py`: Old linear phase modules
- `recall_list_viewer.py`: Old static flashcard list

#### 3. Utility Modules (`utils/`)

##### `database.py` (NEW)
```python
class DatabaseRepository:
    # Project operations
    def create_project(name: str) -> Project
    def get_project(project_id: int) -> Project
    def get_all_projects() -> List[Project]
    
    # Section operations
    def create_section(project_id, content, title, order_index) -> Section
    def get_sections_by_project(project_id) -> List[Section]
    def update_section_pecs_data(section_id, phase, data) -> bool
    def mark_section_completed(section_id, completed) -> bool
    
    # Flashcard operations
    def create_flashcard(project_id, question, answer, section_id) -> Flashcard
    def get_flashcards_by_project(project_id) -> List[Flashcard]
    def get_flashcards_for_review(project_id) -> List[Flashcard]
    def update_flashcard_review(flashcard_id, knew_it) -> bool
```
- **Purpose**: Clean repository pattern for database operations
- **Benefits**: 
  - Type-safe database access
  - Automatic transaction management
  - Error handling
  - Caching support

##### `models.py` (NEW)
```python
class Project(Base):
    id, name, created_at, updated_at
    sections (relationship)
    flashcards (relationship)

class Section(Base):
    id, project_id, title, content, order_index
    pecs_data (JSON), is_completed, completed_at
    project (relationship), flashcards (relationship)

class Flashcard(Base):
    id, project_id, section_id
    question, answer
    last_reviewed, review_count, ease_factor
    interval_days, next_review, is_mastered
```
- **Purpose**: SQLAlchemy ORM models
- **Features**: Relationships, indexes, JSON storage for flexibility

##### `hierarchical_processor.py` (NEW)
```python
class HierarchicalContentProcessor:
    def detect_sections(text: str) -> List[Tuple[int, str, int]]
    def split_into_sections(text, min_size, max_size, overlap) -> List[Tuple[str, Optional[str]]]
    def process_for_user(text, ...) -> List[Tuple[str, Optional[str]]]
```
- **Purpose**: Intelligent section detection and splitting
- **Patterns**: Detects chapters, numbered sections, markdown headers, custom markers
- **Fallback**: LangChain chunking when no structure detected

##### `content_processor.py`
- Still used for basic text loading from files
- Handles encoding and validation

##### `file_converters.py` (NEW)
```python
def convert_file_to_text(uploaded_file) -> Optional[str]
def is_supported_file_type(filename: str) -> bool
def get_file_type_description() -> str
```
- **Purpose**: Convert EPUB, PDF, and Word documents to text using markitdown
- **Features**:
  - Uses markitdown library for format conversion
  - Handles multiple result formats from markitdown
  - Temporary file management
  - Error handling and user feedback
- **Supported Formats**: EPUB, PDF, DOCX, DOC (via markitdown)

##### `llm_service.py`
- **Unchanged**: Still provides AI feedback for all PECS phases
- Uses YAML prompt configuration
- Graceful degradation when API unavailable

##### `migration.py` (NEW)
- **Purpose**: Import old JSON session files into new database
- **Features**: Converts chunks to sections, migrates PECS data, imports flashcards
- **UI**: Streamlit interface for file upload and project naming

##### Legacy Utilities (kept for compatibility)
- `session_manager.py`: Old session state initialization
- `persistence.py`: Old JSON export/import (superseded by database)

### Data Architecture

#### Database Schema

**Projects Table**
- Primary key: `id`
- Fields: `name` (unique), `created_at`, `updated_at`
- Relationships: One-to-many with Sections and Flashcards

**Sections Table**
- Primary key: `id`
- Foreign keys: `project_id` (CASCADE delete)
- Fields: `title`, `content` (TEXT), `order_index`, `pecs_data` (JSON), `is_completed`, `completed_at`
- Indexes: `(project_id, order_index)` for efficient queries
- Relationships: Many-to-one with Project, One-to-many with Flashcards

**Flashcards Table**
- Primary key: `id`
- Foreign keys: `project_id`, `section_id` (both CASCADE delete)
- Fields: `question`, `answer`, `last_reviewed`, `review_count`, `ease_factor`, `interval_days`, `next_review`, `is_mastered`, `created_at`
- Indexes: `(project_id, section_id)`, `next_review` for review queries
- Relationships: Many-to-one with Project and Section

#### PECS Data Structure (Stored as JSON in Sections)
```json
{
  "prime_preview": {
    "initial_thoughts": "string",
    "prior_knowledge": "string",
    "questions": "string"
  },
  "engage_explain": {
    "explanation": "string",
    "analogy": "string"
  },
  "challenge_connect": {
    "critical_questions": "string",
    "connections": "string",
    "new_analogies": "string"
  },
  "solidify_space": {
    "application": "string"
  }
}
```

### AI Integration

#### Prompt Management
- **Location**: `utils/prompts.yaml`
- **Structure**: Organized by module and feature
- **Format**: System + User prompts with template variables

#### AI Features by Module
1. **Prime Module**
   - Section understanding analysis
   - Question quality feedback

2. **Engage Module**
   - Explanation clarity analysis
   - Analogy effectiveness feedback

3. **Challenge Module**
   - Critical thinking analysis
   - Connection relevance feedback

4. **Solidify Module**
   - Flashcard quality analysis
   - Application idea feedback
   - Flashcard generation suggestions

#### API Integration
- **Model**: GPT-3.5-turbo (cost-effective default)
- **Configuration**: Via `.streamlit/secrets.toml`
- **Graceful Degradation**: App works fully without API key

### Testing

#### Test Structure
```
tests/
├── __init__.py
├── test_database.py       # Database repository tests
└── test_hierarchical_processor.py  # Content processing tests
```

#### Test Coverage
- **Database Operations**: CRUD for Projects, Sections, Flashcards
- **Content Processing**: Section detection, splitting, fallback chunking
- **Spaced Repetition**: Review algorithm, interval calculation
- **Migration**: JSON import functionality

#### Running Tests
```bash
pytest
pytest --cov=utils --cov-report=html
```

### Deployment

#### Docker Containerization

**Dockerfile**
- Base: Python 3.10-slim
- Installs system dependencies (gcc, curl)
- Copies requirements and installs Python packages
- Creates data directory for SQLite persistence
- Exposes port 8501
- Health check endpoint

**docker-compose.yml**
- Service definition for pecs-app
- Volume mounting for database persistence (`./data:/app/data`)
- Port mapping: 8501:8501
- Health check configuration
- Restart policy

#### Local Development
```bash
# Traditional
streamlit run app.py

# Docker
docker-compose up
```

#### Production Deployment
- **Streamlit Community Cloud**: One-click deploy from GitHub
- **Requirements**: 
  - Database file stored in persistent volume
  - Secrets configured via Streamlit Cloud UI
  - No additional infrastructure needed

### Error Handling

#### Database Errors
- All database operations wrapped in try-except
- Rollback on errors
- User-friendly error messages
- Validation for required fields

#### Content Processing Errors
- File encoding fallbacks
- Empty input validation
- Section detection failures fall back to chunking

#### LLM Service Errors
- API key validation
- Network timeout handling
- Graceful degradation (app works without AI)

### Performance Considerations

#### Database Optimization
- Indexed queries for common patterns
- Efficient relationship loading
- Pagination for large section lists
- Cached database connection (`@st.cache_resource`)

#### Content Processing
- Lazy loading of section content
- Efficient regex patterns for section detection
- Configurable chunk sizes to balance performance

#### UI Responsiveness
- Streamlit's native optimization
- Minimal reruns through careful state management
- Progressive loading for large projects

### Security & Privacy

#### Data Storage
- **Local First**: All data stored locally in SQLite
- **No Cloud Sync**: By default, no external data transmission
- **Optional AI**: AI features require explicit API key

#### Data Export/Import
- Migration utility for moving data
- Future: JSON export for backup/portability

### Future Enhancements

#### Potential Features
1. **Advanced Analytics**
   - Learning progress visualization
   - Time spent per section
   - Flashcard performance metrics

2. **Enhanced AI**
   - Multiple LLM provider support
   - Custom prompt templates
   - Batch feedback generation

3. **Collaboration**
   - Shared projects (optional)
   - Export/import flashcards
   - Study groups

4. **Mobile Optimization**
   - Responsive design improvements
   - Touch-friendly study mode
   - Offline support

5. **Advanced Spaced Repetition**
   - Alternative algorithms (FSRS)
   - Visual progress graphs
   - Study streak tracking

### Migration Path

#### From Old JSON Format
1. Use `utils/migration.py` migration utility
2. Upload old JSON session file
3. Specify project name
4. Automatic conversion to database format

#### Backward Compatibility
- Old components preserved in codebase
- Old JSON export format can be imported
- Gradual migration path for existing users

### Development Guidelines

#### Code Style
- PEP 8 compliance
- Type hints for all function signatures
- Docstrings for public functions/classes
- Modular, focused functions

#### Testing Requirements
- Unit tests for all utility functions
- Integration tests for database operations
- Test coverage target: >80% for utils/

#### Contribution Guidelines
- All changes must include tests
- Update BLUEPRINT.md for architectural changes
- Follow existing patterns and conventions
