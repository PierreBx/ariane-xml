#ifndef FILE_LIST_HANDLER_H
#define FILE_LIST_HANDLER_H

#include <string>
#include <vector>
#include <optional>
#include <variant>
#include <filesystem>
#include "error/error_codes.h"

namespace ariane_xml {

/**
 * File nature enumeration
 */
enum class FileNature {
    STANDARD,
    DSN
};

/**
 * Information about a single XML file
 */
struct FileInfo {
    std::string filename;           // Just the filename (not full path)
    std::filesystem::path fullPath; // Full path to the file
    size_t size;                    // File size in bytes
    FileNature nature;              // STANDARD or DSN
    std::optional<std::string> dsnVersion;  // P25, P26, etc. (only for DSN files)
    std::optional<bool> isValid;    // Validation result (only for DSN files, std::nullopt if not validated)
    bool isEncrypted;               // Encryption status (only meaningful for DSN files)

    /**
     * Get human-readable size string (e.g., "2.4 KB", "15.2 MB")
     */
    std::string getFormattedSize() const;

    /**
     * Get nature as string
     */
    std::string getNatureString() const;
};

/**
 * Configuration for DSN detection
 */
struct DsnDetectionConfig {
    std::vector<std::string> rootElements;  // List of DSN root element names
    std::string versionXPath;               // XPath to version element

    /**
     * Load configuration from YAML file
     * @param configPath Path to dsn_detection.yml
     * @return true if loaded successfully
     */
    bool loadFromFile(const std::string& configPath);

    /**
     * Get default configuration if file cannot be loaded
     */
    static DsnDetectionConfig getDefault();
};

/**
 * Handler for the LIST command
 * Lists XML files in a directory with detailed information
 */
class FileListHandler {
private:
    DsnDetectionConfig config_;
    std::string configDir_;  // Path to ariane-xml-config directory

public:
    /**
     * Constructor
     * @param configDir Path to ariane-xml-config directory
     */
    explicit FileListHandler(const std::string& configDir = "");

    /**
     * List all XML files in a directory
     * @param directoryPath Path to directory to scan
     * @return Vector of FileInfo structures, or ArianeError if failed
     */
    std::variant<std::vector<FileInfo>, ArianeError> listFiles(const std::string& directoryPath);

    /**
     * Get information about a single XML file
     * @param filePath Path to the XML file
     * @return FileInfo structure, or ArianeError if failed
     */
    std::variant<FileInfo, ArianeError> getFileInfo(const std::filesystem::path& filePath);

    /**
     * Detect if a file is DSN based on root element
     * @param filePath Path to the XML file
     * @return FileNature (STANDARD or DSN)
     */
    FileNature detectNature(const std::filesystem::path& filePath);

    /**
     * Detect DSN version from file content
     * @param filePath Path to the XML file
     * @return Version string (e.g., "P25", "P26"), or std::nullopt if not found
     */
    std::optional<std::string> detectDsnVersion(const std::filesystem::path& filePath);

    /**
     * Check if a DSN file is encrypted
     * @param filePath Path to the XML file
     * @return true if encrypted (has pseudonymisation marker)
     */
    bool isFileEncrypted(const std::filesystem::path& filePath);

    /**
     * Format file list as JSON for output
     * @param files Vector of FileInfo structures
     * @return JSON string
     */
    static std::string formatAsJson(const std::vector<FileInfo>& files);

    /**
     * Format file list as plain text table
     * @param files Vector of FileInfo structures
     * @return Plain text table string
     */
    static std::string formatAsTable(const std::vector<FileInfo>& files);

private:
    /**
     * Find ariane-xml-config directory
     * Searches in common locations
     * @return Path to config directory, or empty string if not found
     */
    std::string findConfigDirectory();

    /**
     * Load DSN detection configuration
     */
    void loadConfig();

    /**
     * Check if a string is a DSN root element
     * @param elementName The root element name
     * @return true if it's in the configured list of DSN root elements
     */
    bool isDsnRootElement(const std::string& elementName) const;
};

} // namespace ariane_xml

#endif // FILE_LIST_HANDLER_H
