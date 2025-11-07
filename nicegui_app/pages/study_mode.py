# -*- coding: utf-8 -*-
"""
Study Mode Page - Flashcard spaced repetition practice
Migrated from components/study_mode.py
"""

from nicegui import ui
from utils.database import DatabaseRepository
from utils.models import Flashcard
from datetime import datetime


class StudyModePage:
    """Interactive flashcard study mode with spaced repetition"""

    def __init__(self, db: DatabaseRepository, project_id: int, user_id: int = None):
        """
        Initialize study mode

        Args:
            db: Database repository
            project_id: Project ID to study
            user_id: Optional user ID (future)
        """
        self.db = db
        self.project_id = project_id
        self.user_id = user_id
        self.project = db.get_project(project_id)

        # Study session state
        self.current_index = 0
        self.show_answer = False
        self.study_cards = []
        self.study_mode = 'due'  # 'due', 'all', or 'mastered'

    def render(self):
        """Render study mode interface"""

        if not self.project:
            ui.label('Project not found').classes('text-xl text-red-500')
            ui.button('� Back', on_click=lambda: ui.navigate.to('/')).classes('mt-4')
            return

        # Header
        with ui.row().classes('w-full items-center gap-2 mb-6'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to(f'/project/{self.project_id}')).props('flat')
            ui.label(f'Study: {self.project.name}').classes('text-xl md:text-2xl font-bold flex-1')

        # Study mode selection
        with ui.row().classes('gap-4 mb-4 flex-wrap'):
            study_mode_radio = ui.radio(
                ['Cards Due for Review', 'All Cards', 'Mastered Cards'],
                value='Cards Due for Review'
            ).props('inline')

            shuffle_checkbox = ui.checkbox('Shuffle cards', value=False).classes('ml-4')

        # Card container (will be updated dynamically)
        card_container = ui.column().classes('w-full max-w-3xl mx-auto')

        def load_cards():
            """Load cards based on selected mode"""
            if study_mode_radio.value == 'Cards Due for Review':
                self.study_cards = self.db.get_flashcards_for_review(self.project_id)
            elif study_mode_radio.value == 'All Cards':
                self.study_cards = self.db.get_flashcards_by_project(self.project_id)
            else:  # Mastered
                all_cards = self.db.get_flashcards_by_project(self.project_id)
                self.study_cards = [c for c in all_cards if c.is_mastered]

            # Shuffle if requested
            if shuffle_checkbox.value and self.study_cards:
                import random
                self.study_cards = random.sample(self.study_cards, len(self.study_cards))

            # Reset state
            self.current_index = 0
            self.show_answer = False

            # Render cards
            render_study_session()

        def render_study_session():
            """Render the study session"""
            card_container.clear()

            with card_container:
                if not self.study_cards:
                    self._render_no_cards(study_mode_radio.value)
                    return

                # Progress
                progress = (self.current_index + 1) / len(self.study_cards) if self.study_cards else 0
                ui.linear_progress(value=progress).classes('mb-2')
                ui.label(f'Card {self.current_index + 1} of {len(self.study_cards)}').classes('text-sm text-gray-600 mb-4')

                # Current card
                current_card = self.study_cards[self.current_index]
                self._render_flashcard(current_card, render_study_session)

                # Navigation
                with ui.row().classes('w-full gap-2 mt-6'):
                    ui.button(
                        '� Previous',
                        on_click=lambda: self._navigate('prev', render_study_session)
                    ).classes('flex-1').props('outline')

                    ui.button(
                        '= Reset',
                        on_click=lambda: self._navigate('reset', render_study_session)
                    ).classes('flex-1').props('outline')

                    ui.button(
                        '� Next',
                        on_click=lambda: self._navigate('next', render_study_session)
                    ).classes('flex-1').props('outline')

        # Listen for mode changes
        study_mode_radio.on('update:modelValue', load_cards)
        shuffle_checkbox.on('update:modelValue', load_cards)

        # Initial load
        load_cards()

        # Sidebar stats
        self._render_stats_sidebar()

    def _render_flashcard(self, card: Flashcard, refresh_callback):
        """Render a single flashcard"""

        with ui.card().classes('w-full p-8 min-h-64'):
            # Question
            ui.label('Question').classes('text-sm text-gray-500 mb-2')
            ui.markdown(f'**{card.question}**').classes('text-xl mb-4')

            if not self.show_answer:
                # Show answer button
                def reveal():
                    self.show_answer = True
                    refresh_callback()

                ui.button(
                    '= Reveal Answer',
                    icon='visibility',
                    on_click=reveal
                ).classes('bg-blue-500 text-lg px-6 py-3 mt-4')

            else:
                # Show answer and review buttons
                ui.separator().classes('my-4')
                ui.label('Answer').classes('text-sm text-gray-500 mb-2')
                ui.markdown(card.answer).classes('text-lg font-semibold')

                # Review buttons
                with ui.row().classes('w-full gap-4 mt-6'):
                    def review_forgot():
                        self._review_card(card, False, refresh_callback)

                    def review_knew():
                        self._review_card(card, True, refresh_callback)

                    ui.button(
                        'L Forgot',
                        icon='close',
                        on_click=review_forgot
                    ).classes('flex-1 bg-red-500 text-lg py-3')

                    ui.button(
                        ' Knew It',
                        icon='check',
                        on_click=review_knew
                    ).classes('flex-1 bg-green-500 text-lg py-3')

                # Card metadata
                with ui.row().classes('gap-4 mt-4 text-xs text-gray-500'):
                    ui.label(f'Review count: {card.review_count}')
                    ui.label(f'Ease factor: {card.ease_factor:.2f}')
                    if card.next_review:
                        days_until = (card.next_review - datetime.utcnow()).days
                        if days_until > 0:
                            ui.label(f'Next review in {days_until} days')
                        elif days_until == 0:
                            ui.label('Due today!')
                        else:
                            ui.label('Overdue!')

    def _render_no_cards(self, mode: str):
        """Render empty state when no cards available"""
        with ui.column().classes('items-center mt-12'):
            ui.icon('style').classes('text-6xl text-gray-400')
            ui.label(f'No cards available for "{mode}"').classes('text-xl text-gray-500 text-center mt-4')
            ui.label('Create some flashcards in the Solidify phase').classes('text-gray-400 text-center')
            ui.button(
                '� Back to Project',
                on_click=lambda: ui.navigate.to(f'/project/{self.project_id}')
            ).classes('mt-4')

    def _review_card(self, card: Flashcard, knew_it: bool, refresh_callback):
        """Review a flashcard and move to next"""
        # Update flashcard review
        self.db.update_flashcard_review(card.id, knew_it)

        # Move to next card
        self.current_index += 1
        self.show_answer = False

        # Check if session complete
        if self.current_index >= len(self.study_cards):
            ui.notify('<� Study session complete! Great work!', color='positive', position='top')
            self.current_index = 0

        refresh_callback()

    def _navigate(self, direction: str, refresh_callback):
        """Navigate between cards"""
        if direction == 'prev':
            self.current_index = max(0, self.current_index - 1)
        elif direction == 'next':
            self.current_index = (self.current_index + 1) % len(self.study_cards) if self.study_cards else 0
        elif direction == 'reset':
            self.current_index = 0

        self.show_answer = False
        refresh_callback()

    def _render_stats_sidebar(self):
        """Render statistics in a card"""
        stats = self.db.get_project_stats(self.project_id)

        with ui.card().classes('w-full max-w-md mx-auto mt-6 p-4'):
            ui.label('=� Study Statistics').classes('text-lg font-bold mb-3')

            with ui.row().classes('w-full justify-around'):
                with ui.column().classes('items-center'):
                    ui.label(str(stats.get('total_flashcards', 0))).classes('text-2xl font-bold text-blue-600')
                    ui.label('Total Cards').classes('text-xs text-gray-600')

                with ui.column().classes('items-center'):
                    ui.label(str(stats.get('mastered_flashcards', 0))).classes('text-2xl font-bold text-green-600')
                    ui.label('Mastered').classes('text-xs text-gray-600')

                with ui.column().classes('items-center'):
                    ui.label(str(stats.get('cards_due_for_review', 0))).classes('text-2xl font-bold text-orange-600')
                    ui.label('Due for Review').classes('text-xs text-gray-600')
