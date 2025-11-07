"""
Project Dashboard - Main landing page
Migrated from components/project_dashboard.py
"""

from nicegui import ui
from utils.database import DatabaseRepository
from utils.models import Project
from datetime import datetime


class DashboardPage:
    """Project dashboard for viewing and managing study projects"""

    def __init__(self, db: DatabaseRepository, user_id: int = None):
        """
        Initialize dashboard

        Args:
            db: Database repository instance
            user_id: Optional user ID for multi-user support (future)
        """
        self.db = db
        self.user_id = user_id  # Future: filter projects by user

    def render(self):
        """Render the complete dashboard page"""

        # Header with branding
        with ui.row().classes('w-full items-center justify-between mb-6 flex-wrap gap-4'):
            ui.label('=Ú P.E.C.S. Learning System').classes('text-2xl md:text-3xl font-bold')
            ui.button(
                '• New Project',
                icon='add',
                on_click=self._show_create_project_dialog
            ).classes('bg-blue-500')

        # Get projects
        projects = self.db.get_all_projects()

        if not projects:
            # Empty state
            self._render_empty_state()
        else:
            # Project grid
            self._render_projects_grid(projects)

    def _render_empty_state(self):
        """Render empty state when no projects exist"""
        with ui.column().classes('items-center justify-center mt-12 px-4 max-w-2xl mx-auto'):
            ui.icon('school').classes('text-6xl text-gray-400 mb-4')
            ui.label('Welcome to P.E.C.S. Learning System!').classes('text-2xl font-bold text-gray-700 text-center')
            ui.label('You don\'t have any projects yet.').classes('text-lg text-gray-500 text-center mb-6')

            # Explainer
            with ui.card().classes('w-full p-6 bg-blue-50'):
                ui.label('What is P.E.C.S.?').classes('text-xl font-bold mb-3')
                with ui.column().classes('gap-2'):
                    ui.label('=Ö P - Prime & Preview: Skim and prepare for deeper reading').classes('text-sm')
                    ui.label(' E - Engage & Explain: Deep reading and understanding in your own words').classes('text-sm')
                    ui.label('> C - Challenge & Connect: Critical thinking and making connections').classes('text-sm')
                    ui.label('<¯ S - Solidify & Space: Create flashcards and spaced repetition review').classes('text-sm')

            ui.button(
                'Create Your First Project',
                icon='add_circle',
                on_click=self._show_create_project_dialog
            ).classes('mt-6 bg-blue-500 text-lg px-8 py-3')

    def _render_projects_grid(self, projects: list[Project]):
        """Render grid of project cards"""
        ui.label(f'Your Projects ({len(projects)})').classes('text-xl font-semibold mb-4')

        # Responsive grid
        with ui.grid(columns='repeat(auto-fill, minmax(300px, 1fr))').classes('w-full gap-4'):
            for project in projects:
                self._render_project_card(project)

    def _render_project_card(self, project: Project):
        """Render a single project card with stats and actions"""

        stats = self.db.get_project_stats(project.id)

        with ui.card().classes('cursor-pointer hover:shadow-lg transition-all'):
            # Header
            with ui.row().classes('w-full items-start justify-between mb-3'):
                with ui.column().classes('flex-1'):
                    ui.label(project.name).classes('text-xl font-bold')
                    created_date = project.created_at.strftime('%b %d, %Y') if project.created_at else 'Unknown'
                    ui.label(f'Created: {created_date}').classes('text-xs text-gray-500')

                ui.icon('folder_open').classes('text-blue-500 text-2xl')

            # Stats row
            with ui.row().classes('w-full gap-4 mb-4'):
                with ui.column().classes('items-center'):
                    ui.label(str(stats.get('total_sections', 0))).classes('text-2xl font-bold text-blue-600')
                    ui.label('Sections').classes('text-xs text-gray-600')

                with ui.column().classes('items-center'):
                    ui.label(str(stats.get('completed_sections', 0))).classes('text-2xl font-bold text-green-600')
                    ui.label('Completed').classes('text-xs text-gray-600')

                with ui.column().classes('items-center'):
                    ui.label(str(stats.get('total_flashcards', 0))).classes('text-2xl font-bold text-purple-600')
                    ui.label('Flashcards').classes('text-xs text-gray-600')

            # Due for review badge
            cards_due = stats.get('cards_due_for_review', 0)
            if cards_due > 0:
                with ui.row().classes('items-center gap-2 mb-3'):
                    ui.icon('alarm').classes('text-orange-500')
                    ui.label(f'{cards_due} cards due for review').classes('text-sm text-orange-600 font-semibold')

            # Progress bar
            total_sections = stats.get('total_sections', 0)
            if total_sections > 0:
                progress = stats.get('completed_sections', 0) / total_sections
                ui.linear_progress(value=progress).classes('mb-2')
                ui.label(f'{int(progress * 100)}% Complete').classes('text-xs text-gray-500')

            # Action buttons
            with ui.row().classes('w-full gap-2 mt-4'):
                ui.button(
                    'Open',
                    icon='arrow_forward',
                    on_click=lambda p=project: ui.navigate.to(f'/project/{p.id}')
                ).classes('flex-1 bg-blue-500')

                ui.button(
                    icon='delete',
                    on_click=lambda p=project: self._confirm_delete_project(p)
                ).props('flat').classes('text-red-500')

    def _show_create_project_dialog(self):
        """Show dialog to create new project"""

        with ui.dialog() as dialog, ui.card().classes('w-full max-w-md mx-4'):
            ui.label('Create New Project').classes('text-2xl font-bold mb-4')

            project_name_input = ui.input(
                label='Project Name',
                placeholder='e.g., Learn Quantum Physics'
            ).classes('w-full').props('autofocus')

            # Error message placeholder
            error_label = ui.label('').classes('text-red-500 text-sm mt-2')
            error_label.visible = False

            async def create_project():
                name = project_name_input.value.strip()

                if not name:
                    error_label.text = 'Please enter a project name'
                    error_label.visible = True
                    return

                # Check for duplicate
                existing_projects = self.db.get_all_projects()
                if any(p.name.lower() == name.lower() for p in existing_projects):
                    error_label.text = 'A project with this name already exists'
                    error_label.visible = True
                    return

                # Create project
                project = self.db.create_project(name)
                if project:
                    ui.notify(f'Project "{name}" created!', color='positive', position='top')
                    dialog.close()
                    ui.navigate.reload()  # Refresh dashboard
                else:
                    error_label.text = 'Failed to create project. Please try again.'
                    error_label.visible = True

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).classes('bg-gray-300')
                ui.button('Create', on_click=create_project).classes('bg-blue-500')

        dialog.open()

    def _confirm_delete_project(self, project: Project):
        """Show confirmation dialog before deleting project"""

        with ui.dialog() as dialog, ui.card().classes('max-w-sm mx-4'):
            ui.label(f'Delete "{project.name}"?').classes('text-xl font-bold')
            ui.label('This will delete all sections and flashcards. This action cannot be undone.').classes('text-gray-600 mt-2')

            async def delete_project():
                if self.db.delete_project(project.id):
                    ui.notify(f'Project "{project.name}" deleted', color='positive', position='top')
                    dialog.close()
                    ui.navigate.reload()  # Refresh dashboard
                else:
                    ui.notify('Failed to delete project', color='negative', position='top')

            with ui.row().classes('w-full gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).classes('flex-1 bg-gray-300')
                ui.button('Delete', on_click=delete_project).classes('flex-1 bg-red-500')

        dialog.open()
