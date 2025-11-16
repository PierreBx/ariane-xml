#!/bin/bash
# Run hard test suite INSIDE Docker container
# Generates test data and runs stress tests natively in the container

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

echo "========================================="
echo "Running Hard Test Suite (Docker Mode)"
echo "========================================="
echo ""

# Ensure container is running
if ! docker ps -q -f name=ariane-xml_container -f status=running | grep -q .; then
    echo "Starting ariane-xml container..."
    docker compose up -d
    sleep 2
fi

# Container paths - use /app which is the mounted project directory
CONTAINER_TEST_SCRIPT="/app/ariane-xml-tests/hard_test.sh"
CONTAINER_OUTPUT_FILE="/tmp/ariane-xml-hard-test-output.log"
CONTAINER_EXIT_FILE="/tmp/ariane-xml-hard-test-exit.txt"

# Ensure binary is built inside container
echo "Checking ariane-xml binary in container..."
if ! docker compose exec -T ariane-xml test -f /app/ariane-xml-c-kernel/build/ariane-xml; then
    echo "Building ariane-xml binary inside container..."
    docker compose exec -T ariane-xml bash -c "
        cd /app/ariane-xml-c-kernel
        mkdir -p build
        cd build
        cmake .. && make -j\$(nproc)
    "
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      RUNNING HARD TESTS                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Clean up any previous test output files
docker compose exec -T ariane-xml rm -f "$CONTAINER_OUTPUT_FILE" "$CONTAINER_EXIT_FILE" 2>/dev/null || true

# Run tests inside container and capture output
# We use a wrapper script to save exit code
docker compose exec -T ariane-xml bash -c "
    cd /app || exit 1
    bash '$CONTAINER_TEST_SCRIPT' 2>&1 | tee '$CONTAINER_OUTPUT_FILE'
    echo \${PIPESTATUS[0]} > '$CONTAINER_EXIT_FILE'
"

# Display final output summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      TEST SUMMARY                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get exit code
EXIT_CODE=$(docker compose exec -T ariane-xml cat "$CONTAINER_EXIT_FILE" 2>/dev/null || echo "1")

# Cleanup
docker compose exec -T ariane-xml rm -f "$CONTAINER_OUTPUT_FILE" "$CONTAINER_EXIT_FILE" 2>/dev/null || true

echo ""
if [ "$EXIT_CODE" -eq 0 ]; then
    echo "✓ Tests completed successfully"
    exit 0
else
    echo "✗ Tests failed (exit code: $EXIT_CODE)"
    exit $EXIT_CODE
fi
