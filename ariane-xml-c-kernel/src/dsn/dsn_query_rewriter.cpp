#include "dsn/dsn_query_rewriter.h"
#include <iostream>
#include <regex>

namespace ariane_xml {

DsnQueryRewriter::DsnQueryRewriter(std::shared_ptr<DsnSchema> schema)
    : schema_(schema) {}

Query DsnQueryRewriter::rewrite(const Query& query) {
    Query rewritten;

    // Copy simple fields
    rewritten.distinct = query.distinct;
    rewritten.from_path = query.from_path;
    rewritten.for_clauses = query.for_clauses;
    rewritten.group_by_fields = query.group_by_fields;
    rewritten.order_by_fields = query.order_by_fields;
    rewritten.limit = query.limit;
    rewritten.offset = query.offset;
    rewritten.has_aggregates = query.has_aggregates;

    // Rewrite SELECT fields
    for (const auto& field : query.select_fields) {
        rewritten.select_fields.push_back(expandFieldPath(field));
    }

    // Rewrite WHERE clause
    if (query.where) {
        rewritten.where = rewriteWhereExpr(query.where.get());
    }

    // Rewrite HAVING clause
    if (query.having) {
        rewritten.having = rewriteWhereExpr(query.having.get());
    }

    return rewritten;
}

FieldPath DsnQueryRewriter::expandFieldPath(const FieldPath& field) {
    FieldPath expanded = field;

    // Expand each component in the path
    std::vector<std::string> newComponents;
    std::string previousComponent = "";

    for (const auto& component : field.components) {
        std::string expandedComponent = expandComponent(component, previousComponent);
        newComponents.push_back(expandedComponent);
        previousComponent = expandedComponent;
    }

    expanded.components = newComponents;

    // Also expand attribute name if it's an attribute reference
    if (field.is_attribute && isShortcutPattern(field.attribute_name)) {
        expanded.attribute_name = expandComponent(field.attribute_name);
    }

    return expanded;
}

std::string DsnQueryRewriter::expandComponent(const std::string& component, const std::string& previousComponent) {
    // Check if this component matches the YY_ZZZ shortcut pattern
    if (!isShortcutPattern(component)) {
        return component;
    }

    // Look up the shortcut in the schema
    auto attributes = schema_->findByShortId(component);

    if (attributes.empty()) {
        // Not a recognized DSN shortcut, return as-is
        return component;
    }

    if (attributes.size() == 1) {
        // Unambiguous shortcut, expand to full name
        return attributes[0].full_name;
    }

    // Ambiguous shortcut - try to disambiguate using previous component
    if (!previousComponent.empty()) {
        // Try to find attribute that belongs to the same bloc as previous component
        for (const auto& attr : attributes) {
            if (attr.full_name.find(previousComponent) == 0) {
                // This attribute starts with the previous component (same hierarchy)
                return attr.full_name;
            }
        }
    }

    // Still ambiguous - report error
    handleAmbiguousShortcut(component, attributes);

    // Return first match as fallback
    return attributes[0].full_name;
}

bool DsnQueryRewriter::isShortcutPattern(const std::string& str) {
    // Check if string matches YY_ZZZ pattern (2+ digits, underscore, 3+ digits)
    std::regex pattern(R"(^\d{2,}_\d{3,}$)");
    return std::regex_match(str, pattern);
}

void DsnQueryRewriter::handleAmbiguousShortcut(const std::string& shortcut, const std::vector<DsnAttribute>& attributes) {
    std::cerr << "\nWarning: Ambiguous DSN shortcut '" << shortcut << "'\n";
    std::cerr << "Could refer to:\n";

    for (const auto& attr : attributes) {
        std::cerr << "  - " << attr.full_name;
        if (!attr.description.empty()) {
            std::cerr << " (" << attr.description << ")";
        }
        std::cerr << "\n";
    }

    std::cerr << "\nPlease specify the full attribute name or use bloc prefix.\n";
    std::cerr << "Using first match: " << attributes[0].full_name << "\n\n";
}

std::unique_ptr<WhereExpr> DsnQueryRewriter::rewriteWhereExpr(const WhereExpr* expr) {
    if (!expr) {
        return nullptr;
    }

    // Check if it's a condition or logical expression
    const WhereCondition* condition = dynamic_cast<const WhereCondition*>(expr);
    if (condition) {
        // Rewrite the field path in the condition
        auto newCondition = std::make_unique<WhereCondition>();
        newCondition->field = expandFieldPath(condition->field);
        newCondition->op = condition->op;
        newCondition->value = condition->value;
        newCondition->is_numeric = condition->is_numeric;
        newCondition->values = condition->values;
        return newCondition;
    }

    const WhereLogical* logical = dynamic_cast<const WhereLogical*>(expr);
    if (logical) {
        // Recursively rewrite both sides
        auto newLogical = std::make_unique<WhereLogical>();
        newLogical->op = logical->op;
        newLogical->left = rewriteWhereExpr(logical->left.get());
        newLogical->right = rewriteWhereExpr(logical->right.get());
        return newLogical;
    }

    return nullptr;
}

} // namespace ariane_xml
