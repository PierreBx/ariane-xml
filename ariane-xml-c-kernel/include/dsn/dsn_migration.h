#ifndef DSN_MIGRATION_H
#define DSN_MIGRATION_H

#include "dsn_schema.h"
#include <string>
#include <vector>
#include <memory>
#include <set>

namespace ariane_xml {

/**
 * Represents a schema difference between versions
 */
struct SchemaDifference {
    enum class Type {
        ADDED,      // Field added in new version
        REMOVED,    // Field removed in new version
        MODIFIED,   // Field modified (type, mandatory status, etc.)
        UNCHANGED   // Field unchanged
    } type;

    std::string field_name;         // Full field name
    std::string description;        // Description of the change
    std::string old_value;          // Old value/property (for MODIFIED)
    std::string new_value;          // New value/property (for MODIFIED)
    std::string category;           // Category of change (field, bloc, etc.)

    SchemaDifference(Type t, const std::string& field,
                    const std::string& desc = "",
                    const std::string& old_val = "",
                    const std::string& new_val = "",
                    const std::string& cat = "field")
        : type(t), field_name(field), description(desc),
          old_value(old_val), new_value(new_val), category(cat) {}
};

/**
 * Result of comparing two DSN schema versions
 */
struct SchemaComparisonResult {
    std::vector<SchemaDifference> differences;
    std::string from_version;
    std::string to_version;
    size_t added_count = 0;
    size_t removed_count = 0;
    size_t modified_count = 0;

    void addDifference(const SchemaDifference& diff) {
        differences.push_back(diff);
        switch (diff.type) {
            case SchemaDifference::Type::ADDED:
                added_count++;
                break;
            case SchemaDifference::Type::REMOVED:
                removed_count++;
                break;
            case SchemaDifference::Type::MODIFIED:
                modified_count++;
                break;
            default:
                break;
        }
    }
};

/**
 * Migration advice for upgrading DSN files
 */
struct MigrationAdvice {
    std::string field_name;
    std::string issue;              // Description of the issue
    std::string recommendation;     // What to do about it
    enum class Severity {
        INFO,       // Informational
        WARNING,    // Should address but not critical
        ERROR       // Must fix for compliance
    } severity;

    MigrationAdvice(const std::string& field, const std::string& iss,
                   const std::string& rec, Severity sev = Severity::INFO)
        : field_name(field), issue(iss), recommendation(rec), severity(sev) {}
};

/**
 * Provides version migration assistance for DSN schemas
 * Features:
 * - Compare P25 vs P26 schemas
 * - Identify new, removed, and modified fields
 * - Check file compatibility with new version
 * - Provide migration recommendations
 */
class DsnMigrationHelper {
public:
    DsnMigrationHelper() = default;

    /**
     * Compare two schema versions
     * @param from_schema The source schema (e.g., P25)
     * @param to_schema The target schema (e.g., P26)
     * @return Comparison result with all differences
     */
    SchemaComparisonResult compareSchemas(
        const DsnSchema& from_schema,
        const DsnSchema& to_schema
    );

    /**
     * Format comparison results for display
     * @param result The comparison result
     * @param verbose Include detailed changes
     * @return Formatted string
     */
    std::string formatComparisonResult(
        const SchemaComparisonResult& result,
        bool verbose = false
    );

    /**
     * Check if a file using old schema is compatible with new schema
     * @param file_fields Fields present in the file
     * @param from_schema Current schema version
     * @param to_schema Target schema version
     * @return List of migration advice items
     */
    std::vector<MigrationAdvice> checkMigrationCompatibility(
        const std::set<std::string>& file_fields,
        const DsnSchema& from_schema,
        const DsnSchema& to_schema
    );

    /**
     * Format migration advice for display
     * @param advice Vector of migration advice items
     * @return Formatted string with recommendations
     */
    std::string formatMigrationAdvice(
        const std::vector<MigrationAdvice>& advice
    );

    /**
     * Generate migration report
     * Combines schema comparison and compatibility check
     */
    std::string generateMigrationReport(
        const DsnSchema& from_schema,
        const DsnSchema& to_schema,
        const std::set<std::string>& file_fields = {}
    );

private:
    /**
     * Find fields that were added in the new schema
     */
    std::vector<SchemaDifference> findAddedFields(
        const DsnSchema& from_schema,
        const DsnSchema& to_schema
    );

    /**
     * Find fields that were removed in the new schema
     */
    std::vector<SchemaDifference> findRemovedFields(
        const DsnSchema& from_schema,
        const DsnSchema& to_schema
    );

    /**
     * Find fields that were modified in the new schema
     */
    std::vector<SchemaDifference> findModifiedFields(
        const DsnSchema& from_schema,
        const DsnSchema& to_schema
    );

    /**
     * Compare two attributes and return differences
     */
    std::vector<SchemaDifference> compareAttributes(
        const DsnAttribute& old_attr,
        const DsnAttribute& new_attr
    );

    /**
     * Get severity icon/symbol
     */
    std::string getSeverityIcon(MigrationAdvice::Severity severity);

    /**
     * Group differences by category
     */
    std::map<std::string, std::vector<SchemaDifference>> groupDifferencesByCategory(
        const std::vector<SchemaDifference>& differences
    );
};

} // namespace ariane_xml

#endif // DSN_MIGRATION_H
