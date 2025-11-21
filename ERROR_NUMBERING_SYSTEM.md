# Ariane-XML Unified Error Numbering System

> **📚 Quick Links:**
> - **Error Lookup Tool:** `python ariane-xml-scripts/error_lookup.py ARX-XXXXX`
> - **Enhancement Guide:** See [ERROR_ENHANCEMENTS_GUIDE.md](ERROR_ENHANCEMENTS_GUIDE.md) for logging, lookup utility, and advanced features
> - **Error Catalog:** [error_catalog.yaml](error_catalog.yaml) - All error codes with suggestions

## Overview

Ariane-XML uses a unified error numbering system inspired by Oracle's error code design. Every error, warning, and success condition is identified by a unique code that enables:

- **Precise error identification** across all documentation and support channels
- **Internationalization** (error codes remain constant across languages)
- **Automated error tracking** and analysis
- **Consistent error handling** across C++ and Python components
- **Easy searchability** in logs and documentation

## Error Code Format

### Structure: `ARX-XXYYY`

- **ARX** = Ariane-Xml prefix (identifies errors from ariane-xml)
- **XX** = Category code (2 digits, range: 00-99)
- **YYY** = Specific error number (3 digits, range: 000-999)

**Total Capacity:** 100 categories × 1,000 codes = **100,000 unique error codes**

### Key Design Principle

**Severity is an attribute, not part of the code.**

Like Oracle's system, each error code (e.g., `ARX-01004`) represents a specific issue, and the severity (Success, Error, Warning, Info) is metadata about that code, not encoded in the identifier itself.

### Display Format

```
ARX-XXYYY [Severity] Message
```

### Examples

- `ARX-00000 [Success] Query executed successfully`
- `ARX-01001 [Error] Missing SELECT keyword`
- `ARX-01004 [Warning] Duplicate field in SELECT list`
- `ARX-02002 [Error] File not found`
- `ARX-80001 [Warning] Deprecated syntax used`
- `ARX-85001 [Info] Query statistics`

## Severity Levels

| Severity | Description | Exit Code | Example |
|----------|-------------|-----------|---------|
| **Success** | Normal completion (ARX-00000 only) | 0 | `ARX-00000 [Success] Query executed successfully` |
| **Error** | Fatal errors that stop execution | 1 | `ARX-01001 [Error] Missing SELECT keyword` |
| **Warning** | Non-fatal issues, execution continues | 0 | `ARX-80001 [Warning] Deprecated syntax used` |
| **Info** | Informational messages | 0 | `ARX-85001 [Info] Query statistics` |

## Category Ranges

### Core Categories (00-19)

| Category | Range | Description |
|----------|-------|-------------|
| **00** | ARX-00000 to ARX-00999 | Success & general parse errors |
| **01** | ARX-01000 to ARX-01999 | SELECT clause errors |
| **02** | ARX-02000 to ARX-02999 | FROM clause errors |
| **03** | ARX-03000 to ARX-03999 | WHERE clause errors |
| **04** | ARX-04000 to ARX-04999 | FOR clause errors (DSN mode) |
| **05** | ARX-05000 to ARX-05999 | XML structure errors |
| **06** | ARX-06000 to ARX-06999 | DSN format errors (SIRET, NIR, dates) |
| **07** | ARX-07000 to ARX-07999 | Schema validation errors |
| **08** | ARX-08000 to ARX-08999 | Field validation errors |
| **09** | ARX-09000 to ARX-09999 | Data integrity errors |
| **10** | ARX-10000 to ARX-10999 | File operations errors |
| **11** | ARX-11000 to ARX-11999 | Memory/resource errors |
| **12** | ARX-12000 to ARX-12999 | Processing errors |
| **13** | ARX-13000 to ARX-13999 | Timeout errors |
| **14** | ARX-14000 to ARX-14999 | Output errors |
| **15** | ARX-15000 to ARX-15999 | Encryption errors |
| **16** | ARX-16000 to ARX-16999 | Decryption errors |
| **17** | ARX-17000 to ARX-17999 | Key management errors |
| **18** | ARX-18000 to ARX-18999 | Certificate errors |
| **19** | ARX-19000 to ARX-19999 | Access control errors |

### Module Categories (20-39)

| Category | Range | Description |
|----------|-------|-------------|
| **20** | ARX-20000 to ARX-20999 | Kernel/CLI errors |
| **21** | ARX-21000 to ARX-21999 | Jupyter integration errors |
| **22** | ARX-22000 to ARX-22999 | DSN mode errors |
| **23** | ARX-23000 to ARX-23999 | Aggregation function errors |
| **24-39** | ARX-24000 to ARX-39999 | Reserved for future features |

### System Categories (40-49)

| Category | Range | Description |
|----------|-------|-------------|
| **40** | ARX-40000 to ARX-40999 | Configuration errors |
| **41** | ARX-41000 to ARX-41999 | Environment errors |
| **42** | ARX-42000 to ARX-42999 | Dependency errors |
| **43** | ARX-43000 to ARX-43999 | System resource errors |
| **44-49** | ARX-44000 to ARX-49999 | Reserved |

### Special Categories (80-99)

| Category | Range | Description |
|----------|-------|-------------|
| **80-84** | ARX-80000 to ARX-84999 | Warnings |
| **85-89** | ARX-85000 to ARX-89999 | Informational messages |
| **90-94** | ARX-90000 to ARX-94999 | Debug/internal errors |
| **95-99** | ARX-95000 to ARX-99999 | Reserved |

## Usage Examples

### C++ Example

```cpp
#include "error/error_codes.h"

using namespace ariane_xml;

try {
    // Success case
    auto result = executeQuery(query);
    std::cout << ARX_SUCCESS().getFullMessage() << std::endl;
    // Output: ARX-00000 [Success] Query executed successfully

} catch (const ArianeError& e) {
    std::cerr << e.getFullMessage() << std::endl;
    return e.getExitCode();
}

// Creating specific errors using category and code numbers
throw ARX_ERROR(ErrorCategory::SELECT_CLAUSE,
                ErrorCodes::SELECT_MISSING_KEYWORD,
                "Missing SELECT keyword");
// Output: ARX-01001 [Error] Missing SELECT keyword

// Creating warnings
throw ARX_WARNING(ErrorCategory::WARNINGS,
                  ErrorCodes::WARN_DEPRECATED_SYNTAX,
                  "Deprecated syntax used");
// Output: ARX-80001 [Warning] Deprecated syntax used

// Error with context
auto error = ARX_ERROR(ErrorCategory::FROM_CLAUSE,
                       ErrorCodes::FROM_FILE_NOT_FOUND,
                       "File not found");
error.setPath("/path/to/file.xml");
error.setLine(42);
throw error;
// Output: ARX-02002 [Error] File not found (line 42) [/path/to/file.xml]
```

### Python Example

```python
from ariane_xml_jupyter_kernel.error_codes import (
    ArianeError, ErrorCategory, ErrorCodes, ErrorSeverity,
    success, error, warning, info
)

# Success case
result = success("Query executed successfully")
print(result.get_full_message())
# Output: ARX-00000 [Success] Query executed successfully

# Creating errors
err = error(
    ErrorCategory.SELECT_CLAUSE.value,
    ErrorCodes.SELECT_MISSING_KEYWORD,
    "Missing SELECT keyword"
)
print(err.get_full_message())
# Output: ARX-01001 [Error] Missing SELECT keyword

# Using convenience function with ErrorCategory enum
err = error(
    ErrorCategory.SELECT_CLAUSE,  # Automatically converts to .value
    ErrorCodes.SELECT_MISSING_KEYWORD,
    "Missing SELECT keyword"
)

# Creating warnings
warn = warning(
    ErrorCategory.WARNINGS,
    ErrorCodes.WARN_DEPRECATED_SYNTAX,
    "Deprecated syntax used"
)
print(warn.get_full_message())
# Output: ARX-80001 [Warning] Deprecated syntax used

# Error with context
err = error(
    ErrorCategory.FROM_CLAUSE,
    ErrorCodes.FROM_FILE_NOT_FOUND,
    "File not found",
    path="/path/to/file.xml",
    line=42
)
print(err.get_full_message())
# Output: ARX-02002 [Error] File not found (line 42) [/path/to/file.xml]

# Get appropriate exit code
exit_code = err.get_exit_code()  # Returns 1 for errors, 0 for warnings
```

### Command Line Examples

```bash
# Success
$ ariane-xml -q "SELECT * FROM file.xml"
ARX-00000 [Success] Query executed successfully

# Error
$ ariane-xml -q "COUNT(*) FROM file.xml"
ARX-01001 [Error] Missing SELECT keyword
💡 Suggestion: Start your query with SELECT followed by field names
📖 Example: SELECT field1, field2 FROM file.xml

# Warning (non-fatal, query continues)
$ ariane-xml -q "SELECT field, field FROM file.xml"
ARX-01004 [Warning] Duplicate field in SELECT list
💡 Suggestion: Remove duplicate field names from your SELECT list
[Results displayed here...]

# File not found
$ ariane-xml -q "SELECT * FROM missing.xml"
ARX-02002 [Error] File not found [missing.xml]
💡 Suggestion: Check that the file path is correct and the file exists
📖 Example: SELECT * FROM '/absolute/path/to/file.xml'
```

## Common Error Codes Quick Reference

### Success
- `ARX-00000` - Success (normal completion)

### General Errors (00xxx)
- `ARX-00001` - Unexpected end of query
- `ARX-00002` - Invalid character in query
- `ARX-00003` - Unmatched parenthesis
- `ARX-00004` - Unexpected token after query
- `ARX-00005` - Missing required keyword

### SELECT Clause (01xxx)
- `ARX-01001` - Missing SELECT keyword
- `ARX-01003` - COUNT(*) not supported (use COUNT(element))
- `ARX-01004` - Duplicate field in SELECT list (Warning)
- `ARX-01011` - Expected field identifier, got number

### FROM Clause (02xxx)
- `ARX-02001` - Missing FROM keyword
- `ARX-02002` - File not found
- `ARX-02005` - Cannot open file for reading

### WHERE Clause (03xxx)
- `ARX-03001` - Invalid WHERE condition
- `ARX-03002` - Missing comparison operator
- `ARX-03005` - Unmatched quotes in string literal

### FOR Clause - DSN Mode (04xxx)
- `ARX-04001` - FOR clause requires DSN mode
- `ARX-04002` - Invalid variable name in FOR clause
- `ARX-04005` - Missing IN keyword in FOR clause

### DSN Format (06xxx)
- `ARX-06001` - Invalid SIRET number format
- `ARX-06002` - Invalid SIRET checksum
- `ARX-06010` - Invalid NIR number format
- `ARX-06011` - Invalid NIR checksum
- `ARX-06020` - Invalid date format

### File Operations (10xxx)
- `ARX-10001` - File not found
- `ARX-10002` - Permission denied
- `ARX-10010` - File is empty

### Kernel/CLI (20xxx)
- `ARX-20001` - Invalid kernel command
- `ARX-20002` - Command execution timeout
- `ARX-20004` - Binary not found

### Warnings (80xxx)
- `ARX-80001` - Deprecated syntax used
- `ARX-80002` - Performance warning: large dataset
- `ARX-80003` - Schema validation disabled

### Informational (85xxx)
- `ARX-85001` - Query statistics

## Error Catalog

The complete error catalog is maintained in `error_catalog.yaml`. Each error includes:

- **Code**: Unique error identifier (ARX-XXYYY)
- **Category**: Error category name
- **Severity**: Success, Error, Warning, or Info
- **Message**: Short error message
- **Description**: Detailed explanation
- **Suggestion**: How to fix or avoid the error
- **Example**: Example of correct usage

### Example Catalog Entry

```yaml
ARX-01003:
  category: "SELECT Clause"
  severity: Error
  message: "COUNT(*) is not supported"
  description: "Aggregate function COUNT(*) cannot be used. You must specify an element name"
  suggestion: "Use COUNT(element_name) instead of COUNT(*)"
  example: "SELECT COUNT(employee) FROM file.xml"
```

## Benefits

### 1. Oracle-Like Simplicity
Each error has one code. Severity is metadata, not identity. This matches Oracle's proven design:
- Oracle: `ORA-00942` - table or view does not exist (it's an ERROR by definition)
- Ariane-XML: `ARX-02002` - File not found (it's an ERROR by definition)

### 2. Fixed-Width Format
All codes are exactly 10 characters: `ARX-01004`
- Easy to parse
- Clean in logs
- Simple to search

### 3. Searchability
Users can search for specific error codes in documentation, forums, and support channels:
```bash
grep "ARX-02002" logfile
grep "\[Error\]" logfile
grep "\[Warning\]" logfile
```

### 4. Internationalization
Error codes remain constant across different languages:
- English: `ARX-01004 [Warning] Duplicate field in SELECT list`
- French: `ARX-01004 [Avertissement] Champ dupliqué dans la liste SELECT`
- The code `ARX-01004` never changes!

### 5. Catalog-Driven Flexibility
Severity is defined in the catalog, not the code:
```yaml
ARX-01004:
  severity: Warning  # Can change this without touching any code!
```

If you later decide `ARX-01004` should be an Error instead, just update the catalog.

### 6. Categorization
The category code (XX) immediately identifies the subsystem:
- `ARX-01xxx` → SELECT clause issue
- `ARX-02xxx` → FROM clause issue
- `ARX-10xxx` → File operation issue
- `ARX-80xxx` → Warning

### 7. Consistency
Unified error handling across:
- C++ backend
- Python kernel
- Jupyter notebook integration
- CLI interface

### 8. Debugging & Support
- Error codes make bug reports more precise
- Support teams can quickly locate relevant documentation
- Developers can track error patterns in logs
- No ambiguity: one code = one specific problem

### 9. Extensibility
The system supports:
- 100 categories (00-99)
- 1,000 errors per category (000-999)
- Total capacity: 100,000 unique error codes

For reference:
- Oracle: ~20,000 documented error codes
- PostgreSQL: ~1,000 error codes
- Ariane-XML capacity: 100,000 codes

## Design Philosophy

### Why Not Encode Severity in the Code?

We considered formats like `ARX-E010001` (severity in code) but chose the simpler `ARX-01001` approach because:

1. **Oracle's Proven Model**: Oracle doesn't encode severity in codes. `ORA-00001` is just `ORA-00001`, and it's always an error.

2. **One Code = One Issue**: Each logical problem has ONE code, not multiple codes for different severities.
   - Better: `ARX-01004` is defined as a Warning in the catalog
   - Not: `ARX-E01004` vs `ARX-W01004` (two codes for same issue)

3. **Flexibility**: Severity can be changed in the catalog without code changes.

4. **Simpler**: Just a number with a prefix. No encoding/decoding logic needed.

5. **Display Flexibility**: The display format can change (colors, languages, formatting) while the code remains constant.

## Migration Strategy

### Phase 1: Foundation (Current) ✅
- Error code enum definitions (C++ and Python)
- ArianeError base class implementations
- Error catalog YAML structure
- Documentation

### Phase 2: Core Errors ✅ COMPLETED
- ✅ Replaced all parsing errors with error codes
- ✅ Updated validation errors
- ✅ Standardized file operation errors
- All parser errors now use ARX-XXYYY format

### Phase 3: Module Errors ✅ COMPLETED
- ✅ Converted execution errors (xml_navigator, xml_loader)
- ✅ Updated schema validation errors (xsd_parser)
- ✅ Standardized file I/O errors
- All module errors now use ARX-XXYYY format

### Phase 4: Enhancement ✅ COMPLETED
- ✅ Added error catalog with suggestions for all codes
- ✅ Implemented error logging system (C++ and Python)
- ✅ Created error lookup utility (ariane-xml-scripts/error_lookup.py)
- ✅ Updated documentation with enhancement guide
- See ERROR_ENHANCEMENTS_GUIDE.md for details

### Phase 5: Testing & Deployment (Next)
- Update test cases
- Backward compatibility layer
- Migration guide for users
- Release notes

## Adding New Errors

### 1. Choose Category and Number

Find the appropriate category for your error:
- Look at existing categories in this document
- Choose the next available number in that category
- Ensure the number doesn't conflict with existing codes

### 2. Add to Error Codes

**C++:** Add constant to `include/error/error_codes.h`
```cpp
namespace ErrorCodes {
    constexpr int SELECT_NEW_ERROR = 15;  // Will be ARX-01015
}
```

**Python:** Add constant to `error_codes.py`
```python
class ErrorCodes:
    SELECT_NEW_ERROR = 15  # Will be ARX-01015
```

### 3. Add to Error Catalog

Update `error_catalog.yaml`:
```yaml
ARX-01015:
  category: "SELECT Clause"
  severity: Error  # or Warning, Info
  message: "Your error message"
  description: "Detailed description of the error"
  suggestion: "How to fix it"
  example: "Example of correct usage"
```

### 4. Use in Code

**C++:**
```cpp
throw ARX_ERROR(ErrorCategory::SELECT_CLAUSE,
                ErrorCodes::SELECT_NEW_ERROR,
                "Your error message");
// Output: ARX-01015 [Error] Your error message
```

**Python:**
```python
raise error(ErrorCategory.SELECT_CLAUSE,
            ErrorCodes.SELECT_NEW_ERROR,
            "Your error message")
# Output: ARX-01015 [Error] Your error message
```

## Error Lookup Utility (Future)

A future enhancement will provide a command-line utility to look up error details:

```bash
$ ariane-xml error ARX-01003

Code: ARX-01003
Category: SELECT Clause
Severity: Error
Message: COUNT(*) is not supported

Description:
  Aggregate function COUNT(*) cannot be used. You must specify an element name

Suggestion:
  Use COUNT(element_name) instead of COUNT(*)

Example:
  SELECT COUNT(employee) FROM file.xml

Documentation:
  https://docs.ariane-xml.org/errors/ARX-01003
```

## Log Examples

### Standard Format
```
2025-11-21 10:15:23 ARX-00000 [Success] Query executed successfully
2025-11-21 10:16:45 ARX-02002 [Error] File not found: data.xml
2025-11-21 10:17:12 ARX-80001 [Warning] Deprecated syntax used
2025-11-21 10:18:05 ARX-85001 [Info] Processed 1,245 records in 0.32s
```

### With Colors (Terminal)
```
✓ ARX-00000 [Success] Query executed successfully
✗ ARX-02002 [Error] File not found: data.xml
⚠ ARX-80001 [Warning] Deprecated syntax used
ℹ ARX-85001 [Info] Processed 1,245 records in 0.32s
```

### Filtering Examples
```bash
# All errors
grep "\[Error\]" logfile

# All warnings
grep "\[Warning\]" logfile

# Specific error code
grep "ARX-02002" logfile

# All FROM clause errors (02xxx)
grep "ARX-02" logfile

# All file operation errors (10xxx)
grep "ARX-10" logfile
```

## References

- C++ error codes: `ariane-xml-c-kernel/include/error/error_codes.h`
- Python error codes: `ariane-xml-jupyter-kernel/ariane_xml_jupyter_kernel/error_codes.py`
- Error catalog: `error_catalog.yaml`
- Oracle error system: ORA-NNNNN format (inspiration)

## Version History

- **v2.0** (2025-11-21) - Refactored to ARX-XXYYY format
  - Simplified from ARX-CCNNNN (4-digit codes) to ARX-XXYYY (3-digit codes)
  - Severity is now an attribute, not encoded in the code
  - Matches Oracle's design philosophy
  - 100,000 code capacity (100 categories × 1,000 codes)
  - Fixed-width 10-character format

- **v1.0** (2025-11-20) - Initial unified error numbering system
  - ARX-CCNNNN format with severity prefix
  - Foundation implementation
