"""
NiceGUI Proof-of-Concept for PECS Learning System
This demonstrates how the Project Dashboard would look in NiceGUI.

Run with: python nicegui_demo.py
Then visit: http://localhost:8502
"""

from nicegui import ui, app
from utils.database import DatabaseRepository
from utils.models import Project
from datetime import datetime

# Initialize database
db = DatabaseRepository()


# ===== PAGE: Dashboard =====
@ui.page('/')
def dashboard():
    """Main dashboard showing all projects"""

    # Header
    with ui.row().classes('w-full items-center justify-between mb-6'):
        ui.label('📚 P.E.C.S. Learning System').classes('text-3xl font-bold')
        ui.button('➕ New Project', on_click=lambda: new_project_dialog.open()).classes('bg-blue-500')

    # Load projects
    projects = db.get_all_projects()

    if not projects:
        # Empty state
        with ui.column().classes('items-center justify-center mt-12'):
            ui.label('No projects yet').classes('text-xl text-gray-500')
            ui.label('Create your first project to start learning!').classes('text-gray-400')
            ui.button('Create Project', on_click=lambda: new_project_dialog.open()).classes('mt-4 bg-blue-500')
    else:
        # Project grid
        with ui.grid(columns=3).classes('w-full gap-4'):
            for project in projects:
                render_project_card(project)

    # New project dialog
    with ui.dialog() as new_project_dialog, ui.card().classes('w-96'):
        ui.label('Create New Project').classes('text-2xl font-bold mb-4')

        project_name_input = ui.input(
            label='Project Name',
            placeholder='e.g., Learn Quantum Physics'
        ).classes('w-full')

        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('Cancel', on_click=new_project_dialog.close).classes('bg-gray-300')
            ui.button(
                'Create',
                on_click=lambda: create_project(project_name_input.value, new_project_dialog)
            ).classes('bg-blue-500')


def render_project_card(project: Project):
    """Render a single project card"""

    # Get project stats
    stats = db.get_project_stats(project.id)

    with ui.card().classes('cursor-pointer hover:shadow-lg transition-shadow'):
        # Project header
        with ui.row().classes('w-full items-start justify-between'):
            ui.label(project.name).classes('text-xl font-bold')
            ui.icon('folder_open').classes('text-blue-500')

        # Stats
        with ui.row().classes('w-full gap-4 mt-4 text-sm text-gray-600'):
            with ui.column().classes('items-center'):
                ui.label(str(stats['total_sections'])).classes('text-2xl font-bold text-blue-600')
                ui.label('Sections').classes('text-xs')

            with ui.column().classes('items-center'):
                ui.label(str(stats['total_flashcards'])).classes('text-2xl font-bold text-green-600')
                ui.label('Flashcards').classes('text-xs')

            with ui.column().classes('items-center'):
                ui.label(str(stats['completed_sections'])).classes('text-2xl font-bold text-purple-600')
                ui.label('Completed').classes('text-xs')

        # Progress bar
        if stats['total_sections'] > 0:
            progress = stats['completed_sections'] / stats['total_sections']
            ui.linear_progress(value=progress).classes('mt-4')
            ui.label(f"{int(progress * 100)}% Complete").classes('text-xs text-gray-500 mt-1')

        # Last updated
        time_diff = datetime.now() - project.updated_at
        if time_diff.days > 0:
            last_updated = f"{time_diff.days} days ago"
        elif time_diff.seconds > 3600:
            last_updated = f"{time_diff.seconds // 3600} hours ago"
        else:
            last_updated = "Recently"

        ui.label(f"Last updated: {last_updated}").classes('text-xs text-gray-400 mt-2')

        # Action buttons
        with ui.row().classes('w-full gap-2 mt-4'):
            ui.button(
                'Open',
                on_click=lambda p=project: open_project(p.id)
            ).classes('flex-1 bg-blue-500')

            ui.button(
                '🗑️',
                on_click=lambda p=project: delete_project_confirm(p)
            ).classes('bg-red-500')


def create_project(name: str, dialog):
    """Create a new project"""
    if not name or not name.strip():
        ui.notify('Project name cannot be empty', color='negative')
        return

    try:
        project = db.create_project(name.strip())
        ui.notify(f'Project "{name}" created!', color='positive')
        dialog.close()
        # Refresh page to show new project
        ui.navigate.to('/')
    except Exception as e:
        ui.notify(f'Error creating project: {str(e)}', color='negative')


def delete_project_confirm(project: Project):
    """Show confirmation dialog before deleting"""
    with ui.dialog() as confirm_dialog, ui.card():
        ui.label(f'Delete "{project.name}"?').classes('text-xl font-bold')
        ui.label('This action cannot be undone.').classes('text-gray-600 mt-2')

        with ui.row().classes('w-full gap-2 mt-4'):
            ui.button('Cancel', on_click=confirm_dialog.close).classes('flex-1 bg-gray-300')
            ui.button(
                'Delete',
                on_click=lambda: delete_project(project.id, confirm_dialog)
            ).classes('flex-1 bg-red-500')

    confirm_dialog.open()


def delete_project(project_id: int, dialog):
    """Delete a project"""
    try:
        db.delete_project(project_id)
        ui.notify('Project deleted', color='positive')
        dialog.close()
        ui.navigate.to('/')
    except Exception as e:
        ui.notify(f'Error deleting project: {str(e)}', color='negative')


def open_project(project_id: int):
    """Navigate to project view"""
    ui.navigate.to(f'/project/{project_id}')


# ===== PAGE: Project View (PECS Learning) =====
@ui.page('/project/{project_id}')
def project_view(project_id: int):
    """Project learning interface with PECS tabs"""

    project = db.get_project(project_id)
    if not project:
        ui.label('Project not found').classes('text-xl text-red-500')
        ui.button('← Back to Dashboard', on_click=lambda: ui.navigate.to('/')).classes('mt-4')
        return

    sections = db.get_sections_by_project(project_id)

    # Header
    with ui.row().classes('w-full items-center justify-between mb-6'):
        with ui.row().classes('items-center gap-4'):
            ui.button('← Back', on_click=lambda: ui.navigate.to('/')).classes('bg-gray-300')
            ui.label(project.name).classes('text-3xl font-bold')

        with ui.row().classes('gap-2'):
            ui.button('📚 Study Mode', on_click=lambda: ui.navigate.to(f'/study/{project_id}')).classes('bg-green-500')
            ui.button('➕ Add Content', on_click=lambda: ui.notify('Upload feature coming soon!')).classes('bg-blue-500')

    if not sections:
        # No content uploaded yet
        with ui.column().classes('items-center justify-center mt-12'):
            ui.label('No content uploaded').classes('text-xl text-gray-500')
            ui.label('Upload a document or paste text to start learning').classes('text-gray-400')
            ui.button('Upload Content', on_click=lambda: ui.notify('Upload feature coming soon!')).classes('mt-4 bg-blue-500')
    else:
        # Section navigator (left sidebar)
        with ui.row().classes('w-full gap-6'):
            # Sidebar
            with ui.column().classes('w-1/4 bg-gray-50 p-4 rounded'):
                ui.label('Sections').classes('text-xl font-bold mb-4')

                search_input = ui.input(
                    placeholder='Search sections...'
                ).classes('w-full mb-4')

                for idx, section in enumerate(sections):
                    section_title = section.title or f"Section {idx + 1}"
                    is_completed = section.is_completed

                    with ui.card().classes('cursor-pointer hover:bg-blue-50 mb-2'):
                        with ui.row().classes('w-full items-center justify-between'):
                            ui.label(section_title).classes('font-semibold')
                            if is_completed:
                                ui.icon('check_circle').classes('text-green-500')

                        ui.button(
                            'Open',
                            on_click=lambda s=section: open_section(project_id, s.id)
                        ).classes('w-full mt-2 bg-blue-500 text-sm')

            # Main content area
            with ui.column().classes('flex-1'):
                ui.label('Select a section to start learning').classes('text-xl text-gray-500')


def open_section(project_id: int, section_id: int):
    """Navigate to section PECS interface"""
    ui.navigate.to(f'/learn/{project_id}/{section_id}')


# ===== PAGE: PECS Learning Interface =====
@ui.page('/learn/{project_id}/{section_id}')
def pecs_learning(project_id: int, section_id: int):
    """PECS 4-phase learning interface"""

    section = db.get_section(section_id)
    if not section:
        ui.label('Section not found').classes('text-xl text-red-500')
        return

    # Header
    with ui.row().classes('w-full items-center gap-4 mb-6'):
        ui.button('← Back', on_click=lambda: ui.navigate.to(f'/project/{project_id}')).classes('bg-gray-300')
        ui.label(section.title or f"Section {section.order_index + 1}").classes('text-2xl font-bold')

    # PECS Tabs
    with ui.tabs().classes('w-full') as tabs:
        prime_tab = ui.tab('P - Prime & Preview')
        engage_tab = ui.tab('E - Engage & Explain')
        challenge_tab = ui.tab('C - Challenge & Connect')
        solidify_tab = ui.tab('S - Solidify & Space')

    with ui.tab_panels(tabs, value=prime_tab).classes('w-full'):
        with ui.tab_panel(prime_tab):
            render_prime_phase(section)

        with ui.tab_panel(engage_tab):
            ui.label('Engage phase - Coming soon!').classes('text-xl')

        with ui.tab_panel(challenge_tab):
            ui.label('Challenge phase - Coming soon!').classes('text-xl')

        with ui.tab_panel(solidify_tab):
            ui.label('Solidify phase - Coming soon!').classes('text-xl')


def render_prime_phase(section):
    """Render Prime & Preview phase"""

    # Get saved data
    pecs_data = section.pecs_data.get('prime_preview', {}) if section.pecs_data else {}

    with ui.column().classes('w-full max-w-4xl'):
        ui.label('📖 Prime & Preview').classes('text-2xl font-bold mb-2')
        ui.label('Read the section and reflect on your understanding').classes('text-gray-600 mb-6')

        # Section content (collapsible)
        with ui.expansion('View Section Content', icon='book').classes('mb-6 bg-gray-50'):
            ui.markdown(section.content[:500] + '...' if len(section.content) > 500 else section.content)

        # Understanding input
        ui.label('What did you understand?').classes('font-semibold mb-2')
        understanding_input = ui.textarea(
            placeholder='Summarize in your own words...',
            value=pecs_data.get('initial_thoughts', '')
        ).classes('w-full mb-4').props('rows=5')

        # Prior knowledge
        ui.label('What do you already know about this?').classes('font-semibold mb-2')
        prior_knowledge_input = ui.textarea(
            placeholder='Connect to prior knowledge...',
            value=pecs_data.get('prior_knowledge', '')
        ).classes('w-full mb-4').props('rows=3')

        # Questions
        ui.label('What questions do you have?').classes('font-semibold mb-2')
        questions_input = ui.textarea(
            placeholder='What are you curious about?',
            value=pecs_data.get('questions', '')
        ).classes('w-full mb-6').props('rows=3')

        # Action buttons
        with ui.row().classes('gap-4'):
            async def save_prime():
                data = {
                    'initial_thoughts': understanding_input.value,
                    'prior_knowledge': prior_knowledge_input.value,
                    'questions': questions_input.value
                }
                db.update_section_pecs_data(section.id, 'prime_preview', data)
                ui.notify('Prime phase saved!', color='positive')

            ui.button('💾 Save Progress', on_click=save_prime).classes('bg-blue-500')

            async def get_ai_feedback():
                if not understanding_input.value:
                    ui.notify('Please write your understanding first', color='warning')
                    return

                # Show loading dialog
                with ui.dialog() as loading_dialog, ui.card():
                    ui.label('Analyzing your response...').classes('text-lg')
                    ui.spinner(size='lg')

                loading_dialog.open()

                try:
                    # Get AI feedback (simulated for demo)
                    # In real app: from utils.llm_service import LLMService
                    # feedback = LLMService().analyze_section_understanding(section.content, understanding_input.value)
                    feedback = "**Great start!** Your summary captures the key concepts. To deepen understanding, try connecting this to real-world examples."

                    loading_dialog.close()

                    # Show feedback dialog
                    with ui.dialog() as feedback_dialog, ui.card().classes('w-96'):
                        ui.label('🤖 AI Feedback').classes('text-xl font-bold mb-4')
                        ui.markdown(feedback)
                        ui.button('Close', on_click=feedback_dialog.close).classes('mt-4 w-full')

                    feedback_dialog.open()
                except Exception as e:
                    loading_dialog.close()
                    ui.notify(f'Error getting feedback: {str(e)}', color='negative')

            ui.button('🤖 Get AI Feedback', on_click=get_ai_feedback).classes('bg-purple-500')


# ===== PAGE: Study Mode (Flashcards) =====
@ui.page('/study/{project_id}')
def study_mode(project_id: int):
    """Flashcard study mode with spaced repetition"""

    project = db.get_project(project_id)
    if not project:
        ui.label('Project not found').classes('text-xl text-red-500')
        return

    # Header
    with ui.row().classes('w-full items-center gap-4 mb-6'):
        ui.button('← Back', on_click=lambda: ui.navigate.to(f'/project/{project_id}')).classes('bg-gray-300')
        ui.label(f'Study: {project.name}').classes('text-2xl font-bold')

    # Get flashcards for review
    cards = db.get_flashcards_for_review(project_id)

    if not cards:
        with ui.column().classes('items-center justify-center mt-12'):
            ui.label('No cards to review!').classes('text-xl text-gray-500')
            ui.label('Create flashcards in the Solidify phase').classes('text-gray-400')
            ui.button('← Back to Project', on_click=lambda: ui.navigate.to(f'/project/{project_id}')).classes('mt-4')
    else:
        # Study session UI
        ui.label(f'{len(cards)} cards ready for review').classes('text-lg text-gray-600 mb-4')

        # Simple demo - show first card
        card = cards[0]

        with ui.card().classes('w-full max-w-2xl mx-auto p-8'):
            ui.label('Question').classes('text-sm text-gray-500 mb-2')
            ui.markdown(card.question).classes('text-xl mb-6')

            show_answer_btn = ui.button(
                'Show Answer',
                on_click=lambda: show_answer(card)
            ).classes('w-full bg-blue-500')


def show_answer(card):
    """Show flashcard answer and review buttons (simplified demo)"""
    ui.notify('Answer shown! (Full implementation in actual migration)', color='positive')


# ===== RUN APP =====
if __name__ in {"__main__", "__mp_main__"}:
    print("\n" + "="*60)
    print("🚀 NiceGUI Demo for PECS Learning System")
    print("="*60)
    print("\n📝 This is a proof-of-concept showing:")
    print("   • Modern, responsive UI")
    print("   • No page reloads (smooth interactions)")
    print("   • 90% backend code reuse")
    print("   • Easy to understand and maintain")
    print("\n🌐 Visit: http://localhost:8502")
    print("\n⚙️  Features demonstrated:")
    print("   ✓ Project dashboard with stats")
    print("   ✓ Create/delete projects")
    print("   ✓ Section navigator")
    print("   ✓ PECS Prime phase (partial)")
    print("   ✓ Smooth dialogs and notifications")
    print("\n" + "="*60 + "\n")

    ui.run(
        port=8502,
        title='PECS Learning System (NiceGUI Demo)',
        favicon='📚',
        reload=True,
        show=False  # Don't auto-open browser
    )
