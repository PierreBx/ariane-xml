# SELECT Statement

## Purpose

Use the `SELECT` statement to retrieve and query data from XML files. The SELECT statement is the primary means of extracting information from XML documents in ariane-xml.

## Prerequisites

To execute SELECT queries, you need:
- Valid XML file(s) in the specified path
- Appropriate file system permissions to read the XML files
- (Optional) An XSD schema for validation and type information

## Syntax

### select_statement

![select_statement](../diagrams/select_statement.svg)

**Simplified Syntax:**

```sql
SELECT [DISTINCT] field_list
FROM file_path
[FOR variable IN field_path [AT position_var]]*
[WHERE condition]
[GROUP BY field_name [, field_name]...]
[HAVING condition]
[ORDER BY field_name [ASC|DESC] [, field_name [ASC|DESC]]...]
[LIMIT number]
[OFFSET number]
```

## Detailed Syntax

### SELECT Clause

The SELECT clause specifies which fields to retrieve from the XML documents.

![field_list](../diagrams/field_list.svg)

![field](../diagrams/field.svg)

**Components:**

- **DISTINCT**: Optional keyword that eliminates duplicate rows from the result set
- **field_list**: Comma-separated list of fields to select. Each field can be:
  - An **aggregation function** (COUNT, SUM, AVG, MIN, MAX)
  - A **field path expression** (with optional AS alias)
  - The special **FILE_NAME** selector to include the source filename

**Aggregation Functions:**

![aggregation_function](../diagrams/aggregation_function.svg)

Supported aggregation functions:
- `COUNT(field)` - Counts non-null occurrences of the field
- `SUM(field)` - Sums numeric values
- `AVG(field)` - Calculates average of numeric values
- `MIN(field)` - Finds minimum value
- `MAX(field)` - Finds maximum value

**Field Path Expressions:**

![field_path_expression](../diagrams/field_path_expression.svg)

Field paths in ariane-xml support multiple notations:

1. **Absolute paths**: `root.element.subelement` or `root/element/subelement`
2. **Partial paths**: `.element.subelement` (leading dot searches from any context)
3. **XML attributes**: `@attribute_name`
4. **Variable references**: `var.field` (when variable is bound by FOR clause)
5. **Position variables**: `pos` (when bound by FOR...AT clause)

**Path separators**: Both `.` (dot) and `/` (slash) are supported and equivalent.

### FROM Clause

The FROM clause specifies the source XML file(s) to query.

![from_clause](../diagrams/from_clause.svg)

**file_path** can be:
- A **string literal**: `FROM "./data/employees.xml"` or `FROM './data/*.xml'`
- A **path expression**: `FROM data/employees.xml`

**Wildcards**: The file path supports glob patterns:
- `*` matches any characters in a filename
- `**` matches any number of directories
- Examples: `./data/*.xml`, `./data/**/*.xml`

### FOR Clause ⭐ (ariane-xml specific)

The FOR clause is a unique feature of ariane-xml that binds iteration variables to XML elements, enabling queries over nested structures.

![for_clause](../diagrams/for_clause.svg)

**Syntax:**
```sql
FOR variable_name IN field_path [AT position_variable]
```

**Semantics:**
- **variable_name**: Identifier for the iteration variable
- **field_path**: Path expression that evaluates to a collection of XML elements
- **AT position_variable**: Optional clause to bind the iteration index (0-based)

**Multiple FOR clauses**: You can chain multiple FOR clauses to iterate over nested structures.

**Example:**
```sql
SELECT emp.name, emp.salary
FROM ./data.xml
FOR emp IN employees.employee
```

This binds `emp` to each `employee` element within `employees`, allowing you to access `emp.name` and `emp.salary`.

### WHERE Clause

The WHERE clause filters results based on specified conditions.

![where_clause](../diagrams/where_clause.svg)

**Logical Structure:**

The WHERE expression is built hierarchically:

1. **OR expressions** (highest precedence):
   ![where_or_expression](../diagrams/where_or_expression.svg)

2. **AND expressions**:
   ![where_and_expression](../diagrams/where_and_expression.svg)

3. **Primary expressions** (conditions or parenthesized sub-expressions):
   ![where_primary](../diagrams/where_primary.svg)

**Conditions:**

![condition](../diagrams/condition.svg)

Supported condition types:

1. **Comparison conditions**: `field = value`, `field != value`, `field < value`, `field > value`, `field <= value`, `field >= value`
2. **NULL conditions**: `field IS NULL`, `field IS NOT NULL`
3. **Pattern matching**: `field LIKE /regex/`, `field NOT LIKE /regex/`
4. **List membership**: `field IN (val1, val2, ...)`, `field NOT IN (...)`

**Operator Precedence** (highest to lowest):
1. Parentheses `()`
2. Comparison operators (`=`, `!=`, `<`, `>`, `<=`, `>=`)
3. `IS [NOT] NULL`, `[NOT] LIKE`, `[NOT] IN`
4. `AND`
5. `OR`

### GROUP BY Clause

The GROUP BY clause groups rows that have the same values in specified fields.

![group_by_clause](../diagrams/group_by_clause.svg)

**Semantics:**
- Groups result rows by the specified field(s)
- Typically used with aggregation functions (COUNT, SUM, AVG, MIN, MAX)
- All non-aggregated fields in SELECT must appear in GROUP BY

### HAVING Clause

The HAVING clause filters grouped results (similar to WHERE, but operates on groups).

![having_clause](../diagrams/having_clause.svg)

**Semantics:**
- Applies conditions to grouped results
- Can use aggregation functions in conditions
- Executed after GROUP BY, before ORDER BY

**Difference from WHERE:**
- WHERE filters individual rows before grouping
- HAVING filters groups after aggregation

### ORDER BY Clause

The ORDER BY clause sorts the result set by one or more fields.

![order_by_clause](../diagrams/order_by_clause.svg)

**Semantics:**
- **ASC**: Ascending order (default)
- **DESC**: Descending order
- Multiple sort keys: Sorts by first field, then by second for ties, etc.

### LIMIT Clause

The LIMIT clause restricts the number of rows returned.

![limit_clause](../diagrams/limit_clause.svg)

**Semantics:**
- Returns at most N rows
- Applied after all other clauses (WHERE, ORDER BY, etc.)

### OFFSET Clause

The OFFSET clause skips a specified number of rows before returning results.

![offset_clause](../diagrams/offset_clause.svg)

**Semantics:**
- Skips the first N rows
- Often used with LIMIT for pagination
- Applied after WHERE and ORDER BY, before LIMIT

## Examples

### Example 1: Simple SELECT

```sql
SELECT employee.name, employee.salary
FROM ./data/employees.xml
```

Retrieves the `name` and `salary` fields from all `employee` elements.

---

### Example 2: SELECT with WHERE

```sql
SELECT name, salary
FROM ./data/employees.xml
WHERE salary > 50000
```

Retrieves employees with salary greater than 50,000.

---

### Example 3: SELECT with FOR Clause

```sql
SELECT emp.name, emp.salary, emp.department
FROM ./data/company.xml
FOR emp IN employees.employee
WHERE emp.salary > 60000
```

Iterates over each `employee` element within `employees` and filters by salary.

---

### Example 4: SELECT with Multiple FOR Clauses (Nested Iteration)

```sql
SELECT company.name, dept.name, emp.name
FROM ./data/*.xml
FOR company IN companies.company
FOR dept IN company.departments.department
FOR emp IN dept.employees.employee
```

Demonstrates nested iteration over companies, departments, and employees.

---

### Example 5: SELECT with FOR...AT (Position Variable)

```sql
SELECT emp.name, position
FROM ./data/employees.xml
FOR emp IN employee AT position
```

Binds `position` to the iteration index (0, 1, 2, ...) for each employee.

---

### Example 6: Aggregation Functions

```sql
SELECT COUNT(employee) AS total_employees,
       AVG(employee.salary) AS average_salary,
       MAX(employee.salary) AS max_salary
FROM ./data/employees.xml
```

Calculates aggregate statistics across all employees.

---

### Example 7: GROUP BY with Aggregation

```sql
SELECT department, COUNT(emp) AS emp_count, AVG(emp.salary) AS avg_salary
FROM ./data/employees.xml
FOR emp IN employee
GROUP BY department
```

Groups employees by department and calculates statistics for each department.

---

### Example 8: HAVING Clause

```sql
SELECT department, COUNT(emp) AS emp_count
FROM ./data/employees.xml
FOR emp IN employee
GROUP BY department
HAVING COUNT(emp) > 5
```

Filters departments to show only those with more than 5 employees.

---

### Example 9: ORDER BY with Multiple Keys

```sql
SELECT emp.department, emp.name, emp.salary
FROM ./data/employees.xml
FOR emp IN employee
ORDER BY emp.department ASC, emp.salary DESC
```

Sorts by department (ascending), then by salary (descending) within each department.

---

### Example 10: Pagination with LIMIT and OFFSET

```sql
SELECT name, salary
FROM ./data/employees.xml
ORDER BY salary DESC
LIMIT 10
OFFSET 20
```

Retrieves rows 21-30 (skips first 20, returns next 10) when sorted by salary.

---

### Example 11: NULL Conditions

```sql
SELECT emp.name, emp.bonus
FROM ./data/employees.xml
FOR emp IN employee
WHERE emp.bonus IS NOT NULL
```

Selects only employees who have a bonus value.

---

### Example 12: LIKE with Regex

```sql
SELECT name
FROM ./data/employees.xml
WHERE name LIKE /^John.*/
```

Selects employees whose name starts with "John" (uses regex pattern matching).

---

### Example 13: IN Operator

```sql
SELECT name, status
FROM ./data/employees.xml
WHERE status IN ('active', 'on-leave', 'probation')
```

Selects employees with specific status values.

---

### Example 14: XML Attributes

```sql
SELECT @id, @status, employee.name
FROM ./data/employees.xml
WHERE @status = 'active'
```

Queries XML attributes using the `@` prefix.

---

### Example 15: FILE_NAME Selector

```sql
SELECT FILE_NAME, COUNT(employee) AS count
FROM ./data/**/*.xml
GROUP BY FILE_NAME
```

Includes the source filename in results, useful when querying multiple files.

---

### Example 16: DISTINCT

```sql
SELECT DISTINCT department
FROM ./data/employees.xml
FOR emp IN employee
```

Returns unique department names (eliminates duplicates).

---

### Example 17: Complex WHERE with AND/OR

```sql
SELECT name, salary, department
FROM ./data/employees.xml
WHERE (salary > 50000 AND department = 'Engineering')
   OR (salary > 70000 AND department = 'Sales')
```

Demonstrates complex logical conditions with parentheses.

---

### Example 18: NOT IN Operator

```sql
SELECT name, status
FROM ./data/employees.xml
WHERE status NOT IN ('terminated', 'resigned')
```

Excludes employees with certain status values.

## Notes

### Performance Considerations

1. **Multi-threaded Processing**: ariane-xml processes multiple XML files in parallel when wildcards are used
2. **WHERE Clause Optimization**: Conditions are evaluated as soon as possible to minimize processing
3. **Index Usage**: Currently, ariane-xml does not use indexes; all filtering is sequential

### Path Resolution

- **Partial paths** (`.field.subfield`) are resolved by searching from any matching ancestor in the XML tree
- **Absolute paths** (`field.subfield`) must match from the document root or current context
- Both `.` and `/` separators are supported and functionally equivalent

### Type Coercion

- Numeric comparisons automatically convert string values to numbers
- String comparisons are lexicographic
- NULL is a distinct value and only matches with `IS NULL` or `IS NOT NULL`

### FOR Clause Scoping

- FOR variables are scoped to the query
- Multiple FOR clauses create nested iteration contexts
- Variable names must be unique within a query
- Variables can be referenced in SELECT, WHERE, GROUP BY, ORDER BY, and HAVING clauses

### Aggregation Restrictions

- When using aggregation functions without GROUP BY, all selected fields must be aggregations
- When using GROUP BY, non-aggregated fields in SELECT must appear in GROUP BY
- Aggregation functions can be used in HAVING but not in WHERE

### Regex Syntax

- LIKE uses **ECMAScript regex syntax** (JavaScript/C++ standard)
- Regex patterns are enclosed in forward slashes: `/pattern/`
- Examples: `/^start/`, `/end$/`, `/contains/`, `/[0-9]+/`

### DSN Mode

- Ariane-xml supports a special **DSN mode** for French tax forms
- In DSN mode, shortcuts like `30.001` are automatically expanded to `S21_G00_30_001`
- See [DSN Mode Documentation](../../DSN_MODE_DESIGN.md) for details

## Related Topics

- [FROM Clause](../04_SQL_Clauses/FROM_Clause.md)
- [FOR Clause](../04_SQL_Clauses/FOR_Clause.md) ⭐
- [WHERE Clause](../04_SQL_Clauses/WHERE_Clause.md)
- [GROUP BY Clause](../04_SQL_Clauses/GROUP_BY_Clause.md)
- [HAVING Clause](../04_SQL_Clauses/HAVING_Clause.md)
- [ORDER BY Clause](../04_SQL_Clauses/ORDER_BY_Clause.md)
- [LIMIT and OFFSET Clauses](../04_SQL_Clauses/LIMIT_OFFSET_Clause.md)
- [Field Path Expressions](../05_SQL_Expressions/Field_Paths.md)
- [Aggregation Functions](../05_SQL_Expressions/Aggregation_Functions.md)
- [Comparison Conditions](../06_SQL_Conditions/Comparison_Conditions.md)
- [NULL Conditions](../06_SQL_Conditions/NULL_Conditions.md)
- [LIKE Conditions](../06_SQL_Conditions/LIKE_Conditions.md)
- [IN Conditions](../06_SQL_Conditions/IN_Conditions.md)
- [DSN Mode](../07_Special_Features/DSN_Mode.md) ⭐

## See Also

- [SQL Language Reference Index](../00_Index.md)
- [Syntax Notation Guide](../02_Syntax_Notation/README.md)
- [Quick Reference](../08_Quick_Reference.md)
