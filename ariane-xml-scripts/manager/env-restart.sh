#!/bin/bash
# Restart Docker containers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

echo "========================================="
echo "Restarting Ariane-XML Containers"
echo "========================================="
echo ""

docker compose restart

echo ""
echo "✓ Containers restarted successfully"
