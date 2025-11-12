# -*- coding: utf-8 -*-
# pylint: disable=mixed-line-endings
"""
Project View Page - Shows project overview and section list
"""

from pathlib import Path
from datetime import datetime
from nicegui import ui

from utils.database import DatabaseRepository
from utils.models import Section
from utils.anki_export import export_flashcards_to_anki


class ProjectViewPage:
    """Project overview with section list and navigation"""

    def __init__(self, db: DatabaseRepository, project_id: int, user_id: int = None):
        """
        Initialize project view

        Args:
            db: Database repository
            project_id: ID of project to display
            user_id: Optional user ID (future)
        """
        self.db = db
        self.project_id = project_id
        self.user_id = user_id
        self.project = db.get_project(project_id)
        self.sections = db.get_sections_by_project(project_id) if self.project else []

    def render(self):
        """Render project view page"""

        if not self.project:
            with ui.column().classes("items-center mt-12"):
                ui.label("Project not found").classes("text-xl text-red-500")
                ui.button(
                    "Back to Dashboard", on_click=lambda: ui.navigate.to("/")
                ).classes("mt-4")
            return

        # Header with project name and actions
        with ui.column().classes("w-full mb-6"):
            with ui.row().classes("w-full items-center gap-2 mb-3"):
                ui.button(
                    icon="arrow_back", on_click=lambda: ui.navigate.to("/")
                ).props("flat")
                ui.label(self.project.name).classes(
                    "text-xl md:text-2xl font-bold flex-1"
                )

            # Stats row
            stats = self.db.get_project_stats(self.project_id)
            with ui.row().classes("gap-4 flex-wrap"):
                with ui.card().classes("px-4 py-2"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("description").classes("text-blue-500")
                        with ui.column():
                            ui.label(str(stats.get("total_sections", 0))).classes(
                                "text-lg font-bold"
                            )
                            ui.label("Sections").classes("text-xs text-gray-600")

                with ui.card().classes("px-4 py-2"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("check_circle").classes("text-green-500")
                        with ui.column():
                            ui.label(str(stats.get("completed_sections", 0))).classes(
                                "text-lg font-bold"
                            )
                            ui.label("Completed").classes("text-xs text-gray-600")

                with ui.card().classes("px-4 py-2"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("style").classes("text-purple-500")
                        with ui.column():
                            ui.label(str(stats.get("total_flashcards", 0))).classes(
                                "text-lg font-bold"
                            )
                            ui.label("Flashcards").classes("text-xs text-gray-600")

                cards_due = stats.get("cards_due_for_review", 0)
                if cards_due > 0:
                    with ui.card().classes("px-4 py-2 bg-orange-50"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("alarm").classes("text-orange-500")
                            with ui.column():
                                ui.label(str(cards_due)).classes(
                                    "text-lg font-bold text-orange-600"
                                )
                                ui.label("Due for Review").classes(
                                    "text-xs text-orange-600"
                                )

            # Action buttons
            with ui.row().classes("w-full gap-2 flex-wrap mt-4"):
                ui.button(
                    "Study Mode",
                    icon="school",
                    on_click=lambda: ui.navigate.to(
                        f"/project/{self.project_id}/study"
                    ),
                ).classes("bg-green-500 flex-1 min-w-40")

                ui.button(
                    "Add Content",
                    icon="add",
                    on_click=lambda: ui.navigate.to(
                        f"/project/{self.project_id}/upload"
                    ),
                ).classes("bg-blue-500 flex-1 min-w-40")

                if stats.get("total_flashcards", 0) > 0:
                    ui.button(
                        "Export to Anki",
                        icon="download",
                        on_click=self._show_anki_export_dialog,
                    ).classes("bg-purple-500 flex-1 min-w-40")

        # Sections list
        if not self.sections:
            self._render_no_sections()
        else:
            self._render_sections_list()

    def _render_no_sections(self):
        """Render empty state when no sections exist"""
        with ui.column().classes("items-center mt-12 px-4"):
            ui.icon("description").classes("text-6xl text-gray-400")
            ui.label("No content yet").classes("text-xl text-gray-500 text-center mt-4")
            ui.label("Upload a document or paste text to start learning").classes(
                "text-gray-400 text-center"
            )
            ui.button(
                "Upload Content",
                icon="upload",
                on_click=lambda: ui.navigate.to(f"/project/{self.project_id}/upload"),
            ).classes("mt-4 bg-blue-500")

    def _render_sections_list(self):
        """Render list of sections with search and filters"""

        ui.label(f"Sections ({len(self.sections)})").classes("text-lg font-bold mb-3")

        # Search box
        search_input = (
            ui.input(placeholder="Search sections...")
            .classes("w-full mb-4")
            .props("clearable")
        )

        # Filter results
        filtered_sections = {"value": self.sections}

        def update_search():
            query = (search_input.value or "").lower()
            if query:
                filtered_sections["value"] = [
                    s
                    for s in self.sections
                    if query in (s.title or "").lower()
                    or query in s.content.lower()[:200]
                ]
            else:
                filtered_sections["value"] = self.sections
            render_section_cards()

        search_input.on("update:modelValue", update_search)

        # Container for section cards
        sections_container = ui.column().classes("w-full gap-3")

        def render_section_cards():
            """Render filtered section cards"""
            sections_container.clear()

            with sections_container:
                if not filtered_sections["value"]:
                    ui.label("No sections match your search").classes(
                        "text-gray-500 text-center py-8"
                    )
                    return

                for idx, section in enumerate(filtered_sections["value"]):
                    self._render_section_card(section, idx)

        render_section_cards()

    def _render_section_card(self, section: Section, _index: int):
        """Render a single section card"""

        section_title = section.title or f"Section {section.order_index + 1}"

        with ui.card().classes(
            "w-full cursor-pointer hover:shadow-md transition-shadow"
        ):
            with ui.row().classes("w-full items-center gap-3"):
                # Completion indicator
                if section.is_completed:
                    ui.icon("check_circle").classes("text-green-500 text-2xl")
                else:
                    ui.icon("radio_button_unchecked").classes("text-gray-400 text-2xl")

                # Section info
                with ui.column().classes("flex-1"):
                    ui.label(section_title).classes("font-semibold text-lg")

                    # Preview
                    preview = (
                        section.content[:100] + "..."
                        if len(section.content) > 100
                        else section.content
                    )
                    ui.label(preview).classes("text-sm text-gray-600")

                    # Metadata
                    with ui.row().classes("gap-4 mt-2"):
                        ui.label(f"{len(section.content)} chars").classes(
                            "text-xs text-gray-500"
                        )

                        # Show PECS progress
                        pecs_data = section.pecs_data or {}
                        phases_completed = sum(
                            1
                            for phase in [
                                "prime_preview",
                                "engage_explain",
                                "challenge_connect",
                                "solidify_space",
                            ]
                            if phase in pecs_data and pecs_data[phase]
                        )
                        if phases_completed > 0:
                            ui.label(f"{phases_completed}/4 PECS phases").classes(
                                "text-xs text-blue-600"
                            )

                        if section.is_completed:
                            ui.label("Completed").classes(
                                "text-xs text-green-600 font-semibold"
                            )

                # Open button
                ui.button(
                    icon="arrow_forward",
                    on_click=lambda s=section: ui.navigate.to(
                        f"/project/{self.project_id}/section/{s.id}"
                    ),
                ).props("flat dense").classes("text-blue-500")

    def _show_anki_export_dialog(self):
        """Show dialog for Anki export options"""

        with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl"):
            ui.label("Export Flashcards to Anki").classes("text-xl font-bold mb-4")

            # Get flashcard count
            flashcards = self.db.get_flashcards_by_project(self.project_id)
            total_cards = len(flashcards)

            ui.label(
                f"Ready to export {total_cards} flashcard{'s' if total_cards != 1 else ''}"
            ).classes("text-gray-700 mb-4")

            # Export method selection
            ui.label("Choose export method:").classes("font-semibold mb-2")

            # Create a single radio group with custom styling
            with ui.column().classes("w-full mb-6"):
                export_method_radio = ui.radio(
                    {
                        "api": "AnkiConnect (Direct) - Push cards directly to Anki via API",
                        "file": "File Export - Download .apkg file for manual import",
                    },
                    value="api",
                ).props("dense")

                # Style cards for each option
                with ui.row().classes("gap-4 mt-2"):
                    with ui.card().classes("flex-1 p-4"):
                        with ui.row().classes("items-center gap-2 mb-2"):
                            ui.icon("cloud_upload").classes("text-blue-500 text-2xl")
                            with ui.column().classes("flex-1"):
                                ui.label("AnkiConnect (Direct)").classes(
                                    "font-semibold"
                                )
                                ui.label("Push cards directly to Anki via API").classes(
                                    "text-sm text-gray-600"
                                )
                                ui.label(
                                    "Requires: Anki running with AnkiConnect add-on"
                                ).classes("text-xs text-orange-600 mt-1")

                    with ui.card().classes("flex-1 p-4"):
                        with ui.row().classes("items-center gap-2 mb-2"):
                            ui.icon("download").classes("text-green-500 text-2xl")
                            with ui.column().classes("flex-1"):
                                ui.label("File Export").classes("font-semibold")
                                ui.label(
                                    "Download .apkg file to double-click import"
                                ).classes("text-sm text-gray-600")
                                ui.label("No setup required - works offline").classes(
                                    "text-xs text-green-600 mt-1"
                                )

            # Deck name input
            deck_name_input = ui.input(
                label="Anki Deck Name",
                value=self.project.name,
                placeholder="Enter deck name",
            ).classes("w-full mb-4")

            # Status message area
            status_container = ui.column().classes("w-full mb-4")

            def perform_export():
                """Execute the export based on selected method"""
                status_container.clear()

                deck_name = deck_name_input.value or self.project.name

                with status_container:
                    with ui.row().classes("items-center gap-2"):
                        ui.spinner(size="sm")
                        ui.label("Exporting...").classes("text-gray-600")

                # Give UI time to update
                ui.timer(0.1, lambda: _do_export(deck_name), once=True)

            def _do_export(deck_name: str):
                """Perform the actual export"""
                method = export_method_radio.value

                if method == "api":
                    result = export_flashcards_to_anki(
                        flashcards=flashcards,
                        deck_name=deck_name,
                        method="api",
                        tags=["PECS", self.project.name],
                    )
                else:  # file
                    # Generate filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_deck_name = "".join(
                        c if c.isalnum() or c in (" ", "-", "_") else "_"
                        for c in deck_name
                    )
                    filename = f"{safe_deck_name}_{timestamp}.apkg"
                    output_path = Path("data") / "exports" / filename

                    result = export_flashcards_to_anki(
                        flashcards=flashcards,
                        deck_name=deck_name,
                        method="file",
                        output_path=output_path,
                        tags=["PECS", self.project.name],
                    )

                # Update status
                status_container.clear()
                with status_container:
                    if result["success"]:
                        with ui.card().classes("w-full bg-green-50 p-4"):
                            with ui.row().classes("items-start gap-2"):
                                ui.icon("check_circle").classes(
                                    "text-green-500 text-2xl"
                                )
                                with ui.column().classes("flex-1"):
                                    ui.label("Success!").classes(
                                        "font-bold text-green-700"
                                    )
                                    ui.label(result["message"]).classes("text-sm")

                                    if method == "file" and "file_path" in result:
                                        # Provide download link
                                        file_path = result["file_path"]
                                        ui.button(
                                            "Download File",
                                            icon="download",
                                            on_click=lambda: ui.download(file_path),
                                        ).classes("bg-green-500 mt-2")

                        if method == "api":
                            ui.label("Open Anki to see your new cards!").classes(
                                "text-sm text-gray-600 mt-2"
                            )
                        else:
                            ui.label(
                                "Double-click the .apkg file to import into Anki"
                            ).classes("text-sm text-gray-600 mt-2")

                    else:
                        with ui.card().classes("w-full bg-red-50 p-4"):
                            with ui.row().classes("items-start gap-2"):
                                ui.icon("error").classes("text-red-500 text-2xl")
                                with ui.column():
                                    ui.label("Export Failed").classes(
                                        "font-bold text-red-700"
                                    )
                                    ui.label(result["message"]).classes(
                                        "text-sm text-red-600"
                                    )

                                    if method == "api":
                                        with ui.column().classes("mt-2 text-xs"):
                                            ui.label("Troubleshooting:").classes(
                                                "font-semibold"
                                            )
                                            ui.label("1. Is Anki running?")
                                            ui.label(
                                                "2. Is AnkiConnect installed? (Code: 2055492159)"
                                            )
                                            ui.label("3. Try restarting Anki")

            # Action buttons
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat")

                ui.button(
                    "Export", icon="file_upload", on_click=perform_export
                ).classes("bg-purple-500")

        dialog.open()
