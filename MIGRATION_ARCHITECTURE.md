# PECS Learning System - NiceGUI Migration Architecture

## Overview

This document outlines the complete migration from Streamlit to NiceGUI, including future multi-user support considerations.

---

## Current Architecture (Streamlit)

```
app.py (170 lines)
├── Session State Management (st.session_state)
│   ├── show_dashboard
│   ├── current_project_id
│   ├── current_section_id
│   ├── view_mode (study/pecs/migration)
│   └── study_mode_* (flashcard state)
│
├── Components (Function-based)
│   ├── project_dashboard.py (106 lines)
│   ├── content_upload_new.py (178 lines)
│   ├── pecs_tabs.py (450 lines) - LARGEST COMPONENT
│   ├── section_navigator.py (83 lines)
│   └── study_mode.py (168 lines)
│
└── Utils (Backend - UNCHANGED)
    ├── database.py (DatabaseRepository)
    ├── models.py (SQLAlchemy ORM)
    ├── llm_service.py (AI integration)
    └── hierarchical_processor.py
```

### Pain Points
1. **Full page reloads** on every interaction
2. **Session state fragility** - easy to lose state
3. **No URL routing** - can't bookmark or share links
4. **Poor mobile UX** - not responsive
5. **No multi-user support** - single session only

---

## New Architecture (NiceGUI)

```
nicegui_app/
├── main.py                         # App entry point + routing
├── config.py                       # App configuration
├── auth/                           # Future: Authentication layer
│   ├── __init__.py
│   ├── models.py                   # User model (future)
│   └── service.py                  # Auth service (future)
├── pages/                          # Page components (class-based)
│   ├── __init__.py
│   ├── dashboard.py                # Project dashboard
│   ├── content_upload.py           # Content upload
│   ├── pecs_learning.py            # PECS 4-phase interface
│   ├── study_mode.py               # Flashcard study
│   └── project_view.py             # Project overview with sections
├── components/                     # Reusable UI components
│   ├── __init__.py
│   ├── flashcard_card.py           # Flashcard display
│   ├── section_card.py             # Section display
│   ├── project_card.py             # Project display
│   └── stats_widget.py             # Statistics widget
├── static/                         # Static assets
│   ├── icons/                      # PWA icons
│   ├── manifest.json               # PWA manifest
│   └── service-worker.js           # Service worker
└── utils/                          # Shared utilities (NEW)
    ├── __init__.py
    ├── state.py                    # State management helpers
    └── navigation.py               # Navigation helpers
```

### Key Improvements
1. **URL-based routing** - Bookmarkable, shareable links
2. **No page reloads** - Smooth, app-like experience
3. **Mobile-responsive** - PWA support out of the box
4. **Multi-user ready** - Auth scaffolding in place
5. **Class-based pages** - Better code organization
6. **Reusable components** - DRY principle

---

## Routing Structure

### URL Routes

| Route | Component | Description | Multi-user Ready? |
|-------|-----------|-------------|-------------------|
| `/` | `dashboard.py` | Landing page / project list | ✅ Add user_id param |
| `/project/new` | `content_upload.py` | Create new project | ✅ Add user_id |
| `/project/{project_id}` | `project_view.py` | Project overview | ✅ Check ownership |
| `/project/{project_id}/upload` | `content_upload.py` | Add content to project | ✅ Check ownership |
| `/project/{project_id}/study` | `study_mode.py` | Flashcard study mode | ✅ Check ownership |
| `/project/{project_id}/section/{section_id}` | `pecs_learning.py` | PECS learning interface | ✅ Check ownership |
| `/login` | `auth/login.py` | Login page (future) | N/A |
| `/register` | `auth/register.py` | Registration (future) | N/A |

### Navigation Flow

```
Landing (/)
  ├─> Create Project → Content Upload → Project View
  ├─> Open Project → Project View
  │                    ├─> Study Mode
  │                    ├─> PECS Learning (Section)
  │                    └─> Add Content
  └─> Delete Project → Refresh Landing
```

---

## Multi-User Support Scaffolding

### Phase 1: Single-User (Current Migration)
**Goal:** Complete feature parity with Streamlit, no authentication

**Database:**
- Projects, Sections, Flashcards (no user ownership)
- No User table yet

**UI:**
- All routes public
- No login/logout
- One person can use the app

### Phase 2: Add User Model (Future)
**Goal:** Add user accounts without breaking existing data

**Database Migration:**
```sql
-- Add users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Add user_id to projects (nullable for backward compatibility)
ALTER TABLE projects ADD COLUMN user_id INTEGER REFERENCES users(id);

-- For multi-tenant support:
-- Sections and Flashcards inherit ownership through project.user_id
```

**Code Changes:**
```python
# database.py (add user_id parameter)
def get_all_projects(self, user_id: int = None):
    """Get projects, optionally filtered by user"""
    query = self.session.query(Project)
    if user_id:
        query = query.filter(Project.user_id == user_id)
    return query.all()
```

### Phase 3: Add Authentication (Future)
**Goal:** Secure routes with login/logout

**UI Changes:**
```python
# main.py
from nicegui import ui, app
from auth.service import AuthService, require_auth

auth_service = AuthService()

@ui.page('/')
async def dashboard():
    user = await require_auth()  # Redirect to /login if not authenticated
    render_dashboard(user.id)

@ui.page('/login')
async def login():
    # Login form
    pass
```

---

## Component Migration Map

### 1. Dashboard (project_dashboard.py → pages/dashboard.py)

**Streamlit (Old):**
```python
def render_project_dashboard(db):
    st.header("📚 My Study Projects")
    projects = db.get_all_projects()
    for project in projects:
        st.markdown(f"### {project.name}")
        if st.button("Open"):
            st.session_state.current_project_id = project.id
            st.rerun()
```

**NiceGUI (New):**
```python
class DashboardPage:
    def __init__(self, db: DatabaseRepository, user_id: int = None):
        self.db = db
        self.user_id = user_id  # Future: filter by user

    def render(self):
        ui.label('📚 My Study Projects').classes('text-3xl font-bold')
        projects = self.db.get_all_projects()  # Future: pass user_id

        with ui.grid(columns='repeat(auto-fill, minmax(300px, 1fr))').classes('w-full gap-4'):
            for project in projects:
                self._render_project_card(project)

    def _render_project_card(self, project):
        with ui.card().classes('cursor-pointer'):
            ui.label(project.name).classes('text-xl font-bold')
            ui.button(
                'Open',
                on_click=lambda p=project: ui.navigate.to(f'/project/{p.id}')
            )
```

**Key Changes:**
- Class-based instead of function
- Navigation via URL instead of session state
- user_id parameter ready for multi-user

### 2. PECS Tabs (pecs_tabs.py → pages/pecs_learning.py)

**Streamlit (Old):**
```python
def render_pecs_phases(db, section):
    tab1, tab2, tab3, tab4 = st.tabs(["Prime", "Engage", "Challenge", "Solidify"])

    with tab1:
        understanding = st.text_area("What did you understand?", ...)
        if st.button("Save"):
            db.update_section_pecs_data(...)
            st.rerun()  # Full page reload!
```

**NiceGUI (New):**
```python
class PECSLearningPage:
    def __init__(self, db, section_id, user_id=None):
        self.db = db
        self.section = db.get_section(section_id)
        self.user_id = user_id  # Future: check ownership

    def render(self):
        with ui.tabs() as tabs:
            prime_tab = ui.tab('Prime')
            engage_tab = ui.tab('Engage')
            # ...

        with ui.tab_panels(tabs):
            with ui.tab_panel(prime_tab):
                self._render_prime_phase()

    def _render_prime_phase(self):
        pecs_data = self.section.pecs_data.get('prime_preview', {})

        understanding = ui.textarea(
            value=pecs_data.get('initial_thoughts', '')
        ).classes('w-full')

        async def save():
            self.db.update_section_pecs_data(
                self.section.id,
                'prime_preview',
                {'initial_thoughts': understanding.value}
            )
            ui.notify('Saved!', color='positive')  # No page reload!

        ui.button('Save', on_click=save)
```

**Key Changes:**
- Real tabs (no page reload on switch)
- Instant feedback with toast notifications
- No st.rerun() needed
- Async save operations

### 3. Study Mode (study_mode.py → pages/study_mode.py)

**Streamlit (Old):**
```python
def render_study_mode(db, project_id):
    if 'current_card_index' not in st.session_state:
        st.session_state.current_card_index = 0

    cards = db.get_flashcards_for_review(project_id)
    current_card = cards[st.session_state.current_card_index]

    st.markdown(current_card.question)
    if st.button("Show Answer"):
        st.session_state.show_answer = True
        st.rerun()  # Full page reload
```

**NiceGUI (New):**
```python
class StudyModePage:
    def __init__(self, db, project_id, user_id=None):
        self.db = db
        self.project_id = project_id
        self.user_id = user_id
        self.cards = db.get_flashcards_for_review(project_id)
        self.current_index = 0
        self.show_answer = False

    def render(self):
        if not self.cards:
            ui.label('No cards to review')
            return

        # Create reactive container
        self.card_container = ui.column().classes('w-full')
        self._render_current_card()

    def _render_current_card(self):
        card = self.cards[self.current_index]

        self.card_container.clear()
        with self.card_container:
            ui.markdown(f"**{card.question}**")

            if not self.show_answer:
                ui.button(
                    'Show Answer',
                    on_click=self._toggle_answer
                )
            else:
                ui.markdown(card.answer)
                with ui.row():
                    ui.button('I Knew It', on_click=lambda: self._review(True))
                    ui.button('Review Again', on_click=lambda: self._review(False))

    def _toggle_answer(self):
        self.show_answer = not self.show_answer
        self._render_current_card()  # Re-render just this component

    def _review(self, knew_it: bool):
        card = self.cards[self.current_index]
        self.db.update_flashcard_review(card.id, knew_it)

        self.current_index += 1
        self.show_answer = False

        if self.current_index >= len(self.cards):
            ui.notify('Session complete! 🎉', color='positive')
            self.current_index = 0

        self._render_current_card()
```

**Key Changes:**
- Component-level state (not global session state)
- Partial re-renders (only update changed components)
- Smooth transitions with no page flicker

---

## State Management Strategy

### Streamlit Approach (Old)
```python
# Global session state
st.session_state.current_project_id = 123
st.session_state.current_section_id = 456
st.session_state.view_mode = 'pecs'

# Problem: State reset on page reload, hard to debug
```

### NiceGUI Approach (New)
```python
# Option 1: URL Parameters (for navigation state)
@ui.page('/project/{project_id}/section/{section_id}')
def pecs_page(project_id: int, section_id: int):
    # State comes from URL - always recoverable
    pass

# Option 2: App-level storage (for user preferences)
from nicegui import app
app.storage.user['theme'] = 'dark'  # Persisted per browser

# Option 3: Component state (for UI state)
class FlashcardComponent:
    def __init__(self):
        self.show_answer = False  # Component-level state
```

---

## Testing Strategy

### Unit Tests (New)

```python
# tests/test_nicegui_components.py
import pytest
from nicegui_app.pages.dashboard import DashboardPage
from utils.database import DatabaseRepository

def test_dashboard_renders_projects(test_db):
    """Test dashboard displays all projects"""
    # Create test projects
    project1 = test_db.create_project("Test Project 1")
    project2 = test_db.create_project("Test Project 2")

    # Render dashboard
    page = DashboardPage(test_db)
    # Test rendering logic
    assert page.db.get_all_projects() == [project1, project2]

def test_pecs_learning_saves_data(test_db):
    """Test PECS phase data is saved correctly"""
    project = test_db.create_project("Test")
    section = test_db.create_section(project.id, "Content", "Title", 0)

    page = PECSLearningPage(test_db, section.id)
    # Simulate save
    page.save_prime_data({'initial_thoughts': 'Test understanding'})

    # Verify
    saved_section = test_db.get_section(section.id)
    assert saved_section.pecs_data['prime_preview']['initial_thoughts'] == 'Test understanding'
```

### Integration Tests (Future)

```python
# tests/integration/test_user_flow.py
def test_complete_learning_flow(test_db, test_client):
    """Test complete user flow from project creation to flashcard review"""
    # 1. Create project
    response = test_client.post('/api/projects', json={'name': 'Test Project'})
    project_id = response.json()['id']

    # 2. Upload content
    response = test_client.post(f'/api/projects/{project_id}/content', ...)

    # 3. Access PECS interface
    response = test_client.get(f'/project/{project_id}/section/1')

    # 4. Save PECS data
    response = test_client.post(f'/api/sections/1/pecs', json={...})

    # 5. Create flashcard
    response = test_client.post(f'/api/flashcards', json={...})

    # 6. Review flashcard
    response = test_client.post(f'/api/flashcards/1/review', json={'knew_it': True})

    assert response.status_code == 200
```

---

## Multi-User Database Schema (Future)

### Current Schema (Single-User)
```
projects
├── id (PK)
├── name
├── created_at
└── updated_at

sections
├── id (PK)
├── project_id (FK → projects)
├── title
├── content
├── order_index
├── pecs_data (JSON)
└── is_completed

flashcards
├── id (PK)
├── project_id (FK → projects)
├── section_id (FK → sections)
├── question
├── answer
└── spaced_repetition_data
```

### Future Schema (Multi-User)
```
users (NEW)
├── id (PK)
├── email (UNIQUE)
├── password_hash
├── created_at
└── updated_at

projects
├── id (PK)
├── user_id (FK → users) ← NEW
├── name
├── created_at
└── updated_at

# Sections and Flashcards inherit ownership through project.user_id
```

---

## Migration Checklist

### Phase 1: Core Migration (Current Sprint)
- [ ] Create new `nicegui_app/` structure
- [ ] Migrate Dashboard component
- [ ] Migrate Content Upload component
- [ ] Migrate PECS Tabs (4 phases)
- [ ] Migrate Section Navigator
- [ ] Migrate Study Mode
- [ ] Add PWA configuration
- [ ] Update Docker setup
- [ ] Write component tests
- [ ] Remove Streamlit code

### Phase 2: Polish & Optimization
- [ ] Add loading states
- [ ] Improve mobile responsiveness
- [ ] Add keyboard shortcuts
- [ ] Add dark mode toggle
- [ ] Optimize database queries
- [ ] Add error boundaries

### Phase 3: Multi-User Prep (Future)
- [ ] Add User model to database
- [ ] Create authentication service
- [ ] Add login/register pages
- [ ] Protect routes with auth middleware
- [ ] Add user-specific data filtering
- [ ] Add user settings page

---

## Rollback Plan

If migration fails:
1. Git revert to last Streamlit commit
2. Keep old `app.py` and `components/` intact until migration complete
3. Run both versions in parallel during testing:
   - Streamlit: `streamlit run app.py --server.port=8501`
   - NiceGUI: `python nicegui_app/main.py` (port 8080)

---

## Success Criteria

✅ All Streamlit features work in NiceGUI
✅ No data loss during migration
✅ Mobile-responsive and PWA-installable
✅ At least 80% test coverage
✅ Performance improvement (no page reloads)
✅ Code is multi-user ready (scaffolding in place)
