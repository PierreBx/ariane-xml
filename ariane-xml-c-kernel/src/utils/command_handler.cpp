#include "utils/command_handler.h"
#include "parser/lexer.h"
#include "generator/xsd_parser.h"
#include "generator/xml_generator.h"
#include "validator/xml_validator.h"
#include "dsn/dsn_schema.h"
#include "dsn/dsn_templates.h"
#include "dsn/dsn_migration.h"
#include <iostream>
#include <filesystem>
#include <fstream>
#include <iomanip>

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

    // Check if it's a DSN_TEMPLATE command
    if (tokens[0].type == TokenType::TEMPLATE) {
        return handleDsnTemplateCommand(input);
    }

    // Check if it's a DSN_COMPARE command
    if (tokens[0].type == TokenType::COMPARE) {
        return handleDsnCompareCommand(input);
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
    if (validateXsdFile(path)) {
        context_.setXsdPath(path);
        std::cout << "XSD path set to: " << path << "\n";
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

    // Validate all files
    XmlValidator validator;
    auto results = validator.validateFiles(files, xsdPath);

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
    // DESCRIBE <field_name>
    // Shows information about a DSN field

    if (!context_.isDsnMode()) {
        std::cerr << "Error: DESCRIBE command only available in DSN mode\n";
        std::cerr << "Use: SET MODE DSN\n";
        return true;
    }

    Lexer lexer(input);
    auto tokens = lexer.tokenize();

    if (tokens.size() < 2) {
        std::cerr << "Error: DESCRIBE requires a field name or bloc\n";
        std::cerr << "Usage: DESCRIBE <field_name>\n";
        std::cerr << "       DESCRIBE S21_G00_30_001\n";
        std::cerr << "       DESCRIBE 30_001\n";
        std::cerr << "       DESCRIBE S21_G00_30\n";
        return true;
    }

    if (!context_.hasDsnSchema()) {
        std::cerr << "Error: No DSN schema loaded\n";
        std::cerr << "Please load a DSN schema first\n";
        return true;
    }

    std::string field_name = tokens[1].value;
    auto schema = context_.getDsnSchema();

    // Try to find by full name
    const DsnAttribute* attr = schema->findByFullName(field_name);
    if (attr) {
        std::cout << "\n";
        std::cout << "══════════════════════════════════════════════════════════════\n";
        std::cout << " Field: " << attr->full_name << "\n";
        std::cout << "══════════════════════════════════════════════════════════════\n\n";
        std::cout << "Shortcut:     " << attr->short_id << "\n";
        std::cout << "Bloc:         " << attr->bloc_name;
        if (!attr->bloc_label.empty()) {
            std::cout << " (" << attr->bloc_label << ")";
        }
        std::cout << "\n";
        std::cout << "Description:  " << attr->description << "\n";
        std::cout << "Type:         " << attr->type << "\n";
        std::cout << "Mandatory:    " << (attr->mandatory ? "Yes" : "No") << "\n";
        std::cout << "Cardinality:  " << attr->min_occurs << "..";
        if (attr->max_occurs < 0) {
            std::cout << "unbounded";
        } else {
            std::cout << attr->max_occurs;
        }
        std::cout << "\n\n";
        return true;
    }

    // Try to find by shortcut
    auto matches = schema->findByShortId(field_name);
    if (!matches.empty()) {
        if (matches.size() == 1) {
            const auto& match = matches[0];
            std::cout << "\n";
            std::cout << "══════════════════════════════════════════════════════════════\n";
            std::cout << " Field: " << match.full_name << "\n";
            std::cout << "══════════════════════════════════════════════════════════════\n\n";
            std::cout << "Shortcut:     " << match.short_id << "\n";
            std::cout << "Bloc:         " << match.bloc_name;
            if (!match.bloc_label.empty()) {
                std::cout << " (" << match.bloc_label << ")";
            }
            std::cout << "\n";
            std::cout << "Description:  " << match.description << "\n";
            std::cout << "Type:         " << match.type << "\n";
            std::cout << "Mandatory:    " << (match.mandatory ? "Yes" : "No") << "\n\n";
        } else {
            std::cout << "\n⚠ Ambiguous shortcut '" << field_name << "' matches multiple fields:\n\n";
            for (const auto& match : matches) {
                std::cout << "  • " << match.full_name << " in " << match.bloc_label << "\n";
                std::cout << "    " << match.description << "\n\n";
            }
            std::cout << "Use the full field name to specify which one you mean.\n\n";
        }
        return true;
    }

    // Try as bloc
    const DsnBloc* bloc = schema->findBloc(field_name);
    if (bloc) {
        std::cout << "\n";
        std::cout << "══════════════════════════════════════════════════════════════\n";
        std::cout << " Bloc: " << bloc->name;
        if (!bloc->label.empty()) {
            std::cout << " (" << bloc->label << ")";
        }
        std::cout << "\n";
        std::cout << "══════════════════════════════════════════════════════════════\n\n";
        if (!bloc->description.empty()) {
            std::cout << "Description:  " << bloc->description << "\n\n";
        }
        std::cout << "Fields:\n";
        for (const auto& attr : bloc->attributes) {
            std::cout << "  • " << std::left << std::setw(25) << attr.full_name
                     << " - " << attr.description << "\n";
        }
        std::cout << "\n";
        return true;
    }

    std::cerr << "Field or bloc not found: " << field_name << "\n";
    return true;
}

bool CommandHandler::handleDsnTemplateCommand(const std::string& input) {
    // TEMPLATE <template_name> [SET param=value ...]
    // Or: TEMPLATE LIST

    if (!context_.isDsnMode()) {
        std::cerr << "Error: TEMPLATE command only available in DSN mode\n";
        std::cerr << "Use: SET MODE DSN\n";
        return true;
    }

    Lexer lexer(input);
    auto tokens = lexer.tokenize();

    if (tokens.size() < 2) {
        std::cerr << "Error: TEMPLATE requires a template name or LIST\n";
        std::cerr << "Usage: TEMPLATE LIST\n";
        std::cerr << "       TEMPLATE <name>\n";
        std::cerr << "       TEMPLATE <name> SET param1=value1 param2=value2\n";
        return true;
    }

    // Create template manager
    DsnTemplateManager tmplMgr;

    // Check for LIST command
    if (tokens[1].type == TokenType::LIST) {
        auto templates = tmplMgr.listTemplates();
        std::cout << DsnTemplateManager::formatTemplateList(templates);
        return true;
    }

    // Get template name
    std::string template_name = tokens[1].value;
    const DsnTemplate* tmpl = tmplMgr.getTemplate(template_name);

    if (!tmpl) {
        std::cerr << "Template not found: " << template_name << "\n";
        std::cerr << "Use: TEMPLATE LIST to see available templates\n";
        return true;
    }

    // Parse parameters if SET keyword is present
    std::map<std::string, std::string> params;
    if (tokens.size() > 2 && tokens[2].type == TokenType::SET) {
        // Parse param=value pairs
        for (size_t i = 3; i < tokens.size(); ++i) {
            if (tokens[i].type == TokenType::END_OF_INPUT) break;

            // Expect: param=value
            std::string param_expr = tokens[i].value;
            size_t eq_pos = param_expr.find('=');
            if (eq_pos != std::string::npos) {
                std::string key = param_expr.substr(0, eq_pos);
                std::string value = param_expr.substr(eq_pos + 1);
                params[key] = value;
            } else if (tokens[i].type == TokenType::IDENTIFIER && i+1 < tokens.size() &&
                      tokens[i+1].type == TokenType::EQUALS && i+2 < tokens.size()) {
                params[tokens[i].value] = tokens[i+2].value;
                i += 2;
            }
        }
    }

    // Expand template
    std::string query = tmplMgr.expandTemplate(template_name, params);

    std::cout << "\nTemplate: " << tmpl->name << "\n";
    std::cout << "Description: " << tmpl->description << "\n\n";
    std::cout << "Expanded query:\n";
    std::cout << "───────────────────────────────────────────────────────────────\n";
    std::cout << query << "\n";
    std::cout << "───────────────────────────────────────────────────────────────\n\n";

    // Note: The actual query execution would be handled by the query executor
    std::cout << "To execute this query, run it directly or integrate with query executor.\n";

    return true;
}

bool CommandHandler::handleDsnCompareCommand(const std::string& input) {
    // COMPARE <version1> <version2>
    // Or: COMPARE <version1> <version2> CHECK <file>

    if (!context_.isDsnMode()) {
        std::cerr << "Error: COMPARE command only available in DSN mode\n";
        std::cerr << "Use: SET MODE DSN\n";
        return true;
    }

    Lexer lexer(input);
    auto tokens = lexer.tokenize();

    if (tokens.size() < 3) {
        std::cerr << "Error: COMPARE requires two version identifiers\n";
        std::cerr << "Usage: COMPARE P25 P26\n";
        std::cerr << "       COMPARE P25 P26 CHECK /path/to/file.xml\n";
        return true;
    }

    std::string version1 = tokens[1].value;
    std::string version2 = tokens[2].value;

    std::cout << "\nComparing DSN schemas: " << version1 << " → " << version2 << "\n";
    std::cout << "\nNote: This feature requires loading both P25 and P26 schemas.\n";
    std::cout << "Schema comparison functionality will display:\n";
    std::cout << "  • New fields added in " << version2 << "\n";
    std::cout << "  • Fields removed from " << version1 << "\n";
    std::cout << "  • Fields with modified properties\n";
    std::cout << "  • Migration compatibility advice\n\n";

    // TODO: Implement actual schema loading and comparison
    // For now, show a placeholder message
    std::cout << "Implementation note: Full schema comparison requires:\n";
    std::cout << "  1. Loading DSN schema for " << version1 << "\n";
    std::cout << "  2. Loading DSN schema for " << version2 << "\n";
    std::cout << "  3. Using DsnMigrationHelper to compare schemas\n\n";

    return true;
}

} // namespace ariane_xml
