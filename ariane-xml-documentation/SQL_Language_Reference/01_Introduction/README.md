# Introduction to Ariane-XML SQL

## Overview

**Ariane-XML** is a specialized SQL query engine designed for querying XML files using familiar SQL syntax. It extends standard SQL with XML-specific features, making it easy to extract, filter, and aggregate data from XML documents without writing XPath or XSLT code.

## Why Ariane-XML?

Traditional XML querying requires:
- **XPath**: Complex syntax for navigating XML trees
- **XSLT**: Verbose transformations
- **Custom parsers**: Time-consuming development

Ariane-XML provides:
- ✅ **Familiar SQL syntax** - Use SELECT, WHERE, GROUP BY, ORDER BY
- ✅ **Powerful iteration** - FOR clause for nested XML structures
- ✅ **Aggregation** - COUNT, SUM, AVG, MIN, MAX functions
- ✅ **Pattern matching** - Regex support with LIKE operator
- ✅ **Multi-file queries** - Query multiple XML files with wildcards
- ✅ **High performance** - Multi-threaded processing

## Basic Concepts

### XML Documents as Data Sources

Ariane-XML treats XML documents as queryable data sources, similar to database tables. However, unlike flat relational tables, XML documents have:
- **Hierarchical structure** - Nested elements
- **Repeating elements** - Lists and collections
- **Attributes** - Metadata on elements

### Field Paths

Instead of column names, ariane-xml uses **field paths** to navigate XML hierarchies:

```sql
-- Access nested elements
SELECT employee.name, employee.address.city
FROM ./data.xml
```

**Supported notations:**
- Dot notation: `root.element.subelement`
- Slash notation: `root/element/subelement`
- Partial paths: `.element` (searches from any context)
- Attributes: `@attribute_name`

### The FOR Clause ⭐

The **FOR clause** is ariane-xml's most powerful feature. It binds variables to iterate over XML collections:

```sql
-- Iterate over employees
SELECT emp.name, emp.salary
FROM ./data.xml
FOR emp IN employees.employee
WHERE emp.salary > 50000
```

This is analogous to a for-each loop in programming languages.

### Multiple FOR Clauses (Nested Iteration)

You can chain FOR clauses to iterate over nested structures:

```sql
-- Iterate over companies → departments → employees
SELECT company.name, dept.name, emp.name
FROM ./data.xml
FOR company IN companies.company
FOR dept IN company.departments.department
FOR emp IN dept.employees.employee
```

## Quick Start Examples

### Example 1: Simple Query

```sql
SELECT employee.name, employee.salary
FROM ./employees.xml
```

Retrieves name and salary from all employee elements.

### Example 2: Filtering with WHERE

```sql
SELECT employee.name
FROM ./employees.xml
WHERE employee.salary > 50000
```

Returns employees with salary greater than 50,000.

### Example 3: Using FOR Clause

```sql
SELECT emp.name, emp.department
FROM ./employees.xml
FOR emp IN employee
WHERE emp.department = 'Engineering'
```

Iterates over employee elements and filters by department.

### Example 4: Aggregation

```sql
SELECT COUNT(employee) AS total,
       AVG(employee.salary) AS avg_salary
FROM ./employees.xml
```

Calculates total count and average salary.

### Example 5: Grouping

```sql
SELECT department, COUNT(emp) AS emp_count
FROM ./employees.xml
FOR emp IN employee
GROUP BY department
```

Groups employees by department and counts each group.

### Example 6: Querying Multiple Files

```sql
SELECT FILE_NAME, COUNT(employee) AS count
FROM ./data/**/*.xml
GROUP BY FILE_NAME
```

Queries all XML files recursively and shows counts per file.

## SQL Dialect Features

### Standard SQL Features

Ariane-XML supports these standard SQL features:

| Feature | Description |
|---------|-------------|
| SELECT | Specify fields to retrieve |
| DISTINCT | Eliminate duplicate rows |
| FROM | Specify source file(s) |
| WHERE | Filter rows |
| GROUP BY | Group rows by field values |
| HAVING | Filter groups |
| ORDER BY | Sort results |
| LIMIT | Limit number of results |
| OFFSET | Skip rows (pagination) |
| Aggregations | COUNT, SUM, AVG, MIN, MAX |
| Comparisons | =, !=, <, >, <=, >= |
| Logical | AND, OR, NOT |
| NULL checks | IS NULL, IS NOT NULL |
| List membership | IN, NOT IN |

### Ariane-XML Extensions ⭐

These features are unique to ariane-xml:

| Feature | Description |
|---------|-------------|
| **FOR clause** | Bind variables to iterate over XML collections |
| **AT clause** | Track iteration index (position variable) |
| **Partial paths** | Leading dot notation for flexible matching |
| **Dual separators** | Use `.` or `/` in paths |
| **XML attributes** | Query attributes with `@attribute` |
| **FILE_NAME** | Special selector for source filename |
| **Regex in LIKE** | Pattern matching with `/regex/` syntax |
| **DSN mode** | Shortcuts for French tax forms |

## Comparison with Other Query Languages

### Ariane-XML vs XPath

| Task | XPath | Ariane-XML SQL |
|------|-------|----------------|
| Select elements | `//employee[@salary>50000]/name` | `SELECT name FROM ... WHERE salary > 50000` |
| Aggregation | Complex (requires XSLT) | `SELECT COUNT(emp) FROM ... FOR emp IN employee` |
| Multiple files | Not supported | `FROM ./data/**/*.xml` |
| Grouping | Not supported | `GROUP BY department` |

### Ariane-XML vs SQL on Relational DBs

| Aspect | Relational SQL | Ariane-XML SQL |
|--------|----------------|----------------|
| Data source | Tables (flat) | XML files (hierarchical) |
| Joins | JOIN keyword | FOR clause (iteration) |
| Nested data | Requires multiple tables | Natural with FOR clause |
| Schema | Required | Optional (XSD) |

## Query Execution Model

1. **File Discovery**: Locate XML files matching the FROM path (supports wildcards)
2. **Parsing**: Parse XML documents into in-memory tree structures
3. **Iteration**: Process FOR clauses to establish iteration contexts
4. **Filtering**: Apply WHERE conditions to filter rows
5. **Grouping**: If GROUP BY is present, group rows by specified fields
6. **Aggregation**: Compute aggregation functions (COUNT, SUM, etc.)
7. **Filtering Groups**: Apply HAVING conditions to groups
8. **Sorting**: Apply ORDER BY to sort results
9. **Pagination**: Apply LIMIT and OFFSET
10. **Output**: Return result set as rows

**Multi-threading**: When querying multiple files, ariane-xml processes files in parallel for improved performance.

## Use Cases

Ariane-XML is ideal for:

✅ **Data extraction** - Extract specific fields from XML documents
✅ **Data analysis** - Aggregate and analyze XML data
✅ **Report generation** - Query XML files to generate reports
✅ **Data validation** - Check XML content against business rules
✅ **ETL processes** - Extract data from XML for transformation
✅ **Configuration querying** - Query XML configuration files
✅ **Log analysis** - Analyze XML-formatted logs
✅ **French tax forms** - DSN mode for Déclaration Sociale Nominative

## Next Steps

- **Learn the SELECT statement**: [SELECT Statement](../03_SQL_Statements/SELECT_Statement.md)
- **Master the FOR clause**: [FOR Clause](../04_SQL_Clauses/FOR_Clause.md)
- **Try examples**: [Examples Collection](../../../ariane-xml-examples/EXAMPLES.md)
- **Read the full reference**: [Index](../00_Index.md)

## Additional Resources

- [CLI Quick Start](../../01a_Quick_Start_CLI.md)
- [Jupyter Notebook Integration](../../01b_Quick_Start_Jupyter.md)
- [Installation Guide](../../02_Installation_Guide.md)
- [DSN Mode Documentation](../../DSN_MODE_DESIGN.md)

---

**Navigation:**
- [← Back to Index](../00_Index.md)
- [Next: Syntax Notation →](../02_Syntax_Notation/README.md)
