#!/bin/bash
# Run light test suite INSIDE Docker container with live progress monitoring
# This solves the stdin piping issue by running tests natively in the container

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

echo "========================================="
echo "Running Light Test Suite (Docker Mode)"
echo "========================================="
echo ""

# Ensure container is running
if ! docker ps -q -f name=ariane-xml_container -f status=running | grep -q .; then
    echo "Starting ariane-xml container..."
    docker compose up -d
    sleep 2
fi

# Container paths
CONTAINER_TEST_SCRIPT="/host_home/$(realpath --relative-to="$HOME" "$PROJECT_ROOT")/ariane-xml-tests/run_tests.sh"
CONTAINER_OUTPUT_FILE="/tmp/ariane-xml-test-output-$$.log"
CONTAINER_PID_FILE="/tmp/ariane-xml-test-pid-$$.txt"

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
echo "Launching tests inside container (background)..."
echo "Output file (inside container): $CONTAINER_OUTPUT_FILE"
echo ""

# Launch tests in background inside container
# Use bash -c with cd to ensure correct working directory
docker compose exec -T -d ariane-xml bash -c "
    cd '$CONTAINER_TEST_SCRIPT/../..' || exit 1
    bash '$CONTAINER_TEST_SCRIPT' > '$CONTAINER_OUTPUT_FILE' 2>&1
    echo \$? > '${CONTAINER_PID_FILE}.exit'
" &

DOCKER_EXEC_PID=$!

# Give it a moment to start
sleep 2

# Monitor progress by tailing the output file
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 LIVE TEST OUTPUT (from container)              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

LAST_LINE_COUNT=0
POLL_INTERVAL=2
MAX_NO_CHANGE_COUNT=3
NO_CHANGE_COUNT=0

while true; do
    # Check if tests are still running by looking for bash process
    if ! docker compose exec -T ariane-xml pgrep -f "run_tests.sh" > /dev/null 2>&1; then
        echo ""
        echo "Tests completed. Fetching final output..."
        sleep 1
        break
    fi

    # Fetch current output
    CURRENT_OUTPUT=$(docker compose exec -T ariane-xml cat "$CONTAINER_OUTPUT_FILE" 2>/dev/null || echo "")
    CURRENT_LINE_COUNT=$(echo "$CURRENT_OUTPUT" | wc -l)

    # Display only new lines since last check
    if [ $CURRENT_LINE_COUNT -gt $LAST_LINE_COUNT ]; then
        NEW_LINES=$((CURRENT_LINE_COUNT - LAST_LINE_COUNT))
        echo "$CURRENT_OUTPUT" | tail -n $NEW_LINES
        LAST_LINE_COUNT=$CURRENT_LINE_COUNT
        NO_CHANGE_COUNT=0
    else
        NO_CHANGE_COUNT=$((NO_CHANGE_COUNT + 1))

        # If no output for a while, show a heartbeat
        if [ $NO_CHANGE_COUNT -ge $MAX_NO_CHANGE_COUNT ]; then
            echo -n "."
            NO_CHANGE_COUNT=0
        fi
    fi

    sleep $POLL_INTERVAL
done

# Display final complete output
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      FINAL TEST RESULTS                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

FINAL_OUTPUT=$(docker compose exec -T ariane-xml cat "$CONTAINER_OUTPUT_FILE" 2>/dev/null)
echo "$FINAL_OUTPUT"

# Get exit code
EXIT_CODE=$(docker compose exec -T ariane-xml cat "${CONTAINER_PID_FILE}.exit" 2>/dev/null || echo "1")

# Cleanup
docker compose exec -T ariane-xml rm -f "$CONTAINER_OUTPUT_FILE" "${CONTAINER_PID_FILE}.exit" 2>/dev/null

echo ""
if [ "$EXIT_CODE" -eq 0 ]; then
    echo "✓ Tests completed successfully"
    exit 0
else
    echo "✗ Tests failed (exit code: $EXIT_CODE)"
    exit $EXIT_CODE
fi
