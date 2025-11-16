# Known Issues - Phase 2

## Working Features
- ✅ Basic SELECT queries with single and multiple fields (column order preserved)
- ✅ WHERE clause with all comparison operators (=, !=, <, >, <=, >=)
- ✅ WHERE clause with AND/OR logical operators
- ✅ Numeric and string comparisons in WHERE clause
- ✅ ORDER BY clause with automatic type detection
- ✅ LIMIT clause for result pagination
- ✅ File and directory scanning
- ✅ FILE_NAME special field
- ✅ Lexer and parser for SQL-like syntax
- ✅ pugixml integration via CMake FetchContent
- ✅ Help command
- ✅ Cross-file queries (multiple XML files in directory)
- ✅ Quoted and unquoted file paths in FROM clause

## Fixed Issues (Phase 2)

### ✅ Multi-Field Query Column Ordering (FIXED)
**Status:** Fixed in Phase 2
**Solution:** Replaced `std::map` with `std::vector<std::pair<>>` to preserve insertion order.
**Result:** Columns now appear in the order specified in the query.

### ✅ Unquoted Path Support (FIXED)
**Status:** Fixed in Phase 2
**Solution:** Enhanced parser to collect path tokens (/, ., identifiers) in FROM clause context.
**Result:** Both quoted and unquoted paths now work:
```bash
./xmlquery "SELECT name FROM /path/to/files"  # WORKS
./xmlquery 'SELECT name FROM "../examples"'    # ALSO WORKS
```

---

## Known Limitations

### 1. Mixed Root Elements Across Files
**Status:** May cause issues
**Description:** If XML files in a directory have different root elements, queries may produce unexpected results.

**Example:**
- `test.xml` has `<breakfast_menu>`
- `lunch.xml` has `<lunch_menu>`

Querying for `breakfast_menu/food/name` will return empty for `lunch.xml`.

**Fix Required:** This is expected behavior but should be documented clearly.

---

## Testing Checklist

### Completed Tests
- [x] Help command
- [x] Basic SELECT single field
- [x] Multi-field SELECT queries
- [x] Single file queries
- [x] Directory scanning
- [x] FILE_NAME field
- [x] Build system (CMake + FetchContent)
- [x] WHERE clause with numeric comparison (<, >, =, !=, <=, >=)
- [x] WHERE clause with string comparison (=)
- [x] Cross-file queries (breakfast_menu vs lunch_menu)

### Not Yet Tested
- [ ] Large file performance
- [ ] Many files in directory (>10 files)
- [ ] Deeply nested XML paths (>5 levels)
- [ ] XML with attributes
- [ ] Malformed XML handling
- [ ] Edge cases: empty values, missing fields
- [ ] Concurrent file access

---

## Recommended Next Steps

1. **Fix column ordering** (Medium priority for usability)
   - Replace `std::map` with ordered data structure
   - Preserve user-specified field order in output

2. **Add comprehensive error messages**
   - Better parsing errors with line/column information
   - Clearer XML loading errors
   - File not found errors with suggestions

3. **Add test suite**
   - Unit tests for lexer
   - Unit tests for parser
   - Integration tests for queries
   - Performance benchmarks

4. **Documentation updates**
   - Update README with "paths must be quoted" requirement
   - Add more query examples
   - Document limitations and edge cases

5. **Phase 2 Features** (After MVP is stable)
   - Multiple WHERE conditions with AND/OR
   - Wildcard support in SELECT
   - ORDER BY and LIMIT clauses
   - Better error messages
