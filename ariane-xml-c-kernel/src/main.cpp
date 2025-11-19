#include "parser/lexer.h"
#include "parser/parser.h"
#include "executor/query_executor.h"
#include "utils/result_formatter.h"
#include "utils/app_context.h"
#include "utils/command_handler.h"
#include "utils/pseudonymisation_checker.h"
#include "dsn/dsn_autocomplete.h"
#include "dsn/dsn_parser.h"
#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>
#include <csignal>
#include <cstdlib>
#include <cstring>
#include <readline/readline.h>
#include <readline/history.h>
#include <sys/stat.h>
#include <unistd.h>
#include <pwd.h>

// History file path
static std::string historyFilePath;

// Global variables for DSN autocompletion
static std::unique_ptr<ariane_xml::DsnAutoComplete> g_autocomplete;
static ariane_xml::AppContext* g_context = nullptr;
static std::vector<std::string> g_completion_matches;

// Signal handler for CTRL-C (SIGINT)
void signalHandler(int signal) {
    if (signal == SIGINT) {
        // Save history before exiting
        if (!historyFilePath.empty()) {
            write_history(historyFilePath.c_str());
        }
        std::cout << "\n\nBye!\n";
        std::exit(0);
    }
}

// Get user's home directory
std::string getHomeDirectory() {
    const char* home = getenv("HOME");
    if (home != nullptr) {
        return std::string(home);
    }

    // Fallback to passwd entry
    struct passwd* pw = getpwuid(getuid());
    if (pw != nullptr && pw->pw_dir != nullptr) {
        return std::string(pw->pw_dir);
    }

    return "";
}

// Get history file path
std::string getHistoryFilePath() {
    std::string home = getHomeDirectory();
    if (home.empty()) {
        return "";
    }
    return home + "/.ariane-xml_history";
}

// Initialize command history
void initializeHistory() {
    historyFilePath = getHistoryFilePath();

    if (historyFilePath.empty()) {
        std::cerr << "Warning: Could not determine history file path\n";
        return;
    }

    // Set maximum history entries
    stifle_history(100);

    // Load existing history file
    read_history(historyFilePath.c_str());
}

// Save command history
void saveHistory() {
    if (!historyFilePath.empty()) {
        write_history(historyFilePath.c_str());
    }
}

// Update autocomplete instance when DSN schema is available
void updateAutoComplete() {
    if (!g_context) {
        return;
    }

    // Initialize autocomplete if in DSN mode and schema is available
    if (g_context->isDsnMode() && g_context->hasDsnSchema()) {
        auto schema = g_context->getDsnSchema();
        if (schema && !g_autocomplete) {
            g_autocomplete = std::make_unique<ariane_xml::DsnAutoComplete>(schema);
        }
    } else if (!g_context->isDsnMode()) {
        // Clear autocomplete when not in DSN mode
        g_autocomplete.reset();
    }
}

// Readline completion generator function
// This is called repeatedly by readline to get the next completion match
char* completion_generator(const char* text __attribute__((unused)), int state) {
    static size_t match_index = 0;

    // On first call (state == 0), generate all matches
    if (state == 0) {
        match_index = 0;
        g_completion_matches.clear();

        // Only provide completions if in DSN mode and autocomplete is initialized
        if (g_context && g_context->isDsnMode() && g_autocomplete) {
            std::string input = rl_line_buffer;
            size_t cursor_pos = rl_point;

            auto suggestions = g_autocomplete->getSuggestions(input, cursor_pos);

            // Extract just the completion strings
            for (const auto& suggestion : suggestions) {
                g_completion_matches.push_back(suggestion.completion);
            }
        }
    }

    // Return next match, or nullptr if no more matches
    if (match_index < g_completion_matches.size()) {
        // readline expects a malloc'd string that it will free
        const std::string& match = g_completion_matches[match_index++];
        char* result = static_cast<char*>(malloc(match.length() + 1));
        strcpy(result, match.c_str());
        return result;
    }

    return nullptr;
}

// Readline attempted completion function
// This is called when user presses TAB
char** attempted_completion(const char* text, int start __attribute__((unused)), int end __attribute__((unused))) {
    // Disable default filename completion
    rl_attempted_completion_over = 1;

    // Only provide completions in DSN mode
    if (!g_context || !g_context->isDsnMode() || !g_autocomplete) {
        return nullptr;
    }

    // Use our custom completion generator
    return rl_completion_matches(text, completion_generator);
}

void printWelcome() {
    std::cout << "XML Query CLI - Phase 2 (Interactive Mode)\n";
    std::cout << "Type 'help' for usage information.\n";
    std::cout << "Type 'exit', 'quit', or press Ctrl+C to exit.\n";
    std::cout << "Use UP/DOWN arrow keys to navigate command history.\n";
    std::cout << "Enter SQL-like queries to search XML files.\n";
    std::cout << "Note: Queries must be terminated with a semicolon (;)\n\n";
}

void printUsage(const char* programName) {
    std::cout << "ariane-xml - a FT XML parser for FT/DSI/DIP\n";
    std::cout << "Usage:\n";
    std::cout << "  " << programName << "              # Start interactive mode\n";
    std::cout << "  " << programName << " [query]      # Execute single query\n\n";
    std::cout << "Query Syntax:\n";
    std::cout << "  SELECT <field>[,<field>...] FROM <path>\n";
    std::cout << "  [WHERE <condition> [AND|OR <condition>...]]\n";
    std::cout << "  [ORDER BY <field>]\n";
    std::cout << "  [LIMIT <number>];\n\n";
    std::cout << "Note: In interactive mode, queries MUST be terminated with a semicolon (;)\n";
    std::cout << "      Multi-line queries are supported - press Enter to continue.\n\n";
    std::cout << "Examples:\n";
    std::cout << "  SELECT name FROM ./data WHERE length < 500;\n";
    std::cout << "  SELECT name FROM /path/to/files WHERE year > 2000 AND price < 30;\n";
    std::cout << "  SELECT name,price FROM ../data ORDER BY price LIMIT 5;\n\n";
    std::cout << "Multi-line example:\n";
    std::cout << "  SELECT name, price\n";
    std::cout << "  FROM ./data\n";
    std::cout << "  WHERE (price < 5 OR calories > 900)\n";
    std::cout << "    AND price < 7;\n\n";
    std::cout << "Features:\n";
    std::cout << "  - Field paths can use '.' or '/' as separators (e.g., food.name or food/name)\n";
    std::cout << "  - File paths can be quoted or unquoted (e.g., ./data or \"./data\")\n";
    std::cout << "  - Special field: FILE_NAME returns the name of the XML file\n";
    std::cout << "  - Comparison operators: =, !=, <, >, <=, >=\n";
    std::cout << "  - Logical operators: AND, OR with parentheses support for precedence\n";
    std::cout << "  - Parentheses: Group conditions (e.g., (A OR B) AND C)\n";
    std::cout << "  - ORDER BY: Sort results by field (numeric or alphabetic)\n";
    std::cout << "  - LIMIT: Restrict number of results returned\n\n";
    std::cout << "Interactive Commands:\n";
    std::cout << "  help, \\h         Show this help message\n";
    std::cout << "  exit, quit       Exit the program\n";
    std::cout << "  Ctrl+C           Exit the program (SIGINT)\n";
    std::cout << "  \\c               Clear screen\n";
    std::cout << "  UP/DOWN arrows   Navigate command history (last 100 queries)\n\n";
    std::cout << "Configuration Commands:\n";
    std::cout << "  SET XSD <path>        Set XSD schema file path\n";
    std::cout << "  SET DEST <path>       Set destination directory path\n";
    std::cout << "  SHOW XSD              Display current XSD path\n";
    std::cout << "  SHOW DEST             Display current DEST path\n\n";
    std::cout << "Generation Commands:\n";
    std::cout << "  GENERATE XML <count>              Generate <count> XML files from XSD\n";
    std::cout << "  GENERATE XML <count> PREFIX <pre> Generate with custom filename prefix\n\n";
    std::cout << "Validation Commands:\n";
    std::cout << "  CHECK <file>        Validate a single XML file against XSD\n";
    std::cout << "  CHECK <directory>   Validate all XML files in a directory\n";
    std::cout << "  CHECK <pattern>     Validate files matching pattern (e.g., /path/*.xml)\n\n";
}

// Helper function to draw progress bar
std::string drawProgressBar(size_t completed, size_t total, size_t barWidth = 30) {
    float progress = total > 0 ? static_cast<float>(completed) / total : 0.0f;
    size_t pos = static_cast<size_t>(barWidth * progress);

    std::string bar = "[";
    for (size_t i = 0; i < barWidth; ++i) {
        if (i < pos) bar += "=";
        else if (i == pos) bar += ">";
        else bar += " ";
    }
    bar += "]";

    return bar;
}

// Helper to check pseudonymisation status of files and display warning in DSN mode
// Returns pair: (pseudonymised_files, non_pseudonymised_files)
std::pair<std::vector<std::string>, std::vector<std::string>>
checkPseudonymisationStatus(const std::vector<std::string>& files) {
    std::vector<std::string> pseudonymised;
    std::vector<std::string> nonPseudonymised;

    for (const auto& file : files) {
        if (ariane_xml::PseudonymisationChecker::isPseudonymised(file)) {
            pseudonymised.push_back(file);
        } else {
            nonPseudonymised.push_back(file);
        }
    }

    return {pseudonymised, nonPseudonymised};
}

// Display pseudonymisation warning for DSN mode
void displayPseudonymisationWarning(const std::vector<std::string>& nonPseudonymisedFiles,
                                     size_t totalFiles) {
    if (nonPseudonymisedFiles.empty()) {
        return;
    }

    std::cout << "\n\033[33m";  // Yellow color
    std::cout << "WARNING: Non-pseudonymised data detected in DSN mode\n";
    std::cout << "=========================================================\n";
    std::cout << nonPseudonymisedFiles.size() << " of " << totalFiles
              << " file(s) are not pseudonymised:\n";

    // Show up to 5 files, then summarize
    size_t showCount = std::min(nonPseudonymisedFiles.size(), size_t(5));
    for (size_t i = 0; i < showCount; ++i) {
        std::cout << "  - " << nonPseudonymisedFiles[i] << "\n";
    }
    if (nonPseudonymisedFiles.size() > 5) {
        std::cout << "  ... and " << (nonPseudonymisedFiles.size() - 5) << " more\n";
    }

    std::cout << "\nDSN mode requires pseudonymised data for compliance.\n";
    std::cout << "Use 'PSEUDONYMISE <file>' to pseudonymise files.\n";
    std::cout << "\033[0m\n";  // Reset color
}

void executeQuery(const std::string& query, const ariane_xml::AppContext* context = nullptr) {
    if (query.empty()) {
        return;
    }

    try {
        // Lexical analysis
        ariane_xml::Lexer lexer(query);
        auto tokens = lexer.tokenize();

        // Syntax analysis
        ariane_xml::Parser parser(tokens);
        auto ast = parser.parse();

        // Check for ambiguous attributes if in verbose mode
        if (context && context->isVerbose()) {
            auto ambiguous = ariane_xml::QueryExecutor::checkForAmbiguousAttributes(*ast);
            if (ambiguous.empty()) {
                std::cout << "\033[32m✓ No ambiguous attributes found\033[0m\n\n";
            } else {
                std::cout << "\033[33m⚠ Ambiguous attribute(s): ";
                for (size_t i = 0; i < ambiguous.size(); ++i) {
                    if (i > 0) std::cout << ", ";
                    std::cout << ambiguous[i];
                }
                std::cout << "\033[0m\n\n";
            }
        }

        // Check pseudonymisation status if in DSN mode
        if (context && context->isDsnMode()) {
            // Get files that will be queried
            auto xmlFiles = ariane_xml::QueryExecutor::getXmlFiles(ast->from_path);

            if (!xmlFiles.empty()) {
                auto [pseudonymised, nonPseudonymised] = checkPseudonymisationStatus(xmlFiles);

                // Display warning for non-pseudonymised files
                displayPseudonymisationWarning(nonPseudonymised, xmlFiles.size());

                // If all files are non-pseudonymised, show additional warning
                if (pseudonymised.empty() && !nonPseudonymised.empty()) {
                    std::cout << "\033[33mNote: Query results may contain sensitive unprotected data.\033[0m\n\n";
                }
                // If some files are pseudonymised, note that results are mixed
                else if (!pseudonymised.empty() && !nonPseudonymised.empty()) {
                    std::cout << "\033[33mNote: Results include data from both protected and unprotected files.\033[0m\n\n";
                }
            }
        }

        // Execute query
        std::vector<ariane_xml::ResultRow> results;

        if (context && context->isVerbose()) {
            // Use progress tracking in VERBOSE mode
            ariane_xml::ExecutionStats stats;
            std::string lastProgressLine;

            auto progressCallback = [&lastProgressLine](size_t completed, size_t total, size_t threadCount) {
                // Clear previous line
                if (!lastProgressLine.empty()) {
                    std::cout << "\r" << std::string(lastProgressLine.length(), ' ') << "\r";
                }

                // Build progress bar
                std::string bar = drawProgressBar(completed, total, 30);
                float percent = total > 0 ? (static_cast<float>(completed) / total * 100.0f) : 0.0f;

                // Format: [========>           ] 45/100 files (8 threads)
                std::ostringstream oss;
                oss << "\033[36m" << bar << " "
                    << completed << "/" << total << " files";

                if (threadCount > 1) {
                    oss << " (" << threadCount << " threads)";
                }

                oss << " " << std::fixed << std::setprecision(1) << percent << "%\033[0m";

                lastProgressLine = oss.str();
                std::cout << lastProgressLine << std::flush;
            };

            results = ariane_xml::QueryExecutor::executeWithProgress(*ast, progressCallback, &stats);

            // Clear progress line
            if (!lastProgressLine.empty()) {
                std::cout << "\r" << std::string(lastProgressLine.length(), ' ') << "\r";
            }

            // Print execution summary
            if (stats.used_threading) {
                std::cout << "\033[32m✓ Processed " << stats.total_files << " files in "
                          << std::fixed << std::setprecision(2) << stats.execution_time_seconds
                          << "s (" << stats.thread_count << " threads)\033[0m\n\n";
            } else {
                std::cout << "\033[32m✓ Processed " << stats.total_files << " file(s) in "
                          << std::fixed << std::setprecision(2) << stats.execution_time_seconds
                          << "s\033[0m\n\n";
            }

        } else {
            // Non-verbose mode: use standard execution
            results = ariane_xml::QueryExecutor::execute(*ast);
        }

        // Format and print results
        ariane_xml::ResultFormatter::print(results);

    } catch (const ariane_xml::ParseError& e) {
        std::cerr << "Parse Error: " << e.what() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

// Helper function to escape JSON strings
std::string escapeJson(const std::string& str) {
    std::string result;
    result.reserve(str.length());

    for (char c : str) {
        switch (c) {
            case '"':  result += "\\\""; break;
            case '\\': result += "\\\\"; break;
            case '\b': result += "\\b";  break;
            case '\f': result += "\\f";  break;
            case '\n': result += "\\n";  break;
            case '\r': result += "\\r";  break;
            case '\t': result += "\\t";  break;
            default:
                if (static_cast<unsigned char>(c) < 0x20) {
                    // Control characters
                    char buf[7];
                    snprintf(buf, sizeof(buf), "\\u%04x", static_cast<unsigned char>(c));
                    result += buf;
                } else {
                    result += c;
                }
                break;
        }
    }

    return result;
}

// Convert AutoCompleteSuggestion type to string
std::string typeToString(ariane_xml::AutoCompleteSuggestion::Type type) {
    switch (type) {
        case ariane_xml::AutoCompleteSuggestion::Type::FIELD:
            return "field";
        case ariane_xml::AutoCompleteSuggestion::Type::BLOC:
            return "bloc";
        case ariane_xml::AutoCompleteSuggestion::Type::KEYWORD:
            return "keyword";
        default:
            return "unknown";
    }
}

// Handle autocomplete request (for Jupyter kernel integration)
int handleAutocomplete(int argc, char* argv[]) {
    // Usage: ariane-xml --autocomplete <query> <cursor_pos> [--version <P25|P26|AUTO>]
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] << " --autocomplete <query> <cursor_pos> [--version <P25|P26|AUTO>]" << std::endl;
        return 1;
    }

    std::string query = argv[2];
    int cursor_pos = std::atoi(argv[3]);
    std::string version = "AUTO";  // Default version

    // Parse optional version parameter
    if (argc >= 6 && std::string(argv[4]) == "--version") {
        version = argv[5];
    }

    try {
        // Initialize context with DSN mode
        ariane_xml::AppContext context;
        context.setMode(ariane_xml::QueryMode::DSN);
        context.setDsnVersion(version);

        // Load DSN schema directly
        std::string schemaDir;
        if (version == "P25") {
            schemaDir = "ariane-xml-schemas/xsd_P25/mensuelle P25";
        } else if (version == "P26") {
            schemaDir = "ariane-xml-schemas/xsd_P26/mensuelle P26";
        } else {
            // AUTO: try P26 first, fallback to P25
            schemaDir = "ariane-xml-schemas/xsd_P26/mensuelle P26";
        }

        // Parse schema from directory
        auto schema = ariane_xml::DsnParser::parseDirectory(schemaDir, version);

        // Check if schema loaded successfully
        if (!schema || schema->getAttributes().empty()) {
            // Return empty suggestions if schema not available
            std::cout << "[]" << std::endl;
            return 0;
        }

        context.setDsnSchema(schema);

        // Create autocomplete instance
        ariane_xml::DsnAutoComplete autocomplete(schema);

        // Get suggestions
        auto suggestions = autocomplete.getSuggestions(query, cursor_pos);

        // Output as JSON array
        std::cout << "[";
        for (size_t i = 0; i < suggestions.size(); ++i) {
            if (i > 0) {
                std::cout << ",";
            }
            std::cout << "{";
            std::cout << "\"completion\":\"" << escapeJson(suggestions[i].completion) << "\",";
            std::cout << "\"display\":\"" << escapeJson(suggestions[i].display) << "\",";
            std::cout << "\"description\":\"" << escapeJson(suggestions[i].description) << "\",";
            std::cout << "\"type\":\"" << typeToString(suggestions[i].type) << "\"";
            std::cout << "}";
        }
        std::cout << "]" << std::endl;

        return 0;

    } catch (const std::exception& e) {
        // On error, return empty array (fail gracefully for autocomplete)
        std::cerr << "Autocomplete error: " << e.what() << std::endl;
        std::cout << "[]" << std::endl;
        return 1;
    }
}

void interactiveMode() {
    // Register signal handler for CTRL-C
    std::signal(SIGINT, signalHandler);

    // Initialize command history
    initializeHistory();

    // Create application context and command handler
    ariane_xml::AppContext context;
    ariane_xml::CommandHandler commandHandler(context);

    // Set global context for autocomplete
    g_context = &context;

    // Set up readline completion
    rl_attempted_completion_function = attempted_completion;

    printWelcome();

    std::string query;
    char* lineBuffer = nullptr;

    while (true) {
        // Set prompt based on whether we're continuing a query
        const char* prompt = query.empty() ? "ariane-xml> " : "      -> ";

        // Read line with readline (supports arrow keys, history, etc.)
        lineBuffer = readline(prompt);

        // Check for EOF (Ctrl+D)
        if (lineBuffer == nullptr) {
            std::cout << "\nBye!\n";
            saveHistory();
            g_context = nullptr;
            g_autocomplete.reset();
            break;
        }

        // Convert to C++ string
        std::string line(lineBuffer);
        free(lineBuffer);

        // Trim leading whitespace only (preserve trailing for semicolon check)
        size_t firstNonSpace = line.find_first_not_of(" \t\n\r");
        if (firstNonSpace == std::string::npos) {
            // Line is all whitespace - treat as empty
            if (query.empty()) {
                continue;  // Skip completely empty lines when no query in progress
            } else {
                // Add newline to query and continue
                query += "\n";
                continue;
            }
        }

        // Trim leading whitespace
        line = line.substr(firstNonSpace);

        // Check for special commands (only when no query is in progress)
        if (query.empty()) {
            // Trim trailing whitespace for command comparison
            std::string trimmedLine = line;
            trimmedLine.erase(trimmedLine.find_last_not_of(" \t\n\r") + 1);

            if (trimmedLine == "exit" || trimmedLine == "quit" || trimmedLine == "\\q") {
                std::cout << "Bye!\n";
                saveHistory();
                g_context = nullptr;
                g_autocomplete.reset();
                break;
            }

            if (trimmedLine == "help" || trimmedLine == "\\h" || trimmedLine == "\\?") {
                printUsage("ariane-xml");
                continue;
            }

            if (trimmedLine == "\\c" || trimmedLine == "clear") {
                std::cout << "\033[2J\033[1;1H"; // ANSI clear screen
                continue;
            }
        }

        // Look for semicolon in the line
        size_t semicolonPos = line.find(';');

        if (semicolonPos != std::string::npos) {
            // Found a semicolon - check if there's anything after it (except whitespace)
            std::string afterSemicolon = line.substr(semicolonPos + 1);
            size_t firstNonWhitespace = afterSemicolon.find_first_not_of(" \t\n\r");

            if (firstNonWhitespace != std::string::npos) {
                // There's non-whitespace content after the semicolon
                std::cerr << "Error: Unexpected text after semicolon: '"
                          << afterSemicolon.substr(firstNonWhitespace) << "'\n";
                query.clear();
                continue;
            }

            // Append everything before the semicolon to the query
            if (!query.empty()) {
                query += " ";
            }
            query += line.substr(0, semicolonPos);

            // Add completed query to history (with semicolon, only if not empty)
            if (!query.empty()) {
                std::string historyEntry = query + ";";
                add_history(historyEntry.c_str());
            }

            // Check if it's a SET or SHOW command
            if (!commandHandler.handleCommand(query)) {
                // Not a command, execute as a query
                executeQuery(query, &context);
                std::cout << std::endl;
            }

            // Update autocomplete after command execution (e.g., after SET MODE DSN)
            updateAutoComplete();

            // Reset for next query
            query.clear();
        } else {
            // No semicolon found - continue accumulating the query
            if (!query.empty()) {
                query += " ";
            }
            query += line;
        }
    }
}

int main(int argc, char* argv[]) {
    try {
        // No arguments: enter interactive mode
        if (argc < 2) {
            interactiveMode();
            return 0;
        }

        // Handle autocomplete mode (for Jupyter kernel integration)
        std::string arg = argv[1];
        if (arg == "--autocomplete") {
            return handleAutocomplete(argc, argv);
        }

        // Handle help flag
        if (arg == "-h" || arg == "--help") {
            printUsage(argv[0]);
            return 0;
        }

        // Single query mode: execute query from command line
        std::string query = argv[1];
        executeQuery(query);

        return 0;

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}
