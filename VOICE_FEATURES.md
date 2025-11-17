# Voice Input & Text-to-Speech Features

## Overview

The PECS Learning System includes comprehensive voice input and text-to-speech capabilities to enhance the learning experience. Speaking your thoughts is often more natural and effective than writing, especially when learning new concepts.

## Features

### 🎙️ Voice Input (Speech-to-Text)

Record your explanations, thoughts, and questions using your voice. The system provides two modes:

1. **High-Quality Recording** (Whisper API)
   - Professional-grade transcription
   - 90%+ accuracy even with accents
   - Handles technical terminology
   - Context-aware (understands what you're learning)
   - Works on all browsers

2. **Real-Time Voice Input** (Web Speech API)
   - Instant transcription as you speak
   - Free (no API costs)
   - Works in Chrome, Edge, and Safari
   - Great for quick notes

### 🔊 Text-to-Speech (TTS)

Listen to AI feedback read aloud with natural-sounding voices:

- Click "🔊 Read Aloud" on any AI response
- High-quality voice synthesis
- Helps with auditory learning
- Perfect for multitasking or reviewing while relaxing

---

## How to Use

### Voice Input

1. **Navigate to any PECS learning phase** (Prime, Engage, or Challenge)
2. You'll see two voice input buttons below each text area:
   - **🎙️ Record & Transcribe (High Quality)** - Best for explanations and detailed responses
   - **🎤 Real-time Voice Input (Quick)** - Best for quick notes (Chrome/Safari only)

3. **Click a button** to start recording
4. **Speak naturally** - explain your thoughts just as you would to a friend
5. **Click "Stop"** when done
6. **Review the transcription** - it will be automatically inserted into the text area
7. **Edit if needed** - the transcription is fully editable

### Text-to-Speech

1. **Get AI feedback** on any learning phase
2. **Look for the 🔊 Read Aloud button** below each AI response
3. **Click to play** - the AI response will be read aloud
4. **Listen and learn** - great for reviewing feedback while away from screen

---

## Setup & Configuration

### Prerequisites

Voice features require an **OpenAI API key**. If you don't have one:

1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Add it to your `.env` file (see below)

### Environment Configuration

Add to your `.env` file:

```bash
# Required for voice features
OPENAI_API_KEY=sk-...

# Optional: Customize voice settings
TTS_VOICE=nova  # Options: alloy, echo, fable, onyx, nova, shimmer
TTS_MODEL=tts-1  # Options: tts-1 (faster), tts-1-hd (higher quality)
WHISPER_MODEL=whisper-1
```

### Voice Options

Choose your preferred TTS voice:

| Voice | Description | Best For |
|-------|-------------|----------|
| **nova** | Warm, engaging female voice (default) | General learning, friendly tone |
| **alloy** | Neutral, balanced voice | Professional content, technical subjects |
| **echo** | Male voice, clear and direct | Straightforward explanations |
| **fable** | British accent, expressive | Literature, storytelling |
| **onyx** | Deep male voice, authoritative | Formal content, lectures |
| **shimmer** | Soft female voice, gentle | Calming, reflective content |

---

## Technical Details

### Speech-to-Text

**Primary Method: OpenAI Whisper API**

- **Accuracy**: 90-95% on clear audio
- **Languages**: 99 languages supported
- **Cost**: $0.006/minute ($0.36/hour)
- **File Formats**: webm, mp3, wav, m4a, and more
- **Max Duration**: 25MB file size limit (~2-3 hours of audio)
- **Context-Aware**: Uses section content to improve accuracy

**How It Works:**

1. Browser records audio using MediaRecorder API
2. Audio sent to backend as WebM file
3. Backend transcribes using Whisper API with contextual prompts
4. Transcript returned and inserted into textarea
5. Auto-saves after transcription completes

**Contextual Transcription:**

The system includes the section content and learning phase in the transcription prompt, which improves accuracy for:
- Technical terminology
- Subject-specific vocabulary
- Proper nouns and concepts from your material

### Text-to-Speech

**OpenAI TTS API**

- **Quality**: Natural-sounding, human-like voices
- **Cost**: $15 per 1 million characters (standard), $30 per 1M (HD)
- **Latency**: ~200ms generation time
- **Format**: MP3 audio
- **Character Limit**: ~4096 characters per request

**How It Works:**

1. Click "Read Aloud" button
2. Text sent to OpenAI TTS API
3. Audio generated and returned as MP3
4. Plays immediately in browser
5. Temporary file cleaned up automatically

---

## Cost Analysis

### For Individual Users

**Voice Input (Whisper):**
- 5-minute recording: $0.03
- 1-hour recording: $0.36
- 10 recordings per week (30 min total): ~$1.80/month

**Text-to-Speech:**
- 500-word feedback: ~3,000 characters
- 10 feedback reads/week: ~120,000 chars/month
- Cost: ~$1.80/month

**Total Estimated Cost:** $3-5/month for active use

### For Teams/Classrooms (100 users)

**Voice Input:**
- 100 users × 10 recordings × 3 min = 3,000 min/month
- Cost: ~$18/month

**Text-to-Speech:**
- 100 users × 10 reads × 3,000 chars = 3M chars/month
- Cost: ~$45/month

**Total: ~$63/month** for 100 active users

---

## Browser Compatibility

### Voice Input

| Browser | Whisper (High Quality) | Web Speech (Real-time) |
|---------|------------------------|------------------------|
| Chrome | ✅ Full Support | ✅ Full Support |
| Edge | ✅ Full Support | ✅ Full Support |
| Safari | ✅ Full Support | ✅ Siri-based Support |
| Firefox | ✅ Full Support | ❌ Not Supported |

**Recommendation:** Use Chrome or Edge for best experience.

### Text-to-Speech

All browsers support audio playback. TTS works universally.

---

## Privacy & Security

### Data Handling

- **Audio recordings**: Sent to OpenAI for transcription, then deleted
- **Transcripts**: Stored in your local database
- **TTS audio**: Generated on-demand, not stored permanently
- **No permanent storage**: Audio files are temporary and cleaned up immediately

### OpenAI Privacy

- OpenAI does not use your audio for training models (as of December 2023)
- Audio is processed and discarded
- See OpenAI's privacy policy: https://openai.com/policies/privacy-policy

### Local Control

- All transcripts stored in your local SQLite database
- You have full control over your data
- No third-party storage

---

## Troubleshooting

### Voice Input Not Working

**Problem**: "Microphone access denied"

**Solution:**
1. Check browser permissions for microphone access
2. Click the lock icon in address bar
3. Allow microphone access
4. Refresh the page and try again

**Problem**: "Voice features require OpenAI API key"

**Solution:**
1. Add `OPENAI_API_KEY` to your `.env` file
2. Restart the application
3. Verify the key is valid

**Problem**: "Transcription failed"

**Solution:**
1. Check audio recording worked (you should see recording timer)
2. Verify OpenAI API key has credits
3. Check internet connection
4. Try shorter recording (under 2 minutes)

### Text-to-Speech Not Working

**Problem**: No audio plays

**Solution:**
1. Check browser audio isn't muted
2. Verify OpenAI API key is set
3. Check browser console for errors
4. Try a different browser

**Problem**: "TTS generation failed"

**Solution:**
1. Verify OpenAI API key has credits
2. Check internet connection
3. Try shorter text (under 1000 words)

---

## Performance Tips

### For Best Transcription Accuracy

1. **Use a good microphone** - Built-in laptop mics work, but headset mics are better
2. **Minimize background noise** - Find a quiet environment
3. **Speak clearly** - No need to be slow, just articulate
4. **Use natural language** - Speak as you would to a friend
5. **Pause between thoughts** - Helps with punctuation
6. **Record in chunks** - Break long explanations into 2-3 minute segments

### For Best TTS Experience

1. **Use headphones** - Better audio quality
2. **Adjust playback speed** - Use browser audio controls if needed
3. **Listen while reviewing notes** - Auditory reinforcement helps learning
4. **Try different voices** - Find the one that works best for you

---

## Developer Guide

### Using Voice Service in Code

```python
from utils.voice_service import get_voice_service

# Get singleton instance
voice_service = get_voice_service()

# Check if available
if voice_service.is_available():
    # Transcribe audio
    transcript = voice_service.transcribe_audio("/path/to/audio.webm")

    # Transcribe with context (better accuracy)
    transcript = voice_service.transcribe_with_context(
        "/path/to/audio.webm",
        section_content="Content being learned",
        phase="engage"  # prime, engage, or challenge
    )

    # Generate speech
    audio_path = voice_service.text_to_speech("Hello, world!")

    # Cleanup
    voice_service.cleanup_temp_file(audio_path)
```

### Adding Voice Input to UI

```python
from nicegui import ui
from nicegui_app.components.voice_input import add_voice_input_buttons

# Create textarea
textarea = ui.textarea(label="Your response")

# Add voice input buttons
add_voice_input_buttons(
    textarea,
    section_content=section.content,  # Optional, for context
    phase="engage",  # Optional, for context
    on_transcribe=lambda text: print(f"Transcribed: {text}")  # Optional callback
)
```

### Testing Voice Features

Run the voice service tests:

```bash
pytest tests/test_voice_service.py -v
```

---

## Roadmap

### Planned Enhancements

- [ ] **Offline voice input** using local Whisper models
- [ ] **Voice recording playback** (review your recordings)
- [ ] **Multiple language support** (Spanish, French, etc.)
- [ ] **Custom voice models** (upload your own TTS voice)
- [ ] **Automatic punctuation** and formatting
- [ ] **Speaker diarization** (multiple speakers)
- [ ] **Real-time feedback** while speaking

### Community Requests

Have ideas for voice features? Open an issue on GitHub!

---

## FAQ

**Q: Do I need an OpenAI API key?**
A: Yes, voice features require an OpenAI API key for Whisper transcription and TTS.

**Q: How much does it cost?**
A: Very affordable! ~$3-5/month for individual use, ~$60/month for 100 active users.

**Q: Does it work offline?**
A: Not currently. Voice features require internet connection for API calls. Local Whisper support is planned for future release.

**Q: What languages are supported?**
A: Whisper supports 99 languages, but the UI is currently English-only. Multilingual UI is planned.

**Q: Can I use my own voice for TTS?**
A: Not yet, but custom voice models are on the roadmap.

**Q: Is my audio data private?**
A: Yes. Audio is sent to OpenAI for processing and immediately deleted. Transcripts are stored locally in your database.

**Q: Can I disable voice features?**
A: Yes, simply don't add `OPENAI_API_KEY` to your `.env` file. The buttons won't appear.

**Q: What microphone should I use?**
A: Built-in mics work fine, but a headset mic provides better quality and fewer errors.

---

## Support

For issues or questions:

- **Documentation**: See this file and `CLAUDE.md`
- **GitHub Issues**: https://github.com/arashbehmand/PECS-learner/issues
- **Test File**: `tests/test_voice_service.py` for examples

---

## Credits

Voice features powered by:

- **OpenAI Whisper** - State-of-the-art speech recognition
- **OpenAI TTS** - Natural-sounding text-to-speech
- **Web Speech API** - Browser-native speech recognition
- **NiceGUI** - Beautiful Python web framework

---

*Last updated: November 2025*
