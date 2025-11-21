#ifndef ARIANE_XML_ERROR_CODES_H
#define ARIANE_XML_ERROR_CODES_H

#include <string>
#include <stdexcept>
#include <sstream>
#include <iomanip>

namespace ariane_xml {

/**
 * Error severity levels
 * These are attributes of error codes, not part of the code itself
 */
enum class ErrorSeverity {
    SUCCESS,   // ARX-00000 only - normal completion
    ERROR,     // Fatal errors that stop execution
    WARNING,   // Non-fatal issues, execution continues
    INFO       // Informational messages
};

/**
 * Error categories for the unified error numbering system
 * Format: ARX-XXYYY where XX is the category code (00-99)
 */
enum class ErrorCategory {
    SUCCESS_GENERAL = 0,      // ARX-00xxx - Success and general errors
    SELECT_CLAUSE = 1,        // ARX-01xxx - SELECT statement issues
    FROM_CLAUSE = 2,          // ARX-02xxx - File paths, table references
    WHERE_CLAUSE = 3,         // ARX-03xxx - Filtering, conditions
    FOR_CLAUSE = 4,           // ARX-04xxx - DSN mode iteration
    XML_STRUCTURE = 5,        // ARX-05xxx - Malformed XML, schema violations
    DSN_FORMAT = 6,           // ARX-06xxx - SIRET, NIR, date formats
    SCHEMA_VALIDATION = 7,    // ARX-07xxx - Schema loading, version mismatches
    FIELD_VALIDATION = 8,     // ARX-08xxx - Unknown fields, type mismatches
    DATA_INTEGRITY = 9,       // ARX-09xxx - Checksums, mandatory fields
    FILE_OPERATIONS = 10,     // ARX-10xxx - File not found, permissions
    MEMORY_RESOURCES = 11,    // ARX-11xxx - Out of memory, buffer overflows
    PROCESSING = 12,          // ARX-12xxx - Query execution failures
    TIMEOUT = 13,             // ARX-13xxx - Execution timeouts
    OUTPUT = 14,              // ARX-14xxx - Result formatting, writing
    ENCRYPTION = 15,          // ARX-15xxx - Key generation, encryption
    DECRYPTION = 16,          // ARX-16xxx - Decryption, key loading
    KEY_MANAGEMENT = 17,      // ARX-17xxx - Key file operations
    CERTIFICATES = 18,        // ARX-18xxx - Certificate validation
    ACCESS_CONTROL = 19,      // ARX-19xxx - Permissions, authentication
    KERNEL_CLI = 20,          // ARX-20xxx - Kernel/CLI errors
    JUPYTER = 21,             // ARX-21xxx - Jupyter integration
    DSN_MODE = 22,            // ARX-22xxx - DSN mode specific
    AGGREGATION = 23,         // ARX-23xxx - Aggregation functions
    CONFIGURATION = 40,       // ARX-40xxx - Configuration errors
    ENVIRONMENT = 41,         // ARX-41xxx - Environment variables, paths
    DEPENDENCIES = 42,        // ARX-42xxx - Missing libraries, versions
    SYSTEM_RESOURCES = 43,    // ARX-43xxx - Disk space, handles
    WARNINGS = 80,            // ARX-80xxx - General warnings
    INFORMATIONAL = 85,       // ARX-85xxx - Informational messages
    DEBUG_INTERNAL = 90       // ARX-90xxx - Debug/internal errors
};

// Success code constant
constexpr int SUCCESS_CATEGORY = 0;
constexpr int SUCCESS_CODE = 0;
constexpr const char* SUCCESS_CODE_STR = "ARX-00000";

/**
 * Convert ErrorSeverity to display string
 */
inline const char* severityToString(ErrorSeverity severity) {
    switch (severity) {
        case ErrorSeverity::SUCCESS:  return "Success";
        case ErrorSeverity::ERROR:    return "Error";
        case ErrorSeverity::WARNING:  return "Warning";
        case ErrorSeverity::INFO:     return "Info";
        default:                      return "Unknown";
    }
}

/**
 * Unified error class for ariane-xml
 * Format: ARX-XXYYY where:
 *   - ARX: Ariane-Xml prefix
 *   - XX: Category code (00-99)
 *   - YYY: Specific error number (000-999)
 *
 * Severity is an attribute of the error, not part of the code.
 * Display format: ARX-XXYYY [Severity] Message
 *
 * Example: ARX-01004 [Warning] Bad attribute in SELECT clause
 */
class ArianeError : public std::runtime_error {
private:
    int category_;              // Category (0-99)
    int code_;                  // Error number within category (0-999)
    std::string codeStr_;       // Formatted code (e.g., "ARX-01004")
    ErrorSeverity severity_;
    std::string context_;       // Additional context information
    int line_ = -1;            // Source line number (if applicable)
    std::string path_;         // File path (if applicable)

public:
    /**
     * Constructor for creating an error
     * @param category Error category (0-99)
     * @param code Specific error number within the category (0-999)
     * @param message Human-readable error message
     * @param severity Error severity (default: ERROR)
     */
    ArianeError(int category, int code,
                const std::string& message,
                ErrorSeverity severity = ErrorSeverity::ERROR)
        : std::runtime_error(message),
          category_(category),
          code_(code),
          severity_(severity) {
        codeStr_ = formatErrorCode(category, code);
    }

    /**
     * Constructor using ErrorCategory enum
     */
    ArianeError(ErrorCategory category, int code,
                const std::string& message,
                ErrorSeverity severity = ErrorSeverity::ERROR)
        : ArianeError(static_cast<int>(category), code, message, severity) {}

    /**
     * Factory method for success code
     * @param message Optional success message
     * @return ArianeError with ARX-00000 code
     */
    static ArianeError Success(const std::string& message = "Query executed successfully") {
        return ArianeError(SUCCESS_CATEGORY, SUCCESS_CODE,
                          message, ErrorSeverity::SUCCESS);
    }

    // Getters
    const std::string& getCode() const { return codeStr_; }
    int getCategory() const { return category_; }
    int getCodeNumber() const { return code_; }
    ErrorSeverity getSeverity() const { return severity_; }
    const std::string& getContext() const { return context_; }
    int getLine() const { return line_; }
    const std::string& getPath() const { return path_; }

    /**
     * Check if this represents a success code
     * @return true if code is ARX-00000
     */
    bool isSuccess() const {
        return category_ == SUCCESS_CATEGORY && code_ == SUCCESS_CODE;
    }

    /**
     * Get severity as string for display
     * @return Severity string ("Success", "Error", "Warning", "Info")
     */
    const char* getSeverityString() const {
        return severityToString(severity_);
    }

    /**
     * Get full formatted error message
     * Format: ARX-XXYYY [Severity] Message
     * Example: ARX-01004 [Warning] Bad attribute in SELECT clause
     *
     * @return Formatted error message
     */
    std::string getFullMessage() const {
        std::ostringstream oss;
        oss << codeStr_ << " [" << getSeverityString() << "] " << what();

        if (line_ >= 0) {
            oss << " (line " << line_ << ")";
        }
        if (!path_.empty()) {
            oss << " [" << path_ << "]";
        }
        if (!context_.empty()) {
            oss << "\n  Context: " << context_;
        }

        return oss.str();
    }

    /**
     * Get exit code for shell (0 for success/warnings, 1 for errors)
     * @return Exit code
     */
    int getExitCode() const {
        if (isSuccess() || severity_ == ErrorSeverity::WARNING) {
            return 0;
        }
        return 1;
    }

    // Setters for optional context
    void setContext(const std::string& context) { context_ = context; }
    void setLine(int line) { line_ = line; }
    void setPath(const std::string& path) { path_ = path; }

private:
    /**
     * Format error code as ARX-XXYYY
     * @param category Error category (0-99)
     * @param code Error number (0-999)
     * @return Formatted error code string
     */
    static std::string formatErrorCode(int category, int code) {
        std::ostringstream oss;
        oss << "ARX-"
            << std::setfill('0') << std::setw(2) << category
            << std::setfill('0') << std::setw(3) << code;
        return oss.str();
    }
};

// Helper macros for creating errors
#define ARX_SUCCESS() \
    ariane_xml::ArianeError::Success()

#define ARX_SUCCESS_MSG(msg) \
    ariane_xml::ArianeError::Success(msg)

#define ARX_ERROR(category, code, message) \
    ariane_xml::ArianeError(category, code, message, \
                            ariane_xml::ErrorSeverity::ERROR)

#define ARX_WARNING(category, code, message) \
    ariane_xml::ArianeError(category, code, message, \
                            ariane_xml::ErrorSeverity::WARNING)

#define ARX_INFO(category, code, message) \
    ariane_xml::ArianeError(category, code, message, \
                            ariane_xml::ErrorSeverity::INFO)

// Common error code constants
// Format: ARX-XXYYY where XX=category, YYY=code
namespace ErrorCodes {
    // Success (00xxx)
    constexpr int SUCCESS = 0;

    // General Errors (00xxx)
    constexpr int GENERAL_UNEXPECTED_END = 1;
    constexpr int GENERAL_INVALID_CHAR = 2;
    constexpr int GENERAL_UNMATCHED_PAREN = 3;
    constexpr int GENERAL_UNEXPECTED_TOKEN = 4;
    constexpr int GENERAL_MISSING_KEYWORD = 5;

    // SELECT Clause Errors (01xxx)
    constexpr int SELECT_MISSING_KEYWORD = 1;
    constexpr int SELECT_INVALID_FIELD = 2;
    constexpr int SELECT_COUNT_STAR_NOT_SUPPORTED = 3;
    constexpr int SELECT_DUPLICATE_FIELD = 4;
    constexpr int SELECT_INVALID_AGGREGATION = 5;
    constexpr int SELECT_EXPECTED_IDENTIFIER = 10;
    constexpr int SELECT_EXPECTED_FIELD_NOT_NUMBER = 11;
    constexpr int SELECT_DISTINCT_NOT_SUPPORTED = 20;

    // FROM Clause Errors (02xxx)
    constexpr int FROM_MISSING_KEYWORD = 1;
    constexpr int FROM_FILE_NOT_FOUND = 2;
    constexpr int FROM_INVALID_PATH = 3;
    constexpr int FROM_PATH_INVALID_CHARS = 4;
    constexpr int FROM_CANNOT_OPEN = 5;
    constexpr int FROM_MULTIPLE_FILES_NOT_SUPPORTED = 10;
    constexpr int FROM_FORMAT_NOT_RECOGNIZED = 20;

    // WHERE Clause Errors (03xxx)
    constexpr int WHERE_INVALID_CONDITION = 1;
    constexpr int WHERE_MISSING_OPERATOR = 2;
    constexpr int WHERE_TYPE_MISMATCH = 3;
    constexpr int WHERE_INVALID_LOGICAL_OP = 4;
    constexpr int WHERE_UNMATCHED_QUOTES = 5;

    // FOR Clause Errors (04xxx)
    constexpr int FOR_REQUIRES_DSN_MODE = 1;
    constexpr int FOR_INVALID_VARIABLE = 2;
    constexpr int FOR_VARIABLE_ALREADY_DEFINED = 3;
    constexpr int FOR_MUST_PRECEDE_WHERE = 4;
    constexpr int FOR_MISSING_IN_KEYWORD = 5;

    // XML Structure Errors (05xxx)
    constexpr int XML_AMBIGUOUS_PARTIAL_PATH = 1;
    constexpr int XML_MALFORMED_DOCUMENT = 2;
    constexpr int XML_INVALID_ELEMENT = 3;

    // DSN Format Errors (06xxx)
    constexpr int DSN_INVALID_SIRET_FORMAT = 1;
    constexpr int DSN_INVALID_SIRET_CHECKSUM = 2;
    constexpr int DSN_INVALID_NIR_FORMAT = 10;
    constexpr int DSN_INVALID_NIR_CHECKSUM = 11;
    constexpr int DSN_INVALID_DATE_FORMAT = 20;
    constexpr int DSN_INVALID_DECIMAL_FORMAT = 30;
    constexpr int DSN_INVALID_NUMERIC_FORMAT = 40;

    // DSN Mode Syntax Errors (22xxx)
    constexpr int DSN_LEADING_DOT_NOT_ALLOWED = 1;
    constexpr int DSN_ONLY_SHORTCUT_FORMAT = 2;
    constexpr int DSN_INVALID_FIELD_FORMAT = 3;

    // Schema Validation (07xxx)
    constexpr int SCHEMA_FILE_NOT_FOUND = 1;
    constexpr int SCHEMA_VERSION_MISMATCH = 2;
    constexpr int SCHEMA_INVALID_FORMAT = 3;
    constexpr int SCHEMA_LOADING_FAILED = 4;
    constexpr int SCHEMA_INCOMPATIBLE_VERSION = 5;
    constexpr int SCHEMA_PARSE_ERROR = 6;
    constexpr int SCHEMA_NO_ROOT_ELEMENT = 7;
    constexpr int SCHEMA_NO_SCHEMA_ELEMENT = 8;

    // File Operations (10xxx)
    constexpr int FILE_NOT_FOUND = 1;
    constexpr int FILE_PERMISSION_DENIED = 2;
    constexpr int FILE_ALREADY_EXISTS = 3;
    constexpr int FILE_DIR_NOT_FOUND = 4;
    constexpr int FILE_CANNOT_CREATE_DIR = 5;
    constexpr int FILE_EMPTY = 10;
    constexpr int FILE_TOO_LARGE = 11;
    constexpr int FILE_XML_LOAD_FAILED = 20;
    constexpr int FILE_XML_PARSE_ERROR = 21;

    // Processing Errors (12xxx)
    constexpr int PROCESSING_INVALID_NUMBER = 1;
    constexpr int PROCESSING_NUMBER_OUT_OF_RANGE = 2;
    constexpr int PROCESSING_VALUE_MUST_BE_NON_NEGATIVE = 3;

    // Kernel/CLI Errors (20xxx)
    constexpr int KERNEL_INVALID_COMMAND = 1;
    constexpr int KERNEL_EXECUTION_TIMEOUT = 2;
    constexpr int KERNEL_SUBPROCESS_FAILED = 3;
    constexpr int KERNEL_BINARY_NOT_FOUND = 4;
    constexpr int KERNEL_INVALID_ARGUMENTS = 5;

    // Warnings (80xxx)
    constexpr int WARN_DEPRECATED_SYNTAX = 1;
    constexpr int WARN_PERFORMANCE_LARGE_DATASET = 2;
    constexpr int WARN_SCHEMA_VALIDATION_DISABLED = 3;
    constexpr int WARN_MISSING_OPTIONAL_FIELD = 10;
}

} // namespace ariane_xml

#endif // ARIANE_XML_ERROR_CODES_H
