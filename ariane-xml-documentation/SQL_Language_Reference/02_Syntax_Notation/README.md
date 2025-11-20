# Syntax Notation Guide

## Overview

This guide explains how to read and interpret the **syntax diagrams** (railroad diagrams) and **EBNF grammar** used throughout the Ariane-XML SQL Language Reference.

## Railroad Diagrams

Railroad diagrams (also called syntax diagrams) provide a visual representation of the SQL grammar. They show the valid paths through a language construct.

### Basic Elements

#### 1. Terminals (Keywords and Symbols)

Terminals are exact tokens that must appear literally in your SQL query.

**Represented as:** Rectangles with rounded corners

**Examples:**
- `SELECT` - SQL keyword
- `(` - Left parenthesis
- `,` - Comma

#### 2. Non-Terminals (Grammar Rules)

Non-terminals are references to other grammar rules defined elsewhere.

**Represented as:** Rectangles with square corners

**Examples:**
- `field_list` - Refers to the field_list grammar rule
- `where_expression` - Refers to the where_expression grammar rule

#### 3. Flow Lines and Arrows

Arrows show the direction of flow through the diagram.

**Rules:**
- Follow arrows from left to right
- Start at the left entry point
- End at the right exit point
- All valid paths from entry to exit are legal syntax

### Diagram Patterns

#### Optional Elements

Elements that may be included or skipped.

**Pattern:** Alternative paths with one path bypassing the element

**Example:** Optional DISTINCT keyword
```
    ┌─────────────┐
    │   DISTINCT  │
    └─────────────┘
         ↓↑
    (path around)
```

**SQL Usage:**
```sql
SELECT name FROM ...          -- Valid (without DISTINCT)
SELECT DISTINCT name FROM ... -- Valid (with DISTINCT)
```

#### Repetition (Zero or More)

Elements that can be repeated zero or more times.

**Pattern:** Loop back path

**Example:** Zero or more FOR clauses
```
    ┌─────────────┐
    │ for_clause  │←─┐
    └─────────────┘  │
         ↓           │
    (loop back)──────┘
    (or skip)
```

**SQL Usage:**
```sql
SELECT ... FROM ...                    -- Valid (zero FOR clauses)
SELECT ... FROM ... FOR x IN y         -- Valid (one FOR clause)
SELECT ... FROM ... FOR x IN y FOR z IN w -- Valid (two FOR clauses)
```

#### Repetition (One or More)

Elements that must appear at least once but can be repeated.

**Pattern:** Required element with loop back

**Example:** One or more fields separated by commas
```
    ┌─────────┐
    │  field  │←─┐
    └─────────┘  │
         ↓       │
      ┌───┐     │
      │ , │─────┘
      └───┘
```

**SQL Usage:**
```sql
SELECT name                    -- Valid (one field)
SELECT name, salary            -- Valid (two fields)
SELECT name, salary, department -- Valid (three fields)
```

#### Choice (Alternatives)

Multiple alternative paths where exactly one must be chosen.

**Pattern:** Branching paths

**Example:** ASC or DESC
```
         ┌─────────┐
    ─────│  ASC    │─────
    │    └─────────┘    │
    │                   │
    │    ┌─────────┐    │
    └────│  DESC   │────┘
         └─────────┘
```

**SQL Usage:**
```sql
ORDER BY salary ASC  -- Valid (choose ASC)
ORDER BY salary DESC -- Valid (choose DESC)
```

#### Sequence

Elements that must appear in order.

**Pattern:** Elements connected in a straight line

**Example:** FROM file_path
```
    ┌──────┐    ┌───────────┐
    │ FROM │────│ file_path │
    └──────┘    └───────────┘
```

**SQL Usage:**
```sql
FROM ./data.xml -- Valid (FROM followed by file_path)
```

### Reading Complex Diagrams

#### Example: WHERE Clause

![where_clause](../diagrams/where_clause.svg)

**Interpretation:**
1. Start at the left entry point
2. Must pass through `WHERE` keyword (terminal)
3. Must pass through `where_expression` (non-terminal)
4. Exit at the right

**Valid SQL:**
```sql
WHERE salary > 50000
```

#### Example: ORDER BY Clause

![order_by_clause](../diagrams/order_by_clause.svg)

**Interpretation:**
1. Must include `ORDER BY` keywords
2. Must include at least one `field_name`
3. Each field_name can optionally be followed by `ASC` or `DESC`
4. Multiple fields can be separated by commas (repetition)

**Valid SQL:**
```sql
ORDER BY salary                      -- One field, no direction
ORDER BY salary DESC                 -- One field with direction
ORDER BY department ASC, salary DESC -- Multiple fields
```

#### Example: Condition

![condition](../diagrams/condition.svg)

**Interpretation:**
1. Choose one of four alternatives:
   - Comparison: `field_path_expression` + comparison operator + `value`
   - NULL check: `field_path_expression` + `IS` + optional `NOT` + `NULL`
   - Pattern match: `field_path_expression` + optional `NOT` + `LIKE` + `regex_pattern`
   - List membership: `field_path_expression` + optional `NOT` + `IN` + `(` + `value_list` + `)`

**Valid SQL:**
```sql
salary > 50000                    -- Comparison
status IS NULL                    -- NULL check
name LIKE /^John/                 -- Pattern match
department IN ('Sales', 'Marketing') -- List membership
```

## EBNF Notation

In addition to railroad diagrams, the complete grammar is defined in **EBNF** (Extended Backus-Naur Form) notation.

### EBNF Symbols

| Symbol | Meaning | Example |
|--------|---------|---------|
| `::=` | "is defined as" | `field ::= identifier` |
| `\|` | "or" (alternative) | `direction ::= ASC \| DESC` |
| `?` | Optional (zero or one) | `distinct?` |
| `*` | Repetition (zero or more) | `for_clause*` |
| `+` | Repetition (one or more) | `field+` |
| `()` | Grouping | `(ASC \| DESC)?` |
| `'x'` | Terminal (literal) | `'SELECT'` |

### EBNF Examples

#### Optional Element
```ebnf
select_statement ::= SELECT distinct? field_list ...
```
**Meaning:** DISTINCT is optional

#### Repetition (Zero or More)
```ebnf
select_statement ::= ... for_clause* where_clause? ...
```
**Meaning:** Zero or more FOR clauses

#### Repetition (One or More)
```ebnf
field_list ::= field (',' field)*
```
**Meaning:** At least one field, optionally followed by comma and more fields

**Equivalent to:** One or more fields separated by commas

#### Choice (Alternatives)
```ebnf
aggregate_name ::= COUNT | SUM | AVG | MIN | MAX
```
**Meaning:** Choose exactly one of the five options

#### Grouping
```ebnf
order_field ::= field_name (ASC | DESC)?
```
**Meaning:** field_name followed by optional ASC or DESC

### Complete EBNF Grammar

The complete EBNF grammar for ariane-xml SQL is available in:
- [ariane-xml-sql-grammar.ebnf](../ebnf/ariane-xml-sql-grammar.ebnf)

## Notation Conventions in Documentation

### Text Conventions

| Convention | Meaning | Example |
|------------|---------|---------|
| `code` | SQL keywords, identifiers, code | `SELECT`, `field_name` |
| **bold** | Emphasis, important terms | **FOR clause** |
| *italic* | Placeholders, notes | *file_path* |
| ⭐ | Ariane-xml specific feature | **FOR clause** ⭐ |

### Placeholder Names

Throughout the documentation, we use consistent placeholder names:

| Placeholder | Meaning |
|-------------|---------|
| `field_name` | Name of a field |
| `field_path` | Path to a field (e.g., `root.element.field`) |
| `file_path` | Path to XML file(s) |
| `identifier` | Variable or field identifier |
| `variable` | Variable name (in FOR clause) |
| `value` | Literal value (string, number, etc.) |
| `number` | Numeric literal |
| `condition` | Boolean condition expression |

### SQL Syntax Format

When presenting SQL syntax, we use:

```sql
SELECT [DISTINCT] field_list
FROM file_path
[FOR variable IN field_path [AT position_var]]*
[WHERE condition]
...
```

**Legend:**
- `UPPERCASE` - SQL keywords
- `lowercase` - Placeholders (non-terminals)
- `[...]` - Optional elements
- `[...]*` - Zero or more repetitions
- `[...]+` - One or more repetitions
- `|` - Alternatives (choose one)

### Example SQL Queries

Example queries are shown in code blocks with syntax highlighting:

```sql
SELECT emp.name, emp.salary
FROM ./data/employees.xml
FOR emp IN employee
WHERE emp.salary > 50000
ORDER BY emp.salary DESC
LIMIT 10
```

## Tips for Reading Syntax

1. **Start simple**: Begin with basic examples, then gradually add complexity
2. **Follow the arrows**: In railroad diagrams, follow all possible paths to understand options
3. **Check examples**: Look at SQL examples to see syntax in action
4. **Optional vs required**: Pay attention to which elements are optional vs required
5. **Order matters**: Elements must appear in the order shown in diagrams
6. **Repetition**: Note whether elements can be repeated and how

## Practice Examples

### Exercise 1: Parse a SELECT Statement

Given this SQL:
```sql
SELECT DISTINCT name, salary
FROM ./employees.xml
FOR emp IN employee
WHERE salary > 50000
ORDER BY salary DESC
LIMIT 10
```

**Identify:**
- ✅ DISTINCT (optional, present)
- ✅ field_list: `name, salary`
- ✅ FROM clause: `./employees.xml`
- ✅ FOR clause: `FOR emp IN employee`
- ✅ WHERE clause: `WHERE salary > 50000`
- ✅ ORDER BY clause: `ORDER BY salary DESC`
- ✅ LIMIT clause: `LIMIT 10`
- ❌ GROUP BY clause (optional, not present)
- ❌ HAVING clause (optional, not present)
- ❌ OFFSET clause (optional, not present)

### Exercise 2: Construct a Valid Query

Using the SELECT statement diagram, construct a query that:
- Selects `department` and count of employees
- Groups by `department`
- Filters groups with more than 5 employees
- Sorts by count in descending order

**Answer:**
```sql
SELECT department, COUNT(emp) AS count
FROM ./employees.xml
FOR emp IN employee
GROUP BY department
HAVING COUNT(emp) > 5
ORDER BY count DESC
```

## Additional Resources

- [SELECT Statement](../03_SQL_Statements/SELECT_Statement.md) - Full SELECT documentation
- [EBNF Grammar](../ebnf/ariane-xml-sql-grammar.ebnf) - Complete grammar definition
- [Railroad Diagram Generator](../generate_diagrams.js) - Script that generates diagrams
- [Examples Collection](../../../ariane-xml-examples/EXAMPLES.md) - Real-world examples

---

**Navigation:**
- [← Back to Introduction](../01_Introduction/README.md)
- [→ Next: SELECT Statement](../03_SQL_Statements/SELECT_Statement.md)
- [↑ Back to Index](../00_Index.md)
