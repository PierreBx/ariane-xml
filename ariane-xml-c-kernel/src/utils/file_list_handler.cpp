#include "utils/file_list_handler.h"
#include "utils/pseudonymisation_checker.h"
#include <pugixml.hpp>
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <cmath>
#include <regex>

namespace ariane_xml {

// ============================================================================
// FileInfo Implementation
// ============================================================================

std::string FileInfo::getFormattedSize() const {
    const double KB = 1024.0;
    const double MB = KB * 1024.0;
    const double GB = MB * 1024.0;

    std::ostringstream oss;
    oss << std::fixed << std::setprecision(1);

    if (size >= GB) {
        oss << (size / GB) << " GB";
    } else if (size >= MB) {
        oss << (size / MB) << " MB";
    } else if (size >= KB) {
        oss << (size / KB) << " KB";
    } else {
        oss << size << " B";
    }

    return oss.str();
}

std::string FileInfo::getNatureString() const {
    return (nature == FileNature::DSN) ? "DSN" : "STANDARD";
}

// ============================================================================
// DsnDetectionConfig Implementation
// ============================================================================

bool DsnDetectionConfig::loadFromFile(const std::string& configPath) {
    std::ifstream file(configPath);
    if (!file.is_open()) {
        return false;
    }

    // Simple YAML parser for our specific needs
    // We're looking for lines like:
    //   - DSN_FCTU_HY
    //   - DSN_FCTU_M
    // under the "dsn_root_elements:" section

    std::string line;
    bool inRootElements = false;

    while (std::getline(file, line)) {
        // Trim whitespace
        line.erase(0, line.find_first_not_of(" \t\r\n"));
        line.erase(line.find_last_not_of(" \t\r\n") + 1);

        // Skip comments and empty lines
        if (line.empty() || line[0] == '#') {
            continue;
        }

        // Check if we're entering the dsn_root_elements section
        if (line.find("dsn_root_elements:") == 0) {
            inRootElements = true;
            continue;
        }

        // Check if we're entering another section
        if (!line.empty() && line[0] != '-' && line[0] != ' ' && line.find(':') != std::string::npos) {
            // Check for version_xpath
            if (line.find("version_xpath:") == 0) {
                inRootElements = false;
                size_t colonPos = line.find(':');
                if (colonPos != std::string::npos) {
                    versionXPath = line.substr(colonPos + 1);
                    // Trim and remove quotes
                    versionXPath.erase(0, versionXPath.find_first_not_of(" \t\""));
                    versionXPath.erase(versionXPath.find_last_not_of(" \t\"") + 1);
                }
                continue;
            }
            inRootElements = false;
        }

        // Parse list items in the dsn_root_elements section
        if (inRootElements && !line.empty() && line[0] == '-') {
            // Extract the value after the '-'
            std::string value = line.substr(1);
            // Trim whitespace and comments
            value.erase(0, value.find_first_not_of(" \t"));
            size_t commentPos = value.find('#');
            if (commentPos != std::string::npos) {
                value = value.substr(0, commentPos);
            }
            value.erase(value.find_last_not_of(" \t") + 1);

            if (!value.empty()) {
                rootElements.push_back(value);
            }
        }
    }

    file.close();
    return !rootElements.empty();
}

DsnDetectionConfig DsnDetectionConfig::getDefault() {
    DsnDetectionConfig config;
    config.rootElements = {
        "DSN_FCTU_HY",
        "DSN_FCTU_M",
        "DSN_FCTU",
        "DSN_SITU",
        "DSN_ANNUL",
        "DSN_RETRAIT"
    };
    config.versionXPath = "//S10_G00_00/S10_G00_00_006";
    return config;
}

// ============================================================================
// FileListHandler Implementation
// ============================================================================

FileListHandler::FileListHandler(const std::string& configDir)
    : configDir_(configDir) {
    if (configDir_.empty()) {
        configDir_ = findConfigDirectory();
    }
    loadConfig();
}

std::string FileListHandler::findConfigDirectory() {
    // Search for ariane-xml-config in common locations
    std::vector<std::string> searchPaths = {
        "./ariane-xml-config",
        "../ariane-xml-config",
        "../../ariane-xml-config",
        std::string(getenv("HOME") ? getenv("HOME") : "") + "/.ariane-xml/config",
        "/etc/ariane-xml/config"
    };

    for (const auto& path : searchPaths) {
        if (std::filesystem::exists(path) && std::filesystem::is_directory(path)) {
            return path;
        }
    }

    return "";
}

void FileListHandler::loadConfig() {
    if (configDir_.empty()) {
        config_ = DsnDetectionConfig::getDefault();
        return;
    }

    std::string configFile = configDir_ + "/dsn_detection.yml";
    if (!config_.loadFromFile(configFile)) {
        // Fall back to default if loading fails
        config_ = DsnDetectionConfig::getDefault();
    }
}

bool FileListHandler::isDsnRootElement(const std::string& elementName) const {
    return std::find(config_.rootElements.begin(), config_.rootElements.end(), elementName)
           != config_.rootElements.end();
}

std::variant<std::vector<FileInfo>, ArianeError> FileListHandler::listFiles(const std::string& directoryPath) {
    namespace fs = std::filesystem;

    // Validate directory path
    if (directoryPath.empty()) {
        return ARX_ERROR(ErrorCategory::KERNEL_CLI, ErrorCodes::LIST_INVALID_PATH,
                        "Directory path is empty");
    }

    fs::path dirPath(directoryPath);

    // Check if directory exists
    if (!fs::exists(dirPath)) {
        return ARX_ERROR(ErrorCategory::KERNEL_CLI, ErrorCodes::LIST_DIRECTORY_NOT_FOUND,
                        "Directory not found: " + directoryPath);
    }

    // Check if it's actually a directory
    if (!fs::is_directory(dirPath)) {
        return ARX_ERROR(ErrorCategory::KERNEL_CLI, ErrorCodes::LIST_INVALID_PATH,
                        "Path is not a directory: " + directoryPath);
    }

    // Check permissions
    std::error_code ec;
    auto dirIter = fs::directory_iterator(dirPath, ec);
    if (ec) {
        return ARX_ERROR(ErrorCategory::KERNEL_CLI, ErrorCodes::LIST_PERMISSION_DENIED,
                        "Cannot access directory: " + ec.message());
    }

    // Collect all XML files
    std::vector<FileInfo> files;

    for (const auto& entry : dirIter) {
        if (!entry.is_regular_file()) {
            continue;
        }

        const auto& path = entry.path();
        std::string extension = path.extension().string();
        std::transform(extension.begin(), extension.end(), extension.begin(), ::tolower);

        if (extension == ".xml") {
            auto result = getFileInfo(path);
            if (std::holds_alternative<FileInfo>(result)) {
                files.push_back(std::get<FileInfo>(result));
            }
            // Skip files that can't be read (permissions, parse errors, etc.)
        }
    }

    // Sort by filename
    std::sort(files.begin(), files.end(),
              [](const FileInfo& a, const FileInfo& b) {
                  return a.filename < b.filename;
              });

    return files;
}

std::variant<FileInfo, ArianeError> FileListHandler::getFileInfo(const std::filesystem::path& filePath) {
    FileInfo info;
    info.filename = filePath.filename().string();
    info.fullPath = filePath;
    info.isEncrypted = false;
    info.isValid = std::nullopt;  // Not validated yet

    // Get file size
    std::error_code ec;
    info.size = std::filesystem::file_size(filePath, ec);
    if (ec) {
        return ARX_ERROR(ErrorCategory::FILE_OPERATIONS, ErrorCodes::FILE_PERMISSION_DENIED,
                        "Cannot get file size: " + ec.message());
    }

    // Detect nature
    info.nature = detectNature(filePath);

    // If DSN, detect version and encryption
    if (info.nature == FileNature::DSN) {
        info.dsnVersion = detectDsnVersion(filePath);
        info.isEncrypted = isFileEncrypted(filePath);
        // Validation will be added when XSD files are provided
        // For now, set to std::nullopt (not validated)
    }

    return info;
}

FileNature FileListHandler::detectNature(const std::filesystem::path& filePath) {
    pugi::xml_document doc;
    pugi::xml_parse_result result = doc.load_file(filePath.c_str());

    if (!result) {
        // If we can't parse, assume STANDARD
        return FileNature::STANDARD;
    }

    // Get the root element
    pugi::xml_node root = doc.document_element();
    if (!root) {
        return FileNature::STANDARD;
    }

    std::string rootName = root.name();

    // Check if root element is in the DSN list
    if (isDsnRootElement(rootName)) {
        return FileNature::DSN;
    }

    return FileNature::STANDARD;
}

std::optional<std::string> FileListHandler::detectDsnVersion(const std::filesystem::path& filePath) {
    pugi::xml_document doc;
    pugi::xml_parse_result result = doc.load_file(filePath.c_str());

    if (!result) {
        return std::nullopt;
    }

    // Try to find the version element using the configured XPath
    // For now, we'll look for S10_G00_00_006 which contains version like "P25V01" or "P26V01"
    pugi::xpath_node versionNode = doc.select_node("//S10_G00_00_006");

    if (versionNode) {
        std::string versionText = versionNode.node().text().as_string();

        // Extract P25 or P26 from strings like "P25V01", "P26V02"
        std::regex versionRegex("^(P\\d{2})V\\d{2}$");
        std::smatch match;

        if (std::regex_match(versionText, match, versionRegex)) {
            return match[1].str();  // Returns "P25" or "P26"
        }
    }

    // If we can't find the version, try to infer from other indicators
    // For now, return unknown
    return std::nullopt;
}

bool FileListHandler::isFileEncrypted(const std::filesystem::path& filePath) {
    return PseudonymisationChecker::isPseudonymised(filePath.string());
}

std::string FileListHandler::formatAsJson(const std::vector<FileInfo>& files) {
    std::ostringstream oss;
    oss << "{\n";
    oss << "  \"files\": [\n";

    for (size_t i = 0; i < files.size(); ++i) {
        const auto& file = files[i];
        oss << "    {\n";
        oss << "      \"filename\": \"" << file.filename << "\",\n";
        oss << "      \"size\": " << file.size << ",\n";
        oss << "      \"formatted_size\": \"" << file.getFormattedSize() << "\",\n";
        oss << "      \"nature\": \"" << file.getNatureString() << "\",\n";

        if (file.dsnVersion.has_value()) {
            oss << "      \"version\": \"" << file.dsnVersion.value() << "\",\n";
        } else {
            oss << "      \"version\": null,\n";
        }

        if (file.isValid.has_value()) {
            oss << "      \"valid\": " << (file.isValid.value() ? "true" : "false") << ",\n";
        } else {
            oss << "      \"valid\": null,\n";
        }

        oss << "      \"encrypted\": " << (file.isEncrypted ? "true" : "false") << "\n";
        oss << "    }" << (i < files.size() - 1 ? "," : "") << "\n";
    }

    oss << "  ],\n";
    oss << "  \"total\": " << files.size() << "\n";
    oss << "}\n";

    return oss.str();
}

std::string FileListHandler::formatAsTable(const std::vector<FileInfo>& files) {
    if (files.empty()) {
        return "No XML files found in directory.";
    }

    std::ostringstream oss;

    // Calculate column widths
    size_t maxFilename = 8;  // "Filename"
    for (const auto& file : files) {
        maxFilename = std::max(maxFilename, file.filename.length());
    }

    // Table header
    oss << std::left;
    oss << std::setw(maxFilename + 2) << "Filename"
        << std::setw(10) << "Size"
        << std::setw(12) << "Nature"
        << std::setw(10) << "Version"
        << std::setw(12) << "Valid"
        << std::setw(12) << "Encrypted"
        << "\n";

    // Separator
    oss << std::string(maxFilename + 2, '-') << " "
        << std::string(9, '-') << " "
        << std::string(11, '-') << " "
        << std::string(9, '-') << " "
        << std::string(11, '-') << " "
        << std::string(11, '-') << "\n";

    // Table rows
    for (const auto& file : files) {
        oss << std::setw(maxFilename + 2) << file.filename
            << std::setw(10) << file.getFormattedSize()
            << std::setw(12) << file.getNatureString();

        // Version
        if (file.dsnVersion.has_value()) {
            oss << std::setw(10) << file.dsnVersion.value();
        } else {
            oss << std::setw(10) << "-";
        }

        // Validation
        if (file.isValid.has_value()) {
            oss << std::setw(12) << (file.isValid.value() ? "Valid" : "Invalid");
        } else {
            oss << std::setw(12) << "-";
        }

        // Encryption
        if (file.nature == FileNature::DSN) {
            oss << std::setw(12) << (file.isEncrypted ? "Yes" : "No");
        } else {
            oss << std::setw(12) << "-";
        }

        oss << "\n";
    }

    oss << "\nTotal: " << files.size() << " XML file(s)\n";

    return oss.str();
}

} // namespace ariane_xml
