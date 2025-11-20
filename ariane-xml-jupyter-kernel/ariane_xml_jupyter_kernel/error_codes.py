"""
Unified error numbering system for ariane-xml
Format: ARX-CCNNNN where:
  - ARX: Ariane-Xml prefix
  - CC: Category code (2 digits)
  - NNNN: Specific error number (4 digits)
"""

from enum import Enum
from typing import Optional


class ErrorCategory(Enum):
    """Error categories for the unified error numbering system"""
    SUCCESS_GENERAL = 0      # ARX-00xxxx - Success and general errors
    SELECT_CLAUSE = 1        # ARX-01xxxx - SELECT statement issues
    FROM_CLAUSE = 2          # ARX-02xxxx - File paths, table references
    WHERE_CLAUSE = 3         # ARX-03xxxx - Filtering, conditions
    FOR_CLAUSE = 4           # ARX-04xxxx - DSN mode iteration
    XML_STRUCTURE = 5        # ARX-05xxxx - Malformed XML, schema violations
    DSN_FORMAT = 6           # ARX-06xxxx - SIRET, NIR, date formats
    SCHEMA_VALIDATION = 7    # ARX-07xxxx - Schema loading, version mismatches
    FIELD_VALIDATION = 8     # ARX-08xxxx - Unknown fields, type mismatches
    DATA_INTEGRITY = 9       # ARX-09xxxx - Checksums, mandatory fields
    FILE_OPERATIONS = 10     # ARX-10xxxx - File not found, permissions
    MEMORY_RESOURCES = 11    # ARX-11xxxx - Out of memory, buffer overflows
    PROCESSING = 12          # ARX-12xxxx - Query execution failures
    TIMEOUT = 13             # ARX-13xxxx - Execution timeouts
    OUTPUT = 14              # ARX-14xxxx - Result formatting, writing
    ENCRYPTION = 15          # ARX-15xxxx - Key generation, encryption
    DECRYPTION = 16          # ARX-16xxxx - Decryption, key loading
    KEY_MANAGEMENT = 17      # ARX-17xxxx - Key file operations
    CERTIFICATES = 18        # ARX-18xxxx - Certificate validation
    ACCESS_CONTROL = 19      # ARX-19xxxx - Permissions, authentication
    KERNEL_CLI = 20          # ARX-20xxxx - Kernel/CLI errors
    JUPYTER = 21             # ARX-21xxxx - Jupyter integration
    DSN_MODE = 22            # ARX-22xxxx - DSN mode specific
    AGGREGATION = 23         # ARX-23xxxx - Aggregation functions
    CONFIGURATION = 40       # ARX-40xxxx - Configuration errors
    ENVIRONMENT = 41         # ARX-41xxxx - Environment variables, paths
    DEPENDENCIES = 42        # ARX-42xxxx - Missing libraries, versions
    SYSTEM_RESOURCES = 43    # ARX-43xxxx - Disk space, handles
    WARNINGS = 80            # ARX-80xxxx - Non-fatal warnings
    INFORMATIONAL = 85       # ARX-85xxxx - Informational messages
    DEBUG_INTERNAL = 90      # ARX-90xxxx - Debug/internal errors


class ErrorSeverity(Enum):
    """Error severity levels"""
    SUCCESS = ""    # ARX-000000 only - normal completion
    ERROR = "E"     # Fatal errors that stop execution
    WARNING = "W"   # Non-fatal issues, execution continues
    INFO = "I"      # Informational messages


# Success code constant
SUCCESS_CODE = 0
SUCCESS_CODE_STR = "ARX-000000"


class ArianeError(Exception):
    """
    Unified error class for ariane-xml

    Format: ARX-CCNNNN where:
      - ARX: Ariane-Xml prefix
      - CC: Category code (2 digits)
      - NNNN: Specific error number (4 digits)

    Example: ARX-010001 = SELECT clause error, missing SELECT keyword
    """

    def __init__(self,
                 category: ErrorCategory,
                 error_number: int,
                 message: str,
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 context: Optional[str] = None,
                 line: Optional[int] = None,
                 path: Optional[str] = None):
        """
        Create an error

        Args:
            category: Error category
            error_number: Specific error number within the category (0-9999)
            message: Human-readable error message
            severity: Error severity (default: ERROR)
            context: Additional context information
            line: Source line number (if applicable)
            path: File path (if applicable)
        """
        self.category = category
        self.error_number = error_number
        self.message = message
        self.severity = severity
        self.context = context
        self.line = line
        self.path = path
        self.code = self._format_code()
        super().__init__(self.get_full_message())

    @classmethod
    def success(cls, message: str = "Success"):
        """
        Factory method for success code

        Args:
            message: Optional success message

        Returns:
            ArianeError with ARX-000000 code
        """
        return cls(ErrorCategory.SUCCESS_GENERAL, SUCCESS_CODE,
                  message, ErrorSeverity.SUCCESS)

    def _format_code(self) -> str:
        """
        Format error code as ARX-CCNNNN

        Returns:
            Formatted error code string
        """
        return f"ARX-{self.category.value:02d}{self.error_number:04d}"

    def is_success(self) -> bool:
        """
        Check if this represents a success code

        Returns:
            True if code is ARX-000000
        """
        return self.code == SUCCESS_CODE_STR

    def get_full_message(self) -> str:
        """
        Get full formatted error message with code and context

        Returns:
            Formatted error message
        """
        prefix = f"{self.severity.value}-" if self.severity.value else ""
        msg = f"{prefix}{self.code}: {self.message}"

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

    # Success (00xxxx)
    SUCCESS = 0

    # SELECT Clause Errors (01xxxx)
    SELECT_MISSING_KEYWORD = 1
    SELECT_INVALID_FIELD = 2
    SELECT_COUNT_STAR_NOT_SUPPORTED = 3
    SELECT_DUPLICATE_FIELD = 4
    SELECT_INVALID_AGGREGATION = 5
    SELECT_EXPECTED_IDENTIFIER = 10
    SELECT_EXPECTED_FIELD_NOT_NUMBER = 11
    SELECT_DISTINCT_NOT_SUPPORTED = 20

    # FROM Clause Errors (02xxxx)
    FROM_MISSING_KEYWORD = 1
    FROM_FILE_NOT_FOUND = 2
    FROM_INVALID_PATH = 3
    FROM_PATH_INVALID_CHARS = 4
    FROM_CANNOT_OPEN = 5
    FROM_MULTIPLE_FILES_NOT_SUPPORTED = 10
    FROM_FORMAT_NOT_RECOGNIZED = 20

    # WHERE Clause Errors (03xxxx)
    WHERE_INVALID_CONDITION = 1
    WHERE_MISSING_OPERATOR = 2
    WHERE_TYPE_MISMATCH = 3
    WHERE_INVALID_LOGICAL_OP = 4
    WHERE_UNMATCHED_QUOTES = 5

    # FOR Clause Errors (04xxxx)
    FOR_REQUIRES_DSN_MODE = 1
    FOR_INVALID_VARIABLE = 2
    FOR_VARIABLE_ALREADY_DEFINED = 3
    FOR_MUST_PRECEDE_WHERE = 4
    FOR_MISSING_IN_KEYWORD = 5

    # DSN Format Errors (06xxxx)
    DSN_INVALID_SIRET_FORMAT = 1
    DSN_INVALID_SIRET_CHECKSUM = 2
    DSN_INVALID_NIR_FORMAT = 10
    DSN_INVALID_NIR_CHECKSUM = 11
    DSN_INVALID_DATE_FORMAT = 20
    DSN_INVALID_DECIMAL_FORMAT = 30
    DSN_INVALID_NUMERIC_FORMAT = 40

    # File Operations (10xxxx)
    FILE_NOT_FOUND = 1
    FILE_PERMISSION_DENIED = 2
    FILE_ALREADY_EXISTS = 3
    FILE_DIR_NOT_FOUND = 4
    FILE_CANNOT_CREATE_DIR = 5
    FILE_EMPTY = 10
    FILE_TOO_LARGE = 11

    # Kernel/CLI Errors (20xxxx)
    KERNEL_INVALID_COMMAND = 1
    KERNEL_EXECUTION_TIMEOUT = 2
    KERNEL_SUBPROCESS_FAILED = 3
    KERNEL_BINARY_NOT_FOUND = 4
    KERNEL_INVALID_ARGUMENTS = 5

    # Warnings (80xxxx)
    WARN_DEPRECATED_SYNTAX = 1
    WARN_PERFORMANCE_LARGE_DATASET = 2
    WARN_SCHEMA_VALIDATION_DISABLED = 3
    WARN_MISSING_OPTIONAL_FIELD = 10


# Convenience functions for creating common errors
def success(message: str = "Success") -> ArianeError:
    """Create a success code"""
    return ArianeError.success(message)


def error(category: ErrorCategory, code: int, message: str,
          **kwargs) -> ArianeError:
    """Create an error"""
    return ArianeError(category, code, message, ErrorSeverity.ERROR, **kwargs)


def warning(category: ErrorCategory, code: int, message: str,
            **kwargs) -> ArianeError:
    """Create a warning"""
    return ArianeError(category, code, message, ErrorSeverity.WARNING, **kwargs)


def info(category: ErrorCategory, code: int, message: str,
         **kwargs) -> ArianeError:
    """Create an informational message"""
    return ArianeError(category, code, message, ErrorSeverity.INFO, **kwargs)
