# 📚 P.E.C.S. Learning System

> **A production-grade, AI-powered learning platform that transforms how you study any material—from articles to entire books**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![NiceGUI](https://img.shields.io/badge/NiceGUI-1.4+-green.svg)](https://nicegui.io/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)](https://www.sqlalchemy.org/)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-1.50+-purple.svg)](https://github.com/BerriAI/litellm)
[![PWA](https://img.shields.io/badge/PWA-Ready-purple.svg)](https://web.dev/progressive-web-apps/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-56%20passing-brightgreen.svg)](./TESTING.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

---

## 🌟 What Makes This Special?

**P.E.C.S.** (Prime → Engage → Challenge → Solidify) is a **scientifically-backed learning methodology** combined with modern AI and spaced repetition. Built entirely in **pure Python with NiceGUI**, this isn't just another note-taking app—it's a comprehensive learning companion that:

✨ **Uses proven learning science** (active recall, spaced repetition, Feynman technique)
🤖 **Leverages AI for personalized feedback** (supports 100+ models via LiteLLM)
📱 **Works anywhere** (PWA installable on any device)
🔄 **Generates intelligent study notes** with rolling context across sections
📊 **Tracks your progress** with SM-2 spaced repetition algorithm
🐳 **Deploys in minutes** with Docker Compose

---

## 🚀 Quick Start (60 seconds)

```bash
# Clone and run with Docker
git clone https://github.com/yourusername/PECS-learner.git
cd PECS-learner

# Start the app (includes database, AI, PWA—everything!)
docker-compose up -d

# Access at http://localhost:8080
# Install as PWA by clicking the install button in your browser
```

That's it! No complex setup, no configuration hell. Just run and learn.

---

## 🎯 Key Features

### 🧠 Intelligent Learning Workflow

**The P.E.C.S. Methodology:**
1. **Prime & Preview** - Activate prior knowledge and set learning intentions
2. **Engage & Explain** - Deep reading with AI-powered conversational feedback
3. **Challenge & Connect** - Critical thinking, connections, and synthesis
4. **Solidify & Space** - Create flashcards and use spaced repetition

Each phase unlocks sequentially, guiding you through a proven learning process.

### 🤖 AI-Powered Features (NEW!)

- **Multi-Provider LLM Support** via [LiteLLM](https://github.com/BerriAI/litellm)
  - OpenAI (GPT-4o, GPT-5, etc.)
  - Anthropic (Claude 3 Opus, Sonnet, Haiku)
  - Google (Gemini Pro, 1.5 Pro)
  - **100+ models** from any provider

- **Rolling Window Context** - Maintains cumulative summaries across sections
  - Preserves narrative flow for book-length materials
  - Helps AI understand connections between chapters
  - Automatically generated as you progress

- **AI Study Notes Generation** - Creates Feynman-style study notes
  - Focus on concepts, connections, and diagrams (not summaries!)
  - Incorporates your full learning journey (all PECS phases)
  - Non-blocking UI with real-time progress
  - Per-section and batch generation modes

- **Smart Flashcard Suggestions** - Context-aware recommendations
  - Prevents duplicates by tracking existing cards
  - Based on your learning journey and material
  - Instant AI feedback on created flashcards

- **LLM Observability** - Optional Langfuse integration
  - Track token usage and costs
  - Monitor AI response quality
  - Debug and optimize prompts

### 📚 Content Management

- **Multi-Format Support**: Import from Text, Markdown, EPUB, PDF, Word
- **Hierarchical Processing**: Auto-detects chapters and sections
- **Multi-Project Support**: Manage multiple books/courses simultaneously
- **Scalable Architecture**: Handle hundreds of sections efficiently

### 🎴 Spaced Repetition Study Mode

- **SM-2 Algorithm** - Scientifically-proven review scheduling
- **Self-Grading System** - "I Knew It" / "Review Again" buttons
- **Smart Filtering** - Study due cards, all cards, or mastered cards
- **Progress Analytics** - Track review counts, ease factors, and mastery

### 📤 Export & Integration

- **Anki Integration** - Two export methods:
  - **AnkiConnect API** - Direct push to Anki (requires add-on)
  - **File Export** - Download `.apkg` files for manual import
- **Markdown Study Notes** - Export generated notes
- **Portable Database** - SQLite for easy backup/migration

### 📱 Modern PWA Experience

- **Installable** - Add to home screen on any device (iOS, Android, Desktop)
- **Offline-Capable** - Database stored locally
- **No Page Reloads** - Smooth, app-like navigation
- **Mobile-Responsive** - Works beautifully on phones and tablets
- **URL Routing** - Bookmarkable links to any section

---

## 📋 System Requirements

- **Python 3.11+** (or use Docker)
- **SQLite 3** (included with Python)
- **Optional**: API key for any LLM provider (OpenAI, Anthropic, Google, etc.)

---

## 🛠️ Installation & Setup

### Option 1: Docker (Recommended for Production)

**Prerequisites**: Docker and Docker Compose installed

```bash
# Clone repository
git clone https://github.com/yourusername/PECS-learner.git
cd PECS-learner

# (Optional) Configure environment
cp .env.example .env
# Edit .env and add your API key

# Start application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down
```

**Access**: http://localhost:8080

### Option 2: Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/PECS-learner.git
cd PECS-learner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Configure environment
cp .env.example .env
# Edit .env and add your API key

# Run application
python nicegui_app/main.py
```

**Access**: http://localhost:8080

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# === Server Configuration ===
HOST=0.0.0.0
PORT=8080

# === LLM Provider (choose one or more) ===
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini
GEMINI_API_KEY=...

# See https://docs.litellm.ai/docs/providers for 100+ more providers

# === Model Configuration (use any LiteLLM-supported model) ===
LLM_MODEL_FAST=gpt-5-mini           # For rolling context generation
LLM_MODEL_QUALITY=gpt-5.1           # For study notes generation
LLM_MODEL_DEFAULT=gpt-5-mini        # For general feedback

# Examples for other providers:
# LLM_MODEL_FAST=claude-3-haiku
# LLM_MODEL_QUALITY=claude-3-opus
# LLM_MODEL_DEFAULT=gemini-1.5-pro

# === Rolling Context Configuration ===
ROLLING_CONTEXT_MAX_CHARS=10000     # Safety limit
ROLLING_CONTEXT_TARGET_TOKENS=400   # Target summary size

# === LLM Observability (optional) ===
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://cloud.langfuse.com

# === Storage ===
NICEGUI_STORAGE_PATH=./data/nicegui_storage

# === Development ===
RELOAD=false                        # Set to true for auto-reload
LITELLM_VERBOSE=false              # Set to true for LLM debugging
```

**See `.env.example` for a complete configuration template.**

---

## 📖 Usage Guide

### 1️⃣ Create a Project

1. Click **"New Project"** on the dashboard
2. Enter a name (e.g., "Deep Learning Textbook")

### 2️⃣ Upload Content

1. Click **"Add Content"**
2. Choose your method:
   - **Paste text** directly
   - **Upload file** (.txt, .md, .epub, .pdf, .docx)
3. System auto-detects structure (chapters, sections)
4. Click **"Process & Create Sections"**

### 3️⃣ Learn with P.E.C.S.

1. Select a section from the project view
2. Work through the guided learning flow:
   - **Prime** - Record first impressions and questions
   - **Engage** - Read deeply and explain concepts (AI conversation available)
   - **Challenge** - Think critically and make connections
   - **Solidify** - Create flashcards and get AI completion summary
3. All progress auto-saves to database
4. Phases unlock sequentially (structured learning!)

### 4️⃣ Generate Study Notes (NEW!)

**Option A: Batch Generation (entire project)**
1. From project view, click **"Generate Study Notes"**
2. Watch real-time progress bar
3. Study notes created for all sections

**Option B: Individual Section**
1. Open any section in PECS Learning view
2. Scroll to "Study Notes" section
3. Click **"Regenerate Notes"** if needed

**Features:**
- Incorporates rolling context from previous sections
- Includes your PECS learning journey
- Focuses on concepts, connections, and diagrams
- Non-blocking UI with progress updates

### 5️⃣ Study with Spaced Repetition

1. Click **"Study Mode"** from project view
2. Review flashcards with self-grading:
   - Click "I Knew It" ✅
   - Click "Review Again" ❌
3. System schedules optimal review intervals (SM-2 algorithm)
4. Track mastery progress

### 6️⃣ Export to Anki (Optional)

1. Click **"Export to Anki"** (appears when you have flashcards)
2. Choose export method:
   - **AnkiConnect (Direct)** - Requires [AnkiConnect add-on](https://ankiweb.net/shared/info/2055492159)
   - **File Export** - Download `.apkg` file (no setup needed)
3. Enter deck name
4. Click **"Export"**

---

## 🏗️ Project Structure

```
PECS-learner/
├── nicegui_app/                  # Main NiceGUI application
│   ├── main.py                  # Entry point with PWA setup
│   ├── config.py                # Configuration (models, paths, etc.)
│   ├── pages/                   # Page implementations
│   │   ├── dashboard.py         # Project dashboard
│   │   ├── content_upload.py    # File upload & processing
│   │   ├── project_view.py      # Section list & study notes generation
│   │   ├── pecs_learning.py     # Core learning interface (4 phases)
│   │   └── study_mode.py        # Flashcard spaced repetition
│   └── static/                  # PWA assets (manifest, icons)
├── utils/                        # Shared utilities
│   ├── database.py              # SQLAlchemy repository layer
│   ├── models.py                # ORM models (Project, Section, Flashcard)
│   ├── llm_service.py           # LiteLLM integration (multi-provider)
│   ├── rolling_context_service.py # Rolling context & study notes generation
│   ├── context_builder.py       # DRY context engineering (100% tested)
│   ├── anki_export.py           # Anki export (API + file-based)
│   ├── hierarchical_processor.py # Auto-detect document structure
│   ├── file_converters.py       # EPUB, PDF, DOCX → text
│   ├── prompts.yaml             # AI prompt templates
│   └── migration.py             # JSON legacy import
├── tests/                        # Comprehensive test suite (56 tests)
│   ├── test_context_builder.py # 100% coverage
│   ├── test_database.py
│   ├── test_llm_service.py
│   ├── test_file_converters.py
│   └── ...
├── data/                         # SQLite database (auto-created)
├── logs/                         # Application logs
├── Dockerfile                    # Production-ready container
├── docker-compose.yml           # One-command deployment
├── requirements.txt             # Python dependencies
├── .env.example                 # Configuration template
├── BLUEPRINT.md                 # Technical architecture docs
├── TESTING.md                   # Test documentation
├── ROLLING_CONTEXT_INTEGRATION.md # Feature documentation
└── README.md                    # This file
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=utils --cov-report=term-missing

# Specific module
pytest tests/test_context_builder.py -v

# Fast tests only
pytest tests/test_context_builder.py tests/test_database.py
```

**Current Test Coverage:**
- ✅ 56 tests passing
- ✅ Context builder: 100% coverage
- ✅ File converters: 87% coverage
- ✅ Database: 62% coverage
- ✅ LLM service: 52% coverage

See [`TESTING.md`](./TESTING.md) for detailed test documentation.

---

## 🐳 Docker Deployment

### Local Development

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f pecs-app

# Stop
docker-compose down

# Clean everything (including volumes)
docker-compose down -v
```

The `data/` directory is mounted as a volume for database persistence.

### Production Deployment

Deploy to any platform that supports Docker:

#### 🚂 Railway (Easiest - Free Tier)
```bash
railway login
railway init
railway up
```
- ✅ Free 500 hours/month
- ✅ Automatic HTTPS
- ✅ One-click deploy

#### 🎨 Render (Free with sleep)
1. Connect GitHub repository
2. Set environment variables
3. Auto-deploy on every push
- ✅ Free tier available
- ✅ Auto-scaling

#### 🌊 DigitalOcean App Platform ($5/month)
1. Import from GitHub
2. Configure environment
3. Deploy
- ✅ Always-on
- ✅ Easy scaling
- ✅ Reliable uptime

#### 🖥️ Self-Hosted VPS ($5/month)
```bash
# On Ubuntu server
curl -fsSL https://get.docker.com | sh
git clone <your-repo>
cd PECS-learner
docker-compose up -d

# Optional: Use Caddy for automatic HTTPS
```

**Required Environment Variables for Production:**
```bash
OPENAI_API_KEY=your-key          # Or any other LLM provider
NICEGUI_STORAGE_PATH=/app/data/nicegui_storage
PORT=8080
```

---

## 📊 Architecture Highlights

### 🎯 Design Principles

**DRY (Don't Repeat Yourself)**
- Single source of truth for AI context ([`context_builder.py`](./utils/context_builder.py))
- Generic phase rendering system
- Reusable format functions

**Database-First**
- Handles book-length materials (100s of sections)
- Automatic persistence with SQLite
- Indexed queries for performance

**Smart AI Context Engineering**
- Includes full learning journey (all PECS phases)
- Only committed flashcards (prevents duplicates)
- Rolling context from previous sections
- Clear visual separators for LLM comprehension

**Testing-Driven**
- Unit tests for all utilities
- Integration tests for workflows
- Mock-based LLM testing
- 100% coverage on critical modules

### 🔄 Rolling Context Architecture

Based on the "rolling window" technique from document summarization:

1. **Section 1** → Generate summary
2. **Section 2** → Include Section 1 summary + generate new summary
3. **Section 3** → Include Section 1-2 summary + generate new summary
4. **Continue...**

This maintains narrative continuity for book-length materials and helps AI understand cross-chapter connections.

### 🤖 LiteLLM Integration

Unified API for **100+ LLM providers**:
- Automatic provider detection from API keys
- Consistent error handling
- Langfuse observability integration
- Drop-in replacement for OpenAI SDK
- Model flexibility (switch providers anytime)

---

## 📝 Documentation

- **[BLUEPRINT.md](./BLUEPRINT.md)** - Complete technical architecture
- **[TESTING.md](./TESTING.md)** - Test coverage and strategies
- **[ROLLING_CONTEXT_INTEGRATION.md](./ROLLING_CONTEXT_INTEGRATION.md)** - Feature documentation
- **Inline Docstrings** - Google style throughout codebase
- **API Docs** - Database methods in [`utils/database.py`](./utils/database.py)

---

## 🔮 Roadmap

### ✅ Completed
- [x] Multi-project support with SQLite
- [x] Hierarchical content processing
- [x] SM-2 spaced repetition algorithm
- [x] Anki export (API + file-based)
- [x] PWA with offline capability
- [x] **LiteLLM multi-provider support** (NEW!)
- [x] **Rolling window context** (NEW!)
- [x] **AI study notes generation** (NEW!)
- [x] **Non-blocking UI with real-time progress** (NEW!)

### 🚧 In Progress
- [ ] Advanced analytics dashboard
- [ ] Export to Quizlet
- [ ] Custom prompt template editor

### 🔮 Future
- [ ] Authentication & multi-user support
- [ ] Collaborative study groups
- [ ] Mobile native apps (React Native)
- [ ] Browser extension for highlighting
- [ ] Voice input for PECS phases
- [ ] Export to Notion, Obsidian, Roam

---

## 🤝 Contributing

Contributions are welcome! This is an open-source learning platform built with care.

**How to contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests (see [`TESTING.md`](./TESTING.md))
5. Update documentation ([`BLUEPRINT.md`](./BLUEPRINT.md) if architecture changes)
6. Submit a pull request

**Areas we'd love help with:**
- Additional LLM providers (local models, Ollama, etc.)
- Mobile UI improvements
- Accessibility (WCAG compliance)
- Internationalization (i18n)
- Performance optimizations

---

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

**TL;DR**: Free to use, modify, and distribute. Attribution appreciated but not required.

---

## 🙏 Acknowledgments

Built with excellent open-source tools:

- **[NiceGUI](https://nicegui.io/)** - Pure Python web framework
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - SQL toolkit and ORM
- **[LiteLLM](https://github.com/BerriAI/litellm)** - Unified LLM API
- **[Langfuse](https://langfuse.com/)** - LLM observability
- **[markitdown](https://github.com/microsoft/markitdown)** - Microsoft's file converter
- **[pytest](https://pytest.org/)** - Testing framework

---

## 🐛 Known Limitations

- Large files (>100MB) may take time to process
- AI features require internet connection
- Study notes generation can take time for large projects (but UI stays responsive!)

---

## 📧 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/PECS-learner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/PECS-learner/discussions)
- **Email**: your.email@example.com

---

<div align="center">

**Made with ❤️ for deep, structured learning**

[⭐ Star this repo](https://github.com/yourusername/PECS-learner) if you find it useful!

</div>
