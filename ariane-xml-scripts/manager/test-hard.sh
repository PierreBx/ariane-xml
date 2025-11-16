#!/bin/bash
# Run hard test suite (stress test)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

echo "========================================="
echo "Running Hard Test Suite"
echo "========================================="
echo ""

# Run the hard stress test
exec "${PROJECT_ROOT}/ariane-xml-tests/hard_test.sh"
