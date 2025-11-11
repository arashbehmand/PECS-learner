# -*- coding: utf-8 -*-
"""
Content Upload Page - Upload or paste learning material
Migrated from components/content_upload_new.py
"""

import os

from nicegui import ui

from utils.database import DatabaseRepository
from utils.hierarchical_processor import create_sections_from_text


class ContentUploadPage:
    """Content upload interface for creating sections from text/files"""

    def __init__(self, db: DatabaseRepository, project_id: int, user_id: int = None):
        """
        Initialize content upload page

        Args:
            db: Database repository
            project_id: ID of project to add content to
            user_id: Optional user ID (future multi-user support)
        """
        self.db = db
        self.project_id = project_id
        self.user_id = user_id
        self.project = db.get_project(project_id)

    def render(self):
        """Render content upload interface"""

        if not self.project:
            ui.label("Project not found").classes("text-xl text-red-500")
            ui.button(
                "Back to Dashboard", on_click=lambda: ui.navigate.to("/")
            ).classes("mt-4")
            return

        # Header
        with ui.row().classes("w-full items-center gap-3 mb-6"):
            ui.button(
                icon="arrow_back",
                on_click=lambda: ui.navigate.to(f"/project/{self.project_id}"),
            ).props("flat")
            ui.label(f"Add Content: {self.project.name}").classes("text-2xl font-bold")

        # Check existing sections
        existing_sections = self.db.get_sections_by_project(self.project_id)
        if existing_sections:
            with ui.card().classes("w-full bg-yellow-50 border border-yellow-200 mb-4"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("warning").classes("text-yellow-600")
                    ui.label(
                        f"This project already has {len(existing_sections)} sections. New content will be appended."
                    ).classes("text-sm")

        # Instructions
        ui.markdown(
            """
        Upload or paste your learning material. The system will automatically detect chapters
        and sections, or you can configure how the content is organized.
        """
        ).classes("mb-4")

        # Input method selection
        with ui.row().classes("gap-4 mb-4"):
            paste_radio = ui.radio(
                ["Paste Text", "Upload File"], value="Paste Text"
            ).props("inline")

        # Content container (reactive)
        content_container = ui.column().classes("w-full")

        # Text content variable
        text_content = {"value": ""}

        def update_input_method():
            """Update UI based on selected input method"""
            content_container.clear()

            with content_container:
                if paste_radio.value == "Paste Text":
                    text_area = (
                        ui.textarea(
                            label="Paste your learning material here",
                            placeholder="Paste text to analyze...",
                        )
                        .classes("w-full")
                        .props("rows=15")
                    )

                    def on_text_change():
                        text_content["value"] = text_area.value or ""

                    text_area.on("update:modelValue", on_text_change)

                else:  # Upload File
                    ui.label("Upload a file:").classes("font-semibold mb-2")
                    ui.label("Supported: TXT, MD, EPUB, PDF, DOCX").classes(
                        "text-sm text-gray-500 mb-2"
                    )

                    # Create textarea for displaying uploaded content
                    uploaded_text_area = (
                        ui.textarea(
                            label="Uploaded content (you can edit if needed)",
                            placeholder="Upload a file to see its content here...",
                        )
                        .classes("w-full mt-4")
                        .props("rows=15")
                    )
                    uploaded_text_area.visible = (
                        False  # Hidden until content is uploaded
                    )

                    async def handle_upload(e):
                        """Handle file upload (use e.file directly for filename & content)"""
                        # Small diagnostic logs to validate event structure
                        print(f"DEBUG: Upload event type: {type(e)}")
                        print(f"DEBUG: Upload event attributes: {dir(e)}")
                        try:
                            print(f"DEBUG: Upload event sender type: {type(e.sender)}")
                            print(
                                f"DEBUG: Upload event sender attributes: {dir(e.sender)}"
                            )
                        except Exception:
                            pass

                        # Prefer direct access to e.file (newer NiceGUI UploadEventArguments)
                        if not hasattr(e, "file") or e.file is None:
                            print("DEBUG: Upload event missing 'file' attribute")
                            ui.notify(
                                "Upload event missing file data",
                                color="negative",
                                position="top",
                            )
                            return

                        # Get filename from e.file.name
                        try:
                            filename = e.file.name
                            print(f"DEBUG: filename from e.file.name: {filename}")
                        except Exception as ex:
                            print(f"DEBUG: Failed to get filename from e.file: {ex}")
                            ui.notify(
                                "Could not determine uploaded filename",
                                color="negative",
                                position="top",
                            )
                            return

                        # Read content via e.file.read() (async)
                        try:
                            uploaded_bytes = await e.file.read()
                            print(
                                f"DEBUG: Read {len(uploaded_bytes) if uploaded_bytes else 0} bytes from e.file"
                            )
                        except Exception as ex:
                            print(
                                f"DEBUG: Failed to read uploaded bytes from e.file: {ex}"
                            )
                            ui.notify(
                                "Could not read uploaded file",
                                color="negative",
                                position="top",
                            )
                            return

                        if not uploaded_bytes:
                            ui.notify(
                                "No file uploaded", color="warning", position="top"
                            )
                            return

                        file_ext = os.path.splitext(filename)[1].lower()

                        try:
                            if file_ext in [".txt", ".md"]:
                                # Simple text file
                                if isinstance(uploaded_bytes, (bytes, bytearray)):
                                    text_content["value"] = uploaded_bytes.decode(
                                        "utf-8"
                                    )
                                else:
                                    text_content["value"] = str(uploaded_bytes)
                                uploaded_text_area.value = text_content["value"]
                                uploaded_text_area.visible = True
                                ui.notify(
                                    f"Loaded {filename} ({len(text_content['value'])} characters)",
                                    color="positive",
                                    position="top",
                                )

                            elif file_ext in [".epub", ".pdf", ".docx", ".doc"]:
                                # Complex format - use converter
                                ui.notify(
                                    f"Converting {file_ext[1:].upper()} file...",
                                    position="top",
                                )

                                # Create temp file for converter
                                import tempfile

                                with tempfile.NamedTemporaryFile(
                                    delete=False, suffix=file_ext
                                ) as tmp:
                                    tmp.write(
                                        uploaded_bytes
                                        if isinstance(
                                            uploaded_bytes, (bytes, bytearray)
                                        )
                                        else str(uploaded_bytes).encode("utf-8")
                                    )
                                    tmp_path = tmp.name

                                # Convert
                                from utils.file_converters import convert_file_to_text

                                converted_text = convert_file_to_text(tmp_path)

                                # Cleanup
                                os.unlink(tmp_path)

                                if converted_text:
                                    text_content["value"] = converted_text
                                    uploaded_text_area.value = converted_text
                                    uploaded_text_area.visible = True
                                    ui.notify(
                                        f"Converted {filename} ({len(converted_text)} characters)",
                                        color="positive",
                                        position="top",
                                    )
                                else:
                                    ui.notify(
                                        "Failed to convert file",
                                        color="negative",
                                        position="top",
                                    )

                            else:
                                ui.notify(
                                    f"Unsupported file type: {file_ext}",
                                    color="negative",
                                    position="top",
                                )

                        except Exception as ex:
                            ui.notify(
                                f"Error reading file: {str(ex)}",
                                color="negative",
                                position="top",
                            )

                    # Update text_content when user edits the textarea
                    def on_uploaded_text_change():
                        text_content["value"] = uploaded_text_area.value or ""

                    uploaded_text_area.on("update:modelValue", on_uploaded_text_change)

                    ui.upload(on_upload=handle_upload, auto_upload=True).classes(
                        "w-full"
                    ).props('accept=".txt,.md,.epub,.pdf,.docx,.doc"')

        # Initialize
        paste_radio.on("update:modelValue", update_input_method)
        update_input_method()

        # Processing configuration
        ui.label("Processing Configuration").classes("text-xl font-bold mt-6 mb-4")

        with ui.grid(columns=2).classes("w-full gap-4"):
            min_size_slider = (
                ui.slider(min=200, max=2000, value=500, step=100)
                .classes("w-full")
                .props("label-always")
            )
            ui.label("Minimum Section Size (characters)").classes("text-sm")

            max_size_slider = (
                ui.slider(min=1000, max=10000, value=5000, step=500)
                .classes("w-full")
                .props("label-always")
            )
            ui.label("Maximum Section Size (characters)").classes("text-sm")

            overlap_slider = (
                ui.slider(min=0, max=500, value=100, step=50)
                .classes("w-full")
                .props("label-always")
            )
            ui.label("Overlap Between Sections (characters)").classes("text-sm")

            ui.checkbox("Enable hierarchical section detection", value=True)
            ui.label("Automatically detect chapters and headings").classes(
                "text-sm text-gray-600"
            )

        # Process button
        async def process_content():
            """Process text and create sections"""

            content = text_content["value"].strip()

            if not content:
                ui.notify(
                    "Please provide some text content to process",
                    color="warning",
                    position="top",
                )
                return

            # Show progress
            with ui.dialog() as progress_dialog, ui.card():
                ui.label("Processing your material...").classes("text-lg font-bold")
                ui.label("Detecting sections and creating content structure").classes(
                    "text-sm text-gray-600 mt-2"
                )
                ui.spinner(size="lg").classes("mt-4")

            progress_dialog.open()

            try:
                # Process text
                sections = create_sections_from_text(
                    content,
                    min_section_size=int(min_size_slider.value),
                    max_section_size=int(max_size_slider.value),
                    overlap=int(overlap_slider.value),
                )

                if not sections:
                    progress_dialog.close()
                    ui.notify(
                        "No valid sections could be created from the text",
                        color="negative",
                        position="top",
                    )
                    return

                # Save sections
                created_count = 0
                start_index = len(existing_sections)

                for order_idx, (section_content, title) in enumerate(sections):
                    section = self.db.create_section(
                        project_id=self.project_id,
                        content=section_content,
                        title=title,
                        order_index=start_index + order_idx,
                    )
                    if section:
                        created_count += 1

                progress_dialog.close()

                if created_count > 0:
                    ui.notify(
                        f"Successfully created {created_count} sections!",
                        color="positive",
                        position="top",
                    )
                    # Redirect to project view
                    ui.navigate.to(f"/project/{self.project_id}")
                else:
                    ui.notify(
                        "Failed to create sections", color="negative", position="top"
                    )

            except Exception as ex:
                progress_dialog.close()
                ui.notify(
                    f"Error processing content: {str(ex)}",
                    color="negative",
                    position="top",
                )

        ui.button(
            "Process & Create Sections", icon="rocket_launch", on_click=process_content
        ).classes("mt-6 bg-blue-500 text-lg px-8 py-3")
