#!/bin/bash
# Test script for C++ autocomplete bridge functionality
# Tests the --autocomplete mode that provides suggestions to Jupyter kernel

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Find the ariane-xml executable
if [ -n "$ARIANE_XML_BIN" ]; then
    ARIANE_XML="$ARIANE_XML_BIN"
elif [ -f "./build/ariane-xml" ]; then
    ARIANE_XML="./build/ariane-xml"
elif [ -f "./tests/bin/ariane-xml" ]; then
    ARIANE_XML="./tests/bin/ariane-xml"
elif [ -f "../build/ariane-xml" ]; then
    ARIANE_XML="../build/ariane-xml"
else
    echo -e "${RED}✗ Error: ariane-xml executable not found${NC}"
    echo "Please build the project first: cd build && cmake .. && make"
    exit 1
fi

echo "Testing with: $ARIANE_XML"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to run a test
run_test() {
    local test_name="$1"
    local query="$2"
    local cursor_pos="$3"
    local expected_pattern="$4"

    echo -n "Test: $test_name... "

    # Run autocomplete command (only capture stdout, ignore stderr)
    result=$("$ARIANE_XML" --autocomplete "$query" "$cursor_pos" 2>/dev/null)
    exit_code=$?

    # Check if it returned valid JSON
    if ! echo "$result" | python3 -m json.tool > /dev/null 2>&1; then
        echo -e "${RED}✗ FAILED${NC} - Invalid JSON output"
        echo "  Output: $result"
        ((TESTS_FAILED++))
        return 1
    fi

    # Check if output contains expected pattern
    if echo "$result" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} - Expected pattern not found: $expected_pattern"
        echo "  Output: $result"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Helper function to check empty suggestions
run_empty_test() {
    local test_name="$1"
    local query="$2"
    local cursor_pos="$3"

    echo -n "Test: $test_name... "

    # Run autocomplete command (only capture stdout, ignore stderr)
    result=$("$ARIANE_XML" --autocomplete "$query" "$cursor_pos" 2>/dev/null)

    # Check if it returned empty array
    if [ "$result" = "[]" ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} - Expected empty array"
        echo "  Output: $result"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "====================================="
echo "C++ Autocomplete Bridge Tests"
echo "====================================="
echo ""

# Test 1: Basic field completion
run_test "Field completion (S21_)" "SELECT S21_" 11 "S21_G00"

# Test 2: Shortcut completion
run_test "Shortcut completion (30_)" "SELECT 30_" 10 "30_001"

# Test 3: Keyword completion
run_test "Keyword completion (SEL)" "SEL" 3 "SELECT"

# Test 4: Empty query
run_empty_test "Empty query" "" 0

# Test 5: Invalid cursor position
run_empty_test "Invalid cursor position" "SELECT" 100

# Test 6: JSON format validation - check for required fields
echo -n "Test: JSON format validation... "
result=$("$ARIANE_XML" --autocomplete "SELECT S21_" 11 2>/dev/null)
if echo "$result" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        if len(data) > 0:
            required_fields = ['completion', 'display', 'description', 'type']
            first_item = data[0]
            if all(field in first_item for field in required_fields):
                print('OK')
                sys.exit(0)
    sys.exit(1)
except:
    sys.exit(1)
" 2>&1 | grep -q "OK"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - Missing required JSON fields"
    echo "  Output: $result"
    ((TESTS_FAILED++))
fi

# Test 7: Check suggestion type values
echo -n "Test: Suggestion type values... "
result=$("$ARIANE_XML" --autocomplete "SELECT S21_" 11 2>/dev/null)
if echo "$result" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    valid_types = ['field', 'bloc', 'keyword']
    if len(data) > 0:
        for item in data:
            if item.get('type') not in valid_types:
                sys.exit(1)
        print('OK')
        sys.exit(0)
    sys.exit(1)
except:
    sys.exit(1)
" 2>&1 | grep -q "OK"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - Invalid suggestion type"
    echo "  Output: $result"
    ((TESTS_FAILED++))
fi

# Test 8: Mid-query completion
run_test "Mid-query completion" "SELECT S21_G00_ FROM file.xml" 15 "S21_G00"

# Test 9: WHERE clause completion
run_test "WHERE clause field completion" "SELECT * FROM file.xml WHERE 30_" 33 "30_"

echo ""
echo "====================================="
echo "Test Summary"
echo "====================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed! ✗${NC}"
    exit 1
fi
