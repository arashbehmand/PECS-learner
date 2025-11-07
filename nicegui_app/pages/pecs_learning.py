# -*- coding: utf-8 -*-
"""
PECS Learning Page - 4-phase learning interface
Migrated from components/pecs_tabs.py (450 lines)
"""

from nicegui import ui
from utils.database import DatabaseRepository
from utils.llm_service import LLMService
from utils.models import Section


class PECSLearningPage:
    """PECS 4-phase learning interface: Prime, Engage, Challenge, Solidify"""

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
            self.section.pecs_data = {}

    def render(self):
        """Render PECS learning interface"""

        if not self.section:
            ui.label('Section not found').classes('text-xl text-red-500')
            ui.button('Back', on_click=lambda: ui.navigate.to(f'/project/{self.project_id}')).classes('mt-4')
            return

        # Header
        with ui.row().classes('w-full items-center gap-2 mb-4'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to(f'/project/{self.project_id}')).props('flat')
            section_title = self.section.title or f'Section {self.section.order_index + 1}'
            ui.label(section_title).classes('text-lg md:text-2xl font-bold flex-1')

        # Tabs for 4 phases
        with ui.tabs().classes('w-full') as tabs:
            prime_tab = ui.tab('P - Prime', icon='visibility')
            engage_tab = ui.tab('E - Engage', icon='edit_note')
            challenge_tab = ui.tab('C - Challenge', icon='psychology')
            solidify_tab = ui.tab('S - Solidify', icon='workspace_premium')

        with ui.tab_panels(tabs, value=prime_tab).classes('w-full mt-4'):
            with ui.tab_panel(prime_tab):
                self._render_prime_phase()
            with ui.tab_panel(engage_tab):
                self._render_engage_phase()
            with ui.tab_panel(challenge_tab):
                self._render_challenge_phase()
            with ui.tab_panel(solidify_tab):
                self._render_solidify_phase()

    def _render_prime_phase(self):
        """Prime & Preview phase"""
        ui.markdown('**Take a moment to skim through this section and prepare for deeper reading.**').classes('mb-4')

        pecs_data = self.section.pecs_data.get('prime_preview', {})

        # Content (collapsible)
        with ui.expansion('View Section Content', icon='book').classes('w-full bg-gray-50 mb-4'):
            ui.markdown(self.section.content)

        # Understanding
        ui.label('What is this section generally about?').classes('font-semibold mb-2')
        understanding_input = ui.textarea(
            placeholder='Share your initial understanding...',
            value=pecs_data.get('initial_thoughts', '')
        ).classes('w-full mb-2').props('rows=4 autogrow')

        with ui.row().classes('gap-2 mb-4'):
            ui.button('Save', on_click=lambda: self._save_prime('initial_thoughts', understanding_input.value)).classes('bg-blue-500')
            if self.llm_service.is_available():
                ui.button('Get AI Feedback', on_click=lambda: self._get_ai_feedback('section_understanding', understanding_input.value)).classes('bg-purple-500')

        # Prior knowledge
        ui.label('What do you already know about this topic?').classes('font-semibold mb-2 mt-4')
        prior_input = ui.textarea(
            placeholder='Connect to prior knowledge...',
            value=pecs_data.get('prior_knowledge', '')
        ).classes('w-full mb-2').props('rows=3 autogrow')
        ui.button('Save', on_click=lambda: self._save_prime('prior_knowledge', prior_input.value)).classes('bg-blue-500 mb-4')

        # Questions
        ui.label('What questions do you have?').classes('font-semibold mb-2 mt-4')
        questions_input = ui.textarea(
            placeholder='What are you curious about?',
            value=pecs_data.get('questions', '')
        ).classes('w-full mb-2').props('rows=3 autogrow')
        ui.button('Save', on_click=lambda: self._save_prime('questions', questions_input.value)).classes('bg-blue-500')

    def _render_engage_phase(self):
        """Engage & Explain phase"""
        ui.markdown('**Read through the material carefully and explain the core concepts in your own words.**').classes('mb-4')

        pecs_data = self.section.pecs_data.get('engage_explain', {})

        # Toggle material
        show_material = ui.checkbox('Show material', value=True).classes('mb-2')
        material_container = ui.column().classes('w-full')

        def toggle_material():
            material_container.clear()
            if show_material.value:
                with material_container:
                    with ui.expansion('Section Content', icon='book').classes('w-full bg-gray-50'):
                        ui.markdown(self.section.content)

        show_material.on('update:modelValue', toggle_material)
        toggle_material()

        # Explanation
        ui.label('Explain the core concepts in your own words').classes('font-semibold mb-2 mt-4')
        explanation_input = ui.textarea(
            placeholder='Explain what you learned...',
            value=pecs_data.get('explanation', '')
        ).classes('w-full mb-2').props('rows=6 autogrow')

        with ui.row().classes('gap-2 mb-4'):
            ui.button('Save', on_click=lambda: self._save_engage('explanation', explanation_input.value)).classes('bg-blue-500')
            if self.llm_service.is_available():
                ui.button('Get AI Feedback', on_click=lambda: self._get_ai_feedback('explanation', explanation_input.value)).classes('bg-purple-500')

        # Self-correction prompts
        with ui.card().classes('w-full bg-blue-50 p-4 mb-4'):
            ui.label('Self-Correction Prompts:').classes('font-semibold mb-2')
            ui.markdown('''
            - Can you simplify this further?
            - Are you using any jargon that could be explained more clearly?
            - Have you captured the main ideas?
            - Could someone new to this topic understand your explanation?
            ''').classes('text-sm')

        # Analogy
        ui.label('Create an analogy to help understand this concept (optional)').classes('font-semibold mb-2 mt-4')
        analogy_input = ui.textarea(
            placeholder='This is like...',
            value=pecs_data.get('analogy', '')
        ).classes('w-full mb-2').props('rows=3 autogrow')
        ui.button('Save', on_click=lambda: self._save_engage('analogy', analogy_input.value)).classes('bg-blue-500')

    def _render_challenge_phase(self):
        """Challenge & Connect phase"""
        ui.markdown('**Think critically about what you\'ve learned and connect it to other knowledge.**').classes('mb-4')

        # Show previous explanation
        engage_data = self.section.pecs_data.get('engage_explain', {})
        if engage_data and 'explanation' in engage_data:
            with ui.expansion('Your Explanation (from Engage phase)', icon='lightbulb').classes('w-full bg-gray-50 mb-4'):
                ui.markdown(engage_data['explanation'])

        pecs_data = self.section.pecs_data.get('challenge_connect', {})

        # Critical thinking
        ui.label('Critical Thinking').classes('text-lg font-bold mb-2')
        ui.markdown('''
        Consider these prompts:
        - Why is this true?
        - What are the underlying assumptions?
        - Are there any exceptions or limitations?
        - How could this be applied differently?
        ''').classes('text-sm mb-3')

        critical_input = ui.textarea(
            placeholder='My challenges & critical questions...',
            value=pecs_data.get('critical_questions', '')
        ).classes('w-full mb-2').props('rows=5 autogrow')

        with ui.row().classes('gap-2 mb-4'):
            ui.button('Save', on_click=lambda: self._save_challenge('critical_questions', critical_input.value)).classes('bg-blue-500')
            if self.llm_service.is_available():
                ui.button('Get AI Feedback', on_click=lambda: self._get_ai_feedback('critical_thinking', critical_input.value)).classes('bg-purple-500')

        # Connections
        ui.label('Making Connections').classes('text-lg font-bold mb-2 mt-4')
        ui.markdown('''
        How does this relate to:
        - Other topics you've learned
        - Real-world applications
        - Your personal experiences
        - Broader concepts or theories
        ''').classes('text-sm mb-3')

        connections_input = ui.textarea(
            placeholder='Connections to other topics/experiences...',
            value=pecs_data.get('connections', '')
        ).classes('w-full mb-2').props('rows=5 autogrow')
        ui.button('Save', on_click=lambda: self._save_challenge('connections', connections_input.value)).classes('bg-blue-500')

    def _render_solidify_phase(self):
        """Solidify & Space phase"""
        ui.markdown('**Reinforce your learning with flashcards and spaced repetition.**').classes('mb-4')

        # Show previous notes
        with ui.expansion('View Previous Notes', icon='notes').classes('w-full bg-gray-50 mb-4'):
            engage_data = self.section.pecs_data.get('engage_explain', {})
            if engage_data and 'explanation' in engage_data:
                ui.label('Your Explanation:').classes('font-semibold')
                ui.markdown(engage_data['explanation']).classes('mb-3')

            challenge_data = self.section.pecs_data.get('challenge_connect', {})
            if challenge_data and 'critical_questions' in challenge_data:
                ui.label('Your Critical Thinking:').classes('font-semibold')
                ui.markdown(challenge_data['critical_questions'])

        # Flashcards
        ui.label('Create Flashcards').classes('text-lg font-bold mb-3')

        # Get existing flashcards
        section_flashcards = self.db.get_flashcards_by_project(self.section.project_id, section_id=self.section_id)

        # AI flashcard suggestions
        if self.llm_service.is_available():
            if ui.button('Get AI Flashcard Suggestions', icon='auto_awesome').classes('bg-purple-500 mb-4'):
                self._generate_ai_flashcards()

        # Add flashcard form
        with ui.card().classes('w-full p-4 bg-gray-50 mb-4'):
            question_input = ui.input(label='Question/Prompt', placeholder='What is...?').classes('w-full mb-2')
            answer_input = ui.textarea(label='Answer/Key Idea', placeholder='Answer...').classes('w-full mb-2').props('rows=3')

            def add_flashcard():
                if question_input.value and answer_input.value:
                    self.db.create_flashcard(
                        project_id=self.section.project_id,
                        question=question_input.value,
                        answer=answer_input.value,
                        section_id=self.section_id
                    )
                    ui.notify('Flashcard added!', color='positive', position='top')
                    question_input.value = ''
                    answer_input.value = ''
                    ui.navigate.reload()  # Refresh to show new card
                else:
                    ui.notify('Please fill in both question and answer', color='warning', position='top')

            ui.button('Add Flashcard', icon='add', on_click=add_flashcard).classes('bg-blue-500')

        # Display existing flashcards
        if section_flashcards:
            ui.label(f'Your Flashcards ({len(section_flashcards)})').classes('text-lg font-bold mb-3')
            for i, card in enumerate(section_flashcards, 1):
                with ui.card().classes('w-full mb-2'):
                    with ui.row().classes('w-full items-start justify-between'):
                        with ui.column().classes('flex-1'):
                            ui.label(f'Q: {card.question}').classes('font-semibold')
                            ui.label(f'A: {card.answer}').classes('text-sm text-gray-700 mt-1')
                        ui.button(
                            icon='delete',
                            on_click=lambda c=card: self._delete_flashcard(c.id)
                        ).props('flat dense').classes('text-red-500')

        # Application
        ui.label('How can you apply this knowledge?').classes('font-semibold mb-2 mt-4')
        solidify_data = self.section.pecs_data.get('solidify_space', {})
        application_input = ui.textarea(
            placeholder='Real-world applications...',
            value=solidify_data.get('application', '')
        ).classes('w-full mb-2').props('rows=3 autogrow')
        ui.button('Save', on_click=lambda: self._save_solidify('application', application_input.value)).classes('bg-blue-500 mb-4')

        # Complete section button
        if not self.section.is_completed:
            ui.button(
                'Mark Section as Complete',
                icon='check_circle',
                on_click=self._mark_complete
            ).classes('bg-green-500 text-lg px-6 py-3 mt-4')
        else:
            ui.label('This section is completed!').classes('text-lg text-green-600 font-semibold mt-4')

    # Helper methods
    def _save_prime(self, field: str, value: str):
        """Save Prime phase data"""
        pecs_data = self.section.pecs_data.get('prime_preview', {})
        pecs_data[field] = value
        self.db.update_section_pecs_data(self.section_id, 'prime_preview', pecs_data)
        ui.notify('Saved!', color='positive', position='top')

    def _save_engage(self, field: str, value: str):
        """Save Engage phase data"""
        pecs_data = self.section.pecs_data.get('engage_explain', {})
        pecs_data[field] = value
        self.db.update_section_pecs_data(self.section_id, 'engage_explain', pecs_data)
        ui.notify('Saved!', color='positive', position='top')

    def _save_challenge(self, field: str, value: str):
        """Save Challenge phase data"""
        pecs_data = self.section.pecs_data.get('challenge_connect', {})
        pecs_data[field] = value
        self.db.update_section_pecs_data(self.section_id, 'challenge_connect', pecs_data)
        ui.notify('Saved!', color='positive', position='top')

    def _save_solidify(self, field: str, value: str):
        """Save Solidify phase data"""
        pecs_data = self.section.pecs_data.get('solidify_space', {})
        pecs_data[field] = value
        self.db.update_section_pecs_data(self.section_id, 'solidify_space', pecs_data)
        ui.notify('Saved!', color='positive', position='top')

    def _get_ai_feedback(self, feedback_type: str, user_input: str):
        """Get AI feedback on user input"""
        if not user_input:
            ui.notify('Please provide some input first', color='warning', position='top')
            return

        with ui.dialog() as dialog, ui.card().classes('max-w-2xl'):
            ui.label('Analyzing...').classes('text-lg font-bold')
            ui.spinner(size='lg')

        dialog.open()

        try:
            feedback = None
            if feedback_type == 'section_understanding':
                feedback = self.llm_service.analyze_section_understanding(self.section.content, user_input)
            elif feedback_type == 'explanation':
                feedback = self.llm_service.analyze_explanation(self.section.content, user_input)
            elif feedback_type == 'critical_thinking':
                feedback = self.llm_service.analyze_critical_thinking(self.section.content, user_input)

            dialog.close()

            if feedback:
                with ui.dialog() as feedback_dialog, ui.card().classes('max-w-2xl'):
                    ui.label('AI Feedback').classes('text-xl font-bold mb-3')
                    ui.markdown(feedback)
                    ui.button('Close', on_click=feedback_dialog.close).classes('mt-4')
                feedback_dialog.open()
            else:
                ui.notify('No feedback available', color='warning', position='top')

        except Exception as e:
            dialog.close()
            ui.notify(f'Error: {str(e)}', color='negative', position='top')

    def _generate_ai_flashcards(self):
        """Generate flashcard suggestions using AI"""
        engage_data = self.section.pecs_data.get('engage_explain', {})
        explanation = engage_data.get('explanation', '')

        if not explanation:
            ui.notify('Please complete the Engage phase first', color='warning', position='top')
            return

        challenge_data = self.section.pecs_data.get('challenge_connect', {})
        suggestions = self.llm_service.suggest_flashcards(
            chunk_text=self.section.content,
            user_explanation=explanation,
            user_challenges=challenge_data.get('critical_questions', '')
        )

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

    def _mark_complete(self):
        """Mark section as completed"""
        self.db.mark_section_completed(self.section_id, completed=True)
        ui.notify('Section completed! Great work!', color='positive', position='top')
        ui.navigate.reload()
