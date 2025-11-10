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

        # Phase configuration - DRY principle
        self.phase_config = {
            'prime_preview': {
                'index': 0,
                'name': 'Phase 1: Prime & Preview',
                'description': 'First Impressions - What stands out to you?',
                'field': 'understanding',
                'label': 'What are your first impressions? What stands out to you?',
                'placeholder': 'Write your initial thoughts about this material...',
                'completed_label': 'Your thoughts:',
                'feedback_type': 'section_understanding',
                'rows': 4
            },
            'engage_explain': {
                'index': 1,
                'name': 'Phase 2: Engage & Explain',
                'description': 'Deep Understanding - Explain the concepts in your own words',
                'field': 'explanation',
                'label': 'Explain the key concepts in your own simple words',
                'placeholder': 'Write your understanding here...',
                'completed_label': 'Your explanation:',
                'feedback_type': 'explanation',
                'rows': 5
            },
            'challenge_connect': {
                'index': 2,
                'name': 'Phase 3: Challenge & Connect',
                'description': 'Critical Thinking - Ask questions, make connections, think deeper',
                'field': 'critical_questions',
                'label': 'What questions do you have? How does this connect to what you know?',
                'placeholder': 'Ask critical questions, make connections...',
                'completed_label': 'Your questions & connections:',
                'feedback_type': 'critical_thinking',
                'rows': 5
            }
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

    def _render_conversation_ui(self, phase_key: str, phase_data: dict, input_widget, is_completed: bool):
        """Render conversation UI (DRY helper)"""
        ai_conversation = phase_data.get('ai_conversation', [])
        if not ai_conversation:
            return

        if is_completed:
            # Completed phase - simple display
            ui.label('AI Conversation:').classes('font-semibold mt-3')
            for msg in ai_conversation:
                if msg['role'] == 'user':
                    ui.label(f"You: {msg['content']}").classes('text-sm p-2 bg-blue-50 rounded mb-1')
                else:
                    ui.markdown(f"**AI:** {msg['content']}").classes('text-sm p-2 bg-purple-50 rounded mb-1')
        else:
            # Active phase - interactive display with continue button
            with ui.card().classes('w-full mt-4 bg-purple-50'):
                ui.label('AI Conversation').classes('font-semibold mb-2')
                with ui.column().classes('w-full gap-1 max-h-64 overflow-auto'):
                    for msg in ai_conversation:
                        if msg['role'] == 'user':
                            ui.label(f"You: {msg['content']}").classes('text-sm p-2 bg-blue-100 rounded')
                        else:
                            ui.markdown(f"**AI:** {msg['content']}").classes('text-sm p-2 bg-white rounded')

                # Continue conversation button
                config = self.phase_config[phase_key]
                async def continue_conv():
                    await self._continue_conversation(phase_key, config['feedback_type'], input_widget.value)

                ui.button(
                    'Continue Conversation',
                    icon='chat',
                    on_click=continue_conv
                ).classes('bg-purple-500 mt-2')

    def _render_learning_phase(self, phase_key: str):
        """Generic learning phase renderer (DRY principle)"""
        config = self.phase_config[phase_key]
        phase_data = self.section.pecs_data.get(phase_key, {})
        is_completed = phase_data.get('completed', False)
        is_unlocked = self._is_phase_unlocked(config['index'])
        current_phase = self._get_current_phase()

        # Phase card styling
        card_classes = 'w-full p-6 '
        if is_completed:
            card_classes += 'bg-green-50 border-l-4 border-green-500'
        elif current_phase == config['index']:
            card_classes += 'bg-blue-50 border-l-4 border-blue-500'
        else:
            card_classes += 'bg-gray-100'

        with ui.card().classes(card_classes):
            # Header
            with ui.row().classes('w-full items-center gap-2 mb-4'):
                if is_completed:
                    ui.icon('check_circle', size='sm').classes('text-green-600')
                elif current_phase == config['index']:
                    ui.icon('play_circle', size='sm').classes('text-blue-600')
                elif not is_unlocked:
                    ui.icon('lock', size='sm').classes('text-gray-400')
                else:
                    ui.icon('radio_button_unchecked', size='sm').classes('text-gray-400')

                ui.label(config['name']).classes('text-xl font-bold flex-1')

            if not is_unlocked:
                ui.label(f'🔒 Complete Phase {config["index"]} first').classes('text-gray-500 italic')
                return

            ui.label(config['description']).classes('text-sm text-gray-600 mb-4')

            # Show completed work (collapsed)
            if is_completed:
                with ui.expansion('See your work', icon='visibility').classes('w-full'):
                    if phase_data.get(config['field']):
                        ui.label(config['completed_label']).classes('font-semibold mt-2')
                        ui.label(phase_data[config['field']]).classes('text-sm p-2 bg-white rounded')

                    # Show conversation
                    self._render_conversation_ui(phase_key, phase_data, None, True)

                    # Unmark button
                    ui.button(
                        'Unmark as Complete',
                        icon='edit',
                        on_click=lambda: self._uncomplete_phase(phase_key)
                    ).classes('bg-gray-500 mt-3')

            # Active input area
            else:
                input_widget = ui.textarea(
                    label=config['label'],
                    placeholder=config['placeholder'],
                    value=phase_data.get(config['field'], '')
                ).classes('w-full').props(f'rows={config["rows"]}')

                # Async wrappers
                async def get_feedback():
                    await self._get_ai_feedback(phase_key, config['feedback_type'], input_widget.value)

                async def complete_phase():
                    await self._complete_phase(phase_key)

                with ui.row().classes('w-full gap-2 mt-3'):
                    ui.button(
                        'Save',
                        icon='save',
                        on_click=lambda: self._save_phase_data(phase_key, config['field'], input_widget.value)
                    ).classes('bg-blue-500')

                    ui.button(
                        'Get AI Feedback',
                        icon='psychology',
                        on_click=get_feedback
                    ).classes('bg-purple-500')

                    if phase_data.get(config['field']):
                        ui.button(
                            'Mark Complete',
                            icon='check',
                            on_click=complete_phase
                        ).classes('bg-green-500')

                # Show conversation
                self._render_conversation_ui(phase_key, phase_data, input_widget, False)

    def _render_prime_phase(self):
        """Phase 1: Prime & Preview - First impressions"""
        self._render_learning_phase('prime_preview')

    def _render_engage_phase(self):
        """Phase 2: Engage & Explain - Deep understanding"""
        self._render_learning_phase('engage_explain')

    def _render_challenge_phase(self):
        """Phase 3: Challenge & Connect - Critical thinking"""
        self._render_learning_phase('challenge_connect')

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
            flashcards = self.db.get_flashcards_by_project(self.section.project_id, self.section_id)

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
                async def complete_solidify():
                    await self._complete_phase('solidify_space')

                ui.button(
                    'Mark Section Complete',
                    icon='check_circle',
                    on_click=complete_solidify
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
                # Save as conversation (not single feedback)
                from datetime import datetime
                pecs_data = self.section.pecs_data.get(phase, {})

                # Initialize conversation if needed
                if 'ai_conversation' not in pecs_data:
                    pecs_data['ai_conversation'] = []

                # Add user message and AI response
                pecs_data['ai_conversation'].append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now().isoformat()
                })
                pecs_data['ai_conversation'].append({
                    'role': 'assistant',
                    'content': feedback,
                    'timestamp': datetime.now().isoformat()
                })

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

    async def _complete_phase(self, phase: str):
        """Mark a phase as completed"""
        pecs_data = self.section.pecs_data.get(phase, {})
        pecs_data['completed'] = True
        self.db.update_section_pecs_data(self.section_id, phase, pecs_data)

        # Refresh section data
        self.section = self.db.get_section(self.section_id)

        # If this is the solidify phase (last phase), generate completion report
        if phase == 'solidify_space' and self.llm_service.is_available():
            ui.notify('Generating your learning summary...', color='info', position='top')
            await self._generate_completion_report()
        else:
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

    def _get_flashcard_context(self, additional_suggestions=None):
        """DRY helper: Get all existing flashcards for context"""
        import logging
        logger = logging.getLogger(__name__)

        # Get existing flashcards from database
        db_flashcards = self.db.get_flashcards_by_project(self.section.project_id, self.section_id)
        existing_db_cards = [{'question': card.question, 'answer': card.answer} for card in db_flashcards]

        # Combine with additional suggestions if provided
        all_cards = existing_db_cards + (additional_suggestions or [])

        logger.info(f"Flashcard context: {len(existing_db_cards)} DB cards + {len(additional_suggestions or [])} suggestions = {len(all_cards)} total")
        return all_cards

    async def _generate_ai_flashcards(self, existing_suggestions=None):
        """Generate flashcard suggestions using AI and show dialog"""
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

            # Get complete context (DRY)
            all_existing_cards = self._get_flashcard_context(existing_suggestions)

            # Run LLM call in thread pool to avoid blocking UI
            import asyncio
            import logging
            logger = logging.getLogger(__name__)

            suggestions = await asyncio.to_thread(
                self.llm_service.suggest_flashcards,
                chunk_text=self.section.content,
                user_explanation=explanation,
                user_challenges=challenge_data.get('critical_questions', ''),
                existing_cards=all_existing_cards
            )

            loading_dialog.close()

            if suggestions:
                logger.info(f"Generated {len(suggestions)} new flashcard suggestions")
                # Open interactive dialog
                await self._show_flashcard_dialog(suggestions, existing_suggestions or [])
            else:
                logger.warning("No flashcard suggestions generated")
                ui.notify('No suggestions available', color='warning', position='top')

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error generating flashcards: {str(e)}', exc_info=True)
            loading_dialog.close()
            ui.notify(f'Error: {str(e)}', color='negative', position='top')

    async def _show_flashcard_dialog(self, new_suggestions: list, previous_suggestions: list = None):
        """Show interactive flashcard dialog that stays open"""
        import logging
        logger = logging.getLogger(__name__)

        if previous_suggestions is None:
            previous_suggestions = []

        # Combine all suggestions
        all_suggestions = previous_suggestions + new_suggestions
        added_indices = set()  # Track which cards have been added

        logger.info(f"Opening flashcard dialog with {len(all_suggestions)} total suggestions ({len(previous_suggestions)} previous + {len(new_suggestions)} new)")

        with ui.dialog() as dialog, ui.card().classes('max-w-3xl'):
            ui.label('AI Flashcard Suggestions').classes('text-xl font-bold mb-3')

            # Loading indicator (initially hidden)
            loading_container = ui.column().classes('w-full').style('display: none')
            with loading_container:
                ui.label('Generating more suggestions...').classes('text-lg')
                ui.spinner(size='lg')

            # Container for suggestions (will be updated)
            suggestions_container = ui.column().classes('w-full')

            def render_suggestions():
                """Render all suggestions with their current state"""
                suggestions_container.clear()
                with suggestions_container:
                    for i, suggestion in enumerate(all_suggestions):
                        is_added = i in added_indices
                        card_class = 'w-full mb-2 bg-green-50' if is_added else 'w-full mb-2 bg-purple-50'

                        with ui.card().classes(card_class):
                            ui.label(f'Card {i + 1}').classes('font-semibold mb-2')
                            ui.label(f'Q: {suggestion["question"]}').classes('text-sm mb-1')
                            ui.label(f'A: {suggestion["answer"]}').classes('text-sm mb-2')

                            if is_added:
                                ui.label('✓ Added to deck').classes('text-green-600 text-sm font-semibold')
                            else:
                                def make_add_handler(idx, sug):
                                    def handler():
                                        # Add to database
                                        self.db.create_flashcard(
                                            project_id=self.section.project_id,
                                            question=sug['question'],
                                            answer=sug['answer'],
                                            section_id=self.section_id
                                        )
                                        added_indices.add(idx)
                                        logger.info(f"Added flashcard {idx + 1} to database")
                                        ui.notify('Flashcard added!', color='positive', position='top')
                                        render_suggestions()  # Re-render to update UI
                                    return handler

                                ui.button(
                                    'Add This Card',
                                    on_click=make_add_handler(i, suggestion)
                                ).classes('bg-blue-500 text-sm')

            # Initial render
            render_suggestions()

            # Action buttons at bottom
            button_row = ui.row().classes('w-full gap-2 mt-4')
            with button_row:
                async def generate_more():
                    """Generate more cards and update THIS dialog"""
                    nonlocal all_suggestions

                    # Show loading, hide buttons
                    loading_container.style('display: block')
                    suggestions_container.style('display: none')
                    button_row.style('display: none')

                    try:
                        logger.info(f"Generating more flashcards with {len(all_suggestions)} existing context")

                        # Get complete context (DRY)
                        all_existing_cards = self._get_flashcard_context(all_suggestions)

                        # Get engage/challenge data
                        engage_data = self.section.pecs_data.get('engage_explain', {})
                        challenge_data = self.section.pecs_data.get('challenge_connect', {})

                        # Generate more cards
                        import asyncio
                        new_cards = await asyncio.to_thread(
                            self.llm_service.suggest_flashcards,
                            chunk_text=self.section.content,
                            user_explanation=engage_data.get('explanation', ''),
                            user_challenges=challenge_data.get('critical_questions', ''),
                            existing_cards=all_existing_cards
                        )

                        if new_cards:
                            logger.info(f"Generated {len(new_cards)} more flashcards")
                            # Add new cards to the list
                            all_suggestions = all_suggestions + new_cards
                            ui.notify(f'Generated {len(new_cards)} more cards!', color='positive', position='top')
                        else:
                            logger.warning("No additional flashcards generated")
                            ui.notify('Could not generate more cards', color='warning', position='top')

                    except Exception as e:
                        logger.error(f'Error generating more flashcards: {str(e)}', exc_info=True)
                        ui.notify(f'Error: {str(e)}', color='negative', position='top')

                    finally:
                        # Hide loading, show cards and buttons
                        loading_container.style('display: none')
                        suggestions_container.style('display: block')
                        button_row.style('display: flex')
                        render_suggestions()  # Re-render with new cards

                ui.button(
                    'Generate More',
                    icon='add_circle',
                    on_click=generate_more
                ).classes('bg-purple-500')

                def close_and_reload():
                    logger.info(f"Closing dialog. Added {len(added_indices)} cards.")
                    dialog.close()
                    if added_indices:
                        ui.navigate.reload()

                ui.button(
                    'Done',
                    icon='check',
                    on_click=close_and_reload
                ).classes('bg-green-500')

        dialog.open()

    def _add_ai_flashcard(self, suggestion: dict, dialog):
        """Add AI-suggested flashcard (legacy method - no longer used)"""
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

    def _uncomplete_phase(self, phase: str):
        """Unmark a phase as completed"""
        pecs_data = self.section.pecs_data.get(phase, {})
        pecs_data['completed'] = False
        self.db.update_section_pecs_data(self.section_id, phase, pecs_data)

        # Refresh section data
        self.section = self.db.get_section(self.section_id)

        ui.notify('Phase unmarked as complete', color='positive', position='top')
        ui.navigate.reload()

    async def _continue_conversation(self, phase: str, feedback_type: str, user_input: str):
        """Continue an existing AI conversation with full context"""
        if not user_input:
            ui.notify('Please write a question or response first', color='warning', position='top')
            return

        # Check if LLM service is available
        if not self.llm_service.is_available():
            ui.notify('AI features require an OpenAI API key. Set OPENAI_API_KEY environment variable.',
                     color='warning', position='top')
            return

        # Create loading dialog
        with ui.dialog() as dialog, ui.card().classes('max-w-2xl'):
            ui.label('AI is thinking...').classes('text-lg font-bold')
            ui.spinner(size='lg')

        dialog.open()

        try:
            # Get conversation history for context
            pecs_data = self.section.pecs_data.get(phase, {})
            conversation = pecs_data.get('ai_conversation', [])

            # Build conversation history
            conversation_history = "\n\n".join([
                f"{'Student' if msg['role'] == 'user' else 'AI'}: {msg['content']}"
                for msg in conversation
            ])

            # Create system prompt based on phase
            phase_context = {
                'prime_preview': 'helping them understand their first impressions',
                'engage_explain': 'helping them explain concepts in their own words',
                'challenge_connect': 'helping them think critically and make connections'
            }
            context_desc = phase_context.get(phase, 'having a learning conversation')

            # Build comprehensive prompt with full context
            system_prompt = f"""You are a learning tutor {context_desc}.
The student is studying this material:

{self.section.content[:1000]}...

Previous conversation:
{conversation_history}

Now respond to their latest question/comment. Build on what you've already discussed.
Be helpful and direct, not artificially enthusiastic."""

            # Run LLM call directly with conversation context
            import asyncio
            feedback = await asyncio.to_thread(
                self.llm_service._make_llm_call,
                system_prompt,
                user_input
            )

            dialog.close()

            if feedback:
                # Add to conversation
                from datetime import datetime
                pecs_data = self.section.pecs_data.get(phase, {})

                if 'ai_conversation' not in pecs_data:
                    pecs_data['ai_conversation'] = []

                pecs_data['ai_conversation'].append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now().isoformat()
                })
                pecs_data['ai_conversation'].append({
                    'role': 'assistant',
                    'content': feedback,
                    'timestamp': datetime.now().isoformat()
                })

                self.db.update_section_pecs_data(self.section_id, phase, pecs_data)

                # Refresh section data
                self.section = self.db.get_section(self.section_id)

                ui.notify('Conversation continued!', color='positive', position='top')
                ui.navigate.reload()
            else:
                ui.notify('Could not generate response', color='warning', position='top')

        except Exception as e:
            dialog.close()
            ui.notify(f'Error: {str(e)}', color='negative', position='top')

    async def _generate_completion_report(self):
        """Generate AI summary of the learner's journey through this section"""
        # Gather all phase data
        all_pecs_data = self.section.pecs_data or {}

        # Build comprehensive summary of learner's work
        summary_text = f"Section: {self.section.title or 'Untitled'}\n\n"
        summary_text += f"Content:\n{self.section.content[:500]}...\n\n"

        for phase_key, phase_name in [
            ('prime_preview', 'Prime & Preview'),
            ('engage_explain', 'Engage & Explain'),
            ('challenge_connect', 'Challenge & Connect'),
            ('solidify_space', 'Solidify & Space')
        ]:
            phase_data = all_pecs_data.get(phase_key, {})
            summary_text += f"\n=== {phase_name} ===\n"

            # Add user inputs
            if phase_key == 'prime_preview' and phase_data.get('understanding'):
                summary_text += f"First impressions: {phase_data['understanding']}\n"
            elif phase_key == 'engage_explain' and phase_data.get('explanation'):
                summary_text += f"Explanation: {phase_data['explanation']}\n"
            elif phase_key == 'challenge_connect' and phase_data.get('critical_questions'):
                summary_text += f"Questions & connections: {phase_data['critical_questions']}\n"

            # Add conversation snippets
            conversation = phase_data.get('ai_conversation', [])
            if conversation:
                summary_text += f"Conversation ({len(conversation)//2} exchanges):\n"
                for msg in conversation[-4:]:  # Last 2 exchanges
                    summary_text += f"  {msg['role']}: {msg['content'][:100]}...\n"

        # Create prompt for AI summary
        prompt = f"""Review this learner's journey through a learning section using the PECS method.

Here is what they did:

{summary_text}

Provide an objective summary that:
1. Identifies the key concepts they engaged with
2. Notes patterns in their thinking (questions they asked, connections they made)
3. Points out any gaps or areas where understanding seems shallow
4. Summarizes their progression through the material
5. Suggests next steps if relevant

Be analytical and honest. Don't be overly enthusiastic or artificially encouraging. Write like a thoughtful reviewer, not a cheerleader."""

        # Show loading
        with ui.dialog() as dialog, ui.card().classes('max-w-3xl'):
            ui.label('Creating your learning summary...').classes('text-lg font-bold')
            ui.spinner(size='lg')

        dialog.open()

        try:
            import asyncio

            # Generate report
            report = await asyncio.to_thread(
                self.llm_service.analyze_section_understanding,
                "",  # No specific content needed
                prompt
            )

            dialog.close()

            if report:
                # Save report to section
                section_pecs_data = self.section.pecs_data or {}
                section_pecs_data['completion_report'] = report
                from datetime import datetime
                section_pecs_data['completed_at'] = datetime.now().isoformat()

                # Need to store the entire updated pecs_data back
                self.section.pecs_data = section_pecs_data
                self.db.update_section_pecs_data(self.section_id, 'solidify_space', self.section.pecs_data['solidify_space'])

                # Show report in a nice dialog
                with ui.dialog() as report_dialog, ui.card().classes('max-w-3xl'):
                    ui.label('Section Review').classes('text-2xl font-bold mb-4')
                    with ui.scroll_area().classes('w-full h-96'):
                        ui.markdown(report).classes('text-sm')
                    ui.button('Close', on_click=lambda: [report_dialog.close(), ui.navigate.reload()]).classes('bg-blue-500 mt-4')
                report_dialog.open()
            else:
                ui.notify('Section completed!', color='positive', position='top')
                ui.navigate.reload()

        except Exception as e:
            dialog.close()
            ui.notify(f'Section completed! (Report generation failed: {str(e)})', color='positive', position='top')
            ui.navigate.reload()
