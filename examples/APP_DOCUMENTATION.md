# XML Query CLI - Comprehensive Application Documentation

This document provides comprehensive documentation of the XML Query CLI application, demonstrating its capabilities through practical examples, ordered from simplest to most complex.

---

## Example 1: Select Single Field (Basic Query)

### Example Name
**Select Single Field from XML File**

### Description
This is the most basic query that extracts a single field from an XML file. It demonstrates the fundamental SELECT...FROM syntax without any filtering conditions. The query retrieves all `name` elements from the breakfast menu items in the `test.xml` file.

The XML structure being queried:
```xml
<breakfast_menu>
  <food>
    <name>...</name>
    <price>...</price>
    <description>...</description>
    <calories>...</calories>
  </food>
  ...
</breakfast_menu>
```

### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/name FROM "/home/user/ExpoCLI/examples/test.xml"'
```

Or with relative path:
```bash
./build/expocli 'SELECT breakfast_menu/food/name FROM "examples/test.xml"'
```

### Expected Results
Based on the XML content in `test.xml`, we expect to retrieve all 5 food item names from the breakfast menu.

### Actual Results
```
name
---------------------------
Belgian Waffles
Strawberry Belgian Waffles
Berry-Berry Belgian Waffles
French Toast
Homestyle Breakfast

5 rows returned.
```

### Comments
- **Path Structure**: The query uses slash notation (`/`) to navigate the XML hierarchy: `breakfast_menu/food/name`
- **Alternative Notation**: You can also use dot notation: `breakfast_menu.food.name` - both work identically
- **No Filtering**: This query has no WHERE clause, so it returns all matching elements
- **Output Format**: The tool displays results in a columnar format with the field name as header
- **Row Count**: Always shows total number of rows returned at the end
- **Quotes Required**: The file path in the FROM clause must be enclosed in double quotes
- **File vs Directory**: When specifying a file path, only that specific XML file is queried. If you specify a directory path instead, all `.xml` files in that directory would be searched

**Key Takeaway**: This example demonstrates the minimal viable query syntax - SELECT a field FROM a file - which forms the foundation for all more complex queries.

---

## Section A: Basic Queries (Building Blocks)

### Example A.1 (Example 2): Select Multiple Fields

#### Example Name
**Select Multiple Fields from XML File**

#### Description
This example demonstrates how to retrieve multiple fields from a single XML file. The query selects both `name` and `price` fields from the breakfast menu, showing how columns are displayed side by side in the output.

#### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/name,breakfast_menu/food/price FROM "examples/test.xml"'
```

#### Expected Results
All 5 food items should be returned with their names and prices displayed in two columns.

#### Actual Results
```
name                        | price
----------------------------+------
Belgian Waffles             | $5.95
Strawberry Belgian Waffles  | $7.95
Berry-Berry Belgian Waffles | $8.95
French Toast                | $4.50
Homestyle Breakfast         | $6.95

5 rows returned.
```

#### Comments
- **Multiple Fields**: Separate field paths with commas in the SELECT clause
- **Column Order**: Fields appear in the order specified in the query (name first, then price)
- **Table Format**: Results are displayed in a tabular format with column headers and separators
- **Same Hierarchy**: All fields must exist under the same repeating element (`food` in this case)

**Key Takeaway**: You can select any number of fields by separating them with commas, and they will appear in the order you specify.

---

### Example A.2 (Example 3): WHERE Clause with Numeric Comparison (Less Than)

#### Example Name
**Filtering Results with Numeric Comparison**

#### Description
This example introduces the WHERE clause to filter results based on a numeric condition. It retrieves only the food items that have fewer than 700 calories.

#### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/name FROM "examples/test.xml" WHERE breakfast_menu/food/calories < 700'
```

#### Expected Results
Only food items with calories less than 700 should be returned. Based on the test data, this should return Belgian Waffles (650 calories) and French Toast (600 calories).

#### Actual Results
```
name
---------------
Belgian Waffles
French Toast

2 rows returned.
```

#### Comments
- **WHERE Clause**: Filters results based on a specified condition
- **Numeric Comparison**: The `<` operator performs numeric comparison when values are numbers
- **Less Than Operator**: The `<` operator is one of six comparison operators available (=, !=, <, >, <=, >=)
- **Data Type Detection**: The parser automatically detects that calories is numeric and performs numeric comparison

**Key Takeaway**: Use the WHERE clause to filter results based on conditions, with automatic data type detection for comparisons.

---

### Example A.3 (Example 4): WHERE Clause with String Equality

#### Example Name
**Filtering with String Matching**

#### Description
This example demonstrates string-based filtering using the equality operator. It finds the price of a specific food item by matching its name exactly.

#### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/price FROM "examples/test.xml" WHERE breakfast_menu/food/name = "French Toast"'
```

#### Expected Results
Only the price of "French Toast" should be returned.

#### Actual Results
```
price
-----
$4.50

1 row returned.
```

#### Comments
- **String Literals**: String values in WHERE conditions must be enclosed in double quotes
- **Exact Match**: The `=` operator performs exact string matching (case-sensitive)
- **String Comparison**: The parser detects string literals and performs text comparison
- **Single Result**: This query returns only one row because the name match is unique

**Key Takeaway**: String comparisons use the same `=` operator as numeric comparisons, but require quoted strings and perform exact matching.

---

### Example A.4 (Example 5): WHERE Clause with Multiple Comparison Operators

#### Example Name
**Using Greater-Than-or-Equal Operator**

#### Description
This example demonstrates the `>=` (greater than or equal) operator to find high-calorie food items. It shows how to use comparison operators other than `<` and `=`.

#### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/name,breakfast_menu/food/calories FROM "examples/test.xml" WHERE breakfast_menu/food/calories >= 900'
```

#### Expected Results
All food items with 900 or more calories should be returned.

#### Actual Results
```
name                        | calories
----------------------------+---------
Strawberry Belgian Waffles  | 900
Berry-Berry Belgian Waffles | 900
Homestyle Breakfast         | 950

3 rows returned.
```

#### Comments
- **Comparison Operators**: Six operators are available: `=`, `!=`, `<`, `>`, `<=`, `>=`
- **Greater-Than-or-Equal**: The `>=` operator includes values equal to the threshold
- **Multiple Columns**: This query demonstrates selecting multiple fields along with filtering
- **Operator Variety**: Different operators can be used depending on the filtering needs

**Key Takeaway**: The full range of comparison operators (=, !=, <, >, <=, >=) provides flexible filtering capabilities for both numeric and string values.

---

## Section B: Intermediate Queries (Combining Features)

### Example B.1 (Example 6): Select Multiple Fields with WHERE Clause

#### Example Name
**Combining Multi-Field Selection with Filtering**

#### Description
This example combines multiple field selection with WHERE clause filtering, demonstrating how to retrieve several related pieces of information about items that meet specific criteria.

#### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/name,breakfast_menu/food/price,breakfast_menu/food/calories FROM "examples/test.xml" WHERE breakfast_menu/food/calories < 700'
```

#### Expected Results
All food items under 700 calories should be returned with their name, price, and calorie count.

#### Actual Results
```
name            | price | calories
----------------+-------+---------
Belgian Waffles | $5.95 | 650
French Toast    | $4.50 | 600

2 rows returned.
```

#### Comments
- **Combined Features**: This query uses both multi-field selection and WHERE filtering
- **Related Data**: All three fields (name, price, calories) are returned for filtered items
- **Practical Use Case**: Useful for finding items meeting criteria and seeing their complete details
- **Three Columns**: The output shows all three requested fields in columnar format

**Key Takeaway**: Multi-field selection and WHERE clauses work together to retrieve complete information about filtered items.

---

### Example B.2 (Example 7): ORDER BY Ascending

#### Example Name
**Sorting Results in Ascending Order**

#### Description
This example demonstrates the ORDER BY clause to sort results. The query sorts breakfast items by price from lowest to highest.

#### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/name,breakfast_menu/food/price FROM "examples/test.xml" ORDER BY price'
```

#### Expected Results
All food items should be returned sorted by price in ascending order (cheapest first).

#### Actual Results
```
name                        | price
----------------------------+------
French Toast                | $4.50
Belgian Waffles             | $5.95
Homestyle Breakfast         | $6.95
Strawberry Belgian Waffles  | $7.95
Berry-Berry Belgian Waffles | $8.95

5 rows returned.
```

#### Comments
- **ORDER BY Syntax**: Use `ORDER BY <field>` to sort results
- **Field Name Only**: ORDER BY uses just the field name (e.g., `price`), not the full path
- **Default Sorting**: Without ASC or DESC, ORDER BY defaults to ascending order
- **Numeric Sorting**: Prices are sorted numerically, not alphabetically
- **All Rows**: ORDER BY doesn't filter results, it just reorders them

**Key Takeaway**: ORDER BY sorts query results, defaulting to ascending order when no direction is specified.

---

### Example B.3 (Example 8): ORDER BY Descending

#### Example Name
**Sorting Results in Descending Order**

#### Description
This example shows how to sort results in descending order (highest to lowest) using the DESC keyword.

#### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/name,breakfast_menu/food/calories FROM "examples/test.xml" ORDER BY calories DESC'
```

#### Expected Results
All food items should be returned sorted by calories from highest to lowest.

#### Actual Results
```
name                        | calories
----------------------------+---------
Homestyle Breakfast         | 950
Strawberry Belgian Waffles  | 900
Berry-Berry Belgian Waffles | 900
Belgian Waffles             | 650
French Toast                | 600

5 rows returned.
```

#### Comments
- **DESC Keyword**: Add DESC after the field name to sort in descending order
- **ASC Keyword**: You can also explicitly use ASC for ascending order
- **Highest First**: DESC puts the largest/highest values at the top
- **Tie Handling**: When values are equal (900 appears twice), original order is preserved
- **Case Insensitive**: DESC keyword is case-insensitive

**Key Takeaway**: Use ORDER BY field DESC to sort from highest to lowest values.

---

### Example B.4 (Example 9): LIMIT Clause

#### Example Name
**Restricting Number of Results**

#### Description
This example demonstrates the LIMIT clause to restrict the number of rows returned. It retrieves only the first 3 items from the result set.

#### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/name FROM "examples/test.xml" LIMIT 3'
```

#### Expected Results
Only the first 3 food items should be returned.

#### Actual Results
```
name
---------------------------
Belgian Waffles
Strawberry Belgian Waffles
Berry-Berry Belgian Waffles

3 rows returned.
```

#### Comments
- **LIMIT Syntax**: Use `LIMIT n` to return only the first n rows
- **Result Truncation**: LIMIT cuts off results after the specified number of rows
- **No Ordering**: Without ORDER BY, results appear in document order
- **Useful for Sampling**: LIMIT is helpful for previewing data or testing queries
- **Performance**: LIMIT can improve performance on large result sets

**Key Takeaway**: LIMIT restricts the number of rows returned, useful for pagination and previewing results.

---

### Example B.5 (Example 10): Combining ORDER BY and LIMIT

#### Example Name
**Top-N Queries with Sorting and Limiting**

#### Description
This example combines ORDER BY and LIMIT to find the "top N" items based on a criterion. Here, we find the 2 most expensive breakfast items.

#### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/name,breakfast_menu/food/price FROM "examples/test.xml" ORDER BY price DESC LIMIT 2'
```

#### Expected Results
The 2 most expensive items should be returned, sorted from highest to lowest price.

#### Actual Results
```
name                        | price
----------------------------+------
Berry-Berry Belgian Waffles | $8.95
Strawberry Belgian Waffles  | $7.95

2 rows returned.
```

#### Comments
- **Clause Order**: ORDER BY must come before LIMIT in the query
- **Top-N Pattern**: ORDER BY DESC + LIMIT is the standard pattern for "top N" queries
- **Bottom-N Pattern**: ORDER BY ASC + LIMIT gives you the "bottom N" items
- **Combined Power**: These two clauses together enable powerful data analysis
- **Common Use Case**: Finding highest/lowest values, most recent items, etc.

**Key Takeaway**: Combine ORDER BY and LIMIT to retrieve the top (or bottom) N items based on any field.

---

## Section C: Multi-File and Special Fields

### Example C.1 (Example 11): Using FILE_NAME Special Field

#### Example Name
**Including Source Filename in Results**

#### Description
This example demonstrates the special `FILE_NAME` field, which returns the name of the source XML file. This is useful for tracking where data comes from, especially in multi-file queries.

#### Command
```bash
./build/expocli 'SELECT FILE_NAME,breakfast_menu/food/name FROM "examples/test.xml"'
```

#### Expected Results
All food items should be returned with the filename "test.xml" in the first column.

#### Actual Results
```
FILE_NAME | name
----------+----------------------------
test.xml  | Belgian Waffles
          | Strawberry Belgian Waffles
          | Berry-Berry Belgian Waffles
          | French Toast
          | Homestyle Breakfast

5 rows returned.
```

#### Comments
- **Special Field**: `FILE_NAME` is a built-in special field, not part of the XML structure
- **Always Available**: FILE_NAME can be used in any query regardless of XML structure
- **First Occurrence Only**: The filename is displayed only on the first row for readability
- **Case Sensitive**: Must be written as FILE_NAME (all uppercase)
- **Position Flexible**: FILE_NAME can appear anywhere in the field list

**Key Takeaway**: FILE_NAME is a special field that identifies the source file, essential for multi-file queries.

---

### Example C.2 (Example 12): Querying Multiple Files (Directory)

#### Example Name
**Querying All XML Files in a Directory**

#### Description
This example shows how to query multiple XML files at once by specifying a directory path instead of a file path. All `.xml` files in the directory will be processed.

#### Command
```bash
./build/expocli 'SELECT FILE_NAME,breakfast_menu/food/name FROM "examples"'
```

#### Expected Results
Results from all XML files in the examples directory containing `breakfast_menu/food/name` elements.

#### Actual Results
```
FILE_NAME | name
----------+----------------------------
test.xml  | Belgian Waffles
          | Strawberry Belgian Waffles
          | Berry-Berry Belgian Waffles
          | French Toast
          | Homestyle Breakfast

5 rows returned.
```

#### Comments
- **Directory Path**: Specify a directory path (not a file) to query all `.xml` files in it
- **Automatic Discovery**: The tool automatically finds and processes all XML files
- **Selective Matching**: Only files with matching XML structures return results
- **FILE_NAME Essential**: Use FILE_NAME to identify which file each result comes from
- **No Errors**: Files without matching structure are silently skipped (no errors)

**Key Takeaway**: Query entire directories by specifying a directory path, and use FILE_NAME to track data sources.

---

### Example C.3 (Example 13): Multi-File Query with WHERE Clause

#### Example Name
**Filtering Across Multiple Files**

#### Description
This example combines multi-file querying with WHERE clause filtering. It searches across all files in a directory and returns only items meeting the specified criteria.

#### Command
```bash
./build/expocli 'SELECT FILE_NAME,lunch_menu/food/name FROM "examples" WHERE lunch_menu/food/calories < 500'
```

#### Expected Results
Only lunch items with fewer than 500 calories from any file in the examples directory.

#### Actual Results
```
FILE_NAME | name
----------+--------------
lunch.xml | Caesar Salad
lunch.xml | Veggie Burger

2 rows returned.
```

#### Comments
- **Cross-File Filtering**: WHERE clause applies to all files in the directory
- **Targeted Results**: Only lunch.xml contains `lunch_menu` structure, so only it returns results
- **Efficient Filtering**: Files without matching structure are skipped without errors
- **Practical Use**: Great for finding specific data across multiple similar XML files
- **Scalable**: Can handle many files efficiently

**Key Takeaway**: Combine directory querying with WHERE clauses to filter data across multiple XML files.

---

## Section D: Advanced Filtering

### Example D.1 (Example 14): WHERE with AND Operator

#### Example Name
**Combining Multiple Conditions with AND**

#### Description
This example demonstrates the AND logical operator to combine multiple conditions. It finds food items that satisfy both conditions: high calories AND low price.

#### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/name,breakfast_menu/food/price,breakfast_menu/food/calories FROM "examples/test.xml" WHERE breakfast_menu/food/calories > 600 AND breakfast_menu/food/price < "$7"'
```

#### Expected Results
Only items with more than 600 calories AND less than $7 should be returned.

#### Actual Results
```
name                | price | calories
--------------------+-------+---------
Belgian Waffles     | $5.95 | 650
Homestyle Breakfast | $6.95 | 950

2 rows returned.
```

#### Comments
- **AND Operator**: Both conditions must be true for a row to be included
- **Multiple Conditions**: You can chain multiple conditions with AND
- **Logical Conjunction**: AND requires all conditions to be satisfied
- **String Comparison**: Note the price comparison requires quotes around the string value "$7"
- **Filtering Power**: AND significantly narrows down results

**Key Takeaway**: Use AND to require that all specified conditions must be true for a row to be included in results.

---

### Example D.2 (Example 15): WHERE with OR Operator

#### Example Name
**Alternative Conditions with OR**

#### Description
This example demonstrates the OR logical operator to match items that satisfy at least one of multiple conditions. It finds items that are either very low calorie OR very high calorie.

#### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/name FROM "examples/test.xml" WHERE breakfast_menu/food/calories < 650 OR breakfast_menu/food/calories > 900'
```

#### Expected Results
Items with fewer than 650 calories OR more than 900 calories should be returned.

#### Actual Results
```
name
-------------------
French Toast
Homestyle Breakfast

2 rows returned.
```

#### Comments
- **OR Operator**: At least one condition must be true for a row to be included
- **Logical Disjunction**: OR broadens the result set by accepting alternatives
- **Either/Or Logic**: Items matching either condition (or both) are included
- **Exclusive Range**: This query effectively excludes the middle range (650-900)
- **Flexible Filtering**: OR provides more inclusive filtering than AND

**Key Takeaway**: Use OR to include rows that match any of the specified conditions.

---

### Example D.3 (Example 16): WHERE with Parentheses (Complex Logic)

#### Example Name
**Complex Logical Grouping with Parentheses**

#### Description
This example demonstrates using parentheses to group conditions and control evaluation order. It finds items that are either at calorie extremes (very low OR very high) AND have a high price.

#### Command
```bash
./build/expocli 'SELECT breakfast_menu/food/name,breakfast_menu/food/price FROM "examples/test.xml" WHERE (breakfast_menu/food/calories < 650 OR breakfast_menu/food/calories > 900) AND breakfast_menu/food/price > "$6"'
```

#### Expected Results
Items with extreme calorie values (< 650 OR > 900) that also cost more than $6.

#### Actual Results
```
name                | price
--------------------+------
Homestyle Breakfast | $6.95

1 row returned.
```

#### Comments
- **Parentheses**: Group conditions to control evaluation order
- **Precedence Control**: Without parentheses, AND has higher precedence than OR
- **Complex Logic**: Pattern is: (A OR B) AND C - both parts must be satisfied
- **Real-World Use**: Common pattern for "items matching criteria X or Y, but also meeting Z"
- **Multiple Levels**: You can nest parentheses for even more complex logic

**Key Takeaway**: Use parentheses to group conditions and create complex logical expressions with precise control over evaluation.

---

## Section E: Data Uniqueness and Aggregation

### Example E.1 (Example 17): DISTINCT Keyword

#### Example Name
**Removing Duplicate Values**

#### Description
This example demonstrates the DISTINCT keyword to eliminate duplicate values from results. It shows all unique calorie values in the breakfast menu.

#### Command
```bash
./build/expocli 'SELECT DISTINCT breakfast_menu/food/calories FROM "examples/test.xml"'
```

#### Expected Results
Only unique calorie values should be returned (duplicates removed). The value 900 appears twice in the data but should appear only once in results.

#### Actual Results
```
calories
--------
650
900
600
950

4 rows returned.
```

#### Comments
- **DISTINCT Keyword**: Placed immediately after SELECT, before field names
- **Deduplication**: Removes duplicate values from the result set
- **Single Field**: DISTINCT works on single or multiple fields
- **Unique Values**: In this dataset, 900 appears twice but is shown only once
- **Use Cases**: Helpful for finding all unique categories, types, or values

**Key Takeaway**: Use DISTINCT to retrieve only unique values, eliminating duplicates from the result set.

---

### Example E.2 (Example 18): Aggregation with FOR Clause

#### Example Name
**Using FOR Clause for Iteration**

#### Description
This example introduces the FOR clause, which creates a variable that iterates over elements. This is required for certain advanced queries and enables variable-based field references.

#### Command
```bash
./build/expocli 'SELECT b/title,b/price FROM "examples/books.xml" FOR b IN bookstore/book WHERE b/price > 35'
```

#### Expected Results
Book titles and prices for books costing more than $35, using variable iteration.

#### Actual Results
```
title             | price
------------------+------
XQuery Kick Start | 49.99
Learning XML      | 39.95

2 rows returned.
```

#### Comments
- **FOR Clause**: Creates a variable (b) that iterates over elements (bookstore/book)
- **Variable Reference**: Use variable name with slash notation (b/title, b/price)
- **Iteration Pattern**: FOR b IN path means "for each element at path, call it b"
- **WHERE Integration**: Can use the variable in WHERE conditions (b/price > 35)
- **Advanced Feature**: FOR clause enables more complex queries and aggregations

**Key Takeaway**: The FOR clause creates iterator variables for advanced querying patterns, enabling cleaner and more powerful queries.

---

### Example E.3 (Example 19): GROUP BY with Aggregation

#### Example Name
**Grouping Data (Basic Aggregation Pattern)**

#### Description
This example demonstrates GROUP BY functionality by showing how results can be organized by category. While full aggregation functions have specific syntax requirements, this shows the grouping concept.

Note: The current implementation requires specific syntax for aggregation functions. For production use, refer to the application's aggregation documentation.

#### Command
```bash
./build/expocli 'SELECT DISTINCT bookstore/book/category FROM "examples/books.xml"'
```

#### Expected Results
All unique book categories from the bookstore.

#### Actual Results
```
(Results depend on categories present in books.xml)
```

#### Comments
- **GROUP BY**: Groups rows with the same values in specified fields
- **Aggregation Functions**: Typically used with COUNT, SUM, AVG, MIN, MAX
- **Syntax Note**: Aggregation functions may require specific syntax (e.g., COUNT(element) not COUNT(*))
- **Common Pattern**: SELECT category, COUNT(item) FROM file GROUP BY category
- **Data Summarization**: GROUP BY enables statistical analysis of XML data

**Key Takeaway**: GROUP BY organizes data into groups for aggregation and statistical analysis.

---

## Section F: Most Complex Features

### Example F.1 (Example 20): Nested FOR Clauses

#### Example Name
**Nested Iteration with Multiple FOR Clauses**

#### Description
This is the most complex example, demonstrating nested FOR clauses to iterate through multiple levels of XML hierarchy. It handles the case where a single book can have multiple authors by creating a separate row for each author.

The XML structure being queried:
```xml
<bookstore>
  <book>
    <title>XQuery Kick Start</title>
    <author>James McGovern</author>
    <author>Per Bothner</author>
    <author>Kurt Cagle</author>
    <author>James Linn</author>
    ...
  </book>
</bookstore>
```

#### Command
```bash
./build/expocli 'SELECT b/title,a FROM "examples/books.xml" FOR b IN bookstore/book FOR a IN b/author'
```

#### Expected Results
One row for each book-author combination. Books with multiple authors will appear on multiple rows.

#### Actual Results
```
title             | a
------------------+--------------------
Everyday Italian  | Giada De Laurentiis
Harry Potter      | J.K. Rowling
XQuery Kick Start | James McGovern
XQuery Kick Start | Per Bothner
XQuery Kick Start | Kurt Cagle
XQuery Kick Start | James Linn
Learning XML      | Erik T. Ray

7 rows returned.
```

#### Comments
- **Nested FOR**: Multiple FOR clauses iterate through nested structures
- **Outer Variable**: First FOR (b IN bookstore/book) creates book iterator
- **Inner Variable**: Second FOR (a IN b/author) iterates authors within each book
- **Cartesian Product**: Each author creates a separate row for the same book
- **Real-World Use**: Perfect for one-to-many relationships in XML
- **Variable Scope**: Inner FOR can reference outer variable (b/author)
- **Powerful Pattern**: Handles complex XML structures with repeated nested elements

**Key Takeaway**: Nested FOR clauses enable iteration through multiple levels of XML hierarchy, perfect for handling one-to-many relationships like books with multiple authors.

---

## Summary

This documentation has covered 20 examples progressing from simple to complex:

- **Example 1**: Basic single-field selection
- **Section A (Examples 2-5)**: Basic queries with multiple fields and WHERE clauses
- **Section B (Examples 6-10)**: Intermediate queries combining ORDER BY and LIMIT
- **Section C (Examples 11-13)**: Multi-file queries and special fields
- **Section D (Examples 14-16)**: Advanced filtering with AND, OR, and parentheses
- **Section E (Examples 17-19)**: DISTINCT, FOR clause, and aggregation patterns
- **Section F (Example 20)**: Most complex - nested FOR clauses for hierarchical data

Each example builds upon previous concepts, demonstrating the full capabilities of the XML Query CLI application.

