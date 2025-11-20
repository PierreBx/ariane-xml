#ifndef ARIANE_XML_ERROR_CODES_H
#define ARIANE_XML_ERROR_CODES_H

#include <string>
#include <stdexcept>
#include <sstream>
#include <iomanip>

namespace ariane_xml {

/**
 * Error categories for the unified error numbering system
 * Format: ARX-CCNNNN where CC is the category code (2 digits)
 */
enum class ErrorCategory {
    SUCCESS_GENERAL = 0,      // ARX-00xxxx - Success and general errors
    SELECT_CLAUSE = 1,        // ARX-01xxxx - SELECT statement issues
    FROM_CLAUSE = 2,          // ARX-02xxxx - File paths, table references
    WHERE_CLAUSE = 3,         // ARX-03xxxx - Filtering, conditions
    FOR_CLAUSE = 4,           // ARX-04xxxx - DSN mode iteration
    XML_STRUCTURE = 5,        // ARX-05xxxx - Malformed XML, schema violations
    DSN_FORMAT = 6,           // ARX-06xxxx - SIRET, NIR, date formats
    SCHEMA_VALIDATION = 7,    // ARX-07xxxx - Schema loading, version mismatches
    FIELD_VALIDATION = 8,     // ARX-08xxxx - Unknown fields, type mismatches
    DATA_INTEGRITY = 9,       // ARX-09xxxx - Checksums, mandatory fields
    FILE_OPERATIONS = 10,     // ARX-10xxxx - File not found, permissions
    MEMORY_RESOURCES = 11,    // ARX-11xxxx - Out of memory, buffer overflows
    PROCESSING = 12,          // ARX-12xxxx - Query execution failures
    TIMEOUT = 13,             // ARX-13xxxx - Execution timeouts
    OUTPUT = 14,              // ARX-14xxxx - Result formatting, writing
    ENCRYPTION = 15,          // ARX-15xxxx - Key generation, encryption
    DECRYPTION = 16,          // ARX-16xxxx - Decryption, key loading
    KEY_MANAGEMENT = 17,      // ARX-17xxxx - Key file operations
    CERTIFICATES = 18,        // ARX-18xxxx - Certificate validation
    ACCESS_CONTROL = 19,      // ARX-19xxxx - Permissions, authentication
    KERNEL_CLI = 20,          // ARX-20xxxx - Kernel/CLI errors
    JUPYTER = 21,             // ARX-21xxxx - Jupyter integration
    DSN_MODE = 22,            // ARX-22xxxx - DSN mode specific
    AGGREGATION = 23,         // ARX-23xxxx - Aggregation functions
    CONFIGURATION = 40,       // ARX-40xxxx - Configuration errors
    ENVIRONMENT = 41,         // ARX-41xxxx - Environment variables, paths
    DEPENDENCIES = 42,        // ARX-42xxxx - Missing libraries, versions
    SYSTEM_RESOURCES = 43,    // ARX-43xxxx - Disk space, handles
    WARNINGS = 80,            // ARX-80xxxx - Non-fatal warnings
    INFORMATIONAL = 85,       // ARX-85xxxx - Informational messages
    DEBUG_INTERNAL = 90       // ARX-90xxxx - Debug/internal errors
};

/**
 * Error severity levels
 */
enum class ErrorSeverity {
    SUCCESS,   // ARX-000000 only - normal completion
    ERROR,     // Fatal errors that stop execution
    WARNING,   // Non-fatal issues, execution continues
    INFO       // Informational messages
};

// Success code constant
constexpr int SUCCESS_CODE = 0;
constexpr const char* SUCCESS_CODE_STR = "ARX-000000";

/**
 * Unified error class for ariane-xml
 * Format: ARX-CCNNNN where:
 *   - ARX: Ariane-Xml prefix
 *   - CC: Category code (2 digits)
 *   - NNNN: Specific error number (4 digits)
 */
class ArianeError : public std::runtime_error {
private:
    std::string code_;          // Error code (e.g., "ARX-010001")
    ErrorCategory category_;
    int errorNumber_;
    ErrorSeverity severity_;
    std::string context_;       // Additional context information
    int line_ = -1;            // Source line number (if applicable)
    std::string path_;         // File path (if applicable)

public:
    /**
     * Constructor for creating an error
     * @param category Error category
     * @param errorNumber Specific error number within the category (0-9999)
     * @param message Human-readable error message
     * @param severity Error severity (default: ERROR)
     */
    ArianeError(ErrorCategory category, int errorNumber,
                const std::string& message,
                ErrorSeverity severity = ErrorSeverity::ERROR)
        : std::runtime_error(message),
          category_(category),
          errorNumber_(errorNumber),
          severity_(severity) {
        code_ = formatErrorCode(category, errorNumber);
    }

    /**
     * Factory method for success code
     * @param message Optional success message
     * @return ArianeError with ARX-000000 code
     */
    static ArianeError Success(const std::string& message = "Success") {
        return ArianeError(ErrorCategory::SUCCESS_GENERAL, SUCCESS_CODE,
                          message, ErrorSeverity::SUCCESS);
    }

    // Getters
    const std::string& getCode() const { return code_; }
    ErrorCategory getCategory() const { return category_; }
    int getErrorNumber() const { return errorNumber_; }
    ErrorSeverity getSeverity() const { return severity_; }
    const std::string& getContext() const { return context_; }
    int getLine() const { return line_; }
    const std::string& getPath() const { return path_; }

    /**
     * Check if this represents a success code
     * @return true if code is ARX-000000
     */
    bool isSuccess() const {
        return code_ == SUCCESS_CODE_STR;
    }

    /**
     * Get full formatted error message with code and context
     * @return Formatted error message
     */
    std::string getFullMessage() const {
        std::string severityPrefix;
        switch (severity_) {
            case ErrorSeverity::SUCCESS:  severityPrefix = ""; break;
            case ErrorSeverity::ERROR:    severityPrefix = "E-"; break;
            case ErrorSeverity::WARNING:  severityPrefix = "W-"; break;
            case ErrorSeverity::INFO:     severityPrefix = "I-"; break;
        }

        std::ostringstream oss;
        if (!severityPrefix.empty()) {
            oss << severityPrefix;
        }
        oss << code_ << ": " << what();

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
     * Format error code as ARX-CCNNNN
     * @param category Error category
     * @param errorNumber Error number (0-9999)
     * @return Formatted error code string
     */
    static std::string formatErrorCode(ErrorCategory category, int errorNumber) {
        std::ostringstream oss;
        oss << "ARX-"
            << std::setfill('0') << std::setw(2) << static_cast<int>(category)
            << std::setfill('0') << std::setw(4) << errorNumber;
        return oss.str();
    }
};

// Helper macros for creating errors
#define ARX_SUCCESS() \
    ariane_xml::ArianeError::Success()

#define ARX_SUCCESS_MSG(msg) \
    ariane_xml::ArianeError::Success(msg)

#define ARX_ERROR(category, number, message) \
    ariane_xml::ArianeError(ariane_xml::ErrorCategory::category, number, message, \
                            ariane_xml::ErrorSeverity::ERROR)

#define ARX_WARNING(category, number, message) \
    ariane_xml::ArianeError(ariane_xml::ErrorCategory::category, number, message, \
                            ariane_xml::ErrorSeverity::WARNING)

#define ARX_INFO(category, number, message) \
    ariane_xml::ArianeError(ariane_xml::ErrorCategory::category, number, message, \
                            ariane_xml::ErrorSeverity::INFO)

// Common error code constants
namespace ErrorCodes {
    // Success (00xxxx)
    constexpr int SUCCESS = 0;

    // SELECT Clause Errors (01xxxx)
    constexpr int SELECT_MISSING_KEYWORD = 1;
    constexpr int SELECT_INVALID_FIELD = 2;
    constexpr int SELECT_COUNT_STAR_NOT_SUPPORTED = 3;
    constexpr int SELECT_DUPLICATE_FIELD = 4;
    constexpr int SELECT_INVALID_AGGREGATION = 5;
    constexpr int SELECT_EXPECTED_IDENTIFIER = 10;
    constexpr int SELECT_EXPECTED_FIELD_NOT_NUMBER = 11;
    constexpr int SELECT_DISTINCT_NOT_SUPPORTED = 20;

    // FROM Clause Errors (02xxxx)
    constexpr int FROM_MISSING_KEYWORD = 1;
    constexpr int FROM_FILE_NOT_FOUND = 2;
    constexpr int FROM_INVALID_PATH = 3;
    constexpr int FROM_PATH_INVALID_CHARS = 4;
    constexpr int FROM_CANNOT_OPEN = 5;
    constexpr int FROM_MULTIPLE_FILES_NOT_SUPPORTED = 10;
    constexpr int FROM_FORMAT_NOT_RECOGNIZED = 20;

    // WHERE Clause Errors (03xxxx)
    constexpr int WHERE_INVALID_CONDITION = 1;
    constexpr int WHERE_MISSING_OPERATOR = 2;
    constexpr int WHERE_TYPE_MISMATCH = 3;
    constexpr int WHERE_INVALID_LOGICAL_OP = 4;
    constexpr int WHERE_UNMATCHED_QUOTES = 5;

    // FOR Clause Errors (04xxxx)
    constexpr int FOR_REQUIRES_DSN_MODE = 1;
    constexpr int FOR_INVALID_VARIABLE = 2;
    constexpr int FOR_VARIABLE_ALREADY_DEFINED = 3;
    constexpr int FOR_MUST_PRECEDE_WHERE = 4;
    constexpr int FOR_MISSING_IN_KEYWORD = 5;

    // DSN Format Errors (06xxxx)
    constexpr int DSN_INVALID_SIRET_FORMAT = 1;
    constexpr int DSN_INVALID_SIRET_CHECKSUM = 2;
    constexpr int DSN_INVALID_NIR_FORMAT = 10;
    constexpr int DSN_INVALID_NIR_CHECKSUM = 11;
    constexpr int DSN_INVALID_DATE_FORMAT = 20;
    constexpr int DSN_INVALID_DECIMAL_FORMAT = 30;
    constexpr int DSN_INVALID_NUMERIC_FORMAT = 40;

    // File Operations (10xxxx)
    constexpr int FILE_NOT_FOUND = 1;
    constexpr int FILE_PERMISSION_DENIED = 2;
    constexpr int FILE_ALREADY_EXISTS = 3;
    constexpr int FILE_DIR_NOT_FOUND = 4;
    constexpr int FILE_CANNOT_CREATE_DIR = 5;
    constexpr int FILE_EMPTY = 10;
    constexpr int FILE_TOO_LARGE = 11;

    // Warnings (80xxxx)
    constexpr int WARN_DEPRECATED_SYNTAX = 1;
    constexpr int WARN_PERFORMANCE_LARGE_DATASET = 2;
    constexpr int WARN_SCHEMA_VALIDATION_DISABLED = 3;
    constexpr int WARN_MISSING_OPTIONAL_FIELD = 10;
}

} // namespace ariane_xml

#endif // ARIANE_XML_ERROR_CODES_H
