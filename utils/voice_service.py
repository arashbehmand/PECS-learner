"""
Voice input and text-to-speech service for PECS Learning System.

This module provides:
- Speech-to-text via OpenAI Whisper API
- Text-to-speech via OpenAI TTS API
- Audio file handling and format conversion
"""

import logging
import os
import tempfile
from typing import Literal, Optional

from litellm import transcription
from openai import OpenAI

logger = logging.getLogger(__name__)


class VoiceServiceError(Exception):
    """Exception raised for errors in the voice service operations."""

    # No implementation needed - just inherit from Exception


# Voice configuration
TtsVoiceOptions = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
TtsModelOptions = Literal["tts-1", "tts-1-hd"]


class VoiceService:
    """Service for speech-to-text and text-to-speech operations."""

    def __init__(
        self,
        *,
        tts_voice: TtsVoiceOptions = "nova",
        tts_model: TtsModelOptions = "tts-1",
        whisper_model: str = "whisper-1",
    ):
        """Initialize voice service.

        Args:
            tts_voice: Voice to use for TTS (default: nova - warm, engaging)
            tts_model: TTS model quality (tts-1 or tts-1-hd)
            whisper_model: Whisper model for transcription
        """
        self.tts_voice = tts_voice
        self.tts_model = tts_model
        self.whisper_model = whisper_model

        # Validate API key availability
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning(
                "OPENAI_API_KEY not found. Voice features will not work. "
                "Please add your OpenAI API key to .env file."
            )

    def transcribe_audio(
        self,
        audio_file_path: str,
        *,
        language: str = "en",
        prompt: Optional[str] = None,
    ) -> str:
        """Transcribe audio file to text using Whisper API.

        Args:
            audio_file_path: Path to audio file (webm, mp3, wav, m4a, etc.)
            language: Language code (default: en for English)
            prompt: Optional prompt to guide transcription style/terminology

        Returns:
            Transcribed text

        Raises:
            VoiceServiceError: If transcription fails
        """
        try:
            logger.info(f"Transcribing audio file: {audio_file_path}")

            # Open audio file
            with open(audio_file_path, "rb") as audio_file:
                # Use litellm's transcription function
                response = transcription(
                    model=self.whisper_model,
                    file=audio_file,
                    language=language,
                    prompt=prompt,
                )

            # Extract text from response
            if hasattr(response, "text"):
                transcript = response.text
            elif isinstance(response, dict) and "text" in response:
                transcript = response["text"]
            else:
                raise ValueError(f"Unexpected response format: {response}")

            logger.info(
                f"Transcription successful. Length: {len(transcript)} characters"
            )
            return transcript.strip()

        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            raise VoiceServiceError(f"Failed to transcribe audio: {str(e)}")

    def text_to_speech(
        self,
        text: str,
        output_path: Optional[str] = None,
    ) -> str:
        """Convert text to speech using OpenAI TTS API.

        Args:
            text: Text to convert to speech
            output_path: Optional path to save audio file. If None, creates temp file.

        Returns:
            Path to generated audio file (MP3 format)

        Raises:
            VoiceServiceError: If TTS generation fails
        """
        try:
            logger.info(f"Generating speech for text ({len(text)} characters)")

            # Create output path if not provided
            if output_path is None:
                # Fixed: Use context manager for resource allocation (pylint W1732)
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp3", prefix="tts_"
                ) as temp_file:
                    output_path = temp_file.name

            # Use OpenAI's TTS via litellm
            # Note: litellm doesn't have direct TTS support, so we use openai directly
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            response = client.audio.speech.create(
                model=self.tts_model,
                voice=self.tts_voice,
                input=text,
            )

            # Save to file
            response.stream_to_file(output_path)

            logger.info(f"TTS generation successful. Saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"TTS generation failed: {e}", exc_info=True)
            raise VoiceServiceError(f"Failed to generate speech: {str(e)}")

    def transcribe_with_context(
        self,
        audio_file_path: str,
        *,
        section_content: Optional[str] = None,
        phase: Optional[str] = None,
    ) -> str:
        """Transcribe audio with contextual prompting for better accuracy.

        Uses the section content and learning phase to guide Whisper transcription,
        improving accuracy for technical terms and concepts.

        Args:
            audio_file_path: Path to audio file
            section_content: Optional section content for context
            phase: Optional learning phase (prime, engage, challenge)

        Returns:
            Transcribed text with improved accuracy
        """
        # Build contextual prompt
        prompt_parts = []

        if phase:
            phase_prompts = {
                "prime": "Student explaining their initial understanding and questions about educational content.",
                "engage": "Student explaining concepts in their own words, demonstrating comprehension.",
                "challenge": "Student analyzing and making critical connections between ideas.",
            }
            if phase in phase_prompts:
                prompt_parts.append(phase_prompts[phase])

        # Extract key terms from section content (first 200 chars)
        if section_content:
            # Get first few sentences as context
            context_snippet = section_content[:200].strip()
            if context_snippet:
                prompt_parts.append(f"Context: {context_snippet}")

        # Combine prompts (max 224 tokens for Whisper prompt)
        prompt = " ".join(prompt_parts)[:500] if prompt_parts else None

        return self.transcribe_audio(audio_file_path, prompt=prompt)

    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """Delete temporary audio file.

        Args:
            file_path: Path to file to delete
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")

    def is_available(self) -> bool:
        """Check if voice service is available (API key configured).

        Returns:
            True if OpenAI API key is configured, False otherwise
        """
        return bool(os.getenv("OPENAI_API_KEY"))


# Global singleton instance - replaced with function attribute to avoid global statement (pylint W0603)
# _voice_service_instance: Optional[VoiceService] = None


def get_voice_service() -> VoiceService:
    """Get or create the VoiceService singleton instance.

    Returns:
        VoiceService singleton instance
    """
    # Use public function attribute instead of global to avoid pylint W0603
    if not hasattr(get_voice_service, "instance"):
        get_voice_service.instance = VoiceService()
    return get_voice_service.instance
