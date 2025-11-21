# Ariane-XML SQL Language Reference

**Comprehensive documentation for the Ariane-XML SQL dialect**

## Overview

This is the official SQL Language Reference for **ariane-xml**, a specialized query engine for XML files. This documentation is modeled after Oracle's SQL Language Reference, providing comprehensive, professional-grade documentation with:

- 📊 **Railroad diagrams** (syntax diagrams) for visual grammar representation
- 📝 **EBNF grammar** specification for formal syntax definition
- 📚 **Detailed semantics** for each SQL construct
- 💡 **Extensive examples** demonstrating real-world usage
- ⭐ **Ariane-xml specific features** clearly marked

## Quick Links

- 🏠 [**Documentation Index**](00_Index.md) - Start here!
- 📖 [**Introduction**](01_Introduction/README.md) - Overview and basic concepts
- 🎯 [**SELECT Statement**](03_SQL_Statements/SELECT_Statement.md) - Main query statement (MVP)
- 📐 [**Syntax Notation Guide**](02_Syntax_Notation/README.md) - How to read diagrams
- 📋 [**EBNF Grammar**](ebnf/ariane-xml-sql-grammar.ebnf) - Formal grammar specification

## Documentation Structure

```
SQL_Language_Reference/
├── 00_Index.md                      # Main table of contents
├── 01_Introduction/                 # Overview and basic concepts
│   └── README.md
├── 02_Syntax_Notation/              # How to read syntax diagrams
│   └── README.md
├── 03_SQL_Statements/               # SQL statement documentation
│   └── SELECT_Statement.md          # ⭐ MVP: Complete SELECT docs
├── 04_SQL_Clauses/                  # Individual clause documentation
├── 05_SQL_Expressions/              # Expression documentation
├── 06_SQL_Conditions/               # Condition documentation
├── 07_Special_Features/             # Ariane-xml specific features
├── 08_Quick_Reference.md            # Quick reference guide
├── diagrams/                        # Railroad diagram SVGs (19 files)
│   ├── select_statement.svg
│   ├── field_list.svg
│   ├── where_clause.svg
│   └── ... (16 more)
├── ebnf/                            # EBNF grammar definition
│   └── ariane-xml-sql-grammar.ebnf
├── generate_diagrams.js             # Diagram generation script
├── package.json                     # Node.js dependencies
└── README.md                        # This file
```

## Key Features Documented

### Standard SQL Features
- ✅ SELECT queries with field selection
- ✅ WHERE clause filtering
- ✅ GROUP BY and HAVING for aggregation
- ✅ ORDER BY for sorting
- ✅ LIMIT and OFFSET for pagination
- ✅ Aggregation functions (COUNT, SUM, AVG, MIN, MAX)
- ✅ Comparison, NULL, LIKE, and IN conditions

### Ariane-XML Extensions ⭐
- ✅ **FOR clause** - Iterate over XML collections with variable binding
- ✅ **AT clause** - Track iteration position
- ✅ **Partial paths** - Leading dot notation (`.field.subfield`)
- ✅ **Dual separators** - Use `.` or `/` in paths
- ✅ **XML attributes** - Query with `@attribute`
- ✅ **FILE_NAME** - Include source filename
- ✅ **Regex LIKE** - Pattern matching with `/regex/`
- ✅ **DSN mode** - French tax form shortcuts

## MVP Status (Current Release)

This is the **Minimum Viable Product (MVP)** release, focusing on the core SELECT statement:

### ✅ Completed
- [x] EBNF grammar definition (W3C notation)
- [x] 19 railroad diagrams generated
- [x] Complete SELECT statement documentation
- [x] Introduction and overview
- [x] Syntax notation guide
- [x] Documentation index
- [x] 18+ comprehensive examples

### 🚧 Future Enhancements
- [ ] Individual clause pages (FROM, WHERE, FOR, etc.)
- [ ] Expression and condition detail pages
- [ ] Other SQL statements (SET, SHOW, DESCRIBE, CHECK)
- [ ] Quick reference page
- [ ] DSN mode detail page
- [ ] Additional examples and tutorials

## How to Use This Documentation

### For New Users

1. **Start with the basics**: Read the [Introduction](01_Introduction/README.md)
2. **Learn to read diagrams**: Review [Syntax Notation Guide](02_Syntax_Notation/README.md)
3. **Study SELECT**: Work through [SELECT Statement](03_SQL_Statements/SELECT_Statement.md)
4. **Practice**: Try examples from the documentation

### For Experienced SQL Users

1. **Quick orientation**: Skim [Introduction](01_Introduction/README.md)
2. **Focus on extensions**: Look for ⭐ markers highlighting ariane-xml specific features
3. **Master FOR clause**: Study the [SELECT Statement](03_SQL_Statements/SELECT_Statement.md) examples
4. **Reference as needed**: Use [Index](00_Index.md) to find specific topics

### For Language Implementers

1. **Study the grammar**: Review [EBNF grammar](ebnf/ariane-xml-sql-grammar.ebnf)
2. **Understand semantics**: Read detailed semantics sections
3. **Check edge cases**: Review all examples
4. **Generate diagrams**: Use `generate_diagrams.js` for visualization

## Railroad Diagrams

Railroad diagrams (syntax diagrams) are generated using the **railroad-diagrams** JavaScript library from EBNF grammar definitions.

### Viewing Diagrams

All diagrams are available as SVG files in the `diagrams/` directory:
- `select_statement.svg` - Main SELECT statement
- `field_list.svg`, `field.svg` - Field selection
- `where_clause.svg`, `condition.svg` - Filtering
- `for_clause.svg` - Iteration (ariane-xml specific)
- ... and 13 more

SVGs can be viewed:
- ✅ Inline in Markdown (GitHub, VS Code, etc.)
- ✅ Directly in web browsers
- ✅ In any SVG viewer

### Regenerating Diagrams

If you modify the EBNF grammar, regenerate diagrams:

```bash
# Install dependencies (first time only)
npm install

# Generate all diagrams
node generate_diagrams.js
```

This will regenerate all 19 SVG files in `diagrams/`.

## EBNF Grammar

The complete formal grammar is defined in:
- [ebnf/ariane-xml-sql-grammar.ebnf](ebnf/ariane-xml-sql-grammar.ebnf)

**Notation**: W3C EBNF (Extended Backus-Naur Form)

**Key symbols**:
- `::=` defines a rule
- `|` separates alternatives
- `?` optional (zero or one)
- `*` repetition (zero or more)
- `+` repetition (one or more)
- `()` grouping

## Examples

The SELECT statement documentation includes **18+ comprehensive examples**:

1. Simple SELECT
2. SELECT with WHERE
3. SELECT with FOR clause
4. Multiple FOR clauses (nested iteration)
5. FOR with AT (position variables)
6. Aggregation functions
7. GROUP BY with aggregation
8. HAVING clause
9. ORDER BY with multiple keys
10. Pagination (LIMIT/OFFSET)
11. NULL conditions
12. LIKE with regex
13. IN operator
14. XML attributes
15. FILE_NAME selector
16. DISTINCT
17. Complex WHERE (AND/OR)
18. NOT IN operator

All examples are executable and demonstrate real-world usage patterns.

## Technical Details

### Grammar Approach

This documentation uses **Option C** from the original proposal:
1. ✅ Define grammar in EBNF (W3C notation)
2. ✅ Generate railroad diagrams from grammar
3. ✅ Create Oracle-style comprehensive documentation

### Tools Used

- **EBNF Notation**: W3C Extended Backus-Naur Form
- **Diagram Generation**: railroad-diagrams JavaScript library
- **Documentation Style**: Oracle SQL Language Reference format
- **Version Control**: Git (integrated with ariane-xml repository)

### Dependencies

```json
{
  "railroad-diagrams": "^1.0.0"
}
```

Install with: `npm install`

## Integration with Ariane-XML

This documentation is part of the main ariane-xml project:

**Location**: `ariane-xml-documentation/SQL_Language_Reference/`

**Related documentation**:
- [Main README](../../README.md)
- [CLI Quick Start](../01a_Quick_Start_CLI.md)
- [Jupyter Quick Start](../01b_Quick_Start_Jupyter.md)
- [DSN Mode Design](../Analysis/DSN_MODE_DESIGN.md)
- [Examples Collection](../../ariane-xml-examples/EXAMPLES.md)

## Contributing

To contribute to this documentation:

1. **Update EBNF grammar**: Edit `ebnf/ariane-xml-sql-grammar.ebnf`
2. **Regenerate diagrams**: Run `node generate_diagrams.js`
3. **Update documentation**: Edit relevant Markdown files
4. **Add examples**: Include practical, executable examples
5. **Test**: Verify all links and examples work
6. **Commit**: Use clear commit messages

## Version History

- **v1.0 (MVP)** - 2025-11-20
  - Initial release with SELECT statement
  - 19 railroad diagrams
  - Complete EBNF grammar
  - Introduction and syntax guide

## License

This documentation is part of the ariane-xml project and follows the same license.

## Feedback

Found an issue or have suggestions?
- Report at the project repository
- Check existing documentation in `ariane-xml-documentation/`

---

**Get Started**: [📖 Documentation Index](00_Index.md)

**Learn by Example**: [💡 SELECT Statement](03_SQL_Statements/SELECT_Statement.md)

**Understand the Syntax**: [📐 Syntax Notation Guide](02_Syntax_Notation/README.md)
