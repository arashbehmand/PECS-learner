# P.E.C.S. Learning System 📚

A production-grade, database-backed learning application that guides users through a structured learning methodology (Prime, Engage, Challenge, Solidify) for any text material—from articles to entire books.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.32+-red.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 Features

### Core Features
- **📚 Multi-Project Support**: Create and manage multiple study projects (e.g., one per book)
- **📄 Multi-Format Support**: Import from Text, Markdown, EPUB, PDF, and Word documents
- **🔍 Hierarchical Content Processing**: Automatically detects chapters, sections, and headings in your text
- **💾 Automatic Persistence**: All progress saved automatically to SQLite database—never lose your work
- **📑 Scalable Navigation**: Handle hundreds of sections with search and pagination
- **📊 Progress Tracking**: Visual indicators for completed sections and flashcard statistics

### P.E.C.S. Learning Phases (Tabbed Interface)
- **P - Prime & Preview**: Initial skimming and preparation
- **E - Engage & Explain**: Deep reading and explanation in your own words
- **C - Challenge & Connect**: Critical thinking and making connections
- **S - Solidify & Space**: Review and create flashcards for spaced repetition

### Interactive Study Mode
- **🎴 Spaced Repetition**: SM-2 algorithm for optimal review scheduling
- **📈 Self-Grading**: "I Knew It" / "Review Again" buttons for active recall
- **🎯 Smart Filtering**: Study cards due for review, all cards, or mastered cards
- **📊 Progress Statistics**: Track review counts, ease factors, and next review dates

### AI-Enhanced Features (Optional)
- **✍️ Writing Coach**: Get AI feedback on explanation clarity and simplicity
- **💡 Flashcard Assistant**: AI-generated flashcard suggestions based on your understanding
- **🔍 Critical Analysis**: AI feedback on critical thinking and connections
- **🎓 Learning Guidance**: Context-aware suggestions throughout all phases

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd PECS-learner

# Start the application
docker-compose up

# Access at http://localhost:8501
```

### Option 2: Local Installation

```bash
# Clone the repository
git clone <repository-url>
cd PECS-learner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## 📋 Requirements

- Python 3.10+
- SQLite 3 (included with Python)
- Optional: OpenAI API key for AI features

## ⚙️ Configuration

### API Keys (Optional)

To enable AI features, create `.streamlit/secrets.toml`:

```toml
[llm]
openai_api_key = "your-openai-api-key-here"
```

**Note**: The application works perfectly without API keys—AI features are optional enhancements.

You can get an OpenAI API key from: https://platform.openai.com/api-keys

## 📖 Usage Guide

### 1. Create a Project
- Click "Create New Project" on the dashboard
- Enter a name for your study project (e.g., "Python Programming Book")

### 2. Upload Content
- Paste your text or upload a `.txt` or `.md` file
- The system automatically detects chapters and sections
- Configure processing options (min/max section size, overlap)
- Click "Process & Create Sections"

### 3. Learn with P.E.C.S.
- Select a section from the sidebar
- Navigate through the four tabs:
  - **Prime**: Skim and prepare
  - **Engage**: Read deeply and explain
  - **Challenge**: Think critically and connect
  - **Solidify**: Create flashcards and apply knowledge
- Use "💾 Auto-save" buttons to save your progress
- Mark sections as complete when finished

### 4. Study with Spaced Repetition
- Navigate to "Study Mode"
- Choose what to study: cards due for review, all cards, or mastered cards
- Review flashcards one at a time
- Self-grade: "I Knew It" or "Review Again"
- The system schedules next reviews based on your performance

## 🗂️ Project Structure

```
PECS-learner/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml         # Docker Compose setup
├── pytest.ini                 # Test configuration
├── README.md                   # This file
├── BLUEPRINT.md                # Technical architecture documentation
├── .streamlit/
│   ├── secrets.toml           # API keys (create from example)
│   └── secrets.toml.example   # Example secrets file
├── components/
│   ├── project_dashboard.py   # Multi-project dashboard
│   ├── content_upload_new.py  # Content import with hierarchical processing
│   ├── section_navigator.py   # Section navigation sidebar
│   ├── pecs_tabs.py           # Unified PECS interface (tabs)
│   ├── study_mode.py           # Interactive study mode
│   └── [legacy modules]       # Old components (preserved for reference)
├── utils/
│   ├── database.py             # Database repository layer
│   ├── models.py               # SQLAlchemy ORM models
│   ├── hierarchical_processor.py  # Intelligent section detection
│   ├── content_processor.py    # Basic text loading
│   ├── llm_service.py          # AI integration
│   ├── migration.py            # JSON import utility
│   ├── prompts.yaml            # AI prompt templates
│   └── [legacy modules]        # Old utilities
├── tests/
│   ├── test_database.py        # Database tests
│   └── test_hierarchical_processor.py  # Content processing tests
└── data/                       # SQLite database (created automatically)
    └── pecs.db
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# With coverage
pytest --cov=utils --cov-report=html

# Specific test file
pytest tests/test_database.py
```

## 🔄 Migration from Old Format

If you have old JSON session files, you can migrate them:

1. In the application, navigate to the migration section
2. Upload your old `pecs_session.json` file
3. Specify a project name
4. Click "Import Session"

All your old chunks, notes, and flashcards will be converted to the new database format.

## 🐳 Docker Details

### Build Image
```bash
docker build -t pecs-learner .
```

### Run Container
```bash
docker run -p 8501:8501 -v $(pwd)/data:/app/data pecs-learner
```

### Docker Compose
```bash
# Start
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Important**: The `data/` directory is mounted as a volume to persist your database across container restarts.

## 🏗️ Architecture Highlights

### Database-First Design
- **Scalability**: Handles book-length materials with hundreds of sections
- **Persistence**: All data automatically saved to SQLite
- **Performance**: Indexed queries for fast navigation

### Hierarchical Content Processing
- Intelligent detection of chapters, sections, and headings
- Maintains document structure instead of flat chunking
- Configurable processing parameters

### Modern UI/UX
- Tabbed interface for non-linear PECS workflow
- Interactive study mode with spaced repetition
- Responsive design with efficient navigation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update BLUEPRINT.md if architecture changes
6. Submit a pull request

## 📝 License

[Add your chosen license here]

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses [SQLAlchemy](https://www.sqlalchemy.org/) for database operations
- AI integration via [OpenAI](https://openai.com/)
- Text processing with [LangChain](https://www.langchain.com/)

## 📚 Documentation

- **Technical Architecture**: See `BLUEPRINT.md` for detailed system design
- **Code Documentation**: Inline docstrings follow Google style
- **API Documentation**: Database schema and repository methods documented in `utils/database.py`

## 🐛 Known Issues & Limitations

- Large text files (>100MB) may take time to process
- Markdown rendering in content areas is basic (plain text display)
- AI features require internet connection and API key

## 🔮 Roadmap

- [ ] Export flashcards to Anki/Quizlet format
- [ ] Collaborative study groups
- [ ] Advanced analytics dashboard
- [ ] Mobile-responsive improvements
- [ ] Multiple LLM provider support
- [ ] Custom prompt template editor
- [ ] Backup/restore functionality

---

**Made with ❤️ for deep, structured learning**

For questions, issues, or feature requests, please open an issue on GitHub.
