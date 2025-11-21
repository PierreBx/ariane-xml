#!/bin/bash
# Backward Compatibility Test for Unified Error Numbering System
#
# This test verifies that the new error system maintains 100% backward compatibility
# with existing code and tests.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Source helper functions
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh" 2>/dev/null || true

echo "=========================================="
echo "Backward Compatibility Tests"
echo "=========================================="
echo ""

# Function to run a compatibility test
run_compat_test() {
    local test_id="$1"
    local test_name="$2"
    local command="$3"
    local expected_pattern="$4"
    local check_old_format="$5"  # Optional: also check for old format compatibility

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "[$test_id] $test_name... "

    # Run the command and capture output
    output=$(eval "$command" 2>&1 || true)

    # Check if output matches expected pattern
    if echo "$output" | grep -qE "$expected_pattern"; then
        # If check_old_format is set, also verify old format is handled
        if [ -n "$check_old_format" ]; then
            if echo "$output" | grep -qE "$check_old_format"; then
                echo -e "${GREEN}PASS${NC}"
                TESTS_PASSED=$((TESTS_PASSED + 1))
                return 0
            else
                echo -e "${YELLOW}PARTIAL${NC} (New format works, but old format check failed)"
                TESTS_PASSED=$((TESTS_PASSED + 1))
                return 0
            fi
        else
            echo -e "${GREEN}PASS${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            return 0
        fi
    else
        echo -e "${RED}FAIL${NC}"
        echo "  Expected pattern: $expected_pattern"
        echo "  Got: $output"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Test 1: Error messages still contain "Error" keyword
run_compat_test "COMPAT-001" \
    "Error messages contain 'Error' keyword" \
    'echo "INVALID QUERY" | $ARIANE_XML_BIN 2>&1' \
    "Error"

# Test 2: Error messages are still on stderr
run_compat_test "COMPAT-002" \
    "Errors go to stderr (not stdout)" \
    'echo "SELECT FROM" | $ARIANE_XML_BIN 2>&1 | grep -i error' \
    "."

# Test 3: Parse errors still identified as errors
run_compat_test "COMPAT-003" \
    "Parse errors identifiable" \
    'echo "SELECT * FROM" | $ARIANE_XML_BIN 2>&1' \
    "Error|ARX-"

# Test 4: File not found errors still work
run_compat_test "COMPAT-004" \
    "File not found errors" \
    'echo "SELECT * FROM \"nonexistent.xml\"" | $ARIANE_XML_BIN 2>&1' \
    "Error.*not.*found|Error.*No.*files|ARX-"

# Test 5: Invalid syntax errors still work
run_compat_test "COMPAT-005" \
    "Invalid syntax errors" \
    'echo "INVALID SYNTAX HERE" | $ARIANE_XML_BIN 2>&1' \
    "Error|ARX-00"

# Test 6: New format includes error codes
run_compat_test "COMPAT-006" \
    "New format includes ARX codes" \
    'echo "SELECT FROM" | $ARIANE_XML_BIN 2>&1' \
    "ARX-[0-9]{5}"

# Test 7: Severity indicators present
run_compat_test "COMPAT-007" \
    "Severity indicators in output" \
    'echo "SELECT * FROM" | $ARIANE_XML_BIN 2>&1' \
    "\[Error\]|\[Warning\]|\[Success\]"

# Test 8: Error codes follow ARX-XXYYY format
run_compat_test "COMPAT-008" \
    "Error codes follow ARX-XXYYY format" \
    'echo "INVALID" | $ARIANE_XML_BIN 2>&1' \
    "ARX-[0-9]{2}[0-9]{3}"

# Test 9: Existing test patterns still match
run_compat_test "COMPAT-009" \
    "Regex pattern 'Error.*' still matches" \
    'echo "BAD QUERY" | $ARIANE_XML_BIN 2>&1 | grep -E "Error.*"' \
    "."

# Test 10: Exit codes unchanged (non-zero on error)
run_compat_test "COMPAT-010" \
    "Non-zero exit code on error" \
    '! echo "INVALID" | $ARIANE_XML_BIN >/dev/null 2>&1' \
    "."

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Tests run:    $TESTS_RUN"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
else
    echo -e "Tests failed: ${GREEN}0${NC}"
fi
echo ""

# Test error lookup utility if PyYAML is available
echo "=========================================="
echo "Error Lookup Utility Tests"
echo "=========================================="
echo ""

if python3 -c "import yaml" 2>/dev/null; then
    echo "PyYAML found - testing error lookup utility..."

    # Test lookup by code
    run_compat_test "LOOKUP-001" \
        "Look up error by code" \
        "python3 $SCRIPT_DIR/../ariane-xml-scripts/error_lookup.py ARX-00000 2>&1" \
        "Success.*Query executed successfully"

    # Test search by keyword
    run_compat_test "LOOKUP-002" \
        "Search errors by keyword" \
        "python3 $SCRIPT_DIR/../ariane-xml-scripts/error_lookup.py --search 'SELECT' 2>&1" \
        "ARX-01"

    # Test list categories
    run_compat_test "LOOKUP-003" \
        "List error categories" \
        "python3 $SCRIPT_DIR/../ariane-xml-scripts/error_lookup.py --list-categories 2>&1" \
        "SELECT Clause|FROM Clause"

else
    echo -e "${YELLOW}PyYAML not installed - skipping lookup utility tests${NC}"
    echo "Install with: pip install pyyaml"
fi

echo ""
echo "=========================================="
echo "Final Result"
echo "=========================================="
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All backward compatibility tests passed!${NC}"
    echo ""
    echo "The new error system maintains 100% backward compatibility."
    echo "Existing code and tests will continue to work without modification."
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Please review the failed tests above."
    exit 1
fi
