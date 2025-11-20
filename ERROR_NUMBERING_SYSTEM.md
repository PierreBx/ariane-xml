# Ariane-XML Unified Error Numbering System

## Overview

Ariane-XML uses a unified error numbering system inspired by Oracle's error code design. Every error, warning, and success condition is identified by a unique code that enables:

- **Precise error identification** across all documentation and support channels
- **Internationalization** (error codes remain constant across languages)
- **Automated error tracking** and analysis
- **Consistent error handling** across C++ and Python components
- **Easy searchability** in logs and documentation

## Error Code Format

### Structure: `ARX-CCNNNN`

- **ARX** = Ariane-Xml prefix (identifies errors from ariane-xml)
- **CC** = Category code (2 digits, range: 00-99)
- **NNNN** = Specific error number (4 digits, range: 0000-9999)

### Severity Prefix

Errors include a severity prefix for better classification:

| Prefix | Severity | Description | Exit Code |
|--------|----------|-------------|-----------|
| *(none)* | Success | Normal completion (ARX-000000 only) | 0 |
| **E-** | Error | Fatal errors that stop execution | 1 |
| **W-** | Warning | Non-fatal issues, execution continues | 0 |
| **I-** | Info | Informational messages | 0 |

### Examples

- `ARX-000000` - Success (no errors)
- `E-ARX-010001` - Error: Missing SELECT keyword
- `W-ARX-800001` - Warning: Deprecated syntax used
- `I-ARX-850001` - Info: Query statistics

## Category Ranges

### Core Categories (00-19)

| Category | Range | Description |
|----------|-------|-------------|
| **00** | ARX-000000 to ARX-009999 | Success & general parse errors |
| **01** | ARX-010000 to ARX-019999 | SELECT clause errors |
| **02** | ARX-020000 to ARX-029999 | FROM clause errors |
| **03** | ARX-030000 to ARX-039999 | WHERE clause errors |
| **04** | ARX-040000 to ARX-049999 | FOR clause errors (DSN mode) |
| **05** | ARX-050000 to ARX-059999 | XML structure errors |
| **06** | ARX-060000 to ARX-069999 | DSN format errors (SIRET, NIR, dates) |
| **07** | ARX-070000 to ARX-079999 | Schema validation errors |
| **08** | ARX-080000 to ARX-089999 | Field validation errors |
| **09** | ARX-090000 to ARX-099999 | Data integrity errors |
| **10** | ARX-100000 to ARX-109999 | File operations errors |
| **11** | ARX-110000 to ARX-119999 | Memory/resource errors |
| **12** | ARX-120000 to ARX-129999 | Processing errors |
| **13** | ARX-130000 to ARX-139999 | Timeout errors |
| **14** | ARX-140000 to ARX-149999 | Output errors |
| **15** | ARX-150000 to ARX-159999 | Encryption errors |
| **16** | ARX-160000 to ARX-169999 | Decryption errors |
| **17** | ARX-170000 to ARX-179999 | Key management errors |
| **18** | ARX-180000 to ARX-189999 | Certificate errors |
| **19** | ARX-190000 to ARX-199999 | Access control errors |

### Module Categories (20-39)

| Category | Range | Description |
|----------|-------|-------------|
| **20** | ARX-200000 to ARX-209999 | Kernel/CLI errors |
| **21** | ARX-210000 to ARX-219999 | Jupyter integration errors |
| **22** | ARX-220000 to ARX-229999 | DSN mode errors |
| **23** | ARX-230000 to ARX-239999 | Aggregation function errors |
| **24-39** | ARX-240000 to ARX-399999 | Reserved for future features |

### System Categories (40-49)

| Category | Range | Description |
|----------|-------|-------------|
| **40** | ARX-400000 to ARX-409999 | Configuration errors |
| **41** | ARX-410000 to ARX-419999 | Environment errors |
| **42** | ARX-420000 to ARX-429999 | Dependency errors |
| **43** | ARX-430000 to ARX-439999 | System resource errors |
| **44-49** | ARX-440000 to ARX-499999 | Reserved |

### Special Categories (80-99)

| Category | Range | Description |
|----------|-------|-------------|
| **80-84** | ARX-800000 to ARX-849999 | Warnings |
| **85-89** | ARX-850000 to ARX-899999 | Informational messages |
| **90-94** | ARX-900000 to ARX-949999 | Debug/internal errors |
| **95-99** | ARX-950000 to ARX-999999 | Reserved |

## Usage Examples

### C++ Example

```cpp
#include "error/error_codes.h"

using namespace ariane_xml;

try {
    // Success case
    auto result = executeQuery(query);
    std::cout << ARX_SUCCESS().getFullMessage() << std::endl;
    // Output: ARX-000000: Success

} catch (const ArianeError& e) {
    std::cerr << e.getFullMessage() << std::endl;
    return e.getExitCode();
}

// Creating specific errors
throw ARX_ERROR(SELECT_CLAUSE, ErrorCodes::SELECT_MISSING_KEYWORD,
                "Missing SELECT keyword");
// Output: E-ARX-010001: Missing SELECT keyword

// Creating warnings
throw ARX_WARNING(WARNINGS, ErrorCodes::WARN_DEPRECATED_SYNTAX,
                  "Deprecated syntax used");
// Output: W-ARX-800001: Deprecated syntax used

// Error with context
auto error = ARX_ERROR(FROM_CLAUSE, ErrorCodes::FROM_FILE_NOT_FOUND,
                       "File not found");
error.setPath("/path/to/file.xml");
error.setLine(42);
throw error;
// Output: E-ARX-020002: File not found (line 42) [/path/to/file.xml]
```

### Python Example

```python
from ariane_xml_jupyter_kernel.error_codes import (
    ArianeError, ErrorCategory, ErrorCodes, success, error, warning
)

# Success case
result = ArianeError.success("Query executed successfully")
print(result.get_full_message())
# Output: ARX-000000: Query executed successfully

# Creating errors
err = error(
    ErrorCategory.SELECT_CLAUSE,
    ErrorCodes.SELECT_MISSING_KEYWORD,
    "Missing SELECT keyword"
)
print(err.get_full_message())
# Output: E-ARX-010001: Missing SELECT keyword

# Creating warnings
warn = warning(
    ErrorCategory.WARNINGS,
    ErrorCodes.WARN_DEPRECATED_SYNTAX,
    "Deprecated syntax used"
)
print(warn.get_full_message())
# Output: W-ARX-800001: Deprecated syntax used

# Error with context
err = error(
    ErrorCategory.FROM_CLAUSE,
    ErrorCodes.FROM_FILE_NOT_FOUND,
    "File not found",
    path="/path/to/file.xml",
    line=42
)
print(err.get_full_message())
# Output: E-ARX-020002: File not found (line 42) [/path/to/file.xml]

# Get appropriate exit code
exit_code = err.get_exit_code()  # Returns 1 for errors, 0 for warnings
```

### Command Line Examples

```bash
# Success
$ ariane-xml -q "SELECT * FROM file.xml"
ARX-000000: Success

# Error
$ ariane-xml -q "COUNT(*) FROM file.xml"
E-ARX-010001: Missing SELECT keyword
💡 Suggestion: Start your query with SELECT followed by field names
📖 Example: SELECT field1, field2 FROM file.xml

# Warning (non-fatal)
$ ariane-xml -q "SELECT * WHERE x='1' FROM file.xml"
W-ARX-800001: Deprecated syntax used (WHERE before FROM)
💡 Suggestion: Place WHERE clause after FROM clause
[Results displayed here...]

# File not found
$ ariane-xml -q "SELECT * FROM missing.xml"
E-ARX-020002: File not found [missing.xml]
💡 Suggestion: Check that the file path is correct and the file exists
📖 Example: SELECT * FROM '/absolute/path/to/file.xml'
```

## Common Error Codes Quick Reference

### Success
- `ARX-000000` - Success (normal completion)

### SELECT Clause (01xxxx)
- `ARX-010001` - Missing SELECT keyword
- `ARX-010003` - COUNT(*) not supported (use COUNT(element))
- `ARX-010011` - Expected field identifier, got number

### FROM Clause (02xxxx)
- `ARX-020001` - Missing FROM keyword
- `ARX-020002` - File not found
- `ARX-020005` - Cannot open file for reading

### WHERE Clause (03xxxx)
- `ARX-030001` - Invalid WHERE condition
- `ARX-030002` - Missing comparison operator
- `ARX-030005` - Unmatched quotes in string literal

### FOR Clause - DSN Mode (04xxxx)
- `ARX-040001` - FOR clause requires DSN mode
- `ARX-040002` - Invalid variable name in FOR clause
- `ARX-040005` - Missing IN keyword in FOR clause

### DSN Format (06xxxx)
- `ARX-060001` - Invalid SIRET number format
- `ARX-060002` - Invalid SIRET checksum
- `ARX-060010` - Invalid NIR number format
- `ARX-060011` - Invalid NIR checksum
- `ARX-060020` - Invalid date format

### File Operations (10xxxx)
- `ARX-100001` - File not found
- `ARX-100002` - Permission denied
- `ARX-100010` - File is empty

### Kernel/CLI (20xxxx)
- `ARX-200001` - Invalid kernel command
- `ARX-200002` - Command execution timeout
- `ARX-200004` - Binary not found

### Warnings (80xxxx)
- `ARX-800001` - Deprecated syntax used
- `ARX-800002` - Performance warning: large dataset
- `ARX-800003` - Schema validation disabled

## Error Catalog

The complete error catalog is maintained in `error_catalog.yaml`. Each error includes:

- **Code**: Unique error identifier (ARX-CCNNNN)
- **Category**: Error category name
- **Severity**: SUCCESS, ERROR, WARNING, or INFO
- **Message**: Short error message
- **Description**: Detailed explanation
- **Suggestion**: How to fix or avoid the error
- **Example**: Example of correct usage

### Example Catalog Entry

```yaml
ARX-010003:
  category: "SELECT Clause"
  severity: ERROR
  message: "COUNT(*) is not supported"
  description: "Aggregate function COUNT(*) cannot be used. You must specify an element name"
  suggestion: "Use COUNT(element_name) instead of COUNT(*)"
  example: "SELECT COUNT(employee) FROM file.xml"
```

## Benefits

### 1. Searchability
Users can search for specific error codes in documentation, forums, and support channels.

### 2. Internationalization
Error codes remain constant across different languages, making them ideal for:
- Multi-language documentation
- International support teams
- Automated error tracking systems

### 3. Categorization
The category code (CC) immediately identifies the subsystem where the error occurred:
- `ARX-01xxxx` → SELECT clause issue
- `ARX-02xxxx` → FROM clause issue
- `ARX-10xxxx` → File operation issue

### 4. Consistency
Unified error handling across:
- C++ backend
- Python kernel
- Jupyter notebook integration
- CLI interface

### 5. Debugging & Support
- Error codes make bug reports more precise
- Support teams can quickly locate relevant documentation
- Developers can track error patterns in logs

### 6. Extensibility
The system supports:
- 100 categories (00-99)
- 10,000 errors per category
- Total capacity: 1,000,000 unique error codes

## Migration Strategy

### Phase 1: Foundation (Current)
✅ Error code enum definitions (C++ and Python)
✅ ArianeError base class implementations
✅ Error catalog YAML structure
✅ Documentation

### Phase 2: Core Errors (Next)
- Replace parsing errors with error codes
- Update validation errors
- Standardize file operation errors

### Phase 3: Module Errors
- Convert execution errors
- Update crypto/security errors
- Standardize kernel/CLI errors

### Phase 4: Enhancement
- Add error enhancement with suggestions
- Implement error logging with codes
- Create error lookup utility
- Update all documentation

### Phase 5: Testing & Deployment
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
    constexpr int SELECT_NEW_ERROR = 15;  // ARX-010015
}
```

**Python:** Add constant to `error_codes.py`
```python
class ErrorCodes:
    SELECT_NEW_ERROR = 15  # ARX-010015
```

### 3. Add to Error Catalog

Update `error_catalog.yaml`:
```yaml
ARX-010015:
  category: "SELECT Clause"
  severity: ERROR
  message: "Your error message"
  description: "Detailed description of the error"
  suggestion: "How to fix it"
  example: "Example of correct usage"
```

### 4. Use in Code

**C++:**
```cpp
throw ARX_ERROR(SELECT_CLAUSE, ErrorCodes::SELECT_NEW_ERROR,
                "Your error message");
```

**Python:**
```python
raise error(ErrorCategory.SELECT_CLAUSE, ErrorCodes.SELECT_NEW_ERROR,
            "Your error message")
```

## Error Lookup Utility

A future enhancement will provide a command-line utility to look up error details:

```bash
$ ariane-xml error ARX-010003

Error Code: ARX-010003
Category: SELECT Clause
Severity: ERROR
Message: COUNT(*) is not supported

Description:
  Aggregate function COUNT(*) cannot be used. You must specify an element name

Suggestion:
  Use COUNT(element_name) instead of COUNT(*)

Example:
  SELECT COUNT(employee) FROM file.xml
```

## References

- Error code definitions: `ariane-xml-c-kernel/include/error/error_codes.h`
- Python error codes: `ariane-xml-jupyter-kernel/ariane_xml_jupyter_kernel/error_codes.py`
- Error catalog: `error_catalog.yaml`
- Oracle error system inspiration: ORA-NNNNN format

## Version History

- **v1.0** (2025-11-20) - Initial unified error numbering system
  - ARX-CCNNNN format
  - 100 categories, 10,000 codes per category
  - Success code: ARX-000000
  - Severity levels: Success, Error, Warning, Info
  - Comprehensive error catalog
