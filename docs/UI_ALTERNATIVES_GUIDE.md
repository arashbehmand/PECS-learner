# PECS Learning System - UI Alternative Implementation Guide

## Current State
- **Framework:** Streamlit 1.32+
- **Lines of UI code:** ~950 lines across components/
- **Tight coupling:** Direct database calls from UI components
- **Pain points:**
  - Page reloads on every interaction
  - Limited styling control
  - Poor mobile experience
  - Session state bugs

---

## Recommended Alternative: NiceGUI

### Why NiceGUI?
1. **Python-only** - No JavaScript knowledge required
2. **Minimal migration effort** - ~1-2 weeks to rewrite UI
3. **Modern components** - Cards, dialogs, proper forms
4. **Better UX** - No full-page reloads, smoother interactions
5. **Mobile-friendly** - Responsive by default

### Installation
```bash
pip install nicegui>=1.4.0
```

### Migration Strategy (Phased Approach)

#### Phase 1: Convert Project Dashboard (2-3 days)
**Current:** `components/project_dashboard.py` (106 lines)
**New:** `nicegui_app/pages/dashboard.py`

**Streamlit → NiceGUI Mapping:**
```python
# BEFORE (Streamlit)
st.title("📚 P.E.C.S. Learning System")
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Your Projects")
    for project in projects:
        if st.button(f"Open {project.name}"):
            st.session_state.current_project_id = project.id

# AFTER (NiceGUI)
from nicegui import ui

@ui.page('/dashboard')
def dashboard_page():
    ui.label('📚 P.E.C.S. Learning System').classes('text-3xl font-bold')

    with ui.row().classes('w-full gap-4'):
        with ui.column().classes('w-3/4'):
            ui.label('Your Projects').classes('text-xl')
            for project in db.get_all_projects():
                with ui.card().classes('cursor-pointer'):
                    ui.label(project.name).classes('font-semibold')
                    ui.button('Open', on_click=lambda p=project: open_project(p.id))

        with ui.column().classes('w-1/4'):
            # Stats sidebar
            ui.label('Statistics').classes('text-lg')
```

#### Phase 2: Convert PECS Tabs (5-7 days)
**Current:** `components/pecs_tabs.py` (450 lines - biggest component)
**New:** `nicegui_app/pages/pecs_learning.py`

**Key improvements with NiceGUI:**
```python
# BETTER: Real tabs (no page reload)
from nicegui import ui

class PECSInterface:
    def __init__(self, section_id: int, db: DatabaseRepository):
        self.section_id = section_id
        self.db = db
        self.section = db.get_section(section_id)

    def render(self):
        with ui.tabs() as tabs:
            prime_tab = ui.tab('P - Prime & Preview')
            engage_tab = ui.tab('E - Engage & Explain')
            challenge_tab = ui.tab('C - Challenge & Connect')
            solidify_tab = ui.tab('S - Solidify & Space')

        with ui.tab_panels(tabs, value=prime_tab):
            with ui.tab_panel(prime_tab):
                self._render_prime_phase()
            with ui.tab_panel(engage_tab):
                self._render_engage_phase()
            with ui.tab_panel(challenge_tab):
                self._render_challenge_phase()
            with ui.tab_panel(solidify_tab):
                self._render_solidify_phase()

    def _render_prime_phase(self):
        """Prime & Preview Phase UI"""
        ui.label('📖 Read the section and reflect').classes('text-lg mb-4')

        # Content display (collapsible)
        with ui.expansion('View Section Content', icon='book'):
            ui.markdown(self.section.content)

        # Input areas
        ui.label('What did you understand?').classes('mt-4 font-semibold')
        understanding_input = ui.textarea(
            placeholder='Summarize in your own words...'
        ).classes('w-full')

        # Save with inline feedback
        async def save_prime():
            data = {
                'initial_thoughts': understanding_input.value,
                'prior_knowledge': prior_knowledge_input.value,
                'questions': questions_input.value
            }
            self.db.update_section_pecs_data(self.section_id, 'prime_preview', data)
            ui.notify('Prime phase saved!', color='positive')

        ui.button('💾 Save Progress', on_click=save_prime).classes('mt-4')

        # AI Feedback (async, no page reload)
        if understanding_input.value:
            async def get_ai_feedback():
                with ui.dialog() as dialog, ui.card():
                    ui.label('Analyzing your response...').classes('text-lg')
                    ui.spinner(size='lg')

                dialog.open()
                feedback = llm_service.analyze_section_understanding(
                    self.section.content,
                    understanding_input.value
                )
                dialog.close()

                with ui.dialog() as feedback_dialog, ui.card():
                    ui.label('AI Feedback').classes('text-xl font-bold')
                    ui.markdown(feedback)
                    ui.button('Close', on_click=feedback_dialog.close)
                feedback_dialog.open()

            ui.button('🤖 Get AI Feedback', on_click=get_ai_feedback)
```

#### Phase 3: Convert Study Mode (3-4 days)
**Current:** `components/study_mode.py` (168 lines)
**New:** `nicegui_app/pages/study.py`

**NiceGUI advantage - smooth card flips:**
```python
class FlashcardStudy:
    def __init__(self, project_id: int, db: DatabaseRepository):
        self.project_id = project_id
        self.db = db
        self.cards = []
        self.current_index = 0
        self.show_answer = False

    def render(self):
        self.cards = self.db.get_flashcards_for_review(self.project_id)

        if not self.cards:
            ui.label('No cards to review!').classes('text-xl')
            return

        # Progress bar
        progress = (self.current_index + 1) / len(self.cards) * 100
        ui.linear_progress(value=progress / 100).classes('mb-4')
        ui.label(f'Card {self.current_index + 1} / {len(self.cards)}')

        # Flashcard display
        self._render_current_card()

    def _render_current_card(self):
        card = self.cards[self.current_index]

        # Card container with flip animation
        card_container = ui.column().classes('w-full max-w-2xl mx-auto')

        with card_container:
            with ui.card().classes('p-8 min-h-64 cursor-pointer'):
                if not self.show_answer:
                    # Question side
                    ui.label('Question').classes('text-sm text-gray-500 mb-2')
                    ui.markdown(card.question).classes('text-xl')
                    ui.button(
                        'Show Answer',
                        on_click=self._toggle_answer
                    ).classes('mt-4')
                else:
                    # Answer side
                    ui.label('Question').classes('text-sm text-gray-500 mb-2')
                    ui.markdown(card.question).classes('text-lg')
                    ui.separator()
                    ui.label('Answer').classes('text-sm text-gray-500 mb-2 mt-4')
                    ui.markdown(card.answer).classes('text-xl font-semibold')

                    # Review buttons
                    with ui.row().classes('mt-6 gap-4'):
                        ui.button(
                            '❌ Forgot',
                            on_click=lambda: self._review_card(False),
                            color='red'
                        ).classes('flex-1')
                        ui.button(
                            '✅ Knew It',
                            on_click=lambda: self._review_card(True),
                            color='green'
                        ).classes('flex-1')

    def _toggle_answer(self):
        self.show_answer = not self.show_answer
        ui.update()  # Re-render

    def _review_card(self, knew_it: bool):
        card = self.cards[self.current_index]
        self.db.update_flashcard_review(card.id, knew_it)

        # Move to next card
        self.show_answer = False
        self.current_index += 1

        if self.current_index >= len(self.cards):
            # Session complete
            ui.notify('Study session complete! 🎉', color='positive')
            ui.navigate.to('/dashboard')
        else:
            ui.update()  # Re-render with next card
```

#### Phase 4: Main App Structure
**New:** `nicegui_app/main.py`

```python
from nicegui import ui, app
from utils.database import DatabaseRepository
from nicegui_app.pages import dashboard, pecs_learning, study

# Initialize database
db = DatabaseRepository()

# Configure app
app.add_static_files('/static', 'nicegui_app/static')

# Landing page (dashboard)
@ui.page('/')
def index():
    dashboard.render(db)

# PECS learning interface
@ui.page('/learn/{project_id}/{section_id}')
def learn_page(project_id: int, section_id: int):
    pecs_interface = pecs_learning.PECSInterface(section_id, db)
    pecs_interface.render()

# Study mode
@ui.page('/study/{project_id}')
def study_page(project_id: int):
    flashcard_study = study.FlashcardStudy(project_id, db)
    flashcard_study.render()

# Run app
ui.run(
    port=8501,
    title='P.E.C.S. Learning System',
    favicon='📚',
    dark=True  # Optional dark mode
)
```

---

## Alternative Option: Reflex (Pure Python → React)

### Why Reflex?
- **Modern React frontend** generated from Python code
- **Better scalability** than NiceGUI
- **Component-based architecture**
- **Proper state management**

### Installation
```bash
pip install reflex>=0.4.0
reflex init
```

### Example: PECS Prime Phase in Reflex

```python
# reflex_app/pages/pecs.py
import reflex as rx
from utils.database import DatabaseRepository

class PECSState(rx.State):
    section_id: int = 0
    section_content: str = ""
    understanding: str = ""
    prior_knowledge: str = ""
    questions: str = ""
    ai_feedback: str = ""
    show_feedback_modal: bool = False

    def load_section(self, section_id: int):
        """Load section data from database"""
        db = DatabaseRepository()
        section = db.get_section(section_id)
        self.section_id = section_id
        self.section_content = section.content

        # Load saved PECS data
        pecs_data = section.pecs_data.get('prime_preview', {})
        self.understanding = pecs_data.get('initial_thoughts', '')
        self.prior_knowledge = pecs_data.get('prior_knowledge', '')
        self.questions = pecs_data.get('questions', '')

    def save_prime_phase(self):
        """Save Prime phase to database"""
        db = DatabaseRepository()
        data = {
            'initial_thoughts': self.understanding,
            'prior_knowledge': self.prior_knowledge,
            'questions': self.questions
        }
        db.update_section_pecs_data(self.section_id, 'prime_preview', data)
        return rx.toast("Prime phase saved!", variant="success")

    async def get_ai_feedback(self):
        """Get AI feedback on understanding"""
        from utils.llm_service import LLMService
        llm = LLMService()

        self.show_feedback_modal = True
        self.ai_feedback = "Analyzing..."

        feedback = llm.analyze_section_understanding(
            self.section_content,
            self.understanding
        )
        self.ai_feedback = feedback

def prime_phase_component() -> rx.Component:
    """Prime & Preview Phase UI Component"""
    return rx.vstack(
        # Header
        rx.heading("📖 Prime & Preview", size="lg"),
        rx.text("Read the section and reflect on your understanding"),

        # Section content (collapsible)
        rx.accordion.root(
            rx.accordion.item(
                header=rx.accordion.header("View Section Content"),
                content=rx.accordion.content(
                    rx.markdown(PECSState.section_content)
                )
            ),
            collapsible=True,
        ),

        # Understanding input
        rx.vstack(
            rx.text("What did you understand?", weight="bold"),
            rx.text_area(
                value=PECSState.understanding,
                on_change=PECSState.set_understanding,
                placeholder="Summarize in your own words...",
                rows=5,
                width="100%"
            ),
            width="100%"
        ),

        # Prior knowledge input
        rx.vstack(
            rx.text("What do you already know about this?", weight="bold"),
            rx.text_area(
                value=PECSState.prior_knowledge,
                on_change=PECSState.set_prior_knowledge,
                placeholder="Connect to prior knowledge...",
                rows=3,
                width="100%"
            ),
            width="100%"
        ),

        # Questions input
        rx.vstack(
            rx.text("What questions do you have?", weight="bold"),
            rx.text_area(
                value=PECSState.questions,
                on_change=PECSState.set_questions,
                placeholder="What are you curious about?",
                rows=3,
                width="100%"
            ),
            width="100%"
        ),

        # Action buttons
        rx.hstack(
            rx.button(
                "💾 Save Progress",
                on_click=PECSState.save_prime_phase,
                variant="solid",
                color_scheme="blue"
            ),
            rx.button(
                "🤖 Get AI Feedback",
                on_click=PECSState.get_ai_feedback,
                variant="outline",
                is_disabled=PECSState.understanding == ""
            ),
        ),

        # AI Feedback Modal
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("AI Feedback"),
                rx.dialog.description(
                    rx.markdown(PECSState.ai_feedback)
                ),
                rx.dialog.close(
                    rx.button("Close", variant="soft")
                ),
            ),
            open=PECSState.show_feedback_modal,
        ),

        spacing="4",
        width="100%",
        max_width="800px",
        margin="0 auto"
    )

@rx.page(route="/learn/[section_id]", on_load=PECSState.load_section)
def pecs_page() -> rx.Component:
    """PECS Learning Page with Tabs"""
    return rx.container(
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("P - Prime & Preview", value="prime"),
                rx.tabs.trigger("E - Engage & Explain", value="engage"),
                rx.tabs.trigger("C - Challenge & Connect", value="challenge"),
                rx.tabs.trigger("S - Solidify & Space", value="solidify"),
            ),
            rx.tabs.content(
                prime_phase_component(),
                value="prime"
            ),
            rx.tabs.content(
                rx.text("Engage phase coming soon..."),
                value="engage"
            ),
            # ... other tabs
            default_value="prime"
        ),
        padding="4"
    )
```

---

## Alternative Option: FastAPI + HTMX

### Why HTMX?
- **Creates proper REST API** (future-proof, can add mobile app later)
- **Minimal JavaScript** (just HTML attributes)
- **Progressive enhancement** (works without JS)
- **Modern UX** (partial page updates, smooth transitions)

### Architecture
```
backend/
  ├── main.py                # FastAPI app
  ├── routers/
  │   ├── projects.py        # /api/projects endpoints
  │   ├── sections.py        # /api/sections endpoints
  │   └── flashcards.py      # /api/flashcards endpoints
  ├── schemas/               # Pydantic models (DTOs)
  ├── templates/             # Jinja2 HTML templates
  │   ├── dashboard.html
  │   ├── pecs_tabs.html
  │   └── study_mode.html
  └── utils/                 # REUSE existing code!
      ├── database.py
      ├── llm_service.py
      └── models.py
```

### Example: Prime Phase with HTMX

**Backend (FastAPI):**
```python
# backend/routers/sections.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from utils.database import DatabaseRepository

router = APIRouter(prefix="/api/sections", tags=["sections"])
templates = Jinja2Templates(directory="templates")
db = DatabaseRepository()

@router.get("/{section_id}/prime", response_class=HTMLResponse)
async def get_prime_phase(request: Request, section_id: int):
    """Render Prime phase HTML"""
    section = db.get_section(section_id)
    return templates.TemplateResponse("prime_phase.html", {
        "request": request,
        "section": section
    })

@router.post("/{section_id}/prime/save")
async def save_prime_phase(section_id: int, form_data: dict):
    """Save Prime phase data"""
    db.update_section_pecs_data(section_id, 'prime_preview', form_data)
    return {"message": "Saved!", "status": "success"}

@router.post("/{section_id}/prime/feedback")
async def get_ai_feedback(section_id: int, understanding: str):
    """Get AI feedback (returns HTML fragment)"""
    section = db.get_section(section_id)
    from utils.llm_service import LLMService
    llm = LLMService()

    feedback = llm.analyze_section_understanding(section.content, understanding)

    return f"""
    <div class="bg-blue-50 border border-blue-200 rounded p-4">
        <h4 class="font-bold mb-2">AI Feedback</h4>
        <div class="prose">{feedback}</div>
    </div>
    """
```

**Frontend (HTML + HTMX):**
```html
<!-- templates/prime_phase.html -->
<div class="p-6 max-w-4xl mx-auto">
    <h2 class="text-2xl font-bold mb-4">📖 Prime & Preview</h2>
    <p class="text-gray-600 mb-6">Read the section and reflect on your understanding</p>

    <!-- Section content (collapsible) -->
    <details class="mb-6">
        <summary class="cursor-pointer font-semibold text-blue-600">
            View Section Content
        </summary>
        <div class="mt-2 p-4 bg-gray-50 rounded">
            {{ section.content }}
        </div>
    </details>

    <!-- Prime phase form -->
    <form
        hx-post="/api/sections/{{ section.id }}/prime/save"
        hx-trigger="submit"
        hx-target="#save-status"
        class="space-y-6"
    >
        <!-- Understanding input -->
        <div>
            <label class="font-semibold block mb-2">
                What did you understand?
            </label>
            <textarea
                name="initial_thoughts"
                rows="5"
                placeholder="Summarize in your own words..."
                class="w-full border rounded p-3"
            >{{ section.pecs_data.get('prime_preview', {}).get('initial_thoughts', '') }}</textarea>
        </div>

        <!-- Prior knowledge -->
        <div>
            <label class="font-semibold block mb-2">
                What do you already know about this?
            </label>
            <textarea
                name="prior_knowledge"
                rows="3"
                placeholder="Connect to prior knowledge..."
                class="w-full border rounded p-3"
            >{{ section.pecs_data.get('prime_preview', {}).get('prior_knowledge', '') }}</textarea>
        </div>

        <!-- Questions -->
        <div>
            <label class="font-semibold block mb-2">
                What questions do you have?
            </label>
            <textarea
                name="questions"
                rows="3"
                placeholder="What are you curious about?"
                class="w-full border rounded p-3"
            >{{ section.pecs_data.get('prime_preview', {}).get('questions', '') }}</textarea>
        </div>

        <!-- Action buttons -->
        <div class="flex gap-4">
            <button
                type="submit"
                class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
                💾 Save Progress
            </button>

            <button
                type="button"
                hx-post="/api/sections/{{ section.id }}/prime/feedback"
                hx-include="[name='initial_thoughts']"
                hx-target="#feedback-container"
                hx-indicator="#feedback-loading"
                class="bg-gray-200 px-6 py-2 rounded hover:bg-gray-300"
            >
                🤖 Get AI Feedback
            </button>
        </div>

        <!-- Status messages -->
        <div id="save-status"></div>
        <div id="feedback-loading" class="htmx-indicator">
            Analyzing your response...
        </div>
    </form>

    <!-- AI Feedback area -->
    <div id="feedback-container" class="mt-6"></div>
</div>
```

**HTMX benefits:**
- No page reloads (AJAX requests automatically)
- Progressive enhancement (works without JS)
- Simple syntax (just HTML attributes)
- Easy to understand and maintain

---

## Migration Effort Comparison

| Alternative | Learning Curve | Migration Time | Code Reuse | UX Improvement | Mobile Support |
|-------------|---------------|----------------|------------|----------------|----------------|
| **NiceGUI** | ⭐ Very Easy | 1-2 weeks | 90% | ⭐⭐⭐ Good | ⭐⭐⭐ Good |
| **Reflex** | ⭐⭐ Easy | 2-3 weeks | 85% | ⭐⭐⭐⭐ Great | ⭐⭐⭐⭐ Excellent |
| **FastAPI + HTMX** | ⭐⭐⭐ Moderate | 3-4 weeks | 80% | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Excellent |

---

## Recommended Path Forward

### Step 1: Try NiceGUI (1-2 weeks)
Convert one component (e.g., Project Dashboard) to NiceGUI and test with users.

**Success criteria:**
- Faster interactions (no page reloads)
- Better mobile experience
- Users prefer it over Streamlit

**If successful:** Continue migrating other components
**If not satisfactory:** Consider Reflex or HTMX

### Step 2: (Optional) Upgrade to Reflex or HTMX (2-4 weeks)
If NiceGUI feels limiting as the app grows, upgrade to:
- **Reflex** if you want to stay Python-only
- **HTMX** if you want a proper API for future mobile app

### Step 3: Polish & Deploy
- Add authentication (if needed)
- Improve styling with TailwindCSS or similar
- Deploy to cloud (Railway, Render, DigitalOcean)

---

## Quick Start: NiceGUI Migration

1. **Install NiceGUI:**
```bash
cd /home/user/PECS-learner
pip install nicegui>=1.4.0
```

2. **Create new app structure:**
```bash
mkdir -p nicegui_app/pages nicegui_app/static
touch nicegui_app/main.py
touch nicegui_app/pages/dashboard.py
```

3. **Convert one component** (start with dashboard)

4. **Run and test:**
```bash
python nicegui_app/main.py
```

5. **Iterate** - migrate one component at a time

---

## Need Help?

- **NiceGUI Docs:** https://nicegui.io
- **Reflex Docs:** https://reflex.dev
- **HTMX Docs:** https://htmx.org

All three have excellent documentation and examples!
