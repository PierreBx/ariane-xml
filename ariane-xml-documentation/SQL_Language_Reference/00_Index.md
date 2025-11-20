# Ariane-XML SQL Language Reference

## Table of Contents

### 1. Introduction
- [Overview and Getting Started](01_Introduction/README.md)

### 2. Syntax Notation
- [How to Read Syntax Diagrams](02_Syntax_Notation/README.md)

### 3. SQL Statements
- [**SELECT Statement**](03_SQL_Statements/SELECT_Statement.md) ⭐ - Query and retrieve data from XML files
- SET Statement *(coming soon)*
- SHOW Statement *(coming soon)*
- DESCRIBE Statement *(coming soon)*
- CHECK Statement *(coming soon)*

### 4. SQL Clauses
- [FROM Clause](04_SQL_Clauses/FROM_Clause.md) - Specify source XML files
- [**FOR Clause**](04_SQL_Clauses/FOR_Clause.md) ⭐ - Bind iteration variables (ariane-xml specific)
- [WHERE Clause](04_SQL_Clauses/WHERE_Clause.md) - Filter query results
- [GROUP BY Clause](04_SQL_Clauses/GROUP_BY_Clause.md) - Group results by field values
- [HAVING Clause](04_SQL_Clauses/HAVING_Clause.md) - Filter grouped results
- [ORDER BY Clause](04_SQL_Clauses/ORDER_BY_Clause.md) - Sort query results
- [LIMIT and OFFSET Clauses](04_SQL_Clauses/LIMIT_OFFSET_Clause.md) - Control result pagination

### 5. SQL Expressions
- [Field Path Expressions](05_SQL_Expressions/Field_Paths.md) - Navigate XML structures
- [Aggregation Functions](05_SQL_Expressions/Aggregation_Functions.md) - COUNT, SUM, AVG, MIN, MAX
- [Comparison Operators](05_SQL_Expressions/Comparison_Operators.md) - =, !=, <, >, <=, >=
- [Logical Operators](05_SQL_Expressions/Logical_Operators.md) - AND, OR, NOT

### 6. SQL Conditions
- [Comparison Conditions](06_SQL_Conditions/Comparison_Conditions.md) - Compare field values
- [NULL Conditions](06_SQL_Conditions/NULL_Conditions.md) - IS NULL, IS NOT NULL
- [LIKE Conditions](06_SQL_Conditions/LIKE_Conditions.md) - Pattern matching with regex
- [IN Conditions](06_SQL_Conditions/IN_Conditions.md) - List membership testing

### 7. Special Features ⭐
- [**DSN Mode**](07_Special_Features/DSN_Mode.md) - French tax form shortcuts and optimizations
- [Position Variables](07_Special_Features/Position_Variables.md) - Track iteration index with AT
- [XML Attributes](07_Special_Features/XML_Attributes.md) - Query XML attributes with @
- [Partial Path Matching](07_Special_Features/Partial_Path_Matching.md) - Leading dot notation

### 8. Quick Reference
- [SQL Keywords](08_Quick_Reference.md#keywords)
- [Operators](08_Quick_Reference.md#operators)
- [Functions](08_Quick_Reference.md#functions)
- [Common Patterns](08_Quick_Reference.md#patterns)

---

## About This Reference

This SQL Language Reference documents the SQL dialect used by **ariane-xml**, a specialized query engine for XML files. Ariane-xml extends standard SQL with XML-specific features while maintaining familiar SQL syntax.

### Key Features

✨ **Ariane-XML Unique Features:**
- **FOR Clause** - Bind variables to iterate over nested XML structures
- **Position Variables** - Track iteration index with AT keyword
- **DSN Mode** - Shortcuts for French tax forms (Déclaration Sociale Nominative)
- **Partial Paths** - Leading dot notation for flexible path matching
- **Dual Separators** - Use `.` or `/` interchangeably in paths

📚 **Standard SQL Features:**
- SELECT queries with filtering (WHERE)
- Aggregation functions (COUNT, SUM, AVG, MIN, MAX)
- Grouping and filtering groups (GROUP BY, HAVING)
- Sorting and pagination (ORDER BY, LIMIT, OFFSET)
- Comparison, NULL, pattern matching, and list conditions

### Documentation Conventions

- ⭐ marks ariane-xml specific features (not in standard SQL)
- `code` denotes SQL keywords, identifiers, and code examples
- **bold** emphasizes important concepts
- *italic* marks placeholders or notes

### Railroad Diagrams

This reference uses **railroad diagrams** (syntax diagrams) to illustrate grammar rules. These visual representations show:
- **Rectangles** (terminals) - Exact keywords or symbols
- **Rounded boxes** (non-terminals) - References to other grammar rules
- **Arrows** - Valid paths through the syntax
- **Branches** - Alternative choices
- **Loops** - Repetition

See [Syntax Notation Guide](02_Syntax_Notation/README.md) for details on reading diagrams.

### Grammar Definition

The complete EBNF (Extended Backus-Naur Form) grammar is available in:
- [ariane-xml-sql-grammar.ebnf](ebnf/ariane-xml-sql-grammar.ebnf)

### Getting Started

New to ariane-xml? Start here:
1. [Introduction](01_Introduction/README.md) - Overview and basic concepts
2. [SELECT Statement](03_SQL_Statements/SELECT_Statement.md) - Learn the primary query statement
3. [FOR Clause](04_SQL_Clauses/FOR_Clause.md) ⭐ - Master the unique iteration feature
4. [Examples and Tutorials](../../ariane-xml-examples/EXAMPLES.md) - Hands-on examples

### Additional Resources

- [Main README](../../README.md) - Project overview and installation
- [CLI Quick Start](../01a_Quick_Start_CLI.md) - Command-line interface guide
- [Jupyter Quick Start](../01b_Quick_Start_Jupyter.md) - Jupyter notebook integration
- [DSN Mode Design](../DSN_MODE_DESIGN.md) - Technical details on DSN mode
- [Examples Collection](../../ariane-xml-examples/EXAMPLES.md) - Real-world query examples

---

## Version Information

- **Document Version**: 1.0 (MVP)
- **Ariane-XML Version**: Compatible with current release
- **Last Updated**: 2025-11-20

## Feedback

Found an error or have suggestions? Please report issues at the project repository.

---

**Navigation:**
- [Next: Introduction →](01_Introduction/README.md)
