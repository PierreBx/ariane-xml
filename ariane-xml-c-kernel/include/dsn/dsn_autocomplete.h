#ifndef DSN_AUTOCOMPLETE_H
#define DSN_AUTOCOMPLETE_H

#include "dsn_schema.h"
#include <string>
#include <vector>
#include <memory>

namespace ariane_xml {

/**
 * Suggestion for auto-completion
 */
struct AutoCompleteSuggestion {
    std::string completion;      // The suggested completion text
    std::string display;         // Display text with description
    std::string description;     // Field or bloc description
    enum class Type {
        FIELD,      // Attribute/field suggestion
        BLOC,       // Bloc suggestion
        KEYWORD     // SQL keyword suggestion
    } type;

    AutoCompleteSuggestion(const std::string& comp, const std::string& disp,
                          const std::string& desc, Type t)
        : completion(comp), display(disp), description(desc), type(t) {}
};

/**
 * Provides smart auto-completion for DSN queries in interactive mode
 * Features:
 * - Tab completion for DSN paths (S21_G00_30_[TAB] -> shows all fields)
 * - Bloc name suggestions with descriptions
 * - Attribute suggestions with field descriptions
 * - Context-aware suggestions based on cursor position
 */
class DsnAutoComplete {
public:
    explicit DsnAutoComplete(std::shared_ptr<DsnSchema> schema);

    /**
     * Get completion suggestions for the given input at cursor position
     * @param input The current input string
     * @param cursor_pos The cursor position in the input
     * @return List of completion suggestions
     */
    std::vector<AutoCompleteSuggestion> getSuggestions(
        const std::string& input,
        size_t cursor_pos
    );

    /**
     * Get suggestions for a partial path
     * Example: "S21_G00_30_" -> suggests all S21_G00_30_XXX fields
     * @param partial_path The partial path to complete
     * @return List of matching attributes/blocs
     */
    std::vector<AutoCompleteSuggestion> getPathSuggestions(
        const std::string& partial_path
    );

    /**
     * Get suggestions for a bloc pattern
     * Example: "S21_" -> suggests S21_G00_06, S21_G00_11, etc.
     * @param partial_bloc The partial bloc name
     * @return List of matching blocs
     */
    std::vector<AutoCompleteSuggestion> getBlocSuggestions(
        const std::string& partial_bloc
    );

    /**
     * Get suggestions for shortcut notation
     * Example: "30_" -> suggests 30_001, 30_002, etc.
     * @param partial_shortcut The partial shortcut
     * @return List of matching shortcuts
     */
    std::vector<AutoCompleteSuggestion> getShortcutSuggestions(
        const std::string& partial_shortcut
    );

    /**
     * Get SQL keyword suggestions
     * @param partial_keyword The partial keyword
     * @return List of matching keywords
     */
    std::vector<AutoCompleteSuggestion> getKeywordSuggestions(
        const std::string& partial_keyword
    );

    /**
     * Format suggestions for display in terminal
     * @param suggestions List of suggestions
     * @param max_display Maximum number of suggestions to display
     * @return Formatted string for terminal output
     */
    static std::string formatSuggestions(
        const std::vector<AutoCompleteSuggestion>& suggestions,
        size_t max_display = 20
    );

private:
    std::shared_ptr<DsnSchema> schema_;

    /**
     * Extract the word/path being completed at cursor position
     */
    std::string extractCurrentWord(const std::string& input, size_t cursor_pos);

    /**
     * Determine the completion context (field, bloc, keyword, etc.)
     */
    enum class CompletionContext {
        FIELD,      // Completing a field path
        BLOC,       // Completing a bloc name
        KEYWORD,    // Completing an SQL keyword
        UNKNOWN
    };

    CompletionContext getContext(const std::string& input, size_t cursor_pos);

    /**
     * Check if a string starts with a given prefix (case-insensitive)
     */
    bool startsWith(const std::string& str, const std::string& prefix);

    /**
     * Common SQL keywords for DSN queries
     */
    static const std::vector<std::string> SQL_KEYWORDS;
};

} // namespace ariane_xml

#endif // DSN_AUTOCOMPLETE_H
