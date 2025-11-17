"""
Voice input component for NiceGUI.

Provides:
- Audio recording with visual feedback
- Real-time speech recognition (Web Speech API)
- Integration with Whisper API for high-quality transcription
- Automatic insertion into text areas
"""

import asyncio
import logging
import os
import tempfile
from typing import Callable, Optional

from nicegui import ui

logger = logging.getLogger(__name__)


class VoiceInputButton:
    """Reusable voice input button component for NiceGUI."""

    def __init__(
        self,
        textarea: ui.textarea,
        *,
        mode: str = "whisper",
        button_text: str = "🎤 Voice Input",
        button_classes: str = "bg-blue-600",
        on_transcribe: Optional[Callable[[str], None]] = None,
        section_content: Optional[str] = None,
        phase: Optional[str] = None,
    ):
        """Create a voice input button.

        Args:
            textarea: The textarea to insert transcription into
            mode: 'whisper' for recorded transcription, 'realtime' for Web Speech API
            button_text: Text to display on button
            button_classes: CSS classes for button styling
            on_transcribe: Optional callback when transcription completes
            section_content: Optional section content for contextual transcription
            phase: Optional learning phase for contextual transcription
        """
        self.textarea = textarea
        self.mode = mode
        self.on_transcribe = on_transcribe
        self.section_content = section_content
        self.phase = phase

        # Create button
        self.button = ui.button(
            button_text,
            on_click=self._handle_click,
        ).classes(button_classes)

        # Add tooltip
        self.button.tooltip(
            "Record your voice and convert to text"
            if mode == "whisper"
            else "Real-time speech recognition (Chrome/Safari only)"
        )

    async def _handle_click(self):
        """Handle button click to start recording."""
        if self.mode == "whisper":
            await self._start_whisper_recording()
        else:
            await self._start_realtime_recognition()

    async def _start_whisper_recording(self):
        """Start audio recording and transcribe with Whisper."""
        # Create recording dialog
        with ui.dialog() as dialog, ui.card().classes("p-6"):
            ui.label("🎙️ Recording...").classes("text-xl font-bold mb-4")
            ui.label("Speak your thoughts. Click 'Stop' when done.").classes("mb-4")

            # Timer display
            timer_label = ui.label("0:00").classes("text-2xl font-mono mb-4")

            # Animated recording indicator
            with ui.row().classes("items-center gap-2 mb-4"):
                ui.icon("mic", size="lg").classes("text-red-500 animate-pulse")
                ui.label("Recording in progress...").classes("text-gray-600")

            # Control buttons
            with ui.row().classes("gap-2"):
                ui.button(
                    "Stop Recording",
                    on_click=lambda: dialog.submit("stop"),
                    color="red",
                )
                ui.button(
                    "Cancel", on_click=lambda: dialog.submit("cancel"), color="gray"
                )

        # Open dialog
        dialog.open()

        # Start recording in JavaScript
        recording_started = await ui.run_javascript(
            """
            new Promise((resolve) => {
                navigator.mediaDevices.getUserMedia({ audio: true })
                    .then(stream => {
                        const mediaRecorder = new MediaRecorder(stream, {
                            mimeType: 'audio/webm;codecs=opus'
                        });
                        const chunks = [];

                        mediaRecorder.ondataavailable = (e) => {
                            if (e.data.size > 0) chunks.push(e.data);
                        };

                        mediaRecorder.start();

                        // Store globally
                        window.activeRecorder = {
                            recorder: mediaRecorder,
                            stream: stream,
                            chunks: chunks,
                            startTime: Date.now()
                        };

                        resolve(true);
                    })
                    .catch(err => {
                        console.error('Microphone access denied:', err);
                        resolve(false);
                    });
            })
            """,
            timeout=10.0,
        )

        if not recording_started:
            dialog.close()
            ui.notify(
                "Microphone access denied. Please allow microphone access.",
                type="negative",
            )
            return

        # Update timer
        async def update_timer():
            while dialog.value is None:
                elapsed = await ui.run_javascript(
                    "window.activeRecorder ? Math.floor((Date.now() - window.activeRecorder.startTime) / 1000) : 0"
                )
                minutes = int(elapsed) // 60
                seconds = int(elapsed) % 60
                timer_label.set_text(f"{minutes}:{seconds:02d}")
                await asyncio.sleep(1)

        # Start timer task
        timer_task = asyncio.create_task(update_timer())

        # Wait for user to stop
        result = await dialog

        # Cancel timer
        timer_task.cancel()

        if result == "cancel":
            # Stop recording and discard
            await ui.run_javascript(
                """
                if (window.activeRecorder) {
                    window.activeRecorder.recorder.stop();
                    window.activeRecorder.stream.getTracks().forEach(t => t.stop());
                    delete window.activeRecorder;
                }
                """
            )
            ui.notify("Recording cancelled", type="info")
            return

        # Show processing dialog
        with ui.dialog() as process_dialog, ui.card().classes("p-6"):
            ui.label("Processing...").classes("text-xl font-bold mb-4")
            ui.spinner(size="lg")
            ui.label("Transcribing your audio with AI...").classes("text-gray-600")

        process_dialog.open()

        try:
            # Stop recording and get blob
            audio_blob_b64 = await ui.run_javascript(
                """
                new Promise((resolve) => {
                    if (!window.activeRecorder) {
                        resolve(null);
                        return;
                    }

                    const rec = window.activeRecorder;

                    rec.recorder.onstop = async () => {
                        const blob = new Blob(rec.chunks, { type: 'audio/webm;codecs=opus' });

                        // Convert to base64
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            const base64 = reader.result.split(',')[1];
                            resolve(base64);
                        };
                        reader.readAsDataURL(blob);

                        // Cleanup
                        rec.stream.getTracks().forEach(t => t.stop());
                    };

                    rec.recorder.stop();
                })
                """,
                timeout=30.0,
            )

            if not audio_blob_b64:
                raise RuntimeError("Failed to capture audio")

            # Send to backend for transcription
            import base64

            audio_data = base64.b64decode(audio_blob_b64)

            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name

            # Import here to avoid circular dependency
            from utils.voice_service import get_voice_service

            voice_service = get_voice_service()

            # Transcribe with context if available
            if self.section_content and self.phase:
                transcript = voice_service.transcribe_with_context(
                    tmp_path,
                    section_content=self.section_content,
                    phase=self.phase,
                )
            else:
                transcript = voice_service.transcribe_audio(tmp_path)

            # Cleanup temp file
            os.unlink(tmp_path)

            # Insert into textarea
            current_value = self.textarea.value or ""
            if current_value and not current_value.endswith("\n"):
                current_value += "\n\n"

            self.textarea.value = current_value + transcript
            self.textarea.update()

            # Call callback if provided
            if self.on_transcribe:
                self.on_transcribe(transcript)

            process_dialog.close()
            ui.notify(
                f"✅ Transcribed {len(transcript)} characters successfully!",
                type="positive",
            )

        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            process_dialog.close()
            ui.notify(f"Transcription failed: {str(e)}", type="negative")

        finally:
            # Cleanup
            await ui.run_javascript("delete window.activeRecorder;")

    async def _start_realtime_recognition(self):
        """Start real-time speech recognition using Web Speech API."""
        # Check browser support
        supported = await ui.run_javascript(
            "!!(window.SpeechRecognition || window.webkitSpeechRecognition)"
        )

        if not supported:
            ui.notify(
                "Real-time speech recognition not supported in this browser. "
                "Try Chrome or Safari, or use 'Record & Transcribe' instead.",
                type="warning",
            )
            return

        # Create recognition dialog
        with ui.dialog() as dialog, ui.card().classes("p-6"):
            ui.label("🎤 Listening...").classes("text-xl font-bold mb-4")
            ui.label("Start speaking. Pauses are automatically detected.").classes(
                "mb-4"
            )

            # Live transcript display
            ui.textarea(label="Live Transcription", value="").classes("w-full").props(
                "readonly rows=6"
            )

            with ui.row().classes("gap-2 mt-4"):
                ui.button("Done", on_click=lambda: dialog.submit("done"), color="green")
                ui.button(
                    "Cancel", on_click=lambda: dialog.submit("cancel"), color="gray"
                )

        dialog.open()

        # Start recognition
        await ui.run_javascript(
            """
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();

            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            let finalTranscript = '';

            recognition.onresult = (event) => {
                let interimTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }

                // Update the transcript area
                const fullText = finalTranscript + interimTranscript;
                const elem = document.querySelector('textarea[label="Live Transcription"]');
                if (elem) elem.value = fullText;

                // Store final transcript
                window.realtimeTranscript = finalTranscript;
            };

            recognition.onerror = (event) => {
                console.error('Recognition error:', event.error);
            };

            recognition.onend = () => {
                // Auto-restart unless stopped
                if (window.realtimeRecognitionActive) {
                    recognition.start();
                }
            };

            window.realtimeRecognitionActive = true;
            window.activeRecognition = recognition;
            recognition.start();
            """
        )

        # Wait for user to finish
        result = await dialog

        # Stop recognition
        await ui.run_javascript(
            """
            window.realtimeRecognitionActive = false;
            if (window.activeRecognition) {
                window.activeRecognition.stop();
            }
            """
        )

        if result == "cancel":
            ui.notify("Cancelled", type="info")
            return

        # Get final transcript
        final_text = await ui.run_javascript("window.realtimeTranscript || ''")

        if final_text:
            # Insert into textarea
            current_value = self.textarea.value or ""
            if current_value and not current_value.endswith("\n"):
                current_value += "\n\n"

            self.textarea.value = current_value + final_text.strip()
            self.textarea.update()

            # Call callback
            if self.on_transcribe:
                self.on_transcribe(final_text.strip())

            ui.notify(
                f"✅ Added {len(final_text)} characters",
                type="positive",
            )

        # Cleanup
        await ui.run_javascript(
            "delete window.realtimeTranscript; delete window.activeRecognition;"
        )


def add_voice_input_buttons(
    textarea: ui.textarea,
    *,
    section_content: Optional[str] = None,
    phase: Optional[str] = None,
    on_transcribe: Optional[Callable[[str], None]] = None,
) -> None:
    """Add voice input buttons below a textarea.

    Creates both high-quality (Whisper) and real-time (Web Speech) options.

    Args:
        textarea: The textarea to attach voice input to
        section_content: Optional section content for contextual transcription
        phase: Optional learning phase for contextual transcription
        on_transcribe: Optional callback when transcription completes
    """
    with ui.row().classes("gap-2 mt-2"):
        # High-quality recording button
        VoiceInputButton(
            textarea,
            mode="whisper",
            button_text="🎙️ Record & Transcribe (High Quality)",
            button_classes="bg-purple-600",
            section_content=section_content,
            phase=phase,
            on_transcribe=on_transcribe,
        )

        # Real-time recognition button
        VoiceInputButton(
            textarea,
            mode="realtime",
            button_text="🎤 Real-time Voice Input (Quick)",
            button_classes="bg-blue-600",
            on_transcribe=on_transcribe,
        )
