"""
Unified error numbering system for ariane-xml
Format: ARX-XXYYY where:
  - ARX: Ariane-Xml prefix
  - XX: Category code (00-99)
  - YYY: Specific error number (000-999)

Severity is an attribute of the error, not part of the code.
Display format: ARX-XXYYY [Severity] Message

Example: ARX-01004 [Warning] Bad attribute in SELECT clause
"""

from enum import Enum
from typing import Optional


class ErrorSeverity(Enum):
    """Error severity levels - these are attributes of error codes"""
    SUCCESS = "Success"    # ARX-00000 only - normal completion
    ERROR = "Error"        # Fatal errors that stop execution
    WARNING = "Warning"    # Non-fatal issues, execution continues
    INFO = "Info"          # Informational messages


class ErrorCategory(Enum):
    """Error categories for the unified error numbering system"""
    SUCCESS_GENERAL = 0      # ARX-00xxx - Success and general errors
    SELECT_CLAUSE = 1        # ARX-01xxx - SELECT statement issues
    FROM_CLAUSE = 2          # ARX-02xxx - File paths, table references
    WHERE_CLAUSE = 3         # ARX-03xxx - Filtering, conditions
    FOR_CLAUSE = 4           # ARX-04xxx - DSN mode iteration
    XML_STRUCTURE = 5        # ARX-05xxx - Malformed XML, schema violations
    DSN_FORMAT = 6           # ARX-06xxx - SIRET, NIR, date formats
    SCHEMA_VALIDATION = 7    # ARX-07xxx - Schema loading, version mismatches
    FIELD_VALIDATION = 8     # ARX-08xxx - Unknown fields, type mismatches
    DATA_INTEGRITY = 9       # ARX-09xxx - Checksums, mandatory fields
    FILE_OPERATIONS = 10     # ARX-10xxx - File not found, permissions
    MEMORY_RESOURCES = 11    # ARX-11xxx - Out of memory, buffer overflows
    PROCESSING = 12          # ARX-12xxx - Query execution failures
    TIMEOUT = 13             # ARX-13xxx - Execution timeouts
    OUTPUT = 14              # ARX-14xxx - Result formatting, writing
    ENCRYPTION = 15          # ARX-15xxx - Key generation, encryption
    DECRYPTION = 16          # ARX-16xxx - Decryption, key loading
    KEY_MANAGEMENT = 17      # ARX-17xxx - Key file operations
    CERTIFICATES = 18        # ARX-18xxx - Certificate validation
    ACCESS_CONTROL = 19      # ARX-19xxx - Permissions, authentication
    KERNEL_CLI = 20          # ARX-20xxx - Kernel/CLI errors
    JUPYTER = 21             # ARX-21xxx - Jupyter integration
    DSN_MODE = 22            # ARX-22xxx - DSN mode specific
    AGGREGATION = 23         # ARX-23xxx - Aggregation functions
    CONFIGURATION = 40       # ARX-40xxx - Configuration errors
    ENVIRONMENT = 41         # ARX-41xxx - Environment variables, paths
    DEPENDENCIES = 42        # ARX-42xxx - Missing libraries, versions
    SYSTEM_RESOURCES = 43    # ARX-43xxx - Disk space, handles
    WARNINGS = 80            # ARX-80xxx - General warnings
    INFORMATIONAL = 85       # ARX-85xxx - Informational messages
    DEBUG_INTERNAL = 90      # ARX-90xxx - Debug/internal errors


# Success code constants
SUCCESS_CATEGORY = 0
SUCCESS_CODE = 0
SUCCESS_CODE_STR = "ARX-00000"


class ArianeError(Exception):
    """
    Unified error class for ariane-xml

    Format: ARX-XXYYY where:
      - ARX: Ariane-Xml prefix
      - XX: Category code (00-99)
      - YYY: Specific error number (000-999)

    Severity is an attribute of the error, not part of the code.
    Display format: ARX-XXYYY [Severity] Message

    Example: ARX-01004 [Warning] Bad attribute in SELECT clause
    """

    def __init__(self,
                 category: int,
                 code: int,
                 message: str,
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 context: Optional[str] = None,
                 line: Optional[int] = None,
                 path: Optional[str] = None):
        """
        Create an error

        Args:
            category: Error category (0-99)
            code: Specific error number within the category (0-999)
            message: Human-readable error message
            severity: Error severity (default: ERROR)
            context: Additional context information
            line: Source line number (if applicable)
            path: File path (if applicable)
        """
        self.category = category
        self.code = code
        self.message = message
        self.severity = severity
        self.context = context
        self.line = line
        self.path = path
        self.code_str = self._format_code()
        super().__init__(self.get_full_message())

    @classmethod
    def from_category_enum(cls,
                          category: ErrorCategory,
                          code: int,
                          message: str,
                          severity: ErrorSeverity = ErrorSeverity.ERROR,
                          **kwargs):
        """
        Create an error using ErrorCategory enum

        Args:
            category: ErrorCategory enum value
            code: Error number
            message: Error message
            severity: Error severity
            **kwargs: Additional keyword arguments (context, line, path)

        Returns:
            ArianeError instance
        """
        return cls(category.value, code, message, severity, **kwargs)

    @classmethod
    def success(cls, message: str = "Query executed successfully"):
        """
        Factory method for success code

        Args:
            message: Optional success message

        Returns:
            ArianeError with ARX-00000 code
        """
        return cls(SUCCESS_CATEGORY, SUCCESS_CODE,
                  message, ErrorSeverity.SUCCESS)

    def _format_code(self) -> str:
        """
        Format error code as ARX-XXYYY

        Returns:
            Formatted error code string
        """
        return f"ARX-{self.category:02d}{self.code:03d}"

    def is_success(self) -> bool:
        """
        Check if this represents a success code

        Returns:
            True if code is ARX-00000
        """
        return self.category == SUCCESS_CATEGORY and self.code == SUCCESS_CODE

    def get_severity_string(self) -> str:
        """
        Get severity as string for display

        Returns:
            Severity string ("Success", "Error", "Warning", "Info")
        """
        return self.severity.value

    def get_full_message(self) -> str:
        """
        Get full formatted error message
        Format: ARX-XXYYY [Severity] Message
        Example: ARX-01004 [Warning] Bad attribute in SELECT clause

        Returns:
            Formatted error message
        """
        msg = f"{self.code_str} [{self.get_severity_string()}] {self.message}"

        if self.line is not None:
            msg += f" (line {self.line})"
        if self.path:
            msg += f" [{self.path}]"
        if self.context:
            msg += f"\n  Context: {self.context}"

        return msg

    def get_exit_code(self) -> int:
        """
        Get appropriate exit code for shell (0 for success/warnings, 1 for errors)

        Returns:
            Exit code (0 or 1)
        """
        if self.is_success() or self.severity == ErrorSeverity.WARNING:
            return 0
        return 1


# Common error code constants
class ErrorCodes:
    """Common error code constants"""

    # Success (00xxx)
    SUCCESS = 0

    # General Errors (00xxx)
    GENERAL_UNEXPECTED_END = 1
    GENERAL_INVALID_CHAR = 2
    GENERAL_UNMATCHED_PAREN = 3
    GENERAL_UNEXPECTED_TOKEN = 4
    GENERAL_MISSING_KEYWORD = 5

    # SELECT Clause Errors (01xxx)
    SELECT_MISSING_KEYWORD = 1
    SELECT_INVALID_FIELD = 2
    SELECT_COUNT_STAR_NOT_SUPPORTED = 3
    SELECT_DUPLICATE_FIELD = 4
    SELECT_INVALID_AGGREGATION = 5
    SELECT_EXPECTED_IDENTIFIER = 10
    SELECT_EXPECTED_FIELD_NOT_NUMBER = 11
    SELECT_DISTINCT_NOT_SUPPORTED = 20

    # FROM Clause Errors (02xxx)
    FROM_MISSING_KEYWORD = 1
    FROM_FILE_NOT_FOUND = 2
    FROM_INVALID_PATH = 3
    FROM_PATH_INVALID_CHARS = 4
    FROM_CANNOT_OPEN = 5
    FROM_MULTIPLE_FILES_NOT_SUPPORTED = 10
    FROM_FORMAT_NOT_RECOGNIZED = 20

    # WHERE Clause Errors (03xxx)
    WHERE_INVALID_CONDITION = 1
    WHERE_MISSING_OPERATOR = 2
    WHERE_TYPE_MISMATCH = 3
    WHERE_INVALID_LOGICAL_OP = 4
    WHERE_UNMATCHED_QUOTES = 5

    # FOR Clause Errors (04xxx)
    FOR_REQUIRES_DSN_MODE = 1
    FOR_INVALID_VARIABLE = 2
    FOR_VARIABLE_ALREADY_DEFINED = 3
    FOR_MUST_PRECEDE_WHERE = 4
    FOR_MISSING_IN_KEYWORD = 5

    # XML Structure Errors (05xxx)
    XML_AMBIGUOUS_PARTIAL_PATH = 1
    XML_MALFORMED_DOCUMENT = 2
    XML_INVALID_ELEMENT = 3

    # DSN Format Errors (06xxx)
    DSN_INVALID_SIRET_FORMAT = 1
    DSN_INVALID_SIRET_CHECKSUM = 2
    DSN_INVALID_NIR_FORMAT = 10
    DSN_INVALID_NIR_CHECKSUM = 11
    DSN_INVALID_DATE_FORMAT = 20
    DSN_INVALID_DECIMAL_FORMAT = 30
    DSN_INVALID_NUMERIC_FORMAT = 40

    # Schema Validation (07xxx)
    SCHEMA_FILE_NOT_FOUND = 1
    SCHEMA_VERSION_MISMATCH = 2
    SCHEMA_INVALID_FORMAT = 3
    SCHEMA_LOADING_FAILED = 4
    SCHEMA_INCOMPATIBLE_VERSION = 5
    SCHEMA_PARSE_ERROR = 6
    SCHEMA_NO_ROOT_ELEMENT = 7
    SCHEMA_NO_SCHEMA_ELEMENT = 8

    # File Operations (10xxx)
    FILE_NOT_FOUND = 1
    FILE_PERMISSION_DENIED = 2
    FILE_ALREADY_EXISTS = 3
    FILE_DIR_NOT_FOUND = 4
    FILE_CANNOT_CREATE_DIR = 5
    FILE_EMPTY = 10
    FILE_TOO_LARGE = 11
    FILE_XML_LOAD_FAILED = 20
    FILE_XML_PARSE_ERROR = 21

    # Processing Errors (12xxx)
    PROCESSING_INVALID_NUMBER = 1
    PROCESSING_NUMBER_OUT_OF_RANGE = 2
    PROCESSING_VALUE_MUST_BE_NON_NEGATIVE = 3

    # Kernel/CLI Errors (20xxx)
    KERNEL_INVALID_COMMAND = 1
    KERNEL_EXECUTION_TIMEOUT = 2
    KERNEL_SUBPROCESS_FAILED = 3
    KERNEL_BINARY_NOT_FOUND = 4
    KERNEL_INVALID_ARGUMENTS = 5

    # DSN Mode Syntax Errors (22xxx)
    DSN_LEADING_DOT_NOT_ALLOWED = 1
    DSN_ONLY_SHORTCUT_FORMAT = 2
    DSN_INVALID_FIELD_FORMAT = 3

    # Warnings (80xxx)
    WARN_DEPRECATED_SYNTAX = 1
    WARN_PERFORMANCE_LARGE_DATASET = 2
    WARN_SCHEMA_VALIDATION_DISABLED = 3
    WARN_MISSING_OPTIONAL_FIELD = 10


# Convenience functions for creating common errors
def success(message: str = "Query executed successfully") -> ArianeError:
    """Create a success code"""
    return ArianeError.success(message)


def error(category: int, code: int, message: str, **kwargs) -> ArianeError:
    """
    Create an error

    Args:
        category: Error category (0-99) or ErrorCategory enum
        code: Error code (0-999)
        message: Error message
        **kwargs: Additional arguments (context, line, path)

    Returns:
        ArianeError instance
    """
    if isinstance(category, ErrorCategory):
        category = category.value
    return ArianeError(category, code, message, ErrorSeverity.ERROR, **kwargs)


def warning(category: int, code: int, message: str, **kwargs) -> ArianeError:
    """
    Create a warning

    Args:
        category: Error category (0-99) or ErrorCategory enum
        code: Error code (0-999)
        message: Warning message
        **kwargs: Additional arguments (context, line, path)

    Returns:
        ArianeError instance
    """
    if isinstance(category, ErrorCategory):
        category = category.value
    return ArianeError(category, code, message, ErrorSeverity.WARNING, **kwargs)


def info(category: int, code: int, message: str, **kwargs) -> ArianeError:
    """
    Create an informational message

    Args:
        category: Error category (0-99) or ErrorCategory enum
        code: Error code (0-999)
        message: Info message
        **kwargs: Additional arguments (context, line, path)

    Returns:
        ArianeError instance
    """
    if isinstance(category, ErrorCategory):
        category = category.value
    return ArianeError(category, code, message, ErrorSeverity.INFO, **kwargs)
