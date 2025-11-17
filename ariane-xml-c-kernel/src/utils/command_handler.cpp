#include "utils/command_handler.h"
#include "parser/lexer.h"
#include "generator/xsd_parser.h"
#include "generator/xml_generator.h"
#include "validator/xml_validator.h"
#include "dsn/dsn_schema.h"
#include "dsn/dsn_parser.h"
#include "dsn/dsn_validator.h"
#include <iostream>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <regex>

namespace ariane_xml {

CommandHandler::CommandHandler(AppContext& context)
    : context_(context) {}

bool CommandHandler::handleCommand(const std::string& input) {
    // Tokenize the input to identify the command
    Lexer lexer(input);
    auto tokens = lexer.tokenize();

    if (tokens.empty() || tokens[0].type == TokenType::END_OF_INPUT) {
        return false;
    }

    // Check if it's a SET command
    if (tokens[0].type == TokenType::SET) {
        return handleSetCommand(input);
    }

    // Check if it's a SHOW command
    if (tokens[0].type == TokenType::SHOW) {
        return handleShowCommand(input);
    }

    // Check if it's a GENERATE command
    if (tokens[0].type == TokenType::GENERATE) {
        return handleGenerateCommand(input);
    }

    // Check if it's a CHECK command
    if (tokens[0].type == TokenType::CHECK) {
        return handleCheckCommand(input);
    }

    // Check if it's a DESCRIBE command
    if (tokens[0].type == TokenType::DESCRIBE) {
        return handleDescribeCommand(input);
    }

    // Not a recognized command, treat as query
    return false;
}

bool CommandHandler::handleSetCommand(const std::string& input) {
    Lexer lexer(input);
    auto tokens = lexer.tokenize();

    // Expect: SET <XSD|DEST|VERBOSE|MODE> <path|value>
    if (tokens.size() < 2) {
        std::cerr << "Error: SET command requires a parameter\n";
        std::cerr << "Usage: SET XSD /path/to/file.xsd\n";
        std::cerr << "       SET DEST /path/to/directory\n";
        std::cerr << "       SET VERBOSE\n";
        std::cerr << "       SET MODE <STANDARD|DSN>\n";
        return true;
    }

    TokenType paramType = tokens[1].type;

    // Handle VERBOSE (no path required)
    if (paramType == TokenType::VERBOSE) {
        context_.setVerbose(true);
        std::cout << "Verbose mode enabled. Queries will be checked for ambiguous attributes.\n";
        return true;
    }

    // Handle MODE command: SET MODE <STANDARD|DSN>
    if (paramType == TokenType::MODE) {
        if (tokens.size() < 3) {
            std::cerr << "Error: SET MODE requires a mode value (STANDARD or DSN)\n";
            std::cerr << "Usage: SET MODE STANDARD\n";
            std::cerr << "       SET MODE DSN\n";
            return true;
        }

        if (tokens[2].type == TokenType::STANDARD) {
            context_.setMode(QueryMode::STANDARD);
            std::cout << "Query mode set to STANDARD\n";
        } else if (tokens[2].type == TokenType::DSN) {
            context_.setMode(QueryMode::DSN);
            std::cout << "Query mode set to DSN\n";
            std::cout << "DSN mode features:\n";
            std::cout << "  - YY_ZZZ shortcut notation for attributes\n";
            std::cout << "  - Schema version auto-detection\n";
            std::cout << "  - Use DESCRIBE <field> to explore DSN schema\n";
        } else {
            std::cerr << "Error: Invalid mode. Use STANDARD or DSN\n";
        }
        return true;
    }

    // For XSD and DEST, require a path
    if (tokens.size() < 3) {
        std::cerr << "Error: SET command requires a path for XSD or DEST\n";
        std::cerr << "Usage: SET XSD /path/to/file.xsd\n";
        std::cerr << "       SET DEST /path/to/directory\n";
        return true;
    }

    // Collect path from remaining tokens
    std::string path;
    for (size_t i = 2; i < tokens.size(); ++i) {
        if (tokens[i].type == TokenType::END_OF_INPUT) {
            break;
        }
        // Don't add spaces for path separators or punctuation
        if (!path.empty() &&
            tokens[i].type != TokenType::DOT &&
            tokens[i].type != TokenType::SLASH &&
            tokens[i].type != TokenType::COMMA &&
            tokens[i-1].type != TokenType::DOT &&
            tokens[i-1].type != TokenType::SLASH) {
            // For paths, only add space if previous token wasn't a separator
            // and we're dealing with identifiers (like quoted strings with spaces)
            if (tokens[i].type == TokenType::STRING_LITERAL ||
                (tokens[i-1].type == TokenType::STRING_LITERAL)) {
                path += " ";
            }
        }
        path += tokens[i].value;
    }

    if (path.empty()) {
        std::cerr << "Error: Path cannot be empty\n";
        return true;
    }

    // Handle based on parameter type
    if (paramType == TokenType::XSD) {
        setXsdPath(path);
    } else if (paramType == TokenType::DEST) {
        setDestPath(path);
    } else {
        std::cerr << "Error: Unknown SET parameter. Use XSD or DEST\n";
    }

    return true;
}

bool CommandHandler::handleShowCommand(const std::string& input) {
    Lexer lexer(input);
    auto tokens = lexer.tokenize();

    // Expect: SHOW <XSD|DEST|MODE>
    if (tokens.size() < 2) {
        std::cerr << "Error: SHOW command requires a parameter (XSD, DEST, or MODE)\n";
        std::cerr << "Usage: SHOW XSD\n";
        std::cerr << "       SHOW DEST\n";
        std::cerr << "       SHOW MODE\n";
        return true;
    }

    TokenType paramType = tokens[1].type;

    // Handle based on parameter type
    if (paramType == TokenType::XSD) {
        showXsdPath();
    } else if (paramType == TokenType::DEST) {
        showDestPath();
    } else if (paramType == TokenType::MODE) {
        showMode();
    } else {
        std::cerr << "Error: Unknown SHOW parameter. Use XSD, DEST, or MODE\n";
    }

    return true;
}

void CommandHandler::setXsdPath(const std::string& path) {
    // Check if path exists
    if (!std::filesystem::exists(path)) {
        std::cerr << "Error: Path does not exist: " << path << "\n";
        return;
    }

    // Handle directories (for DSN schemas with multiple XSD files)
    if (std::filesystem::is_directory(path)) {
        if (context_.isDsnMode()) {
            // Try to parse as DSN schema directory
            std::cout << "Parsing DSN schema directory: " << path << "\n";

            // Auto-detect version from path (P25, P26, etc.)
            std::string version = context_.getDsnVersion();
            if (version == "AUTO") {
                if (path.find("P26") != std::string::npos) {
                    version = "P26";
                } else if (path.find("P25") != std::string::npos) {
                    version = "P25";
                } else {
                    version = "P26"; // Default to latest
                }
                context_.setDsnVersion(version);
                std::cout << "Auto-detected DSN version: " << version << "\n";
            }

            // Parse the DSN schema
            try {
                auto schema = DsnParser::parseDirectory(path, version);
                context_.setDsnSchema(schema);
                context_.setXsdPath(path);
                std::cout << "DSN schema loaded successfully\n";
                std::cout << "  Attributes: " << schema->getAttributes().size() << "\n";
                std::cout << "  Blocs: " << schema->getBlocs().size() << "\n";
            } catch (const std::exception& e) {
                std::cerr << "Error loading DSN schema: " << e.what() << "\n";
            }
        } else {
            std::cerr << "Error: Directory paths are only supported in DSN mode\n";
            std::cerr << "Use: SET MODE DSN\n";
        }
        return;
    }

    // Handle single XSD files
    if (validateXsdFile(path)) {
        context_.setXsdPath(path);
        std::cout << "XSD path set to: " << path << "\n";

        // If in DSN mode, try to parse as DSN schema
        if (context_.isDsnMode()) {
            std::cout << "Parsing DSN schema file...\n";

            std::string version = context_.getDsnVersion();
            if (version == "AUTO") {
                if (path.find("P26") != std::string::npos) {
                    version = "P26";
                } else if (path.find("P25") != std::string::npos) {
                    version = "P25";
                } else {
                    version = "P26";
                }
                context_.setDsnVersion(version);
                std::cout << "Auto-detected DSN version: " << version << "\n";
            }

            try {
                auto schema = DsnParser::parse(path, version);
                context_.setDsnSchema(schema);
                std::cout << "DSN schema loaded successfully\n";
                std::cout << "  Attributes: " << schema->getAttributes().size() << "\n";
            } catch (const std::exception& e) {
                std::cerr << "Warning: Could not parse as DSN schema: " << e.what() << "\n";
            }
        }
    }
}

void CommandHandler::setDestPath(const std::string& path) {
    if (validateAndCreateDestDirectory(path)) {
        context_.setDestPath(path);
        std::cout << "DEST path set to: " << path << "\n";
    }
}

void CommandHandler::showXsdPath() {
    if (context_.hasXsdPath()) {
        std::cout << "XSD: " << context_.getXsdPath().value() << "\n";
    } else {
        std::cout << "XSD: (not set)\n";
    }
}

void CommandHandler::showDestPath() {
    if (context_.hasDestPath()) {
        std::cout << "DEST: " << context_.getDestPath().value() << "\n";
    } else {
        std::cout << "DEST: (not set)\n";
    }
}

void CommandHandler::showMode() {
    QueryMode mode = context_.getMode();
    if (mode == QueryMode::DSN) {
        std::cout << "MODE: DSN\n";
        std::cout << "DSN Version: " << context_.getDsnVersion() << "\n";
        if (context_.hasDsnSchema()) {
            std::cout << "DSN Schema: Loaded\n";
        } else {
            std::cout << "DSN Schema: Not loaded\n";
        }
    } else {
        std::cout << "MODE: STANDARD\n";
    }
}

bool CommandHandler::validateXsdFile(const std::string& path) {
    // Check if file exists
    if (!std::filesystem::exists(path)) {
        std::cerr << "Error: XSD file does not exist: " << path << "\n";
        return false;
    }

    // Check if it's a regular file
    if (!std::filesystem::is_regular_file(path)) {
        std::cerr << "Error: Path is not a file: " << path << "\n";
        return false;
    }

    // Check if file has .xsd extension
    std::filesystem::path filePath(path);
    if (filePath.extension() != ".xsd") {
        std::cerr << "Warning: File does not have .xsd extension: " << path << "\n";
    }

    // Basic validation: check if file can be opened and is not empty
    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << "Error: Cannot open XSD file: " << path << "\n";
        return false;
    }

    // Check if file is not empty
    file.seekg(0, std::ios::end);
    if (file.tellg() == 0) {
        std::cerr << "Error: XSD file is empty: " << path << "\n";
        return false;
    }

    // Basic XML structure check
    file.seekg(0, std::ios::beg);
    std::string firstLine;
    std::getline(file, firstLine);

    // Very basic check: should start with XML declaration or have schema tag
    if (firstLine.find("<?xml") == std::string::npos &&
        firstLine.find("<xs:schema") == std::string::npos &&
        firstLine.find("<xsd:schema") == std::string::npos &&
        firstLine.find("<schema") == std::string::npos) {
        std::cerr << "Warning: File may not be a valid XSD (no XML/schema declaration found)\n";
    }

    return true;
}

bool CommandHandler::validateAndCreateDestDirectory(const std::string& path) {
    // Check if directory exists
    if (std::filesystem::exists(path)) {
        if (!std::filesystem::is_directory(path)) {
            std::cerr << "Error: Path exists but is not a directory: " << path << "\n";
            return false;
        }
        // Directory exists and is valid
        return true;
    }

    // Directory doesn't exist, ask user if they want to create it
    std::cout << "Directory does not exist: " << path << "\n";
    std::cout << "Do you want to create it? (y/n): ";

    std::string response;
    std::getline(std::cin, response);

    if (response.empty() || (response[0] != 'y' && response[0] != 'Y')) {
        std::cout << "Directory creation cancelled.\n";
        return false;
    }

    // Try to create the directory
    try {
        std::filesystem::create_directories(path);
        std::cout << "Directory created successfully: " << path << "\n";
        return true;
    } catch (const std::filesystem::filesystem_error& e) {
        std::cerr << "Error: Failed to create directory: " << e.what() << "\n";
        return false;
    }
}

bool CommandHandler::handleGenerateCommand(const std::string& input) {
    Lexer lexer(input);
    auto tokens = lexer.tokenize();

    // Expect: GENERATE XML <count> [PREFIX <prefix>]
    if (tokens.size() < 3) {
        std::cerr << "Error: GENERATE command requires XML and count\n";
        std::cerr << "Usage: GENERATE XML <count>\n";
        std::cerr << "       GENERATE XML <count> PREFIX <prefix>\n";
        return true;
    }

    // Check for XML keyword
    if (tokens[1].type != TokenType::XML) {
        std::cerr << "Error: Expected XML after GENERATE\n";
        return true;
    }

    // Get count
    if (tokens[2].type != TokenType::NUMBER) {
        std::cerr << "Error: Expected number after GENERATE XML\n";
        return true;
    }

    int count = 0;
    try {
        count = std::stoi(tokens[2].value);
    } catch (...) {
        std::cerr << "Error: Invalid count value\n";
        return true;
    }

    if (count <= 0) {
        std::cerr << "Error: Count must be positive\n";
        return true;
    }

    // Check for optional PREFIX
    std::string prefix = "generated_";
    if (tokens.size() >= 5 && tokens[3].type == TokenType::PREFIX) {
        if (tokens[4].type == TokenType::IDENTIFIER ||
            tokens[4].type == TokenType::STRING_LITERAL) {
            prefix = tokens[4].value;
        }
    }

    // Check if XSD is set
    if (!context_.hasXsdPath()) {
        std::cerr << "Error: XSD path not set. Use SET XSD <path> first\n";
        return true;
    }

    // Check if DEST is set
    if (!context_.hasDestPath()) {
        std::cerr << "Error: DEST path not set. Use SET DEST <path> first\n";
        return true;
    }

    std::string xsdPath = context_.getXsdPath().value();
    std::string destPath = context_.getDestPath().value();

    try {
        // Parse XSD schema
        std::cout << "Parsing XSD schema: " << xsdPath << "\n";
        auto schema = XsdParser::parse(xsdPath);

        // Generate XML files
        XmlGenerator generator;
        generator.generateFiles(*schema, count, destPath, prefix);

    } catch (const std::exception& e) {
        std::cerr << "Error generating XML files: " << e.what() << "\n";
        return true;
    }

    return true;
}

bool CommandHandler::handleCheckCommand(const std::string& input) {
    Lexer lexer(input);
    auto tokens = lexer.tokenize();

    // Expect: CHECK <path/pattern>
    if (tokens.size() < 2) {
        std::cerr << "Error: CHECK command requires a path or pattern\n";
        std::cerr << "Usage: CHECK /path/to/file.xml\n";
        std::cerr << "       CHECK /path/to/directory/\n";
        std::cerr << "       CHECK /path/to/*.xml\n";
        return true;
    }

    // Check if XSD is set
    if (!context_.hasXsdPath()) {
        std::cerr << "Error: XSD path not set. Use SET XSD <path> first\n";
        return true;
    }

    // Collect path from remaining tokens
    std::string pattern;
    for (size_t i = 1; i < tokens.size(); ++i) {
        if (tokens[i].type == TokenType::END_OF_INPUT) {
            break;
        }
        // Build path from tokens
        if (!pattern.empty() &&
            tokens[i].type != TokenType::DOT &&
            tokens[i].type != TokenType::SLASH &&
            tokens[i-1].type != TokenType::DOT &&
            tokens[i-1].type != TokenType::SLASH) {
            // Add space for paths with spaces
            if (tokens[i].type == TokenType::STRING_LITERAL ||
                tokens[i-1].type == TokenType::STRING_LITERAL) {
                pattern += " ";
            }
        }
        pattern += tokens[i].value;
    }

    if (pattern.empty()) {
        std::cerr << "Error: Pattern cannot be empty\n";
        return true;
    }

    std::string xsdPath = context_.getXsdPath().value();

    // Expand pattern to file list
    std::vector<std::string> files = XmlValidator::expandPattern(pattern);

    if (files.empty()) {
        std::cerr << "No XML files found matching pattern: " << pattern << "\n";
        return true;
    }

    std::cout << "\nValidating " << files.size() << " file(s) against XSD: "
              << xsdPath << "\n\n";

    // Validate all files with XSD
    XmlValidator validator;
    auto results = validator.validateFiles(files, xsdPath);

    // If in DSN mode and schema is loaded, perform DSN-specific validation
    if (context_.isDsnMode() && context_.hasDsnSchema()) {
        std::cout << "Performing DSN-specific validation...\n\n";

        DsnValidator dsnValidator(context_.getDsnSchema());

        // Perform DSN validation on each file
        for (auto& [filename, xsdResult] : results) {
            auto dsnResult = dsnValidator.validate(filename);

            // Add DSN errors
            for (const auto& dsnError : dsnResult.errors) {
                ValidationError error;
                error.message = "[DSN] " + dsnError.message;
                error.path = dsnError.field;
                xsdResult.errors.push_back(error);
                xsdResult.isValid = false;
            }

            // Add DSN warnings
            for (const auto& warning : dsnResult.warnings) {
                xsdResult.warnings.push_back("[DSN] " + warning);
            }
        }
    }

    // Display results
    int validCount = 0;
    int invalidCount = 0;

    for (const auto& [filename, result] : results) {
        // Get just the filename for cleaner display
        std::filesystem::path p(filename);
        std::string displayName = p.filename().string();

        if (result.isValid) {
            std::cout << "✓ " << displayName;
            if (!result.warnings.empty()) {
                std::cout << " (" << result.warnings.size() << " warning(s))";
            }
            std::cout << "\n";
            validCount++;

            // Show warnings if any
            if (!result.warnings.empty()) {
                for (const auto& warning : result.warnings) {
                    std::cout << "  ⚠ " << warning << "\n";
                }
            }
        } else {
            std::cout << "✗ " << displayName << " - INVALID\n";
            invalidCount++;

            // Show errors
            for (const auto& error : result.errors) {
                std::cout << "  ✗ " << error.message;
                if (!error.path.empty()) {
                    std::cout << " at " << error.path;
                }
                std::cout << "\n";
            }

            // Show warnings if any
            if (!result.warnings.empty()) {
                for (const auto& warning : result.warnings) {
                    std::cout << "  ⚠ " << warning << "\n";
                }
            }
        }
    }

    // Summary
    std::cout << "\n" << std::string(60, '-') << "\n";
    std::cout << "Summary: " << validCount << " valid, "
              << invalidCount << " invalid";
    if (validCount + invalidCount != static_cast<int>(files.size())) {
        int errorCount = files.size() - validCount - invalidCount;
        std::cout << ", " << errorCount << " error(s)";
    }
    std::cout << "\n";

    return true;
}

bool CommandHandler::handleDescribeCommand(const std::string& input) {
    Lexer lexer(input);
    auto tokens = lexer.tokenize();

    // Expect: DESCRIBE <field_name>
    if (tokens.size() < 2) {
        std::cerr << "Error: DESCRIBE command requires a field name\n";
        std::cerr << "Usage: DESCRIBE <field_name>\n";
        std::cerr << "Examples:\n";
        std::cerr << "  DESCRIBE 30_001          -- Show info for shortcut\n";
        std::cerr << "  DESCRIBE S21_G00_30_001  -- Show info for full name\n";
        std::cerr << "  DESCRIBE S21_G00_30      -- Show all fields in bloc\n";
        return true;
    }

    // Check if we're in DSN mode
    if (!context_.isDsnMode()) {
        std::cerr << "Error: DESCRIBE command is only available in DSN mode\n";
        std::cerr << "Use: SET MODE DSN\n";
        return true;
    }

    // Check if DSN schema is loaded
    if (!context_.hasDsnSchema()) {
        std::cerr << "Error: DSN schema not loaded\n";
        std::cerr << "Please set XSD path to a DSN schema file first\n";
        std::cerr << "Example: SET XSD ./ariane-xml-schemas/xsd_P26/mensuelle\\ P26/\n";
        return true;
    }

    // Get the field name from tokens
    std::string fieldName;
    for (size_t i = 1; i < tokens.size(); ++i) {
        if (tokens[i].type == TokenType::END_OF_INPUT) {
            break;
        }
        if (!fieldName.empty() && tokens[i].type != TokenType::DOT &&
            tokens[i-1].type != TokenType::DOT) {
            fieldName += "_";
        }
        fieldName += tokens[i].value;
    }

    if (fieldName.empty()) {
        std::cerr << "Error: Field name cannot be empty\n";
        return true;
    }

    auto schema = context_.getDsnSchema();

    // Check if it's a shortcut pattern (YY_ZZZ)
    std::regex shortcutPattern(R"(^\d{2,}_\d{3,}$)");
    bool isShortcut = std::regex_match(fieldName, shortcutPattern);

    // Check if it's a bloc pattern (SXX_GXX_YY or SXX.GXX.YY)
    std::regex blocPattern(R"(^S\d+[._]G\d+[._]\d+$)");
    bool isBloc = std::regex_match(fieldName, blocPattern);

    if (isShortcut) {
        // Look up by shortcut
        auto attributes = schema->findByShortId(fieldName);

        if (attributes.empty()) {
            std::cerr << "No DSN field found with shortcut: " << fieldName << "\n";
            return true;
        }

        if (attributes.size() == 1) {
            // Display single attribute
            const auto& attr = attributes[0];
            displayAttribute(attr);
        } else {
            // Multiple matches - show all
            std::cout << "Multiple fields found with shortcut '" << fieldName << "':\n\n";
            for (size_t i = 0; i < attributes.size(); ++i) {
                std::cout << "[" << (i+1) << "] ";
                displayAttribute(attributes[i]);
                if (i < attributes.size() - 1) {
                    std::cout << "\n";
                }
            }
        }
    } else if (isBloc) {
        // Convert dot notation to underscore if needed
        std::string blocName = fieldName;
        std::replace(blocName.begin(), blocName.end(), '_', '.');

        const DsnBloc* bloc = schema->findBloc(blocName);

        if (!bloc) {
            std::cerr << "No DSN bloc found: " << fieldName << "\n";
            return true;
        }

        displayBloc(*bloc);
    } else {
        // Try to find by full name
        const DsnAttribute* attr = schema->findByFullName(fieldName);

        if (!attr) {
            std::cerr << "No DSN field found: " << fieldName << "\n";
            std::cerr << "Use shortcut notation (e.g., 30_001) or full name (e.g., S21_G00_30_001)\n";
            return true;
        }

        displayAttribute(*attr);
    }

    return true;
}

void CommandHandler::displayAttribute(const DsnAttribute& attr) {
    std::cout << "╔═══════════════════════════════════════════════════════════════════\n";
    std::cout << "║ DSN Field Information\n";
    std::cout << "╠═══════════════════════════════════════════════════════════════════\n";
    std::cout << "║ Full Name:    " << attr.full_name << "\n";
    std::cout << "║ Shortcut:     " << attr.short_id << "\n";
    std::cout << "║ Bloc:         " << attr.bloc_name;
    if (!attr.bloc_label.empty()) {
        std::cout << " (" << attr.bloc_label << ")";
    }
    std::cout << "\n";

    if (!attr.description.empty()) {
        std::cout << "║ Description:  " << attr.description << "\n";
    }

    std::cout << "║ Type:         " << attr.type << "\n";
    std::cout << "║ Mandatory:    " << (attr.mandatory ? "Yes" : "No") << "\n";
    std::cout << "║ Occurrences:  " << attr.min_occurs << ".."
              << (attr.max_occurs == -1 ? "*" : std::to_string(attr.max_occurs)) << "\n";

    if (!attr.versions.empty()) {
        std::cout << "║ Versions:     ";
        for (size_t i = 0; i < attr.versions.size(); ++i) {
            std::cout << attr.versions[i];
            if (i < attr.versions.size() - 1) std::cout << ", ";
        }
        std::cout << "\n";
    }

    std::cout << "╚═══════════════════════════════════════════════════════════════════\n";
}

void CommandHandler::displayBloc(const DsnBloc& bloc) {
    std::cout << "╔═══════════════════════════════════════════════════════════════════\n";
    std::cout << "║ DSN Bloc Information\n";
    std::cout << "╠═══════════════════════════════════════════════════════════════════\n";
    std::cout << "║ Bloc Name:    " << bloc.name << "\n";
    std::cout << "║ Label:        " << bloc.label << "\n";

    if (!bloc.description.empty()) {
        std::cout << "║ Description:  " << bloc.description << "\n";
    }

    std::cout << "║ Mandatory:    " << (bloc.mandatory ? "Yes" : "No") << "\n";
    std::cout << "║ Occurrences:  " << bloc.min_occurs << ".."
              << (bloc.max_occurs == -1 ? "*" : std::to_string(bloc.max_occurs)) << "\n";
    std::cout << "║\n";
    std::cout << "║ Fields in this bloc:\n";
    std::cout << "╠═══════════════════════════════════════════════════════════════════\n";

    for (const auto& attr : bloc.attributes) {
        std::cout << "║ • " << attr.short_id << " (" << attr.full_name << ")\n";
        if (!attr.description.empty()) {
            std::cout << "║   " << attr.description << "\n";
        }
        std::cout << "║   Type: " << attr.type
                  << ", Mandatory: " << (attr.mandatory ? "Yes" : "No") << "\n";
    }

    std::cout << "╚═══════════════════════════════════════════════════════════════════\n";
}

} // namespace ariane_xml
