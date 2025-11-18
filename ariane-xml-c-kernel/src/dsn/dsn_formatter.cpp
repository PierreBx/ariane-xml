#include "dsn/dsn_formatter.h"
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <regex>

namespace ariane_xml {

DsnFormatter::DsnFormatter(std::shared_ptr<DsnSchema> schema)
    : schema_(schema) {}

std::string DsnFormatter::format(
    const std::vector<ResultRow>& results,
    DsnOutputFormat format
) {
    switch (format) {
        case DsnOutputFormat::TABLE:
            return formatTable(results);
        case DsnOutputFormat::DSN_STRUCTURED:
            return formatDsnStructured(results);
        case DsnOutputFormat::JSON:
            return formatJson(results);
        case DsnOutputFormat::CSV:
            return formatCsv(results);
        case DsnOutputFormat::COMPACT:
            return formatCompact(results);
        default:
            return formatTable(results);
    }
}

std::string DsnFormatter::formatTable(const std::vector<ResultRow>& results) {
    if (results.empty()) {
        return "No results.\n";
    }

    std::ostringstream output;
    auto fields = getFieldNames(results);

    // Calculate column widths
    std::map<std::string, size_t> widths;
    for (const auto& field : fields) {
        widths[field] = std::min(field.length(), max_field_width_);
        for (const auto& row : results) {
            size_t value_len = row.get(field).length();
            widths[field] = std::max(widths[field], std::min(value_len, max_field_width_));
        }
    }

    // Header
    output << "\n";
    for (const auto& field : fields) {
        output << "| " << std::left << std::setw(widths[field]) << truncate(field, widths[field]) << " ";
    }
    output << "|\n";

    // Separator
    for (const auto& field : fields) {
        output << "|-" << drawLine('-', widths[field]) << "-";
    }
    output << "|\n";

    // Rows
    for (const auto& row : results) {
        for (const auto& field : fields) {
            std::string value = row.get(field);
            output << "| " << std::left << std::setw(widths[field])
                   << truncate(value, widths[field]) << " ";
        }
        output << "|\n";
    }

    output << "\n" << results.size() << " row(s) returned.\n";
    return output.str();
}

std::string DsnFormatter::formatDsnStructured(const std::vector<ResultRow>& results) {
    if (results.empty()) {
        return "No results.\n";
    }

    std::ostringstream output;
    auto fields = getFieldNames(results);
    auto bloc_groups = groupFieldsByBloc(fields);

    // Process each result row
    for (size_t i = 0; i < results.size(); i++) {
        const auto& row = results[i];

        output << "\n" << drawLine('=', 70) << "\n";
        output << " Record " << (i + 1) << " of " << results.size() << "\n";
        output << drawLine('=', 70) << "\n";

        // Display fields grouped by bloc
        for (const auto& [bloc_name, bloc_fields] : bloc_groups) {
            if (!bloc_fields.empty()) {
                // Bloc header
                output << "\n";
                if (show_bloc_labels_ && schema_) {
                    std::string label = getBlocLabel(bloc_name);
                    if (!label.empty()) {
                        output << "┌─ " << bloc_name << " (" << label << ")\n";
                    } else {
                        output << "┌─ " << bloc_name << "\n";
                    }
                } else {
                    output << "┌─ " << bloc_name << "\n";
                }

                // Display fields in this bloc
                for (const auto& field : bloc_fields) {
                    std::string value = row.get(field);
                    if (value.empty()) {
                        value = "(null)";
                    }

                    output << "│  ";

                    // Show field description if available
                    if (show_descriptions_ && schema_) {
                        std::string desc = getFieldDescription(field);
                        if (!desc.empty()) {
                            output << std::left << std::setw(30) << truncate(desc, 30)
                                   << ": " << value << "\n";
                        } else {
                            output << std::left << std::setw(30) << truncate(field, 30)
                                   << ": " << value << "\n";
                        }
                    } else {
                        output << std::left << std::setw(30) << truncate(field, 30)
                               << ": " << value << "\n";
                    }
                }

                output << "└" << drawLine('-', 68) << "\n";
            }
        }
    }

    output << "\n" << results.size() << " record(s) displayed.\n";
    return output.str();
}

std::string DsnFormatter::formatJson(const std::vector<ResultRow>& results) {
    std::ostringstream output;
    output << "[\n";

    for (size_t i = 0; i < results.size(); i++) {
        const auto& row = results[i];
        output << "  {\n";

        size_t field_idx = 0;
        for (const auto& [field, value] : row.fields) {
            output << "    \"" << escapeJson(field) << "\": \"" << escapeJson(value) << "\"";
            if (field_idx < row.fields.size() - 1) {
                output << ",";
            }
            output << "\n";
            field_idx++;
        }

        output << "  }";
        if (i < results.size() - 1) {
            output << ",";
        }
        output << "\n";
    }

    output << "]\n";
    return output.str();
}

std::string DsnFormatter::formatCsv(const std::vector<ResultRow>& results) {
    if (results.empty()) {
        return "";
    }

    std::ostringstream output;
    auto fields = getFieldNames(results);

    // Header
    for (size_t i = 0; i < fields.size(); i++) {
        output << escapeCsv(fields[i]);
        if (i < fields.size() - 1) {
            output << ",";
        }
    }
    output << "\n";

    // Rows
    for (const auto& row : results) {
        for (size_t i = 0; i < fields.size(); i++) {
            output << escapeCsv(row.get(fields[i]));
            if (i < fields.size() - 1) {
                output << ",";
            }
        }
        output << "\n";
    }

    return output.str();
}

std::string DsnFormatter::formatCompact(const std::vector<ResultRow>& results) {
    if (results.empty()) {
        return "No results.\n";
    }

    std::ostringstream output;
    auto fields = getFieldNames(results);

    for (size_t i = 0; i < results.size(); i++) {
        const auto& row = results[i];
        output << "[" << (i + 1) << "] ";

        for (size_t j = 0; j < fields.size(); j++) {
            output << fields[j] << "=" << row.get(fields[j]);
            if (j < fields.size() - 1) {
                output << " | ";
            }
        }
        output << "\n";
    }

    return output.str();
}

std::map<std::string, std::vector<std::string>> DsnFormatter::groupFieldsByBloc(
    const std::vector<std::string>& fields
) {
    std::map<std::string, std::vector<std::string>> groups;

    for (const auto& field : fields) {
        std::string bloc = extractBlocName(field);
        if (bloc.empty()) {
            bloc = "Other";
        }
        groups[bloc].push_back(field);
    }

    return groups;
}

std::string DsnFormatter::getFieldDescription(const std::string& field_name) {
    if (!schema_) {
        return "";
    }

    const DsnAttribute* attr = schema_->findByFullName(field_name);
    if (attr) {
        return attr->description;
    }

    return "";
}

std::string DsnFormatter::getBlocLabel(const std::string& bloc_name) {
    if (!schema_) {
        return "";
    }

    const DsnBloc* bloc = schema_->findBloc(bloc_name);
    if (bloc) {
        return bloc->label;
    }

    return "";
}

std::string DsnFormatter::extractBlocName(const std::string& field_name) {
    // DSN field pattern: SXX_GYY_ZZ_NNN
    // Bloc is: SXX.GYY.ZZ
    std::regex pattern(R"((S\d+)_(G\d+)_(\d+)_\d+)");
    std::smatch matches;

    if (std::regex_match(field_name, matches, pattern)) {
        return matches[1].str() + "." + matches[2].str() + "." + matches[3].str();
    }

    return "";
}

std::string DsnFormatter::truncate(const std::string& str, size_t max_width) {
    if (str.length() <= max_width) {
        return str;
    }
    return str.substr(0, max_width - 3) + "...";
}

std::string DsnFormatter::escapeJson(const std::string& str) {
    std::ostringstream escaped;
    for (char c : str) {
        switch (c) {
            case '"': escaped << "\\\""; break;
            case '\\': escaped << "\\\\"; break;
            case '\b': escaped << "\\b"; break;
            case '\f': escaped << "\\f"; break;
            case '\n': escaped << "\\n"; break;
            case '\r': escaped << "\\r"; break;
            case '\t': escaped << "\\t"; break;
            default:
                escaped << c;
        }
    }
    return escaped.str();
}

std::string DsnFormatter::escapeCsv(const std::string& str) {
    bool needs_quotes = str.find(',') != std::string::npos ||
                       str.find('"') != std::string::npos ||
                       str.find('\n') != std::string::npos;

    if (!needs_quotes) {
        return str;
    }

    std::ostringstream escaped;
    escaped << '"';
    for (char c : str) {
        if (c == '"') {
            escaped << "\"\"";  // Escape quotes by doubling
        } else {
            escaped << c;
        }
    }
    escaped << '"';
    return escaped.str();
}

std::string DsnFormatter::drawLine(char c, size_t length) {
    return std::string(length, c);
}

std::vector<std::string> DsnFormatter::getFieldNames(
    const std::vector<ResultRow>& results
) {
    std::vector<std::string> fields;
    if (results.empty()) {
        return fields;
    }

    // Get all unique field names from the first row
    // (assuming all rows have the same fields)
    for (const auto& [field, value] : results[0].fields) {
        fields.push_back(field);
    }

    return fields;
}

} // namespace ariane_xml
