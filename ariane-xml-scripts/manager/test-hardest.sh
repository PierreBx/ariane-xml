#!/bin/bash
# Run hardest test suite (extreme stress test)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

echo "========================================="
echo "Running Hardest Test Suite"
echo "========================================="
echo ""

# Run the hardest stress test
exec "${PROJECT_ROOT}/ariane-xml-tests/hardest_test.sh"
