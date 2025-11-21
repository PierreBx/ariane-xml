#ifndef ARIANE_XML_ERROR_LOGGER_H
#define ARIANE_XML_ERROR_LOGGER_H

#include "error/error_codes.h"
#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <memory>

namespace ariane_xml {

/**
 * ErrorLogger - Simple logging system for Ariane-XML errors
 *
 * Features:
 * - Logs errors with timestamps
 * - Supports file and console output
 * - Formats errors in ARX-XXYYY [Severity] Message format
 * - Optional colored output for terminals
 */
class ErrorLogger {
public:
    enum class OutputMode {
        CONSOLE_ONLY,
        FILE_ONLY,
        BOTH
    };

    /**
     * Get the singleton instance of ErrorLogger
     */
    static ErrorLogger& instance() {
        static ErrorLogger logger;
        return logger;
    }

    /**
     * Initialize the logger with output mode and optional log file
     */
    void initialize(OutputMode mode = OutputMode::CONSOLE_ONLY,
                   const std::string& log_file = "") {
        output_mode_ = mode;

        if (mode == OutputMode::FILE_ONLY || mode == OutputMode::BOTH) {
            if (!log_file.empty()) {
                log_stream_.open(log_file, std::ios::app);
                if (!log_stream_.is_open()) {
                    std::cerr << "Warning: Failed to open log file: " << log_file << std::endl;
                    // Fall back to console only
                    output_mode_ = OutputMode::CONSOLE_ONLY;
                }
            }
        }
    }

    /**
     * Log an ArianeError
     */
    void log(const ArianeError& error) {
        std::string log_entry = format_log_entry(error);
        write_log(log_entry, error.getSeverity());
    }

    /**
     * Log a custom message with specific code
     */
    void log(ErrorCategory category, int code, ErrorSeverity severity,
             const std::string& message) {
        ArianeError error(category, code, severity, message);
        log(error);
    }

    /**
     * Enable or disable colored output for console
     */
    void set_colored_output(bool enabled) {
        colored_output_ = enabled;
    }

    /**
     * Close the log file if open
     */
    void close() {
        if (log_stream_.is_open()) {
            log_stream_.close();
        }
    }

    // Delete copy constructor and assignment operator
    ErrorLogger(const ErrorLogger&) = delete;
    ErrorLogger& operator=(const ErrorLogger&) = delete;

private:
    ErrorLogger() : output_mode_(OutputMode::CONSOLE_ONLY), colored_output_(true) {}
    ~ErrorLogger() { close(); }

    /**
     * Format a log entry with timestamp
     */
    std::string format_log_entry(const ArianeError& error) {
        std::ostringstream oss;

        // Add timestamp
        auto now = std::chrono::system_clock::now();
        auto time_t_now = std::chrono::system_clock::to_time_t(now);
        auto tm_now = *std::localtime(&time_t_now);

        oss << std::put_time(&tm_now, "%Y-%m-%d %H:%M:%S") << " ";

        // Add error code and message
        oss << error.getFullMessage();

        return oss.str();
    }

    /**
     * Get ANSI color code for severity
     */
    std::string get_color_code(ErrorSeverity severity) {
        if (!colored_output_) return "";

        switch (severity) {
            case ErrorSeverity::SUCCESS:
                return "\033[32m"; // Green
            case ErrorSeverity::ERROR:
                return "\033[31m"; // Red
            case ErrorSeverity::WARNING:
                return "\033[33m"; // Yellow
            case ErrorSeverity::INFO:
                return "\033[36m"; // Cyan
            default:
                return "";
        }
    }

    /**
     * Get ANSI reset code
     */
    std::string get_reset_code() {
        return colored_output_ ? "\033[0m" : "";
    }

    /**
     * Get symbol for severity (Unicode)
     */
    std::string get_severity_symbol(ErrorSeverity severity) {
        if (!colored_output_) return "";

        switch (severity) {
            case ErrorSeverity::SUCCESS:
                return "✓ ";
            case ErrorSeverity::ERROR:
                return "✗ ";
            case ErrorSeverity::WARNING:
                return "⚠ ";
            case ErrorSeverity::INFO:
                return "ℹ ";
            default:
                return "";
        }
    }

    /**
     * Write log entry to appropriate output(s)
     */
    void write_log(const std::string& entry, ErrorSeverity severity) {
        // Write to console
        if (output_mode_ == OutputMode::CONSOLE_ONLY || output_mode_ == OutputMode::BOTH) {
            std::string console_entry = get_color_code(severity) +
                                       get_severity_symbol(severity) +
                                       entry +
                                       get_reset_code();
            std::cerr << console_entry << std::endl;
        }

        // Write to file (no colors)
        if (output_mode_ == OutputMode::FILE_ONLY || output_mode_ == OutputMode::BOTH) {
            if (log_stream_.is_open()) {
                log_stream_ << entry << std::endl;
                log_stream_.flush();
            }
        }
    }

    OutputMode output_mode_;
    std::ofstream log_stream_;
    bool colored_output_;
};

// Convenience macros for logging
#define LOG_ERROR(category, code, message) \
    ariane_xml::ErrorLogger::instance().log(category, code, ariane_xml::ErrorSeverity::ERROR, message)

#define LOG_WARNING(category, code, message) \
    ariane_xml::ErrorLogger::instance().log(category, code, ariane_xml::ErrorSeverity::WARNING, message)

#define LOG_INFO(category, code, message) \
    ariane_xml::ErrorLogger::instance().log(category, code, ariane_xml::ErrorSeverity::INFO, message)

#define LOG_SUCCESS(message) \
    ariane_xml::ErrorLogger::instance().log(ariane_xml::ErrorCategory::SUCCESS_GENERAL, 0, \
                                           ariane_xml::ErrorSeverity::SUCCESS, message)

#define LOG_ARIANE_ERROR(error) \
    ariane_xml::ErrorLogger::instance().log(error)

} // namespace ariane_xml

#endif // ARIANE_XML_ERROR_LOGGER_H
