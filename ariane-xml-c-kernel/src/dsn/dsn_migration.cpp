#include "dsn/dsn_migration.h"
#include <sstream>
#include <iomanip>
#include <algorithm>

namespace ariane_xml {

SchemaComparisonResult DsnMigrationHelper::compareSchemas(
    const DsnSchema& from_schema,
    const DsnSchema& to_schema
) {
    SchemaComparisonResult result;
    result.from_version = from_schema.getVersion();
    result.to_version = to_schema.getVersion();

    // Find added fields
    auto added = findAddedFields(from_schema, to_schema);
    for (const auto& diff : added) {
        result.addDifference(diff);
    }

    // Find removed fields
    auto removed = findRemovedFields(from_schema, to_schema);
    for (const auto& diff : removed) {
        result.addDifference(diff);
    }

    // Find modified fields
    auto modified = findModifiedFields(from_schema, to_schema);
    for (const auto& diff : modified) {
        result.addDifference(diff);
    }

    return result;
}

std::string DsnMigrationHelper::formatComparisonResult(
    const SchemaComparisonResult& result,
    bool verbose
) {
    std::ostringstream output;

    output << "\n";
    output << "═══════════════════════════════════════════════════════════════════\n";
    output << " DSN Schema Comparison: " << result.from_version << " → " << result.to_version << "\n";
    output << "═══════════════════════════════════════════════════════════════════\n\n";

    output << "Summary:\n";
    output << "  ✓ Added fields:    " << result.added_count << "\n";
    output << "  ✗ Removed fields:  " << result.removed_count << "\n";
    output << "  ≠ Modified fields: " << result.modified_count << "\n";
    output << "  Total changes:     " << result.differences.size() << "\n\n";

    // Group by category
    auto groups = groupDifferencesByCategory(result.differences);

    // Display added fields
    if (result.added_count > 0) {
        output << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
        output << "New in " << result.to_version << ":\n";
        output << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";

        for (const auto& diff : result.differences) {
            if (diff.type == SchemaDifference::Type::ADDED) {
                output << "  + " << std::left << std::setw(30) << diff.field_name;
                if (verbose && !diff.description.empty()) {
                    output << " - " << diff.description;
                }
                output << "\n";
            }
        }
        output << "\n";
    }

    // Display removed fields
    if (result.removed_count > 0) {
        output << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
        output << "Deprecated in " << result.to_version << ":\n";
        output << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";

        for (const auto& diff : result.differences) {
            if (diff.type == SchemaDifference::Type::REMOVED) {
                output << "  - " << std::left << std::setw(30) << diff.field_name;
                if (verbose && !diff.description.empty()) {
                    output << " - " << diff.description;
                }
                output << "\n";
            }
        }
        output << "\n";
    }

    // Display modified fields
    if (result.modified_count > 0) {
        output << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
        output << "Modified in " << result.to_version << ":\n";
        output << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";

        for (const auto& diff : result.differences) {
            if (diff.type == SchemaDifference::Type::MODIFIED) {
                output << "  ≠ " << std::left << std::setw(30) << diff.field_name;
                if (verbose) {
                    output << " (" << diff.old_value << " → " << diff.new_value << ")";
                    if (!diff.description.empty()) {
                        output << "\n    " << diff.description;
                    }
                }
                output << "\n";
            }
        }
        output << "\n";
    }

    return output.str();
}

std::vector<MigrationAdvice> DsnMigrationHelper::checkMigrationCompatibility(
    const std::set<std::string>& file_fields,
    const DsnSchema& from_schema,
    const DsnSchema& to_schema
) {
    std::vector<MigrationAdvice> advice;

    // Compare schemas
    auto comparison = compareSchemas(from_schema, to_schema);

    // Check for removed fields that are used in the file
    for (const auto& diff : comparison.differences) {
        if (diff.type == SchemaDifference::Type::REMOVED) {
            if (file_fields.find(diff.field_name) != file_fields.end()) {
                advice.emplace_back(
                    diff.field_name,
                    "Field removed in " + to_schema.getVersion(),
                    "Remove this field from your data or map to replacement field",
                    MigrationAdvice::Severity::ERROR
                );
            }
        }
    }

    // Check for new mandatory fields
    for (const auto& diff : comparison.differences) {
        if (diff.type == SchemaDifference::Type::ADDED) {
            // If it's a new mandatory field, warn about it
            if (diff.description.find("mandatory") != std::string::npos) {
                advice.emplace_back(
                    diff.field_name,
                    "New mandatory field in " + to_schema.getVersion(),
                    "You must provide a value for this field",
                    MigrationAdvice::Severity::ERROR
                );
            } else {
                advice.emplace_back(
                    diff.field_name,
                    "New optional field in " + to_schema.getVersion(),
                    "Consider if this field is relevant to your use case",
                    MigrationAdvice::Severity::INFO
                );
            }
        }
    }

    // Check for modified fields
    for (const auto& diff : comparison.differences) {
        if (diff.type == SchemaDifference::Type::MODIFIED) {
            if (file_fields.find(diff.field_name) != file_fields.end()) {
                advice.emplace_back(
                    diff.field_name,
                    "Field modified: " + diff.description,
                    "Review and update field value to match new requirements",
                    MigrationAdvice::Severity::WARNING
                );
            }
        }
    }

    return advice;
}

std::string DsnMigrationHelper::formatMigrationAdvice(
    const std::vector<MigrationAdvice>& advice
) {
    if (advice.empty()) {
        return "\n✓ No migration issues found. File is compatible with new schema version.\n";
    }

    std::ostringstream output;
    output << "\n";
    output << "═══════════════════════════════════════════════════════════════════\n";
    output << " Migration Compatibility Report\n";
    output << "═══════════════════════════════════════════════════════════════════\n\n";

    // Count by severity
    size_t errors = 0, warnings = 0, infos = 0;
    for (const auto& item : advice) {
        switch (item.severity) {
            case MigrationAdvice::Severity::ERROR: errors++; break;
            case MigrationAdvice::Severity::WARNING: warnings++; break;
            case MigrationAdvice::Severity::INFO: infos++; break;
        }
    }

    output << "Summary:\n";
    output << "  ✗ Errors:   " << errors << " (must fix)\n";
    output << "  ⚠ Warnings: " << warnings << " (should review)\n";
    output << "  ℹ Info:     " << infos << " (informational)\n\n";

    // Group by severity
    output << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
    output << "Required Changes (Errors):\n";
    output << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";

    for (const auto& item : advice) {
        if (item.severity == MigrationAdvice::Severity::ERROR) {
            output << getSeverityIcon(item.severity) << " " << item.field_name << "\n";
            output << "   Issue: " << item.issue << "\n";
            output << "   Action: " << item.recommendation << "\n\n";
        }
    }

    if (warnings > 0) {
        output << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
        output << "Recommended Changes (Warnings):\n";
        output << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";

        for (const auto& item : advice) {
            if (item.severity == MigrationAdvice::Severity::WARNING) {
                output << getSeverityIcon(item.severity) << " " << item.field_name << "\n";
                output << "   Issue: " << item.issue << "\n";
                output << "   Suggestion: " << item.recommendation << "\n\n";
            }
        }
    }

    if (infos > 0) {
        output << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
        output << "Additional Information:\n";
        output << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";

        for (const auto& item : advice) {
            if (item.severity == MigrationAdvice::Severity::INFO) {
                output << getSeverityIcon(item.severity) << " " << item.field_name << "\n";
                output << "   Info: " << item.issue << "\n";
                output << "   Note: " << item.recommendation << "\n\n";
            }
        }
    }

    return output.str();
}

std::string DsnMigrationHelper::generateMigrationReport(
    const DsnSchema& from_schema,
    const DsnSchema& to_schema,
    const std::set<std::string>& file_fields
) {
    std::ostringstream output;

    // Schema comparison
    auto comparison = compareSchemas(from_schema, to_schema);
    output << formatComparisonResult(comparison, true);

    // Compatibility check if file fields provided
    if (!file_fields.empty()) {
        auto advice = checkMigrationCompatibility(file_fields, from_schema, to_schema);
        output << "\n" << formatMigrationAdvice(advice);
    }

    return output.str();
}

std::vector<SchemaDifference> DsnMigrationHelper::findAddedFields(
    const DsnSchema& from_schema,
    const DsnSchema& to_schema
) {
    std::vector<SchemaDifference> added;

    const auto& old_attrs = from_schema.getAttributes();
    const auto& new_attrs = to_schema.getAttributes();

    for (const auto& [field_name, attr] : new_attrs) {
        if (old_attrs.find(field_name) == old_attrs.end()) {
            std::string desc = attr.description;
            if (attr.mandatory) {
                desc += " [MANDATORY]";
            }
            added.emplace_back(
                SchemaDifference::Type::ADDED,
                field_name,
                desc
            );
        }
    }

    return added;
}

std::vector<SchemaDifference> DsnMigrationHelper::findRemovedFields(
    const DsnSchema& from_schema,
    const DsnSchema& to_schema
) {
    std::vector<SchemaDifference> removed;

    const auto& old_attrs = from_schema.getAttributes();
    const auto& new_attrs = to_schema.getAttributes();

    for (const auto& [field_name, attr] : old_attrs) {
        if (new_attrs.find(field_name) == new_attrs.end()) {
            removed.emplace_back(
                SchemaDifference::Type::REMOVED,
                field_name,
                attr.description
            );
        }
    }

    return removed;
}

std::vector<SchemaDifference> DsnMigrationHelper::findModifiedFields(
    const DsnSchema& from_schema,
    const DsnSchema& to_schema
) {
    std::vector<SchemaDifference> modified;

    const auto& old_attrs = from_schema.getAttributes();
    const auto& new_attrs = to_schema.getAttributes();

    for (const auto& [field_name, new_attr] : new_attrs) {
        auto it = old_attrs.find(field_name);
        if (it != old_attrs.end()) {
            const auto& old_attr = it->second;
            auto diffs = compareAttributes(old_attr, new_attr);
            modified.insert(modified.end(), diffs.begin(), diffs.end());
        }
    }

    return modified;
}

std::vector<SchemaDifference> DsnMigrationHelper::compareAttributes(
    const DsnAttribute& old_attr,
    const DsnAttribute& new_attr
) {
    std::vector<SchemaDifference> diffs;

    // Check if mandatory status changed
    if (old_attr.mandatory != new_attr.mandatory) {
        diffs.emplace_back(
            SchemaDifference::Type::MODIFIED,
            new_attr.full_name,
            "Mandatory status changed",
            old_attr.mandatory ? "mandatory" : "optional",
            new_attr.mandatory ? "mandatory" : "optional"
        );
    }

    // Check if type changed
    if (old_attr.type != new_attr.type) {
        diffs.emplace_back(
            SchemaDifference::Type::MODIFIED,
            new_attr.full_name,
            "Type changed",
            old_attr.type,
            new_attr.type
        );
    }

    // Check if occurrences changed
    if (old_attr.min_occurs != new_attr.min_occurs ||
        old_attr.max_occurs != new_attr.max_occurs) {
        std::string old_occ = std::to_string(old_attr.min_occurs) + ".." +
                             (old_attr.max_occurs < 0 ? "unbounded" : std::to_string(old_attr.max_occurs));
        std::string new_occ = std::to_string(new_attr.min_occurs) + ".." +
                             (new_attr.max_occurs < 0 ? "unbounded" : std::to_string(new_attr.max_occurs));

        diffs.emplace_back(
            SchemaDifference::Type::MODIFIED,
            new_attr.full_name,
            "Cardinality changed",
            old_occ,
            new_occ
        );
    }

    return diffs;
}

std::string DsnMigrationHelper::getSeverityIcon(MigrationAdvice::Severity severity) {
    switch (severity) {
        case MigrationAdvice::Severity::ERROR: return "✗";
        case MigrationAdvice::Severity::WARNING: return "⚠";
        case MigrationAdvice::Severity::INFO: return "ℹ";
        default: return "?";
    }
}

std::map<std::string, std::vector<SchemaDifference>>
DsnMigrationHelper::groupDifferencesByCategory(
    const std::vector<SchemaDifference>& differences
) {
    std::map<std::string, std::vector<SchemaDifference>> groups;

    for (const auto& diff : differences) {
        groups[diff.category].push_back(diff);
    }

    return groups;
}

} // namespace ariane_xml
