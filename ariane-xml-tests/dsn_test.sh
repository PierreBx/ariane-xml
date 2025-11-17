#!/bin/bash
# Ariane-XML DSN Mode Test Suite
# Tests DSN-specific features with automatic dataset generation
# Covers: P25/P26 schemas, FCTU/mensuelle/SADV types, shortcuts, templates

set -e

# Source helper functions
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

# Test-specific directories
DSN_TEST_DIR="$TEST_OUTPUT_DIR/dsn_test"
DSN_TEST_DATA="$DSN_TEST_DIR/data"

# DSN schema paths
DSN_P25_FCTU="ariane-xml-schemas/xsd_P25/FCTU P25/FCTUHY.xsd"
DSN_P25_MENSUELLE="ariane-xml-schemas/xsd_P25/mensuelle P25/Bloc3_NAT_DSN_MENSUELLE.xsd"
DSN_P26_FCTU="ariane-xml-schemas/xsd_P26/FCTU P26/FCTUHY.xsd"
DSN_P26_MENSUELLE="ariane-xml-schemas/xsd_P26/mensuelle P26/Bloc3_NAT_DSN_MENSUELLE.xsd"
DSN_P26_SADV="ariane-xml-schemas/xsd_P26/SADV P26/Bloc3_SADV.xsd"

# Initialize
print_category "DSN MODE TEST SUITE"

echo -e "${COLOR_CYAN}This test suite validates DSN mode features:${COLOR_RESET}"
echo "  1. DSN mode activation and configuration"
echo "  2. Schema version auto-detection (P25/P26)"
echo "  3. DSN type detection (FCTU, mensuelle, SADV)"
echo "  4. YY_ZZZ shortcut notation"
echo "  5. Field queries with DSN paths"
echo "  6. Template queries"
echo "  7. DESCRIBE command"
echo "  8. DSN validation"
echo ""
echo -e "${COLOR_YELLOW}Dataset generation:${COLOR_RESET}"
echo "  - P25 FCTU files (if not present)"
echo "  - P25 mensuelle files (if not present)"
echo "  - P26 FCTU files (if not present)"
echo "  - P26 mensuelle files (if not present)"
echo "  - P26 SADV files (if not present)"
echo ""

# Create test directories
mkdir -p "$DSN_TEST_DATA/p25_fctu"
mkdir -p "$DSN_TEST_DATA/p25_mensuelle"
mkdir -p "$DSN_TEST_DATA/p26_fctu"
mkdir -p "$DSN_TEST_DATA/p26_mensuelle"
mkdir -p "$DSN_TEST_DATA/p26_sadv"

# ============================================================================
# PHASE 1: Generate DSN Test Data (if not already present)
# ============================================================================
echo -e "${COLOR_BOLD}${COLOR_YELLOW}Phase 1: DSN Test Data Preparation${COLOR_RESET}"
echo ""

generate_dsn_dataset() {
    local schema=$1
    local dest_dir=$2
    local prefix=$3
    local num_files=$4
    local dataset_name=$5

    local file_count=$(ls -1 "$dest_dir"/${prefix}*.xml 2>/dev/null | wc -l)

    if [ "$file_count" -ge "$num_files" ]; then
        echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} $dataset_name: Using existing $file_count files"
        return 0
    fi

    echo -e "  ${COLOR_CYAN}→${COLOR_RESET} $dataset_name: Generating $num_files files..."

    # Clean up any partial files
    rm -f "$dest_dir"/${prefix}*.xml 2>/dev/null

    # Generate files
    local gen_output="$DSN_TEST_DIR/gen_${dataset_name}.log"
    echo -e "SET XSD $schema;\nSET DEST $dest_dir;\nGENERATE XML $num_files PREFIX ${prefix}_;\nexit;" | \
        $ARIANE_XML_BIN > "$gen_output" 2>&1

    if [ $? -ne 0 ]; then
        echo -e "  ${COLOR_RED}✗${COLOR_RESET} $dataset_name: Generation failed"
        cat "$gen_output"
        return 1
    fi

    file_count=$(ls -1 "$dest_dir"/${prefix}*.xml 2>/dev/null | wc -l)
    if [ "$file_count" -eq "$num_files" ]; then
        echo -e "  ${COLOR_GREEN}✓${COLOR_RESET} $dataset_name: Generated $file_count files successfully"
    else
        echo -e "  ${COLOR_YELLOW}⚠${COLOR_RESET} $dataset_name: Expected $num_files, got $file_count files"
    fi
}

# Generate datasets (5 files each for faster testing)
generate_dsn_dataset "$DSN_P25_FCTU" "$DSN_TEST_DATA/p25_fctu" "p25_fctu" 5 "P25_FCTU"
generate_dsn_dataset "$DSN_P25_MENSUELLE" "$DSN_TEST_DATA/p25_mensuelle" "p25_mensuelle" 5 "P25_MENSUELLE"
generate_dsn_dataset "$DSN_P26_FCTU" "$DSN_TEST_DATA/p26_fctu" "p26_fctu" 5 "P26_FCTU"
generate_dsn_dataset "$DSN_P26_MENSUELLE" "$DSN_TEST_DATA/p26_mensuelle" "p26_mensuelle" 5 "P26_MENSUELLE"
generate_dsn_dataset "$DSN_P26_SADV" "$DSN_TEST_DATA/p26_sadv" "p26_sadv" 5 "P26_SADV"

echo ""

# ============================================================================
# PHASE 2: DSN Mode Activation and Configuration
# ============================================================================
print_category "2. DSN Mode Activation and Configuration"

run_test "DSN-001" \
    "Set DSN mode" \
    'SET MODE DSN; exit;' \
    "Mode set to DSN|DSN mode enabled"

run_test "DSN-002" \
    "Show current mode" \
    'SET MODE DSN; SHOW MODE; exit;' \
    "DSN|Current mode"

run_test "DSN-003" \
    "Set DSN version P25" \
    'SET MODE DSN; SET DSN_VERSION P25; exit;' \
    "P25|DSN version set"

run_test "DSN-004" \
    "Set DSN version P26" \
    'SET MODE DSN; SET DSN_VERSION P26; exit;' \
    "P26|DSN version set"

run_test "DSN-005" \
    "Set DSN version AUTO" \
    'SET MODE DSN; SET DSN_VERSION AUTO; exit;' \
    "AUTO|DSN version set"

run_test "DSN-006" \
    "Show DSN schema info" \
    'SET MODE DSN; SET DSN_VERSION P26; SHOW DSN_SCHEMA; exit;' \
    "P26|DSN|schema"

run_test "DSN-007" \
    "Return to STANDARD mode" \
    'SET MODE DSN; SET MODE STANDARD; SHOW MODE; exit;' \
    "STANDARD|Standard mode"

# ============================================================================
# PHASE 3: Basic DSN Queries (Standard Paths)
# ============================================================================
print_category "3. Basic DSN Queries - P26 FCTU"

run_test "DSN-101" \
    "Select from P26 FCTU with full path" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT S10_G00_01.S10_G00_01_001 FROM \"$DSN_TEST_DATA/p26_fctu/\"; exit;" \
    ".*"

run_test "DSN-102" \
    "Select multiple fields P26 FCTU" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT S10_G00_01.S10_G00_01_001, S10_G00_01.S10_G00_01_003 FROM \"$DSN_TEST_DATA/p26_fctu/\"; exit;" \
    ".*"

run_test "DSN-103" \
    "Count FCTU files" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT COUNT(*) FROM \"$DSN_TEST_DATA/p26_fctu/\"; exit;" \
    "[0-9]"

# ============================================================================
# PHASE 4: DSN Shortcut Notation (YY_ZZZ)
# ============================================================================
print_category "4. DSN Shortcut Notation"

run_test "DSN-201" \
    "Select with YY_ZZZ shortcut" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT 01_001 FROM \"$DSN_TEST_DATA/p26_fctu/\"; exit;" \
    ".*"

run_test "DSN-202" \
    "Select multiple shortcuts" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT 01_001, 01_003 FROM \"$DSN_TEST_DATA/p26_fctu/\"; exit;" \
    ".*"

run_test "DSN-203" \
    "WHERE clause with shortcut" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT 01_001 FROM \"$DSN_TEST_DATA/p26_fctu/\" WHERE 01_001 IS NOT NULL; exit;" \
    ".*"

run_test "DSN-204" \
    "Mix full path and shortcut" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT S10_G00_01.S10_G00_01_001, 01_003 FROM \"$DSN_TEST_DATA/p26_fctu/\"; exit;" \
    ".*"

# ============================================================================
# PHASE 5: P25 Schema Tests
# ============================================================================
print_category "5. P25 Schema Tests"

run_test "DSN-301" \
    "P25 FCTU basic query" \
    "SET MODE DSN; SET DSN_VERSION P25; SELECT 01_001 FROM \"$DSN_TEST_DATA/p25_fctu/\"; exit;" \
    ".*"

run_test "DSN-302" \
    "P25 mensuelle basic query" \
    "SET MODE DSN; SET DSN_VERSION P25; SELECT 01_001 FROM \"$DSN_TEST_DATA/p25_mensuelle/\"; exit;" \
    ".*"

run_test "DSN-303" \
    "P25 with WHERE clause" \
    "SET MODE DSN; SET DSN_VERSION P25; SELECT 01_001, 01_003 FROM \"$DSN_TEST_DATA/p25_fctu/\" WHERE 01_001 IS NOT NULL; exit;" \
    ".*"

# ============================================================================
# PHASE 6: P26 Schema Tests (All Types)
# ============================================================================
print_category "6. P26 Schema Tests - All DSN Types"

run_test "DSN-401" \
    "P26 FCTU query" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT 01_001, 01_003 FROM \"$DSN_TEST_DATA/p26_fctu/\"; exit;" \
    ".*"

run_test "DSN-402" \
    "P26 mensuelle query" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT 01_001 FROM \"$DSN_TEST_DATA/p26_mensuelle/\"; exit;" \
    ".*"

run_test "DSN-403" \
    "P26 SADV query" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT 01_001 FROM \"$DSN_TEST_DATA/p26_sadv/\"; exit;" \
    ".*"

run_test "DSN-404" \
    "P26 FCTU with aggregation" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT COUNT(01_001) FROM \"$DSN_TEST_DATA/p26_fctu/\"; exit;" \
    "[0-9]"

run_test "DSN-405" \
    "P26 mensuelle with LIMIT" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT 01_001 FROM \"$DSN_TEST_DATA/p26_mensuelle/\" LIMIT 2; exit;" \
    ".*"

# ============================================================================
# PHASE 7: DESCRIBE Command
# ============================================================================
print_category "7. DESCRIBE Command"

run_test "DSN-501" \
    "DESCRIBE field by shortcut" \
    'SET MODE DSN; SET DSN_VERSION P26; DESCRIBE 01_001; exit;' \
    "01_001|Rubrique|SIREN|description"

run_test "DSN-502" \
    "DESCRIBE field by full path" \
    'SET MODE DSN; SET DSN_VERSION P26; DESCRIBE S10_G00_01_001; exit;' \
    "S10_G00_01_001|SIREN|description"

run_test "DSN-503" \
    "DESCRIBE bloc" \
    'SET MODE DSN; SET DSN_VERSION P26; DESCRIBE S10_G00_01; exit;' \
    "S10_G00_01|EMETTEUR|fields|bloc"

# ============================================================================
# PHASE 8: Template Queries
# ============================================================================
print_category "8. DSN Template Queries"

run_test "DSN-601" \
    "List available templates" \
    'SET MODE DSN; SET DSN_VERSION P26; TEMPLATE LIST; exit;' \
    "template|available|list"

run_test "DSN-602" \
    "Show specific template" \
    'SET MODE DSN; SET DSN_VERSION P26; TEMPLATE list_employees; exit;' \
    "list_employees|template|query"

run_test "DSN-603" \
    "Execute template (list_establishments)" \
    "SET MODE DSN; SET DSN_VERSION P26; TEMPLATE list_establishments SET file=\"$DSN_TEST_DATA/p26_fctu/\"; exit;" \
    ".*"

run_test "DSN-604" \
    "Execute template (company_info)" \
    "SET MODE DSN; SET DSN_VERSION P26; TEMPLATE company_info SET file=\"$DSN_TEST_DATA/p26_fctu/\"; exit;" \
    ".*"

# ============================================================================
# PHASE 9: Complex DSN Queries
# ============================================================================
print_category "9. Complex DSN Queries"

run_test "DSN-701" \
    "AND operator with shortcuts" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT 01_001 FROM \"$DSN_TEST_DATA/p26_fctu/\" WHERE 01_001 IS NOT NULL AND 01_003 IS NOT NULL; exit;" \
    ".*"

run_test "DSN-702" \
    "OR operator with shortcuts" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT 01_001 FROM \"$DSN_TEST_DATA/p26_fctu/\" WHERE 01_001 IS NULL OR 01_003 IS NULL; exit;" \
    ".*"

run_test "DSN-703" \
    "LIKE operator on DSN field" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT 01_001, 01_003 FROM \"$DSN_TEST_DATA/p26_fctu/\" WHERE 01_003 LIKE /.*Test.*/; exit;" \
    ".*"

run_test "DSN-704" \
    "ORDER BY DSN field" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT 01_001 FROM \"$DSN_TEST_DATA/p26_fctu/\" ORDER BY 01_001 LIMIT 3; exit;" \
    ".*"

run_test "DSN-705" \
    "DISTINCT on DSN field" \
    "SET MODE DSN; SET DSN_VERSION P26; SELECT DISTINCT 01_001 FROM \"$DSN_TEST_DATA/p26_fctu/\"; exit;" \
    ".*"

# ============================================================================
# PHASE 10: Validation and Error Handling
# ============================================================================
print_category "10. DSN Validation and Error Handling"

run_test "DSN-801" \
    "CHECK command with DSN schema" \
    "SET MODE DSN; SET DSN_VERSION P26; SET XSD $DSN_P26_FCTU; CHECK \"$DSN_TEST_DATA/p26_fctu/\"; exit;" \
    "Validating|valid|Summary"

run_test "DSN-802" \
    "Query non-existent DSN field" \
    'SET MODE DSN; SET DSN_VERSION P26; SELECT 99_999 FROM "data/test.xml"; exit;' \
    "Error|not found|does not exist"

run_test "DSN-803" \
    "Invalid DSN mode query" \
    'SET MODE DSN; INVALID DSN QUERY; exit;' \
    "Error|Parse Error"

# ============================================================================
# PHASE 11: Auto-Detection Tests
# ============================================================================
print_category "11. DSN Version Auto-Detection"

run_test "DSN-901" \
    "Auto-detect P25 version" \
    "SET MODE DSN; SET DSN_VERSION AUTO; SELECT 01_001 FROM \"$DSN_TEST_DATA/p25_fctu/\" LIMIT 1; exit;" \
    ".*"

run_test "DSN-902" \
    "Auto-detect P26 version" \
    "SET MODE DSN; SET DSN_VERSION AUTO; SELECT 01_001 FROM \"$DSN_TEST_DATA/p26_fctu/\" LIMIT 1; exit;" \
    ".*"

# ============================================================================
# PHASE 12: Performance Tests
# ============================================================================
print_category "12. DSN Performance Tests"

echo -e "${COLOR_CYAN}Measuring query performance across all DSN types...${COLOR_RESET}"
echo ""

test_query_performance() {
    local dataset=$1
    local version=$2
    local description=$3

    local start_time=$(date +%s.%N)
    echo -e "SET MODE DSN; SET DSN_VERSION $version; SELECT 01_001, 01_003 FROM \"$dataset/\"; exit;" | \
        $ARIANE_XML_BIN > /dev/null 2>&1
    local end_time=$(date +%s.%N)
    local duration=$(awk "BEGIN {print $end_time - $start_time}")

    printf "  %-30s %.3f seconds\n" "$description:" "$duration"
}

test_query_performance "$DSN_TEST_DATA/p25_fctu" "P25" "P25 FCTU (5 files)"
test_query_performance "$DSN_TEST_DATA/p25_mensuelle" "P25" "P25 mensuelle (5 files)"
test_query_performance "$DSN_TEST_DATA/p26_fctu" "P26" "P26 FCTU (5 files)"
test_query_performance "$DSN_TEST_DATA/p26_mensuelle" "P26" "P26 mensuelle (5 files)"
test_query_performance "$DSN_TEST_DATA/p26_sadv" "P26" "P26 SADV (5 files)"

echo ""

# ============================================================================
# PHASE 13: Summary and Statistics
# ============================================================================
print_category "13. Test Data Summary"

echo ""
echo -e "${COLOR_CYAN}Dataset Statistics:${COLOR_RESET}"
echo ""

show_dataset_stats() {
    local dataset=$1
    local description=$2

    if [ -d "$dataset" ]; then
        local file_count=$(ls -1 "$dataset"/*.xml 2>/dev/null | wc -l)
        local total_size=$(du -sh "$dataset" 2>/dev/null | cut -f1)
        printf "  %-25s %3d files, %6s\n" "$description:" "$file_count" "$total_size"
    fi
}

show_dataset_stats "$DSN_TEST_DATA/p25_fctu" "P25 FCTU"
show_dataset_stats "$DSN_TEST_DATA/p25_mensuelle" "P25 mensuelle"
show_dataset_stats "$DSN_TEST_DATA/p26_fctu" "P26 FCTU"
show_dataset_stats "$DSN_TEST_DATA/p26_mensuelle" "P26 mensuelle"
show_dataset_stats "$DSN_TEST_DATA/p26_sadv" "P26 SADV"

TOTAL_SIZE=$(du -sh "$DSN_TEST_DATA" 2>/dev/null | cut -f1)
echo ""
printf "  %-25s %s\n" "Total data size:" "$TOTAL_SIZE"
echo ""

# ============================================================================
# Print Final Summary
# ============================================================================
print_summary

# Cleanup
cleanup_tests

# Test files are preserved for reuse on subsequent runs
# To regenerate: rm -rf ariane-xml-tests/output/dsn_test/data/

# Exit with appropriate code
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${COLOR_GREEN}✓ DSN test suite completed successfully!${COLOR_RESET}"
    echo -e "${COLOR_CYAN}  All DSN mode features validated across P25/P26 schemas${COLOR_RESET}"
    echo ""
    exit 0
else
    echo -e "${COLOR_RED}✗ DSN test suite completed with failures${COLOR_RESET}"
    echo ""
    exit 1
fi
