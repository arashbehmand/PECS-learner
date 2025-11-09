# -*- coding: utf-8 -*-
"""
PECS Learning Page - Guided vertical learning flow
Redesigned for natural learning progression
"""

from nicegui import ui
from utils.database import DatabaseRepository
from utils.llm_service import LLMService
from utils.models import Section


class PECSLearningPage:
    """PECS 4-phase guided learning flow: Prime → Engage → Challenge → Solidify"""

    def __init__(self, db: DatabaseRepository, project_id: int, section_id: int, user_id: int = None):
        """
        Initialize PECS learning page

        Args:
            db: Database repository
            project_id: Project ID
            section_id: Section ID to learn
            user_id: Optional user ID (future)
        """
        self.db = db
        self.project_id = project_id
        self.section_id = section_id
        self.user_id = user_id
        self.section = db.get_section(section_id)
        self.llm_service = LLMService()

        # Initialize PECS data if needed
        if self.section and not self.section.pecs_data:
            self.section.pecs_data = {
                'prime_preview': {},
                'engage_explain': {},
                'challenge_connect': {},
                'solidify_space': {}
            }

    def render(self):
        """Render guided learning flow"""

        if not self.section:
            ui.label('Section not found').classes('text-xl text-red-500')
            ui.button('Back', on_click=lambda: ui.navigate.to(f'/project/{self.project_id}')).classes('mt-4')
            return

        # Header
        with ui.row().classes('w-full items-center gap-2 mb-4'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to(f'/project/{self.project_id}')).props('flat')
            section_title = self.section.title or f'Section {self.section.order_index + 1}'
            ui.label(section_title).classes('text-lg md:text-2xl font-bold flex-1')

        # Progress indicator
        self._render_progress_indicator()

        # Content section (always visible)
        with ui.card().classes('w-full mb-4 bg-gray-50'):
            ui.label('Learning Material').classes('text-xl font-bold mb-3')
            with ui.scroll_area().classes('w-full h-64'):
                ui.markdown(self.section.content or 'No content available').classes('text-sm')

        # Vertical learning flow
        with ui.column().classes('w-full gap-4'):
            self._render_prime_phase()
            self._render_engage_phase()
            self._render_challenge_phase()
            self._render_solidify_phase()

    def _render_progress_indicator(self):
        """Render progress bar showing current phase"""
        phases = ['Prime', 'Engage', 'Challenge', 'Solidify']
        current_phase = self._get_current_phase()

        with ui.row().classes('w-full items-center gap-2 mb-4 p-4 bg-blue-50 rounded'):
            ui.label('Progress:').classes('font-semibold')
            for i, phase in enumerate(phases):
                if i > 0:
                    # Arrow between phases
                    if i <= current_phase:
                        ui.label('▶').classes('text-blue-500')
                    else:
                        ui.label('→').classes('text-gray-300')

                # Phase name
                if i < current_phase:
                    ui.label(f'✓ {phase}').classes('text-green-600 font-semibold')
                elif i == current_phase:
                    ui.label(f'▶ {phase}').classes('text-blue-600 font-bold')
                else:
                    ui.label(phase).classes('text-gray-400')

    def _get_current_phase(self) -> int:
        """Get current phase index (0-3)"""
        pecs_data = self.section.pecs_data or {}

        # Check completion status of each phase
        if not pecs_data.get('prime_preview', {}).get('completed'):
            return 0
        elif not pecs_data.get('engage_explain', {}).get('completed'):
            return 1
        elif not pecs_data.get('challenge_connect', {}).get('completed'):
            return 2
        elif not pecs_data.get('solidify_space', {}).get('completed'):
            return 3
        else:
            return 3  # All complete

    def _is_phase_unlocked(self, phase_index: int) -> bool:
        """Check if a phase is unlocked"""
        if phase_index == 0:
            return True  # Prime is always unlocked

        # Check if previous phase is completed
        pecs_data = self.section.pecs_data or {}
        phases = ['prime_preview', 'engage_explain', 'challenge_connect', 'solidify_space']

        if phase_index > 0:
            previous_phase = phases[phase_index - 1]
            return pecs_data.get(previous_phase, {}).get('completed', False)

        return True

    def _render_prime_phase(self):
        """Phase 1: Prime & Preview - First impressions"""
        phase_data = self.section.pecs_data.get('prime_preview', {})
        is_completed = phase_data.get('completed', False)
        current_phase = self._get_current_phase()

        # Phase card
        card_classes = 'w-full p-6 '
        if is_completed:
            card_classes += 'bg-green-50 border-l-4 border-green-500'
        elif current_phase == 0:
            card_classes += 'bg-blue-50 border-l-4 border-blue-500'
        else:
            card_classes += 'bg-gray-100'

        with ui.card().classes(card_classes):
            # Header
            with ui.row().classes('w-full items-center gap-2 mb-4'):
                if is_completed:
                    ui.icon('check_circle', size='sm').classes('text-green-600')
                elif current_phase == 0:
                    ui.icon('play_circle', size='sm').classes('text-blue-600')
                else:
                    ui.icon('radio_button_unchecked', size='sm').classes('text-gray-400')

                ui.label('Phase 1: Prime & Preview').classes('text-xl font-bold flex-1')

            ui.label('First Impressions - What do you notice? What stands out?').classes('text-sm text-gray-600 mb-4')

            # Show completed work (collapsed)
            if is_completed:
                with ui.expansion('See your work', icon='visibility').classes('w-full'):
                    if phase_data.get('understanding'):
                        ui.label('Your thoughts:').classes('font-semibold mt-2')
                        ui.label(phase_data['understanding']).classes('text-sm p-2 bg-white rounded')

                    if phase_data.get('ai_feedback'):
                        ui.label('AI Feedback:').classes('font-semibold mt-3')
                        ui.markdown(phase_data['ai_feedback']).classes('text-sm p-3 bg-purple-50 rounded')

            # Active input area
            else:
                understanding_input = ui.textarea(
                    label='What are your first impressions? What stands out to you?',
                    placeholder='Write your initial thoughts about this material...',
                    value=phase_data.get('understanding', '')
                ).classes('w-full').props('rows=4')

                with ui.row().classes('w-full gap-2 mt-3'):
                    ui.button(
                        'Save',
                        icon='save',
                        on_click=lambda: self._save_phase_data('prime_preview', 'understanding', understanding_input.value)
                    ).classes('bg-blue-500')

                    ui.button(
                        'Get AI Feedback',
                        icon='psychology',
                        on_click=lambda: self._get_ai_feedback('prime_preview', 'section_understanding', understanding_input.value)
                    ).classes('bg-purple-500')

                    if phase_data.get('understanding'):
                        ui.button(
                            'Mark Complete',
                            icon='check',
                            on_click=lambda: self._complete_phase('prime_preview')
                        ).classes('bg-green-500')

                # Show AI feedback if available
                if phase_data.get('ai_feedback'):
                    with ui.card().classes('w-full mt-4 bg-purple-50'):
                        ui.label('AI Feedback').classes('font-semibold mb-2')
                        ui.markdown(phase_data['ai_feedback']).classes('text-sm')

    def _render_engage_phase(self):
        """Phase 2: Engage & Explain - Deep understanding"""
        phase_data = self.section.pecs_data.get('engage_explain', {})
        is_completed = phase_data.get('completed', False)
        is_unlocked = self._is_phase_unlocked(1)
        current_phase = self._get_current_phase()

        # Phase card
        card_classes = 'w-full p-6 '
        if is_completed:
            card_classes += 'bg-green-50 border-l-4 border-green-500'
        elif current_phase == 1:
            card_classes += 'bg-blue-50 border-l-4 border-blue-500'
        else:
            card_classes += 'bg-gray-100'

        with ui.card().classes(card_classes):
            # Header
            with ui.row().classes('w-full items-center gap-2 mb-4'):
                if is_completed:
                    ui.icon('check_circle', size='sm').classes('text-green-600')
                elif current_phase == 1:
                    ui.icon('play_circle', size='sm').classes('text-blue-600')
                elif not is_unlocked:
                    ui.icon('lock', size='sm').classes('text-gray-400')
                else:
                    ui.icon('radio_button_unchecked', size='sm').classes('text-gray-400')

                ui.label('Phase 2: Engage & Explain').classes('text-xl font-bold flex-1')

            if not is_unlocked:
                ui.label('🔒 Complete Phase 1 first').classes('text-gray-500 italic')
                return

            ui.label('Deep Understanding - Explain the concepts in your own words').classes('text-sm text-gray-600 mb-4')

            # Show completed work (collapsed)
            if is_completed:
                with ui.expansion('See your work', icon='visibility').classes('w-full'):
                    if phase_data.get('explanation'):
                        ui.label('Your explanation:').classes('font-semibold mt-2')
                        ui.label(phase_data['explanation']).classes('text-sm p-2 bg-white rounded')

                    if phase_data.get('ai_feedback'):
                        ui.label('AI Feedback:').classes('font-semibold mt-3')
                        ui.markdown(phase_data['ai_feedback']).classes('text-sm p-3 bg-purple-50 rounded')

            # Active input area
            else:
                explanation_input = ui.textarea(
                    label='Explain the key concepts in your own simple words',
                    placeholder='Write your understanding here...',
                    value=phase_data.get('explanation', '')
                ).classes('w-full').props('rows=5')

                with ui.row().classes('w-full gap-2 mt-3'):
                    ui.button(
                        'Save',
                        icon='save',
                        on_click=lambda: self._save_phase_data('engage_explain', 'explanation', explanation_input.value)
                    ).classes('bg-blue-500')

                    ui.button(
                        'Get AI Feedback',
                        icon='psychology',
                        on_click=lambda: self._get_ai_feedback('engage_explain', 'explanation', explanation_input.value)
                    ).classes('bg-purple-500')

                    if phase_data.get('explanation'):
                        ui.button(
                            'Mark Complete',
                            icon='check',
                            on_click=lambda: self._complete_phase('engage_explain')
                        ).classes('bg-green-500')

                # Show AI feedback if available
                if phase_data.get('ai_feedback'):
                    with ui.card().classes('w-full mt-4 bg-purple-50'):
                        ui.label('AI Feedback').classes('font-semibold mb-2')
                        ui.markdown(phase_data['ai_feedback']).classes('text-sm')

    def _render_challenge_phase(self):
        """Phase 3: Challenge & Connect - Critical thinking"""
        phase_data = self.section.pecs_data.get('challenge_connect', {})
        is_completed = phase_data.get('completed', False)
        is_unlocked = self._is_phase_unlocked(2)
        current_phase = self._get_current_phase()

        # Phase card
        card_classes = 'w-full p-6 '
        if is_completed:
            card_classes += 'bg-green-50 border-l-4 border-green-500'
        elif current_phase == 2:
            card_classes += 'bg-blue-50 border-l-4 border-blue-500'
        else:
            card_classes += 'bg-gray-100'

        with ui.card().classes(card_classes):
            # Header
            with ui.row().classes('w-full items-center gap-2 mb-4'):
                if is_completed:
                    ui.icon('check_circle', size='sm').classes('text-green-600')
                elif current_phase == 2:
                    ui.icon('play_circle', size='sm').classes('text-blue-600')
                elif not is_unlocked:
                    ui.icon('lock', size='sm').classes('text-gray-400')
                else:
                    ui.icon('radio_button_unchecked', size='sm').classes('text-gray-400')

                ui.label('Phase 3: Challenge & Connect').classes('text-xl font-bold flex-1')

            if not is_unlocked:
                ui.label('🔒 Complete Phase 2 first').classes('text-gray-500 italic')
                return

            ui.label('Critical Thinking - Ask questions, make connections, think deeper').classes('text-sm text-gray-600 mb-4')

            # Show completed work (collapsed)
            if is_completed:
                with ui.expansion('See your work', icon='visibility').classes('w-full'):
                    if phase_data.get('critical_questions'):
                        ui.label('Your questions & connections:').classes('font-semibold mt-2')
                        ui.label(phase_data['critical_questions']).classes('text-sm p-2 bg-white rounded')

                    if phase_data.get('ai_feedback'):
                        ui.label('AI Feedback:').classes('font-semibold mt-3')
                        ui.markdown(phase_data['ai_feedback']).classes('text-sm p-3 bg-purple-50 rounded')

            # Active input area
            else:
                critical_input = ui.textarea(
                    label='What questions do you have? How does this connect to what you know?',
                    placeholder='Ask critical questions, make connections...',
                    value=phase_data.get('critical_questions', '')
                ).classes('w-full').props('rows=5')

                with ui.row().classes('w-full gap-2 mt-3'):
                    ui.button(
                        'Save',
                        icon='save',
                        on_click=lambda: self._save_phase_data('challenge_connect', 'critical_questions', critical_input.value)
                    ).classes('bg-blue-500')

                    ui.button(
                        'Get AI Feedback',
                        icon='psychology',
                        on_click=lambda: self._get_ai_feedback('challenge_connect', 'critical_thinking', critical_input.value)
                    ).classes('bg-purple-500')

                    if phase_data.get('critical_questions'):
                        ui.button(
                            'Mark Complete',
                            icon='check',
                            on_click=lambda: self._complete_phase('challenge_connect')
                        ).classes('bg-green-500')

                # Show AI feedback if available
                if phase_data.get('ai_feedback'):
                    with ui.card().classes('w-full mt-4 bg-purple-50'):
                        ui.label('AI Feedback').classes('font-semibold mb-2')
                        ui.markdown(phase_data['ai_feedback']).classes('text-sm')

    def _render_solidify_phase(self):
        """Phase 4: Solidify & Space - Create flashcards"""
        phase_data = self.section.pecs_data.get('solidify_space', {})
        is_completed = phase_data.get('completed', False)
        is_unlocked = self._is_phase_unlocked(3)
        current_phase = self._get_current_phase()

        # Phase card
        card_classes = 'w-full p-6 '
        if is_completed:
            card_classes += 'bg-green-50 border-l-4 border-green-500'
        elif current_phase == 3:
            card_classes += 'bg-blue-50 border-l-4 border-blue-500'
        else:
            card_classes += 'bg-gray-100'

        with ui.card().classes('w-full p-6 bg-gray-100'):
            # Header
            with ui.row().classes('w-full items-center gap-2 mb-4'):
                if is_completed:
                    ui.icon('check_circle', size='sm').classes('text-green-600')
                elif current_phase == 3:
                    ui.icon('play_circle', size='sm').classes('text-blue-600')
                elif not is_unlocked:
                    ui.icon('lock', size='sm').classes('text-gray-400')
                else:
                    ui.icon('radio_button_unchecked', size='sm').classes('text-gray-400')

                ui.label('Phase 4: Solidify & Space').classes('text-xl font-bold flex-1')

            if not is_unlocked:
                ui.label('🔒 Complete Phase 3 first').classes('text-gray-500 italic')
                return

            ui.label('Create Flashcards - Turn key concepts into spaced repetition cards').classes('text-sm text-gray-600 mb-4')

            # Flashcard management
            flashcards = self.db.get_flashcards_by_section(self.section_id)

            if flashcards:
                ui.label(f'Your Flashcards ({len(flashcards)})').classes('font-semibold mb-3')
                for card in flashcards:
                    with ui.card().classes('w-full mb-2 bg-white'):
                        ui.label(f'Q: {card.question}').classes('text-sm font-semibold')
                        ui.label(f'A: {card.answer}').classes('text-sm text-gray-600 mt-1')
                        ui.button(
                            icon='delete',
                            on_click=lambda c=card.id: self._delete_flashcard(c)
                        ).props('flat dense').classes('text-red-500')

            # Add flashcard form
            ui.label('Add New Flashcard').classes('font-semibold mt-4 mb-2')

            question_input = ui.input(
                label='Question',
                placeholder='What question tests understanding?'
            ).classes('w-full')

            answer_input = ui.textarea(
                label='Answer',
                placeholder='The answer...'
            ).classes('w-full').props('rows=3')

            with ui.row().classes('w-full gap-2 mt-3'):
                ui.button(
                    'Add Flashcard',
                    icon='add',
                    on_click=lambda: self._add_flashcard(question_input, answer_input)
                ).classes('bg-blue-500')

                if self.llm_service.is_available():
                    ui.button(
                        'AI Flashcard Suggestions',
                        icon='auto_awesome',
                        on_click=self._generate_ai_flashcards
                    ).classes('bg-purple-500')

            # Mark complete button
            if flashcards:
                ui.button(
                    'Mark Section Complete',
                    icon='check_circle',
                    on_click=lambda: self._complete_phase('solidify_space')
                ).classes('bg-green-500 mt-4')

    def _save_phase_data(self, phase: str, field: str, value: str):
        """Save data for a specific field in a phase"""
        pecs_data = self.section.pecs_data.get(phase, {})
        pecs_data[field] = value
        self.db.update_section_pecs_data(self.section_id, phase, pecs_data)

        # Refresh section data
        self.section = self.db.get_section(self.section_id)

        ui.notify('Saved!', color='positive', position='top')
        ui.navigate.reload()

    async def _get_ai_feedback(self, phase: str, feedback_type: str, user_input: str):
        """Get AI feedback and save it permanently"""
        if not user_input:
            ui.notify('Please write something first', color='warning', position='top')
            return

        # Check if LLM service is available
        if not self.llm_service.is_available():
            ui.notify('AI features require an OpenAI API key. Set OPENAI_API_KEY environment variable.',
                     color='warning', position='top')
            return

        # Create loading dialog
        with ui.dialog() as dialog, ui.card().classes('max-w-2xl'):
            ui.label('Analyzing with AI...').classes('text-lg font-bold')
            ui.spinner(size='lg')

        dialog.open()

        try:
            # Run LLM call in thread pool to avoid blocking UI
            import asyncio
            feedback = None

            if feedback_type == 'section_understanding':
                feedback = await asyncio.to_thread(
                    self.llm_service.analyze_section_understanding,
                    self.section.content,
                    user_input
                )
            elif feedback_type == 'explanation':
                feedback = await asyncio.to_thread(
                    self.llm_service.analyze_explanation,
                    self.section.content,
                    user_input
                )
            elif feedback_type == 'critical_thinking':
                feedback = await asyncio.to_thread(
                    self.llm_service.analyze_critical_thinking,
                    self.section.content,
                    user_input
                )

            dialog.close()

            if feedback:
                # Save feedback to database permanently
                pecs_data = self.section.pecs_data.get(phase, {})
                pecs_data['ai_feedback'] = feedback
                self.db.update_section_pecs_data(self.section_id, phase, pecs_data)

                # Refresh section data
                self.section = self.db.get_section(self.section_id)

                ui.notify('AI feedback saved!', color='positive', position='top')
                ui.navigate.reload()
            else:
                ui.notify('Could not generate feedback', color='warning', position='top')

        except Exception as e:
            dialog.close()
            ui.notify(f'Error: {str(e)}', color='negative', position='top')

    def _complete_phase(self, phase: str):
        """Mark a phase as completed"""
        pecs_data = self.section.pecs_data.get(phase, {})
        pecs_data['completed'] = True
        self.db.update_section_pecs_data(self.section_id, phase, pecs_data)

        # Refresh section data
        self.section = self.db.get_section(self.section_id)

        ui.notify('Phase completed!', color='positive', position='top')
        ui.navigate.reload()

    def _add_flashcard(self, question_input, answer_input):
        """Add a flashcard"""
        if not question_input.value or not answer_input.value:
            ui.notify('Please fill in both question and answer', color='warning', position='top')
            return

        self.db.create_flashcard(
            project_id=self.section.project_id,
            question=question_input.value,
            answer=answer_input.value,
            section_id=self.section_id
        )

        question_input.value = ''
        answer_input.value = ''

        ui.notify('Flashcard added!', color='positive', position='top')
        ui.navigate.reload()

    async def _generate_ai_flashcards(self):
        """Generate flashcard suggestions using AI"""
        engage_data = self.section.pecs_data.get('engage_explain', {})
        explanation = engage_data.get('explanation', '')

        if not explanation:
            ui.notify('Please complete the Engage phase first', color='warning', position='top')
            return

        # Check if LLM service is available
        if not self.llm_service.is_available():
            ui.notify('AI features require an OpenAI API key. Set OPENAI_API_KEY environment variable.',
                     color='warning', position='top')
            return

        # Show loading indicator
        with ui.dialog() as loading_dialog, ui.card().classes('max-w-2xl'):
            ui.label('Generating flashcard suggestions...').classes('text-lg font-bold')
            ui.spinner(size='lg')

        loading_dialog.open()

        try:
            challenge_data = self.section.pecs_data.get('challenge_connect', {})

            # Run LLM call in thread pool to avoid blocking UI
            import asyncio
            suggestions = await asyncio.to_thread(
                self.llm_service.suggest_flashcards,
                chunk_text=self.section.content,
                user_explanation=explanation,
                user_challenges=challenge_data.get('critical_questions', '')
            )

            loading_dialog.close()

            if suggestions:
                with ui.dialog() as dialog, ui.card().classes('max-w-2xl'):
                    ui.label('AI Flashcard Suggestions').classes('text-xl font-bold mb-3')
                    for i, suggestion in enumerate(suggestions, 1):
                        with ui.card().classes('w-full mb-2 bg-purple-50'):
                            ui.label(f'Suggestion {i}').classes('font-semibold mb-2')
                            ui.label(f'Q: {suggestion["question"]}').classes('text-sm mb-1')
                            ui.label(f'A: {suggestion["answer"]}').classes('text-sm mb-2')
                            ui.button(
                                'Add This Card',
                                on_click=lambda s=suggestion: self._add_ai_flashcard(s, dialog)
                            ).classes('bg-blue-500 text-sm')
                    ui.button('Close', on_click=dialog.close).classes('mt-4')
                dialog.open()
            else:
                ui.notify('No suggestions available', color='warning', position='top')

        except Exception as e:
            loading_dialog.close()
            ui.notify(f'Error: {str(e)}', color='negative', position='top')

    def _add_ai_flashcard(self, suggestion: dict, dialog):
        """Add AI-suggested flashcard"""
        self.db.create_flashcard(
            project_id=self.section.project_id,
            question=suggestion['question'],
            answer=suggestion['answer'],
            section_id=self.section_id
        )
        ui.notify('Flashcard added!', color='positive', position='top')
        dialog.close()
        ui.navigate.reload()

    def _delete_flashcard(self, flashcard_id: int):
        """Delete a flashcard"""
        self.db.delete_flashcard(flashcard_id)
        ui.notify('Flashcard deleted', color='positive', position='top')
        ui.navigate.reload()
