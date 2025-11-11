# P.E.C.S. Learning System 📚

A production-grade, PWA-enabled learning application built with NiceGUI that guides users through a structured learning methodology (Prime, Engage, Challenge, Solidify) for any text material—from articles to entire books.

**✨ Pure NiceGUI Architecture**
- ✅ Mobile-responsive PWA (installable on any device)
- ✅ No page reloads - smooth, app-like experience
- ✅ URL-based routing - bookmarkable links
- ✅ Multi-user ready architecture
- ✅ Comprehensive test coverage

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![NiceGUI](https://img.shields.io/badge/NiceGUI-1.4+-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)
![PWA](https://img.shields.io/badge/PWA-Ready-purple.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)

## 🎯 Features

### Core Features
- **📚 Multi-Project Support**: Create and manage multiple study projects
- **📄 Multi-Format Support**: Import from Text, Markdown, EPUB, PDF, and Word documents
- **🔍 Hierarchical Content Processing**: Automatically detects chapters and sections
- **💾 Automatic Persistence**: All progress saved to SQLite database
- **📑 Scalable Navigation**: Handle hundreds of sections efficiently
- **📊 Progress Tracking**: Visual indicators for completion and statistics

### P.E.C.S. Learning Phases
- **P - Prime & Preview**: First impressions and initial understanding
- **E - Engage & Explain**: Deep reading with interactive AI conversation
- **C - Challenge & Connect**: Critical thinking and making connections
- **S - Solidify & Space**: Create flashcards for spaced repetition

### Interactive Study Mode
- **🎴 Spaced Repetition**: SM-2 algorithm for optimal review scheduling
- **📈 Self-Grading**: "I Knew It" / "Review Again" buttons
- **🎯 Smart Filtering**: Study due cards, all cards, or mastered cards
- **📊 Progress Statistics**: Track reviews, ease factors, and intervals
- **📤 Anki Export**: Direct API push via AnkiConnect or file-based export

### AI-Enhanced Features (Optional)
- **✍️ Context-Aware Feedback**: AI feedback based on your complete learning journey
- **💡 Smart Flashcard Generation**: AI suggestions that avoid duplicates
- **🔍 Critical Analysis**: AI feedback on thinking and connections
- **📈 LLM Observability**: Optional Langfuse integration for tracking usage and costs

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd PECS-learner

# Start the application
docker-compose up --build

# Access at http://localhost:8080
# Install as PWA: Click "Install" button in browser
```

### Option 2: Local Installation

```bash
# Clone and setup
git clone <repository-url>
cd PECS-learner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python nicegui_app/main.py

# Access at http://localhost:8080
```

## 📋 Requirements

- Python 3.11+
- SQLite 3 (included with Python)
- Optional: OpenAI API key for AI features

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Server configuration
HOST=0.0.0.0
PORT=8080

# AI Features (optional)
OPENAI_API_KEY=your-key-here

# LLM Observability (optional)
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_HOST=https://cloud.langfuse.com

# Storage
NICEGUI_STORAGE_PATH=./data/nicegui_storage
```

### Langfuse Setup (Optional)

[Langfuse](https://langfuse.com/) provides observability for LLM calls:

1. Sign up at https://cloud.langfuse.com
2. Create a new project
3. Copy your keys to `.env` file
4. All LLM calls will be tracked automatically

Benefits:
- Track token usage and costs
- Debug LLM responses
- Monitor performance
- Analyze conversation quality

## 📖 Usage Guide

### 1. Create a Project
- Click "New Project" on dashboard
- Enter a project name (e.g., "Python Programming")

### 2. Upload Content
- Click "Upload Content"
- Paste text or upload file (.txt, .md, .epub, .pdf, .docx)
- System automatically detects structure
- Click "Process & Create Sections"

### 3. Learn with P.E.C.S.
- Select a section from project view
- Work through the vertical learning flow:
  - **Prime**: Record first impressions
  - **Engage**: Explain in your own words (with AI conversation)
  - **Challenge**: Think critically and make connections
  - **Solidify**: Create flashcards and get completion summary
- Progress unlocks sequentially
- All work auto-saved to database

### 4. Study with Spaced Repetition
- Click "Study Mode" from project view
- Review flashcards with self-grading
- System schedules optimal review intervals

### 5. Export to Anki
- Click "Export to Anki" button from project view (appears when you have flashcards)
- Choose your export method:
  - **AnkiConnect (Direct)**: Push cards directly to Anki via API (requires setup)
  - **File Export**: Download .apkg file to double-click import (no setup needed)
- Enter deck name and click "Export"

#### AnkiConnect Setup (for direct API export)
1. Install AnkiConnect add-on in Anki:
   - Open Anki → Tools → Add-ons → Browse & Install
   - Enter code: `2055492159`
   - Restart Anki
2. Make sure Anki is running before exporting
3. Cards will appear immediately in your chosen deck

#### File Export (alternative method)
1. Choose "File Export" option
2. Download the generated .apkg file
3. Double-click the .apkg file to automatically import into Anki
4. All cards will be imported with their tags into the specified deck

## 🗂️ Project Structure

```
PECS-learner/
├── nicegui_app/              # Main NiceGUI application
│   ├── main.py              # Entry point with PWA setup
│   ├── config.py            # Configuration
│   ├── pages/               # Page implementations
│   │   ├── dashboard.py     # Project dashboard
│   │   ├── content_upload.py
│   │   ├── project_view.py
│   │   ├── pecs_learning.py # Core learning interface
│   │   └── study_mode.py    # Flashcard practice
│   └── static/              # PWA assets (icons, manifest)
├── utils/                    # Shared utilities
│   ├── database.py          # SQLAlchemy repository
│   ├── models.py            # ORM models
│   ├── llm_service.py       # AI integration
│   ├── context_builder.py   # DRY context engineering
│   ├── anki_export.py       # Anki export (API + file)
│   ├── hierarchical_processor.py
│   ├── file_converters.py
│   └── migration.py         # JSON import utility
├── tests/                    # Test suite (56 tests)
│   ├── test_database.py
│   ├── test_llm_service.py
│   ├── test_context_builder.py
│   ├── test_file_converters.py
│   └── ...
├── data/                     # SQLite database (auto-created)
├── logs/                     # Application logs
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── BLUEPRINT.md             # Technical architecture
├── TESTING.md               # Test documentation
└── README.md               # This file
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=utils --cov-report=term-missing

# Specific test file
pytest tests/test_context_builder.py -v

# Run fast tests only (excludes langchain-dependent)
pytest tests/test_llm_service.py tests/test_context_builder.py tests/test_database.py
```

**Test Coverage:**
- 56 tests passing
- Context builder: 100% coverage
- File converters: 87% coverage
- Database operations: 62% coverage
- LLM service: 52% coverage

See `TESTING.md` for detailed test documentation.

## 📋 Logging and Debugging

Comprehensive logging to both console and file:

**Log Locations:**
- **Console**: Terminal output
- **File**: `logs/pecs_learning.log` (auto-created)

**Log Levels:**
- `INFO`: Application flow and events
- `DEBUG`: LLM calls, database operations
- `WARNING`: Potential issues
- `ERROR`: Errors with stack traces

**Viewing Logs:**
```bash
# Watch logs in real-time
tail -f logs/pecs_learning.log

# View errors only
grep ERROR logs/pecs_learning.log

# View LLM activity
grep "llm_service" logs/pecs_learning.log
```

## 🐳 Docker Usage

### Local Development

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

The `data/` directory is mounted as a volume for database persistence.

### Production Deployment

Deploy to any platform that supports Docker:

**Recommended Platforms:**

1. **Railway** (Easiest)
   - Free tier: 500 hours/month
   - Automatic HTTPS
   - One-click deploy
   ```bash
   railway login
   railway init
   railway up
   ```

2. **Render** (Free tier with sleep)
   - Connect GitHub repo
   - Auto-deploy on push
   - Free tier available

3. **DigitalOcean App Platform** ($5/month)
   - Always-on
   - Easy scaling
   - Reliable

4. **Self-hosted VPS** ($5/month)
   - Full control
   - Use Caddy for automatic HTTPS
   ```bash
   # Install Docker on Ubuntu
   curl -fsSL https://get.docker.com | sh

   # Clone and run
   git clone <repo>
   cd PECS-learner
   docker-compose up -d
   ```

**Environment Variables for Production:**
```bash
OPENAI_API_KEY=your-key
NICEGUI_STORAGE_PATH=/app/data/nicegui_storage
PORT=8080
```

**Making it a PWA:**
The app is already configured as a PWA! Users can install it on any device:

- **iPhone/iPad**: Share → Add to Home Screen
- **Android**: Menu → Install app
- **Desktop**: Click install icon in address bar

## 🏗️ Architecture Highlights

### DRY (Don't Repeat Yourself) Principles
- **Context Engineering**: Single source of truth for AI context via `context_builder.py`
- **Phase Rendering**: Generic renderer for all learning phases
- **Format Functions**: Separate formatters for different use cases

### Database-First Design
- **Scalability**: Handles book-length materials
- **Persistence**: Automatic SQLite storage
- **Performance**: Indexed queries

### Smart AI Context
- Includes full learning journey (all phases)
- ONLY committed flashcards (prevents duplicates)
- Conversation history when needed
- Clear visual separators for AI comprehension

### Testing Strategy
- Unit tests for utilities
- Integration tests for workflows
- Mock-based LLM testing
- 100% coverage on critical modules

## 🔄 Migration from Old Format

If you have old JSON session files:

1. Navigate to dashboard
2. Look for migration option
3. Upload `pecs_session.json`
4. Specify project name
5. Click "Import"

All chunks, notes, and flashcards will be migrated to the new database.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests (see `TESTING.md`)
5. Update `BLUEPRINT.md` if needed
6. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [NiceGUI](https://nicegui.io/)
- Database: [SQLAlchemy](https://www.sqlalchemy.org/)
- AI: [OpenAI](https://openai.com/)
- File conversion: [markitdown](https://github.com/microsoft/markitdown)
- Testing: [pytest](https://pytest.org/)

## 📚 Documentation

- **Architecture**: `BLUEPRINT.md` - Complete system design
- **Testing**: `TESTING.md` - Test coverage and strategies
- **Code**: Inline docstrings (Google style)
- **API**: Database methods documented in `utils/database.py`

## 🐛 Known Limitations

- Large files (>100MB) may take time to process
- AI features require internet connection
- Pre-alpha: No backward compatibility guaranteed

## 🔮 Roadmap

- [x] Export flashcards to Anki (AnkiConnect API + .apkg export)
- [ ] Export flashcards to Quizlet
- [ ] Advanced analytics dashboard
- [ ] Multiple LLM provider support
- [ ] Custom prompt template editor
- [ ] Authentication & multi-user support
- [ ] Collaborative study groups

---

**Made with ❤️ for deep, structured learning**

For questions or issues, please open a GitHub issue.
