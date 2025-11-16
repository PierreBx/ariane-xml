#!/bin/bash
# Run light test suite

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

echo "========================================="
echo "Running Light Test Suite"
echo "========================================="
echo ""

# Run the comprehensive test suite
exec "${PROJECT_ROOT}/ariane-xml-tests/run_tests.sh"
