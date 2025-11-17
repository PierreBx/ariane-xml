#ifndef DSN_QUERY_REWRITER_H
#define DSN_QUERY_REWRITER_H

#include "dsn_schema.h"
#include "parser/ast.h"
#include <string>
#include <memory>

namespace ariane_xml {

/**
 * Rewrites DSN queries to expand YY_ZZZ shortcuts to full attribute names
 * Example: "30_001" -> "S21_G00_30_001"
 */
class DsnQueryRewriter {
public:
    explicit DsnQueryRewriter(std::shared_ptr<DsnSchema> schema);

    /**
     * Rewrite a query to expand DSN shortcuts
     * @param query The original query
     * @return Rewritten query with expanded attribute names
     */
    Query rewrite(const Query& query);

private:
    std::shared_ptr<DsnSchema> schema_;

    /**
     * Expand a field path if it contains DSN shortcuts
     * @param field The field path to expand
     * @return Expanded field path
     */
    FieldPath expandFieldPath(const FieldPath& field);

    /**
     * Expand a single path component if it's a DSN shortcut
     * @param component The component to expand
     * @param previousComponent Previous component (for disambiguation)
     * @return Expanded component or original if not a shortcut
     */
    std::string expandComponent(const std::string& component, const std::string& previousComponent = "");

    /**
     * Check if a string matches the YY_ZZZ pattern
     * @param str The string to check
     * @return true if it matches YY_ZZZ pattern
     */
    bool isShortcutPattern(const std::string& str);

    /**
     * Handle ambiguous shortcuts by providing helpful error messages
     * @param shortcut The ambiguous shortcut
     * @param attributes All possible matches
     */
    void handleAmbiguousShortcut(const std::string& shortcut, const std::vector<DsnAttribute>& attributes);

    /**
     * Rewrite WHERE clause to expand shortcuts
     */
    std::unique_ptr<WhereExpr> rewriteWhereExpr(const WhereExpr* expr);
};

} // namespace ariane_xml

#endif // DSN_QUERY_REWRITER_H
