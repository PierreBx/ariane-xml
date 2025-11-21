# Migration Guide: Unified Error Numbering System

This guide helps you migrate to Ariane-XML's new unified error numbering system (ARX-XXYYY format).

## Executive Summary

✅ **Good News:** The migration is **100% backward compatible**!
✅ **No Code Changes Required** for existing applications
✅ **Optional Enhancements** available when you're ready

## What Changed?

### Before (Old System)
```cpp
// C++
throw std::runtime_error("Missing SELECT keyword");
throw ParseError("Invalid field identifier");

// Python
raise RuntimeError("File not found")
```

### After (New System)
```cpp
// C++
throw ARX_ERROR(ErrorCategory::SELECT_CLAUSE,
                ErrorCodes::SELECT_MISSING_KEYWORD,
                "Missing SELECT keyword");
// Outputs: ARX-01001 [Error] Missing SELECT keyword

// Python
raise ArianeError(1, 1, ErrorSeverity.ERROR, "Missing SELECT keyword")
# Outputs: ARX-01001 [Error] Missing SELECT keyword
```

## For End Users

### What You'll Notice

**Error messages now include error codes:**

```
Before: Error: File not found: data.xml
After:  ARX-10001 [Error] File not found: data.xml
```

**Benefits for you:**
1. **Look up errors easily:** `python ariane-xml-scripts/error_lookup.py ARX-10001`
2. **Search documentation:** Error codes are consistent across all docs
3. **Get help faster:** Report error code instead of full message
4. **Find solutions:** Every error has a suggestion in the catalog

### No Action Required

Your existing:
- ✅ Queries continue to work unchanged
- ✅ Scripts continue to work unchanged
- ✅ Notebooks continue to work unchanged
- ✅ Error handling patterns still work (regex still matches)

### Optional: Use the Error Lookup Tool

When you encounter an error, look it up:

```bash
# Look up an error code
python ariane-xml-scripts/error_lookup.py ARX-10001

# Search for errors about a topic
python ariane-xml-scripts/error_lookup.py --search "file not found"

# List all errors in a category
python ariane-xml-scripts/error_lookup.py --category "File Operations"
```

## For Application Developers (C++)

### Backward Compatibility

The old `ParseError` type still works:

```cpp
// Still works! ParseError is an alias for ArianeError
try {
    parser.parse(query);
} catch (const ParseError& e) {
    std::cerr << "Parse error: " << e.what() << std::endl;
}

// Also works with new type
try {
    parser.parse(query);
} catch (const ArianeError& e) {
    std::cerr << "Error: " << e.getFullMessage() << std::endl;
}
```

### Migration Path (Optional)

**Option 1: No Changes (Recommended Initially)**
- Keep your existing `catch (const ParseError&)` blocks
- Everything continues to work

**Option 2: Update to ArianeError (When Ready)**
```cpp
// Before
catch (const ParseError& e) {
    std::cerr << "Parse error: " << e.what() << std::endl;
}

// After (optional)
catch (const ArianeError& e) {
    std::cerr << "Error: " << e.getFullMessage() << std::endl;
    // Now you get: "ARX-01001 [Error] Missing SELECT keyword"
}
```

**Option 3: Add Error Logging (When Ready)**
```cpp
#include "error/error_logger.h"

// Initialize once at startup
ErrorLogger::instance().initialize(
    ErrorLogger::OutputMode::BOTH,
    "/var/log/ariane-xml.log"
);

// In your catch blocks
catch (const ArianeError& e) {
    LOG_ARIANE_ERROR(e);  // Logs with timestamp and color
    throw; // Re-throw if needed
}
```

### If You Were Throwing std::runtime_error

**Before:**
```cpp
if (!file_exists) {
    throw std::runtime_error("File not found: " + filename);
}
```

**After (recommended):**
```cpp
#include "error/error_codes.h"

if (!file_exists) {
    throw ARX_ERROR(ErrorCategory::FILE_OPERATIONS,
                   ErrorCodes::FILE_NOT_FOUND,
                   "File not found: " + filename);
}
```

**Why change?**
- Consistent error codes across the codebase
- Automatic categorization and severity
- Better error tracking and logging
- Helpful suggestions in error catalog

## For Application Developers (Python)

### Backward Compatibility

Your existing exception handling still works:

```python
# Still works!
try:
    kernel.execute(query)
except RuntimeError as e:
    print(f"Error: {e}")

# Also works with new type
try:
    kernel.execute(query)
except ArianeError as e:
    print(f"Error: {e.get_full_message()}")
```

### Migration Path (Optional)

**Option 1: No Changes (Recommended Initially)**
- Keep your existing exception handlers
- Everything continues to work

**Option 2: Update to ArianeError (When Ready)**
```python
from ariane_xml_jupyter_kernel.error_codes import ArianeError

# Before
except RuntimeError as e:
    print(f"Error: {e}")

# After (optional)
except ArianeError as e:
    print(f"Error: {e.get_full_message()}")
    # Now you get: "ARX-01001 [Error] Missing SELECT keyword"
```

**Option 3: Add Error Logging (When Ready)**
```python
from ariane_xml_jupyter_kernel.error_logger import (
    ErrorLogger, OutputMode, log_ariane_error
)

# Initialize once at startup
logger = ErrorLogger.instance()
logger.initialize(OutputMode.BOTH, "/var/log/ariane-xml.log")

# In your except blocks
except ArianeError as e:
    log_ariane_error(e)  # Logs with timestamp and color
    raise  # Re-raise if needed
```

### If You Were Raising RuntimeError

**Before:**
```python
if not file_exists:
    raise RuntimeError(f"File not found: {filename}")
```

**After (recommended):**
```python
from ariane_xml_jupyter_kernel.error_codes import (
    ArianeError, ErrorSeverity
)

if not file_exists:
    raise ArianeError(
        category=10,  # FILE_OPERATIONS
        code=1,       # FILE_NOT_FOUND
        severity=ErrorSeverity.ERROR,
        message=f"File not found: {filename}"
    )
```

**Why change?**
- Consistent error codes across the codebase
- Better integration with error catalog
- Helpful suggestions available
- Better error tracking

## For Test Writers

### Existing Tests Should Work

Most tests check for the word "Error" in output, which still works:

```bash
# Before: matches "Error: File not found"
# After:  matches "ARX-10001 [Error] File not found"
run_test "TEST-001" "..." "..." "Error"
```

### Update Tests to Check Error Codes (Optional)

For more precise testing:

```bash
# Check for specific error code
run_test "TEST-001" \
    "Missing SELECT keyword" \
    "INVALID QUERY" \
    "ARX-01001"

# Check for error category (SELECT clause errors)
run_test "TEST-002" \
    "SELECT clause error" \
    "SELECT FROM file.xml" \
    "ARX-01"
```

### Python Test Updates (Optional)

```python
# Before
def test_file_not_found():
    with pytest.raises(RuntimeError, match="File not found"):
        load_file("nonexistent.xml")

# After (more precise)
def test_file_not_found():
    with pytest.raises(ArianeError, match="ARX-10001"):
        load_file("nonexistent.xml")
```

## Migration Timeline (Suggested)

### Phase 1: Observe (Week 1-2)
- ✅ Update to new version
- ✅ Run existing tests (should all pass)
- ✅ Monitor application logs
- ✅ Use error lookup tool when issues arise

### Phase 2: Learn (Week 3-4)
- 📖 Read ERROR_ENHANCEMENTS_GUIDE.md
- 🔍 Try the error lookup utility
- 📝 Familiarize team with error categories
- 💡 Identify errors that occur frequently

### Phase 3: Enhance (Month 2)
- 📊 Enable error logging in development
- 🔄 Update catch blocks to use ArianeError (optional)
- ✏️ Update tests to check error codes (optional)
- 📚 Update internal documentation

### Phase 4: Optimize (Month 3+)
- 🎯 Add error logging in production
- 📈 Analyze error patterns from logs
- 🛠️ Use error suggestions to improve UX
- 📊 Track error rates by category

## Troubleshooting Migration Issues

### Issue: "ParseError not found"

**Cause:** Header not included
**Solution:**
```cpp
#include "parser/parser.h"  // ParseError defined here
```

### Issue: "ArianeError not found"

**Cause:** Header not included
**Solution:**
```cpp
#include "error/error_codes.h"
```

### Issue: Tests failing with error format

**Cause:** Test expects exact old error format
**Solution:** Update regex to match either format:
```bash
# Before: "Error: File not found"
# After:  "Error|ARX-.*File not found"
"Error.*File not found"  # Matches both!
```

### Issue: Can't find error_lookup.py

**Cause:** Running from wrong directory
**Solution:**
```bash
# Run from project root
cd /path/to/ariane-xml
python ariane-xml-scripts/error_lookup.py ARX-01001

# Or specify catalog path
python error_lookup.py --catalog /path/to/error_catalog.yaml ARX-01001
```

### Issue: Error logger not writing to file

**Cause:** File permissions or path
**Solution:**
```cpp
// Check directory exists and is writable
ErrorLogger::instance().initialize(
    ErrorLogger::OutputMode::BOTH,
    "/tmp/ariane-xml.log"  // Use writable location
);
```

## Frequently Asked Questions

### Q: Do I need to change my code?

**A:** No! The system is 100% backward compatible. Changes are optional enhancements.

### Q: Will my existing error handlers break?

**A:** No! `ParseError` still works, and all errors still contain the word "Error".

### Q: Should I update my code immediately?

**A:** No rush! Update when convenient. Start by using the lookup tool, then gradually adopt other features.

### Q: What if I don't want error codes in output?

**A:** Error codes are integral to the system and help with troubleshooting. They don't interfere with parsing or scripts since they're at the start of messages.

### Q: Can I suppress the color output?

**A:** Yes:
```cpp
ErrorLogger::instance().set_colored_output(false);
```
```python
ErrorLogger.instance().set_colored_output(False)
```

### Q: How do I find what error code replaced what message?

**A:** Use the lookup tool:
```bash
python ariane-xml-scripts/error_lookup.py --search "old message text"
```

### Q: Are error codes stable across versions?

**A:** Yes! Error codes are permanent. New codes may be added, but existing codes won't change meaning.

### Q: What if I encounter an error not in the catalog?

**A:** Please report it! We'll add it to the catalog in the next release.

## Getting Help

### Error Lookup
```bash
python ariane-xml-scripts/error_lookup.py ARX-XXXXX
```

### Documentation
- ERROR_NUMBERING_SYSTEM.md - Complete error code reference
- ERROR_ENHANCEMENTS_GUIDE.md - Advanced features guide
- error_catalog.yaml - All error codes with suggestions

### Support
- Check error suggestions in catalog first
- Search logs for error code (e.g., `grep ARX-10001 log.txt`)
- Include error code when reporting issues

## Summary

✅ **Backward Compatible** - No breaking changes
✅ **Optional Migration** - Update at your own pace
✅ **Better Errors** - Codes, categories, and suggestions
✅ **Easy Lookup** - Find solutions quickly
✅ **Enhanced Logging** - Track and analyze errors

Take your time, migrate incrementally, and enjoy better error handling!
