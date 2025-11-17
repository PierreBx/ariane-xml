#ifndef DSN_FORMATTER_H
#define DSN_FORMATTER_H

#include "dsn_schema.h"
#include <string>
#include <vector>
#include <map>
#include <memory>

namespace ariane_xml {

/**
 * Represents a result row with field values
 */
struct ResultRow {
    std::map<std::string, std::string> fields;  // field_name -> value

    std::string get(const std::string& field) const {
        auto it = fields.find(field);
        return (it != fields.end()) ? it->second : "";
    }

    void set(const std::string& field, const std::string& value) {
        fields[field] = value;
    }

    bool has(const std::string& field) const {
        return fields.find(field) != fields.end();
    }
};

/**
 * Output format options for DSN results
 */
enum class DsnOutputFormat {
    TABLE,           // Standard table format (default)
    DSN_STRUCTURED,  // Hierarchical DSN format with blocs
    JSON,            // JSON export
    CSV,             // CSV export
    COMPACT          // Compact single-line format
};

/**
 * Formats query results for DSN data with enhanced readability
 * Features:
 * - Hierarchical display organized by blocs
 * - Field descriptions and labels
 * - Multiple output formats (table, JSON, CSV, DSN-structured)
 * - Automatic bloc grouping
 */
class DsnFormatter {
public:
    explicit DsnFormatter(std::shared_ptr<DsnSchema> schema);

    /**
     * Format query results in the specified format
     * @param results Vector of result rows
     * @param format Output format
     * @return Formatted string
     */
    std::string format(
        const std::vector<ResultRow>& results,
        DsnOutputFormat format = DsnOutputFormat::TABLE
    );

    /**
     * Format in standard table format
     */
    std::string formatTable(const std::vector<ResultRow>& results);

    /**
     * Format in DSN-structured hierarchical format
     * Groups fields by bloc and shows descriptions
     */
    std::string formatDsnStructured(const std::vector<ResultRow>& results);

    /**
     * Format as JSON
     */
    std::string formatJson(const std::vector<ResultRow>& results);

    /**
     * Format as CSV
     */
    std::string formatCsv(const std::vector<ResultRow>& results);

    /**
     * Format in compact single-line format
     */
    std::string formatCompact(const std::vector<ResultRow>& results);

    /**
     * Set maximum field width for table output
     */
    void setMaxFieldWidth(size_t width) { max_field_width_ = width; }

    /**
     * Enable/disable showing field descriptions
     */
    void setShowDescriptions(bool show) { show_descriptions_ = show; }

    /**
     * Enable/disable showing bloc labels
     */
    void setShowBlocLabels(bool show) { show_bloc_labels_ = show; }

private:
    std::shared_ptr<DsnSchema> schema_;
    size_t max_field_width_ = 40;
    bool show_descriptions_ = true;
    bool show_bloc_labels_ = true;

    /**
     * Group fields by their bloc
     * Returns map: bloc_name -> vector of field names
     */
    std::map<std::string, std::vector<std::string>> groupFieldsByBloc(
        const std::vector<std::string>& fields
    );

    /**
     * Get field description from schema
     */
    std::string getFieldDescription(const std::string& field_name);

    /**
     * Get bloc label from schema
     */
    std::string getBlocLabel(const std::string& bloc_name);

    /**
     * Extract bloc name from full field path
     * Example: S21_G00_30_001 -> S21.G00.30
     */
    std::string extractBlocName(const std::string& field_name);

    /**
     * Truncate string to max width with ellipsis
     */
    std::string truncate(const std::string& str, size_t max_width);

    /**
     * Escape string for JSON
     */
    std::string escapeJson(const std::string& str);

    /**
     * Escape string for CSV
     */
    std::string escapeCsv(const std::string& str);

    /**
     * Draw a horizontal line for tables
     */
    std::string drawLine(char c, size_t length);

    /**
     * Get all unique field names from results
     */
    std::vector<std::string> getFieldNames(const std::vector<ResultRow>& results);
};

} // namespace ariane_xml

#endif // DSN_FORMATTER_H
