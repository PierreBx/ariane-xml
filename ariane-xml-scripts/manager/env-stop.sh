#!/bin/bash
# Stop Docker containers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

echo "========================================="
echo "Stopping Ariane-XML Containers"
echo "========================================="
echo ""

docker compose down

echo ""
echo "✓ Containers stopped successfully"
