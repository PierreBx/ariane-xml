#include "dsn/dsn_autocomplete.h"
#include <algorithm>
#include <sstream>
#include <iomanip>
#include <cctype>

namespace ariane_xml {

// SQL keywords commonly used in DSN queries
const std::vector<std::string> DsnAutoComplete::SQL_KEYWORDS = {
    "SELECT", "FROM", "WHERE", "AND", "OR", "NOT", "IS", "NULL",
    "LIMIT", "OFFSET", "ORDER", "BY", "ASC", "DESC", "DISTINCT",
    "COUNT", "SUM", "AVG", "MIN", "MAX",
    "SET", "MODE", "DSN", "STANDARD", "SHOW", "DESCRIBE",
    "CHECK", "GENERATE", "VERBOSE"
};

DsnAutoComplete::DsnAutoComplete(std::shared_ptr<DsnSchema> schema)
    : schema_(schema) {}

std::vector<AutoCompleteSuggestion> DsnAutoComplete::getSuggestions(
    const std::string& input,
    size_t cursor_pos
) {
    std::vector<AutoCompleteSuggestion> suggestions;

    if (!schema_) {
        return suggestions;
    }

    // Extract the word being completed
    std::string current_word = extractCurrentWord(input, cursor_pos);
    if (current_word.empty()) {
        return suggestions;
    }

    // Determine context
    CompletionContext ctx = getContext(input, cursor_pos);

    // Get suggestions based on context
    switch (ctx) {
        case CompletionContext::FIELD:
            suggestions = getPathSuggestions(current_word);
            if (suggestions.empty()) {
                auto shortcut_sugs = getShortcutSuggestions(current_word);
                suggestions.insert(suggestions.end(), shortcut_sugs.begin(), shortcut_sugs.end());
            }
            break;

        case CompletionContext::BLOC:
            suggestions = getBlocSuggestions(current_word);
            break;

        case CompletionContext::KEYWORD:
            suggestions = getKeywordSuggestions(current_word);
            break;

        case CompletionContext::UNKNOWN:
            // Try all contexts
            suggestions = getKeywordSuggestions(current_word);
            auto path_sugs = getPathSuggestions(current_word);
            suggestions.insert(suggestions.end(), path_sugs.begin(), path_sugs.end());
            auto bloc_sugs = getBlocSuggestions(current_word);
            suggestions.insert(suggestions.end(), bloc_sugs.begin(), bloc_sugs.end());
            break;
    }

    return suggestions;
}

std::vector<AutoCompleteSuggestion> DsnAutoComplete::getPathSuggestions(
    const std::string& partial_path
) {
    std::vector<AutoCompleteSuggestion> suggestions;

    if (!schema_) {
        return suggestions;
    }

    // Get all attributes from schema
    const auto& attrs = schema_->getAttributes();

    for (const auto& [full_name, attr] : attrs) {
        if (startsWith(full_name, partial_path)) {
            std::ostringstream display;
            display << std::left << std::setw(25) << full_name;
            if (!attr.description.empty()) {
                display << " - " << attr.description;
            }

            suggestions.emplace_back(
                full_name,
                display.str(),
                attr.description,
                AutoCompleteSuggestion::Type::FIELD
            );
        }
    }

    return suggestions;
}

std::vector<AutoCompleteSuggestion> DsnAutoComplete::getBlocSuggestions(
    const std::string& partial_bloc
) {
    std::vector<AutoCompleteSuggestion> suggestions;

    if (!schema_) {
        return suggestions;
    }

    // Get all blocs from schema
    const auto& blocs = schema_->getBlocs();

    for (const auto& bloc : blocs) {
        // Convert bloc.name (S21.G00.30) to path format (S21_G00_30)
        std::string bloc_path = bloc.name;
        std::replace(bloc_path.begin(), bloc_path.end(), '.', '_');

        if (startsWith(bloc_path, partial_bloc)) {
            std::ostringstream display;
            display << std::left << std::setw(20) << bloc_path;
            if (!bloc.label.empty()) {
                display << " (" << bloc.label << ")";
            }

            suggestions.emplace_back(
                bloc_path,
                display.str(),
                bloc.label + ": " + bloc.description,
                AutoCompleteSuggestion::Type::BLOC
            );
        }
    }

    return suggestions;
}

std::vector<AutoCompleteSuggestion> DsnAutoComplete::getShortcutSuggestions(
    const std::string& partial_shortcut
) {
    std::vector<AutoCompleteSuggestion> suggestions;

    if (!schema_) {
        return suggestions;
    }

    // Get all shortcuts from schema
    const auto& shortcuts = schema_->getShortcutMap();

    for (const auto& [shortcut, attrs] : shortcuts) {
        if (startsWith(shortcut, partial_shortcut)) {
            // If multiple attributes match (ambiguous), show all
            for (const auto& attr : attrs) {
                std::ostringstream display;
                display << std::left << std::setw(15) << shortcut
                        << " -> " << std::setw(25) << attr.full_name;
                if (!attr.description.empty()) {
                    display << " - " << attr.description.substr(0, 50);
                }

                std::string desc = attr.description;
                if (attrs.size() > 1) {
                    desc = "[AMBIGUOUS] " + desc + " (in " + attr.bloc_label + ")";
                }

                suggestions.emplace_back(
                    attr.full_name,  // Complete to full name to avoid ambiguity
                    display.str(),
                    desc,
                    AutoCompleteSuggestion::Type::FIELD
                );
            }
        }
    }

    return suggestions;
}

std::vector<AutoCompleteSuggestion> DsnAutoComplete::getKeywordSuggestions(
    const std::string& partial_keyword
) {
    std::vector<AutoCompleteSuggestion> suggestions;

    // Convert partial to uppercase for comparison
    std::string upper_partial = partial_keyword;
    std::transform(upper_partial.begin(), upper_partial.end(),
                   upper_partial.begin(), ::toupper);

    for (const auto& keyword : SQL_KEYWORDS) {
        if (startsWith(keyword, upper_partial)) {
            suggestions.emplace_back(
                keyword,
                keyword,
                "SQL keyword",
                AutoCompleteSuggestion::Type::KEYWORD
            );
        }
    }

    return suggestions;
}

std::string DsnAutoComplete::formatSuggestions(
    const std::vector<AutoCompleteSuggestion>& suggestions,
    size_t max_display
) {
    if (suggestions.empty()) {
        return "";
    }

    std::ostringstream output;
    output << "\nSuggestions:\n";

    size_t count = 0;
    for (const auto& sug : suggestions) {
        if (count >= max_display) {
            output << "  ... (" << (suggestions.size() - max_display)
                   << " more suggestions)\n";
            break;
        }

        output << "  " << sug.display << "\n";
        count++;
    }

    return output.str();
}

std::string DsnAutoComplete::extractCurrentWord(
    const std::string& input,
    size_t cursor_pos
) {
    if (input.empty() || cursor_pos > input.length()) {
        return "";
    }

    // Find word boundaries
    size_t start = cursor_pos;
    while (start > 0 && !std::isspace(input[start - 1]) &&
           input[start - 1] != ',' && input[start - 1] != '(' &&
           input[start - 1] != ')') {
        start--;
    }

    size_t end = cursor_pos;
    while (end < input.length() && !std::isspace(input[end]) &&
           input[end] != ',' && input[end] != '(' && input[end] != ')') {
        end++;
    }

    return input.substr(start, end - start);
}

DsnAutoComplete::CompletionContext DsnAutoComplete::getContext(
    const std::string& input,
    size_t cursor_pos
) {
    // Simple heuristic: look for keywords before cursor
    std::string before_cursor = input.substr(0, cursor_pos);
    std::transform(before_cursor.begin(), before_cursor.end(),
                   before_cursor.begin(), ::toupper);

    // If we find SELECT, FROM, or WHERE recently, we're likely completing a field
    if (before_cursor.find("SELECT") != std::string::npos ||
        before_cursor.find("WHERE") != std::string::npos) {
        return CompletionContext::FIELD;
    }

    // If we find FROM, we might be completing a path
    if (before_cursor.find("FROM") != std::string::npos) {
        // Check if there's already a path after FROM
        size_t from_pos = before_cursor.rfind("FROM");
        if (from_pos != std::string::npos) {
            std::string after_from = before_cursor.substr(from_pos + 4);
            if (after_from.find_first_not_of(" \t\n") == std::string::npos) {
                return CompletionContext::UNKNOWN;  // Expecting file path
            }
        }
        return CompletionContext::FIELD;
    }

    // If at the start or after whitespace, likely a keyword
    if (cursor_pos == 0 || std::isspace(input[cursor_pos - 1])) {
        return CompletionContext::KEYWORD;
    }

    return CompletionContext::UNKNOWN;
}

bool DsnAutoComplete::startsWith(const std::string& str, const std::string& prefix) {
    if (prefix.length() > str.length()) {
        return false;
    }

    return std::equal(prefix.begin(), prefix.end(), str.begin(),
                     [](char a, char b) {
                         return std::tolower(a) == std::tolower(b);
                     });
}

} // namespace ariane_xml
