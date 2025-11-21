# Ariane-XML Error System Enhancements (Phase 4)

This guide documents the Phase 4 enhancements to the Ariane-XML unified error numbering system.

## Overview

Phase 4 adds the following enhancements:
1. **Complete Error Catalog** - All error codes documented with suggestions
2. **Error Lookup Utility** - Command-line tool for searching error codes
3. **Error Logging System** - Structured logging with timestamps and colors
4. **Enhanced Error Messages** - Every error includes helpful suggestions

## 1. Error Catalog (error_catalog.yaml)

The error catalog is a comprehensive YAML file containing all Ariane-XML error codes with:
- **Code**: ARX-XXYYY format
- **Category**: Error classification (e.g., "SELECT Clause", "File Operations")
- **Severity**: Success, Error, Warning, or Info
- **Message**: Short description of the error
- **Description**: Detailed explanation
- **Suggestion**: How to fix the error
- **Example**: Code example or command to resolve

### Example Entry:
```yaml
ARX-05001:
  category: "XML Structure"
  severity: Error
  message: "Ambiguous partial path"
  description: "The partial path matches multiple locations in the XML document"
  suggestion: "Use the full path to disambiguate between multiple matches"
  example: "Use 'company.employee.name' instead of '.name'"
```

## 2. Error Lookup Utility

The error lookup utility (`ariane-xml-scripts/error_lookup.py`) allows you to search and view error information from the command line.

### Installation

The utility requires PyYAML:
```bash
pip install pyyaml
```

### Usage

**Look up a specific error code:**
```bash
python ariane-xml-scripts/error_lookup.py ARX-05001
```

**Search by keyword:**
```bash
python ariane-xml-scripts/error_lookup.py --search "duplicate"
```

**List errors by category:**
```bash
python ariane-xml-scripts/error_lookup.py --category "SELECT Clause"
```

**List all categories:**
```bash
python ariane-xml-scripts/error_lookup.py --list-categories
```

**Verbose output (includes examples):**
```bash
python ariane-xml-scripts/error_lookup.py ARX-01004 -v
```

### Output Format

```
======================================================================
Error Code: ARX-05001
Category:   XML Structure
Severity:   Error
======================================================================

Message:
  Ambiguous partial path

Description:
  The partial path matches multiple locations in the XML document

Suggestion:
  Use the full path to disambiguate between multiple matches
```

## 3. Error Logging System

Phase 4 introduces structured error logging with timestamp formatting and colored output.

### C++ Error Logger

Include the error logger header:
```cpp
#include "error/error_logger.h"
```

**Initialize the logger:**
```cpp
using namespace ariane_xml;

// Console only (default)
ErrorLogger::instance().initialize();

// Log to file only
ErrorLogger::instance().initialize(
    ErrorLogger::OutputMode::FILE_ONLY,
    "ariane-xml.log"
);

// Both console and file
ErrorLogger::instance().initialize(
    ErrorLogger::OutputMode::BOTH,
    "ariane-xml.log"
);
```

**Log errors:**
```cpp
// Log an ArianeError
try {
    // ... code that might throw
} catch (const ArianeError& e) {
    LOG_ARIANE_ERROR(e);
    throw;
}

// Log custom messages
LOG_ERROR(ErrorCategory::FILE_OPERATIONS,
          ErrorCodes::FILE_NOT_FOUND,
          "Could not find file: data.xml");

LOG_WARNING(ErrorCategory::SELECT_CLAUSE,
            ErrorCodes::SELECT_DUPLICATE_FIELD,
            "Duplicate field 'name' in SELECT list");

LOG_SUCCESS("Query executed successfully");
```

**Disable colored output:**
```cpp
ErrorLogger::instance().set_colored_output(false);
```

### Python Error Logger

Import the error logger:
```python
from ariane_xml_jupyter_kernel.error_logger import (
    ErrorLogger, OutputMode,
    log_error, log_warning, log_info, log_success
)
```

**Initialize the logger:**
```python
# Console only (default)
logger = ErrorLogger.instance()
logger.initialize()

# Log to file only
logger.initialize(OutputMode.FILE_ONLY, "ariane-xml.log")

# Both console and file
logger.initialize(OutputMode.BOTH, "ariane-xml.log")
```

**Log errors:**
```python
# Log an ArianeError
try:
    # ... code that might raise
except ArianeError as e:
    log_ariane_error(e)
    raise

# Log custom messages
log_error(5, 1, "Ambiguous partial path '.name'")
log_warning(1, 4, "Duplicate field in SELECT list")
log_success("Query executed successfully")
```

### Log Output Format

**Console with colors:**
```
✓ 2025-11-21 10:15:23 ARX-00000 [Success] Query executed successfully
✗ 2025-11-21 10:16:45 ARX-02002 [Error] File not found: data.xml
⚠ 2025-11-21 10:17:12 ARX-01004 [Warning] Duplicate field in SELECT list
ℹ 2025-11-21 10:18:05 ARX-85001 [Info] Processed 1,245 records
```

**File format (no colors):**
```
2025-11-21 10:15:23 ARX-00000 [Success] Query executed successfully
2025-11-21 10:16:45 ARX-02002 [Error] File not found: data.xml
2025-11-21 10:17:12 ARX-01004 [Warning] Duplicate field in SELECT list
2025-11-21 10:18:05 ARX-85001 [Info] Processed 1,245 records
```

## 4. Error Message Enhancements

All error messages now follow a consistent format with helpful suggestions:

```
ARX-05001 [Error] Ambiguous partial path '.' + targetName + ': found at multiple locations:
  - company.employee.name
  - company.department.name
Use full path to disambiguate.
```

### Best Practices

1. **Always log errors** - Use the logging system to track issues
2. **Include context** - Add relevant details to error messages
3. **Look up error codes** - Use the lookup utility when encountering unfamiliar errors
4. **Read suggestions** - Error catalog suggestions help resolve issues quickly
5. **Check examples** - Use -v flag with error lookup for code examples

## 5. Integration Examples

### Full C++ Example
```cpp
#include "error/error_codes.h"
#include "error/error_logger.h"

int main() {
    using namespace ariane_xml;

    // Initialize logger
    ErrorLogger::instance().initialize(
        ErrorLogger::OutputMode::BOTH,
        "/var/log/ariane-xml.log"
    );

    try {
        // Your code here
        throw ARX_ERROR(ErrorCategory::XML_STRUCTURE,
                       ErrorCodes::XML_AMBIGUOUS_PARTIAL_PATH,
                       "Path '.name' matches multiple locations");
    } catch (const ArianeError& e) {
        LOG_ARIANE_ERROR(e);
        std::cerr << "Error: " << e.getFullMessage() << std::endl;
        return 1;
    }

    LOG_SUCCESS("Application completed successfully");
    return 0;
}
```

### Full Python Example
```python
from ariane_xml_jupyter_kernel.error_codes import ArianeError, ErrorSeverity
from ariane_xml_jupyter_kernel.error_logger import ErrorLogger, OutputMode, log_ariane_error

def main():
    # Initialize logger
    logger = ErrorLogger.instance()
    logger.initialize(OutputMode.BOTH, "/var/log/ariane-xml.log")

    try:
        # Your code here
        raise ArianeError(5, 1, ErrorSeverity.ERROR,
                         "Path '.name' matches multiple locations")
    except ArianeError as e:
        log_ariane_error(e)
        print(f"Error: {e.get_full_message()}", file=sys.stderr)
        return 1

    log_success("Application completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## 6. Migration from Phase 3

If you're upgrading from Phase 3, no code changes are required! The enhancements are additive:

- **Error codes remain the same** - ARX-XXYYY format unchanged
- **ArianeError API unchanged** - Existing code continues to work
- **Logging is optional** - You can enable it gradually
- **Lookup utility is standalone** - Use it independently of your code

## 7. Error Categories Reference

| Category | Code Range | Description |
|----------|------------|-------------|
| Success & General | ARX-00xxx | General errors and success |
| SELECT Clause | ARX-01xxx | SELECT clause parsing errors |
| FROM Clause | ARX-02xxx | FROM clause and file path errors |
| WHERE Clause | ARX-03xxx | WHERE condition errors |
| FOR Clause | ARX-04xxx | FOR loop errors (DSN mode) |
| XML Structure | ARX-05xxx | XML document structure errors |
| DSN Format | ARX-06xxx | DSN data format validation errors |
| Schema Validation | ARX-07xxx | Schema loading and validation |
| File Operations | ARX-10xxx | File I/O errors |
| Processing | ARX-12xxx | Data processing errors |
| Kernel/CLI | ARX-20xxx | Jupyter kernel and CLI errors |
| DSN Mode Syntax | ARX-22xxx | DSN mode syntax errors |
| Warnings | ARX-80xxx | Non-fatal warnings |
| Informational | ARX-85xxx | Informational messages |

## 8. Troubleshooting

**Error lookup doesn't find catalog:**
```bash
# Run from ariane-xml root directory, or specify path:
python ariane-xml-scripts/error_lookup.py --catalog /path/to/error_catalog.yaml ARX-01004
```

**Logger not writing to file:**
- Check file permissions
- Verify directory exists
- Check disk space

**Colors not showing in terminal:**
- Enable colored output: `logger.set_colored_output(true)`
- Some terminals don't support ANSI colors
- Colors are disabled when piping output

## 9. Future Enhancements (Phase 5)

Planned for Phase 5:
- Automated test cases for all error codes
- Error recovery suggestions in error messages
- Interactive error resolution wizard
- Error analytics and statistics
- Integration with external error tracking systems

## Summary

Phase 4 completes the error enhancement system with:
- ✅ Complete error catalog with suggestions
- ✅ Command-line lookup utility
- ✅ Structured logging system (C++ and Python)
- ✅ Colored console output
- ✅ File logging support
- ✅ Comprehensive documentation

All errors now provide helpful suggestions, and the lookup utility makes it easy to find solutions to any error you encounter.
