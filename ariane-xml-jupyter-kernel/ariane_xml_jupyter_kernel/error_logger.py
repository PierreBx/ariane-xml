"""
Ariane-XML Error Logger

Simple logging system for Ariane-XML errors with:
- Timestamp formatting
- File and console output
- Colored terminal output
- ARX-XXYYY [Severity] Message format
"""

import sys
from datetime import datetime
from typing import Optional, TextIO
from enum import Enum
from .error_codes import ArianeError, ErrorSeverity


class OutputMode(Enum):
    """Output modes for error logger"""
    CONSOLE_ONLY = "console"
    FILE_ONLY = "file"
    BOTH = "both"


class ErrorLogger:
    """
    Singleton logger for Ariane-XML errors

    Usage:
        logger = ErrorLogger.instance()
        logger.initialize(OutputMode.BOTH, "ariane-xml.log")
        logger.log(error)
    """

    _instance = None

    def __init__(self):
        if ErrorLogger._instance is not None:
            raise RuntimeError("Use ErrorLogger.instance() to get the singleton")

        self.output_mode = OutputMode.CONSOLE_ONLY
        self.log_file: Optional[TextIO] = None
        self.colored_output = True
        self._log_file_path: Optional[str] = None

    @classmethod
    def instance(cls) -> 'ErrorLogger':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self, mode: OutputMode = OutputMode.CONSOLE_ONLY,
                  log_file: str = "") -> None:
        """
        Initialize the logger with output mode and optional log file

        Args:
            mode: Output mode (CONSOLE_ONLY, FILE_ONLY, or BOTH)
            log_file: Path to log file (required for FILE_ONLY or BOTH)
        """
        self.output_mode = mode

        if mode in (OutputMode.FILE_ONLY, OutputMode.BOTH):
            if not log_file:
                print("Warning: Log file path required for FILE_ONLY or BOTH mode",
                      file=sys.stderr)
                self.output_mode = OutputMode.CONSOLE_ONLY
                return

            try:
                self.log_file = open(log_file, 'a', encoding='utf-8')
                self._log_file_path = log_file
            except OSError as e:
                print(f"Warning: Failed to open log file {log_file}: {e}",
                      file=sys.stderr)
                self.output_mode = OutputMode.CONSOLE_ONLY

    def set_colored_output(self, enabled: bool) -> None:
        """Enable or disable colored console output"""
        self.colored_output = enabled

    def log(self, error: ArianeError) -> None:
        """Log an ArianeError with timestamp"""
        log_entry = self._format_log_entry(error)
        self._write_log(log_entry, error.severity)

    def log_message(self, category: int, code: int, severity: ErrorSeverity,
                   message: str) -> None:
        """Log a custom message with specific error code"""
        error = ArianeError(category, code, severity, message)
        self.log(error)

    def close(self) -> None:
        """Close the log file if open"""
        if self.log_file:
            self.log_file.close()
            self.log_file = None

    def _format_log_entry(self, error: ArianeError) -> str:
        """Format log entry with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{timestamp} {error.get_full_message()}"

    def _get_color_code(self, severity: ErrorSeverity) -> str:
        """Get ANSI color code for severity"""
        if not self.colored_output:
            return ""

        color_map = {
            ErrorSeverity.SUCCESS: "\033[32m",  # Green
            ErrorSeverity.ERROR: "\033[31m",    # Red
            ErrorSeverity.WARNING: "\033[33m",  # Yellow
            ErrorSeverity.INFO: "\033[36m",     # Cyan
        }
        return color_map.get(severity, "")

    def _get_reset_code(self) -> str:
        """Get ANSI reset code"""
        return "\033[0m" if self.colored_output else ""

    def _get_severity_symbol(self, severity: ErrorSeverity) -> str:
        """Get Unicode symbol for severity"""
        if not self.colored_output:
            return ""

        symbol_map = {
            ErrorSeverity.SUCCESS: "✓ ",
            ErrorSeverity.ERROR: "✗ ",
            ErrorSeverity.WARNING: "⚠ ",
            ErrorSeverity.INFO: "ℹ ",
        }
        return symbol_map.get(severity, "")

    def _write_log(self, entry: str, severity: ErrorSeverity) -> None:
        """Write log entry to appropriate output(s)"""
        # Write to console
        if self.output_mode in (OutputMode.CONSOLE_ONLY, OutputMode.BOTH):
            console_entry = (self._get_color_code(severity) +
                           self._get_severity_symbol(severity) +
                           entry +
                           self._get_reset_code())
            print(console_entry, file=sys.stderr)

        # Write to file (no colors)
        if self.output_mode in (OutputMode.FILE_ONLY, OutputMode.BOTH):
            if self.log_file:
                self.log_file.write(entry + '\n')
                self.log_file.flush()

    def __del__(self):
        """Cleanup: close log file"""
        self.close()


# Convenience functions
def log_error(category: int, code: int, message: str) -> None:
    """Log an error message"""
    ErrorLogger.instance().log_message(category, code, ErrorSeverity.ERROR, message)


def log_warning(category: int, code: int, message: str) -> None:
    """Log a warning message"""
    ErrorLogger.instance().log_message(category, code, ErrorSeverity.WARNING, message)


def log_info(category: int, code: int, message: str) -> None:
    """Log an info message"""
    ErrorLogger.instance().log_message(category, code, ErrorSeverity.INFO, message)


def log_success(message: str = "Query executed successfully") -> None:
    """Log a success message"""
    ErrorLogger.instance().log_message(0, 0, ErrorSeverity.SUCCESS, message)


def log_ariane_error(error: ArianeError) -> None:
    """Log an ArianeError"""
    ErrorLogger.instance().log(error)
