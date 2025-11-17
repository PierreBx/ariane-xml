#!/bin/bash
# Run DSN mode test suite in Docker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

echo "========================================="
echo "Running DSN Mode Test Suite (Docker)"
echo "========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: docker-compose.yml not found in project root"
    exit 1
fi

# Run the DSN test suite in Docker
docker compose exec -T ariane-xml bash -c "cd /app && ./ariane-xml-tests/dsn_test.sh"
