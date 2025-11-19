"""
Tests for voice service (speech-to-text and text-to-speech).
"""

import os
import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest

from utils.voice_service import VoiceService, get_voice_service


class TestVoiceService:
    """Tests for VoiceService class."""

    def test_initialization_default_values(self):
        """Test VoiceService initializes with default values."""
        service = VoiceService()

        assert service.tts_voice == "nova"
        assert service.tts_model == "tts-1"
        assert service.whisper_model == "whisper-1"

    def test_initialization_custom_values(self):
        """Test VoiceService initializes with custom values."""
        service = VoiceService(
            tts_voice="alloy", tts_model="tts-1-hd", whisper_model="whisper-1"
        )

        assert service.tts_voice == "alloy"
        assert service.tts_model == "tts-1-hd"
        assert service.whisper_model == "whisper-1"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_is_available_with_api_key(self):
        """Test is_available returns True when API key is set."""
        service = VoiceService()
        assert service.is_available() is True

    @patch.dict(os.environ, {}, clear=True)
    def test_is_available_without_api_key(self):
        """Test is_available returns False when API key is not set."""
        service = VoiceService()
        assert service.is_available() is False

    @patch("utils.voice_service.transcription")
    def test_transcribe_audio_success(self, mock_transcription):
        """Test successful audio transcription."""
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(b"fake audio data")
            tmp_path = tmp.name

        try:
            # Mock transcription response
            mock_response = Mock()
            mock_response.text = "This is a test transcription."
            mock_transcription.return_value = mock_response

            service = VoiceService()
            result = service.transcribe_audio(tmp_path)

            assert result == "This is a test transcription."
            mock_transcription.assert_called_once()

            # Verify call arguments
            call_args = mock_transcription.call_args
            assert call_args.kwargs["model"] == "whisper-1"
            assert call_args.kwargs["language"] == "en"

        finally:
            os.unlink(tmp_path)

    @patch("utils.voice_service.transcription")
    def test_transcribe_audio_with_prompt(self, mock_transcription):
        """Test transcription with custom prompt."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(b"fake audio data")
            tmp_path = tmp.name

        try:
            mock_response = Mock()
            mock_response.text = "Transcribed text"
            mock_transcription.return_value = mock_response

            service = VoiceService()
            result = service.transcribe_audio(
                tmp_path, prompt="Technical lecture about machine learning"
            )

            assert result == "Transcribed text"

            call_args = mock_transcription.call_args
            assert (
                call_args.kwargs["prompt"] == "Technical lecture about machine learning"
            )

        finally:
            os.unlink(tmp_path)

    @patch("utils.voice_service.transcription")
    def test_transcribe_audio_dict_response(self, mock_transcription):
        """Test transcription with dict response format."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(b"fake audio data")
            tmp_path = tmp.name

        try:
            # Mock dict response
            mock_transcription.return_value = {"text": "Dict response text"}

            service = VoiceService()
            result = service.transcribe_audio(tmp_path)

            assert result == "Dict response text"

        finally:
            os.unlink(tmp_path)

    @patch("utils.voice_service.transcription")
    def test_transcribe_audio_failure(self, mock_transcription):
        """Test transcription failure handling."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(b"fake audio data")
            tmp_path = tmp.name

        try:
            mock_transcription.side_effect = Exception("API error")

            service = VoiceService()

            with pytest.raises(Exception) as exc_info:
                service.transcribe_audio(tmp_path)

            assert "Failed to transcribe audio" in str(exc_info.value)

        finally:
            os.unlink(tmp_path)

    @patch("utils.voice_service.OpenAI")
    def test_text_to_speech_success(self, mock_openai_class):
        """Test successful text-to-speech generation."""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock speech response
        mock_response = MagicMock()
        mock_client.audio.speech.create.return_value = mock_response

        service = VoiceService()
        result = service.text_to_speech("Hello, world!")

        assert result is not None
        assert result.endswith(".mp3")

        # Verify API call
        mock_client.audio.speech.create.assert_called_once_with(
            model="tts-1", voice="nova", input="Hello, world!"
        )

        # Verify file was written
        mock_response.stream_to_file.assert_called_once()

        # Cleanup
        if os.path.exists(result):
            os.unlink(result)

    @patch("utils.voice_service.OpenAI")
    def test_text_to_speech_custom_output_path(self, mock_openai_class):
        """Test TTS with custom output path."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_client.audio.speech.create.return_value = mock_response

        custom_path = "/tmp/custom_output.mp3"

        service = VoiceService()
        result = service.text_to_speech("Test", output_path=custom_path)

        assert result == custom_path
        mock_response.stream_to_file.assert_called_once_with(custom_path)

    @patch("utils.voice_service.OpenAI")
    def test_text_to_speech_failure(self, mock_openai_class):
        """Test TTS failure handling."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_client.audio.speech.create.side_effect = Exception("API error")

        service = VoiceService()

        with pytest.raises(Exception) as exc_info:
            service.text_to_speech("Test")

        assert "Failed to generate speech" in str(exc_info.value)

    @patch("utils.voice_service.transcription")
    def test_transcribe_with_context(self, mock_transcription):
        """Test contextual transcription with section content."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(b"fake audio data")
            tmp_path = tmp.name

        try:
            mock_response = Mock()
            mock_response.text = "Transcribed with context"
            mock_transcription.return_value = mock_response

            service = VoiceService()
            result = service.transcribe_with_context(
                tmp_path,
                section_content="This is a lecture about neural networks and deep learning.",
                phase="engage",
            )

            assert result == "Transcribed with context"

            # Verify prompt was included
            call_args = mock_transcription.call_args
            assert call_args.kwargs["prompt"] is not None
            assert "explaining concepts" in call_args.kwargs["prompt"].lower()

        finally:
            os.unlink(tmp_path)

    @patch("utils.voice_service.transcription")
    def test_transcribe_with_context_prime_phase(self, mock_transcription):
        """Test contextual transcription for prime phase."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(b"fake audio data")
            tmp_path = tmp.name

        try:
            mock_response = Mock()
            mock_response.text = "Prime phase transcription"
            mock_transcription.return_value = mock_response

            service = VoiceService()
            result = service.transcribe_with_context(tmp_path, phase="prime")

            assert result == "Prime phase transcription"

            call_args = mock_transcription.call_args
            assert "initial understanding" in call_args.kwargs["prompt"].lower()

        finally:
            os.unlink(tmp_path)

    def test_cleanup_temp_file(self):
        """Test temporary file cleanup."""
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        assert os.path.exists(tmp_path)

        VoiceService.cleanup_temp_file(tmp_path)

        assert not os.path.exists(tmp_path)

    def test_cleanup_temp_file_nonexistent(self):
        """Test cleanup of nonexistent file (should not raise)."""
        VoiceService.cleanup_temp_file("/nonexistent/file.mp3")
        # Should not raise exception


class TestGetVoiceService:
    """Tests for get_voice_service singleton."""

    def test_singleton_returns_same_instance(self):
        """Test that get_voice_service returns the same instance."""
        service1 = get_voice_service()
        service2 = get_voice_service()

        assert service1 is service2

    def test_singleton_returns_voice_service(self):
        """Test that singleton returns VoiceService instance."""
        service = get_voice_service()

        assert isinstance(service, VoiceService)
