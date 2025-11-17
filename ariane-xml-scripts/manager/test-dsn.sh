#!/bin/bash
# Run DSN mode test suite

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

echo "========================================="
echo "Running DSN Mode Test Suite"
echo "========================================="
echo ""

# Run the DSN test suite
exec "${PROJECT_ROOT}/ariane-xml-tests/dsn_test.sh"
