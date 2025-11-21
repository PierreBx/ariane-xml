#ifndef PARSER_H
#define PARSER_H

#include "ast.h"
#include "error/error_codes.h"
#include <vector>
#include <memory>
#include <stdexcept>

namespace ariane_xml {

class AppContext; // Forward declaration

// ParseError is now an alias for ArianeError for backward compatibility
// All parsing errors should use the unified error numbering system
using ParseError = ArianeError;

class Parser {
public:
    explicit Parser(const std::vector<Token>& tokens, const AppContext* context = nullptr);

    // Parse the tokens into a Query AST
    std::unique_ptr<Query> parse();

private:
    std::vector<Token> tokens_;
    size_t current_;
    const AppContext* context_;

    // Helper methods
    Token peek() const;
    Token advance();
    bool check(TokenType type) const;
    bool match(TokenType type);
    bool isAtEnd() const;
    void expect(TokenType type, const std::string& message);

    // Parsing methods
    FieldPath parseFieldPath();
    FieldPath parseSelectField();  // Parse SELECT field (may include aggregation)
    std::string parseFilePath();  // Parse filesystem path (quoted or unquoted)
    ForClause parseForClause();   // Parse FOR...IN clause
    std::unique_ptr<WhereExpr> parseWhereClause();
    std::unique_ptr<WhereExpr> parseWhereExpression();
    std::unique_ptr<WhereExpr> parseWhereOr();
    std::unique_ptr<WhereExpr> parseWhereAnd();
    std::unique_ptr<WhereExpr> parseWherePrimary();
    std::unique_ptr<WhereExpr> parseWhereCondition();
    ComparisonOp parseComparisonOp();
    std::string parseRegexPattern();  // Parse regex pattern between / delimiters
    void parseOrderByClause(Query& query);
    void parseLimitClause(Query& query);
    void parseOffsetClause(Query& query);
    void parseGroupByClause(Query& query);  // Parse GROUP BY clause
    void parseHavingClause(Query& query);   // Parse HAVING clause
    void markVariableReferencesInWhere(WhereExpr* expr, const Query& query);

    // DSN mode helpers
    bool isDsnShortcutPattern(const std::string& component) const;
    std::string convertDsnShortcutToFullName(const std::string& shortcut) const;
};

} // namespace ariane_xml

#endif // PARSER_H
