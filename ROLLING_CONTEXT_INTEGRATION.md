# Rolling Context & Study Notes Integration

## Overview

This document describes the integration of two key features from the original document summarizer script into the PECS learning system:

1. **Rolling Window Context**: Maintains a cumulative summary across sections based on material sequence
2. **Study Notes Generation**: Creates diagram-style study notes focusing on connections, definitions, and key concepts

## Key Features

### 1. Rolling Window Context

**What it does:**
- Maintains a "summary so far" as content flows through sections
- Each section's rolling summary includes context from all previous sections (by order_index)
- This is based on **material sequence**, not user progress
- Provides narrative continuity, especially important for books where concepts build on each other

**How it works:**
- When generated for section N, it includes summaries of sections 0 to N-1
- Summaries are concise (target: 300-400 words, max: 2000 chars)
- Stored in `sections.rolling_summary` field
- Generated on-demand or in batch mode

**Use cases:**
- Better AI understanding across multi-section materials
- Reduces repetition in AI responses
- Helps AI spot connections between sections
- Creates continuity for book-length materials

### 2. Study Notes Generation

**What it does:**
- Generates study notes for each section in the style students write when truly understanding material (Feynman method)
- Focuses on: key concepts, definitions, connections, diagrams, relationships
- **NOT a summary** - it's active learning notes
- Aligns with PECS Challenge phase goals

**How it works:**
- Includes rolling context from previous sections
- Incorporates student's PECS learning journey (if available)
- Stored in `sections.study_notes` field (markdown format)
- Generated on-demand or in batch mode

**Use cases:**
- Final review before exams
- Quick reference for key concepts
- Understanding connections across sections
- Feynman technique learning aid

## Recent Updates

### v1.1 - LiteLLM Integration & Non-Blocking UI (Latest)

**Major Improvements:**

1. **Replaced OpenAI SDK with LiteLLM**
   - Now supports multiple LLM providers (OpenAI, Anthropic, Gemini, etc.)
   - Configure via standard environment variables
   - Unified API across all providers
   - Better error handling and provider flexibility

2. **Fixed Blocking UI Issue**
   - **Problem**: UI froze for 30+ minutes during generation, progress bar stuck at 0%
   - **Solution**: Background threading with real-time progress updates
   - Now shows actual progress as sections are processed
   - UI remains responsive during generation
   - Progress updates every 100ms via polling

3. **Supported LLM Providers** (via LiteLLM)
   - OpenAI: `gpt-4o`, `gpt-4o-mini`, `gpt-5-mini`, `gpt-5.1`
   - Anthropic: `claude-3-opus`, `claude-3-sonnet`, `claude-3-haiku`
   - Google: `gemini-pro`, `gemini-1.5-pro`
   - And 100+ other models via LiteLLM

See configuration section below for setup details.

---

## Architecture

### Database Schema Changes

**New fields in `sections` table:**
```sql
rolling_summary TEXT  -- Cumulative summary of previous sections
study_notes TEXT      -- Study notes for this section (markdown)
```

### Configuration (environment variables)

#### API Keys (choose your provider)

```bash
# OpenAI (default)
OPENAI_API_KEY=your_openai_key

# Or Anthropic
ANTHROPIC_API_KEY=your_anthropic_key

# Or Google Gemini
GEMINI_API_KEY=your_gemini_key

# LiteLLM supports 100+ providers - see: https://docs.litellm.ai/docs/providers
```

#### Model Configuration

```bash
# Model selection (configurable, use any LiteLLM-supported model)
LLM_MODEL_FAST=gpt-5-mini                    # For rolling context (fast/cheap)
LLM_MODEL_QUALITY=gpt-5.1                    # For study notes (high quality)
LLM_MODEL_DEFAULT=gpt-5-mini                 # For general PECS feedback

# Examples for other providers:
# LLM_MODEL_FAST=claude-3-haiku
# LLM_MODEL_QUALITY=claude-3-opus
# LLM_MODEL_DEFAULT=gemini-1.5-pro

# Rolling context limits
ROLLING_CONTEXT_MAX_CHARS=10000         # Safety net (hard limit)
ROLLING_CONTEXT_TARGET_TOKENS=400       # Target size (~300-400 words)

# Optional: LiteLLM debugging
LITELLM_VERBOSE=false                   # Set to true for debugging
```

#### Observability (optional)

```bash
# Langfuse integration (works with LiteLLM)
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

### New Modules

1. **`utils/rolling_context_service.py`**
   - `RollingContextService`: Main service for generating rolling context and study notes
   - Methods:
     - `generate_rolling_summary(section_id)` - Generate for single section
     - `generate_rolling_summaries_batch(project_id)` - Generate for all sections
     - `generate_study_notes(section_id)` - Generate notes for single section
     - `generate_study_notes_batch(project_id)` - Generate notes for all sections

2. **`utils/migrate_add_rolling_context.py`**
   - Database migration script for existing installations
   - Adds `rolling_summary` and `study_notes` columns

### Updated Modules

1. **`utils/models.py`**
   - Added `rolling_summary` and `study_notes` columns to `Section` model

2. **`utils/llm_service.py`**
   - Added configurable model support (`model_fast`, `model_quality`, `model`)
   - New methods:
     - `generate_rolling_summary()` - LLM call for rolling context
     - `generate_study_notes()` - LLM call for study notes
     - `combine_study_notes()` - Reduce phase (if needed for book-wide notes)
     - `refine_study_notes()` - Consistency phase (if needed)

3. **`utils/context_builder.py`**
   - Added `rolling_summary` parameter to `build_learning_context()`
   - New function: `format_context_with_rolling_summary()` - Formats context with rolling summary for AI calls

4. **`utils/prompts.yaml`**
   - Added `rolling_context_module` with `generate_summary` prompt
   - Added `study_notes_module` with:
     - `generate_section_notes` - Per-section study notes
     - `combine_section_notes` - Reduce phase
     - `refine_study_notes` - Consistency phase

5. **`nicegui_app/config.py`**
   - Added model configuration variables
   - Added rolling context configuration variables

## Usage

### For Developers

#### Generate Rolling Context

```python
from utils.rolling_context_service import RollingContextService
from utils.llm_service import LLMService
from utils.database import DatabaseRepository

# Initialize services
llm_service = LLMService()
db = DatabaseRepository()
rolling_service = RollingContextService(llm_service, db)

# Generate for single section
rolling_summary = rolling_service.generate_rolling_summary(section_id=123)

# Generate for all sections in project (batch mode)
def progress_callback(current, total, title):
    print(f"Processing {current}/{total}: {title}")

results = rolling_service.generate_rolling_summaries_batch(
    project_id=1,
    progress_callback=progress_callback
)
```

#### Generate Study Notes

```python
# Generate for single section
study_notes = rolling_service.generate_study_notes(section_id=123)

# Generate for all sections (batch mode with rolling context)
results = rolling_service.generate_study_notes_batch(
    project_id=1,
    progress_callback=progress_callback
)
```

#### Use Rolling Context in PECS AI Calls

```python
from utils.context_builder import build_learning_context, format_context_with_rolling_summary

# Build context with rolling summary
section = db.get_section(section_id)
context = build_learning_context(
    section_content=section.content,
    pecs_data=section.pecs_data,
    flashcards=flashcards,
    rolling_summary=section.rolling_summary  # ← Include rolling context
)

# Format for AI prompt
formatted = format_context_with_rolling_summary(context)

# Use in LLM call
response = llm_service.analyze_section_understanding(
    chunk_text=formatted,
    student_response=student_response
)
```

### For Users

#### Migrating Existing Database

```bash
python utils/migrate_add_rolling_context.py
```

#### Running the Application

```bash
# Set model preferences (optional)
export LLM_MODEL_FAST=gpt-4o-mini
export LLM_MODEL_QUALITY=gpt-4o

# Run application
python nicegui_app/main.py
```

## Generation Modes

### 1. On-Demand Generation
- Generate rolling context/study notes for specific section when needed
- Useful for incremental learning
- Lower cost (only generates what's needed)

### 2. Batch Generation (1-Click)
- Generate for all sections in a project at once
- Useful for completed materials
- Higher upfront cost but comprehensive coverage
- Shows progress dialog during generation

## Cost Optimization

### Token Usage
- **Rolling context**: ~800 tokens per section (using fast model)
- **Study notes**: ~2000 tokens per section (using quality model)

### Recommendations
- Use `gpt-4o-mini` for rolling context (fast, cheap, good enough)
- Use `gpt-4o` or better for study notes (quality matters)
- Generate in batch mode overnight for large projects
- Rolling context is generated sequentially (each depends on previous)
- Study notes can be parallelized (after rolling context exists)

## Integration Points

### Future UI Integration (TODO)

1. **Project View Page**
   - "Generate Study Notes" button (batch mode)
   - Progress dialog showing: "Phase 1: Generating context..." → "Phase 2: Generating notes..."
   - View generated study notes in new tab/page
   - Export to markdown file

2. **Section View Page**
   - "Generate Study Notes for Section" button (single section mode)
   - View/edit study notes inline
   - Indicator showing if rolling context exists

3. **PECS Learning Page** (Optional)
   - Optionally show rolling context summary at top
   - "View Previous Sections Summary" collapsible
   - Helps students understand where they are in the narrative

## Testing

### Test Coverage TODO

1. **Unit Tests**
   - `test_rolling_context_service.py`
     - Test rolling summary generation
     - Test batch generation
     - Test study notes generation
     - Test error handling

2. **Integration Tests**
   - Test full pipeline: upload content → generate rolling context → generate study notes
   - Test with PECS data included
   - Test without PECS data

3. **Database Tests**
   - Test migration script
   - Test column defaults
   - Test null handling

## Backward Compatibility

- ✅ All new fields are nullable (won't break existing data)
- ✅ Rolling context is optional (works without it)
- ✅ Study notes are optional (works without them)
- ✅ Existing PECS workflow unchanged
- ✅ Migration script provided for existing databases
- ✅ New features are additive only

## Design Decisions

### Why Rolling Context at Section Level?
- **Alternative considered**: Store at Project level
- **Decision**: Section level
- **Reason**: Each section needs its own cumulative summary. Storing at section level makes it easier to regenerate individual sections and maintain consistency.

### Why Not Automatic Generation?
- **Decision**: On-demand and batch modes, not automatic
- **Reason**:
  - Cost control (LLM API calls)
  - User control (when to generate)
  - Flexibility (regenerate anytime)

### Why Two Models?
- **Decision**: Fast model for rolling context, quality model for study notes
- **Reason**:
  - Rolling context needs consistency and speed
  - Study notes need quality and creativity
  - Cost optimization

## Original Script Comparison

### What Was Adapted

| Original Script | PECS Integration |
|----------------|------------------|
| Single document input | Per-section generation |
| Flat map-reduce | Sequential rolling summaries |
| Command-line tool | Service module |
| Cache files | Database fields |
| Hardcoded models | Configurable models |
| Summary focus | Study notes focus (diagrams, connections) |

### What Was Preserved

✅ Rolling window context concept
✅ Map-reduce pattern (available for book-wide notes)
✅ Consistency/refinement phase
✅ Concise summary generation
✅ Study notes philosophy (diagrams > summaries)

## Future Enhancements

### Short Term
- [ ] UI integration (buttons, progress dialogs, view pages)
- [ ] Comprehensive test suite
- [ ] Book-wide combined study notes export

### Medium Term
- [ ] Parallel generation for study notes (after rolling context exists)
- [ ] Caching and incremental updates
- [ ] User-editable study notes
- [ ] Study notes versioning

### Long Term
- [ ] AI-suggested connections between sections
- [ ] Concept graph visualization
- [ ] Smart regeneration (detect section changes)
- [ ] Export to various formats (PDF, Anki, notion)

## Troubleshooting

### Progress Bar Not Updating

**Problem**: Progress bar shows 0% for a long time then jumps to 100%

**Solution**: This was fixed in v1.1. Make sure you have the latest version:
- Run `git pull` to get the latest code
- Generation now runs in background with real-time updates
- Progress updates every 100ms
- UI stays responsive during generation

### LiteLLM Provider Errors

**Problem**: Getting errors with non-OpenAI providers

**Solutions**:
1. Check API key is set correctly: `echo $ANTHROPIC_API_KEY`
2. Verify model name is correct for your provider
3. Enable debug mode: `export LITELLM_VERBOSE=true`
4. Check [LiteLLM docs](https://docs.litellm.ai/docs/providers) for provider-specific setup

### Rolling Context Too Long
- Check `ROLLING_CONTEXT_MAX_CHARS` setting
- Regenerate with fresh prompt emphasizing conciseness
- Review prompt template in `prompts.yaml`

### Study Notes Quality Issues
- Try better model (`export LLM_MODEL_QUALITY=gpt-4o`)
- Include PECS data (complete Prime, Engage, Challenge phases first)
- Check rolling context exists (generate if missing)

### Migration Fails
- Backup database first: `cp data/pecs.db data/pecs.db.backup`
- Check database permissions
- Run migration manually:
  ```sql
  ALTER TABLE sections ADD COLUMN rolling_summary TEXT;
  ALTER TABLE sections ADD COLUMN study_notes TEXT;
  ```

## Credits

Adapted from the original document summarizer script's rolling window context approach. The key innovation was the "summary so far" concept that maintains narrative continuity across chunks, which translates perfectly to PECS's section-based learning flow.

---

**Status**: ✅ Core implementation complete
**Next Steps**: UI integration, testing, documentation
