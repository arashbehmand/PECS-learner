# Test Coverage Analysis & Gaps

## Current Test Coverage Status

### ✅ Well Tested
- **`utils/database.py`** - 61% coverage (basic CRUD operations)
  - ✅ Project creation/retrieval
  - ✅ Section operations
  - ✅ Flashcard creation
  - ✅ PECS data updates
  - ⚠️ Missing: Error handling, edge cases, flashcard review algorithms
  
- **`utils/hierarchical_processor.py`** - 89% coverage
  - ✅ Section detection
  - ✅ Section splitting
  - ✅ Custom markers
  - ⚠️ Missing: Edge cases, very large files, empty files

### ❌ Not Tested (0% Coverage)

#### High Priority

1. **`utils/file_converters.py`** (NEW - Critical)
   - ❌ `convert_file_to_text()` - File format conversion
   - ❌ `is_supported_file_type()` - File type validation
   - ❌ `get_file_type_description()` - Helper function
   - **Impact**: EPUB/PDF support is untested
   - **Risk**: Format conversion failures in production

2. **`utils/migration.py`** (Critical for data migration)
   - ❌ `migrate_json_to_database()` - JSON to database migration
   - ❌ Error handling for malformed JSON
   - ❌ Missing field validation
   - **Impact**: Users can't migrate old sessions
   - **Risk**: Data loss during migration

3. **`utils/content_processor.py`** (Core functionality)
   - ❌ `load_text_from_input()` - Text loading
   - ❌ `chunk_text_content()` - Text chunking
   - **Impact**: Basic text processing untested
   - **Risk**: File encoding issues, empty input handling

#### Medium Priority

4. **`utils/database.py`** - Additional edge cases needed
   - ❌ `update_project()` - Project updates
   - ❌ `delete_project()` - Project deletion with cascades
   - ❌ `get_flashcards_for_review()` - Review query logic
   - ❌ Error handling for invalid IDs
   - ❌ Transaction rollback scenarios
   - ❌ Concurrency issues

5. **`utils/models.py`** - Model validation
   - ❌ Model creation validation
   - ❌ Relationship integrity
   - ❌ JSON field validation

#### Low Priority (Legacy/Complex)

6. **`utils/llm_service.py`** - AI integration (requires mocking)
   - ❌ API call mocking
   - ❌ Error handling
   - ❌ Prompt loading
   - **Note**: Requires OpenAI API mocking

7. **`utils/persistence.py`** - Legacy JSON export (still used?)
   - ❌ JSON export/import
   - **Note**: May be deprecated in favor of database

8. **`utils/session_manager.py`** - Legacy session state (still used?)
   - ❌ Session initialization
   - **Note**: May be deprecated

## Recommended Test Files to Create

### Priority 1: Critical New Features

1. **`tests/test_file_converters.py`**
   - Test EPUB/PDF conversion (with mocks)
   - Test file type detection
   - Test error handling (missing library, invalid files)
   - Test empty file handling

2. **`tests/test_migration.py`**
   - Test valid JSON migration
   - Test invalid JSON handling
   - Test missing fields
   - Test PECS data migration
   - Test flashcard migration

3. **`tests/test_content_processor.py`**
   - Test text loading from pasted text
   - Test text loading from files
   - Test encoding handling (UTF-8, errors)
   - Test empty input handling
   - Test chunking with various sizes

### Priority 2: Enhanced Database Tests

4. **`tests/test_database_extended.py`**
   - Test update_project()
   - Test delete_project() with cascades
   - Test get_flashcards_for_review()
   - Test error scenarios (invalid IDs, None inputs)
   - Test transaction handling
   - Test edge cases (empty results, null values)

### Priority 3: Edge Cases & Integration

5. **`tests/test_hierarchical_processor_extended.py`**
   - Test very large files
   - Test empty files
   - Test files with no structure
   - Test overlapping sections
   - Test minimum/maximum size boundaries

## Test Coverage Goals

- **Target**: 80%+ coverage for all critical utilities
- **Current**: ~42% overall
- **Critical Modules**: file_converters, migration, content_processor → 0% → Target 80%+
- **Database**: 61% → Target 85%+
- **Hierarchical Processor**: 89% → Target 95%+

## Notes

- Streamlit components are difficult to test (UI-focused)
- LLM service requires API mocking (use `pytest-mock` or `unittest.mock`)
- File converters require markitdown library or mocking
- Integration tests needed for end-to-end workflows

