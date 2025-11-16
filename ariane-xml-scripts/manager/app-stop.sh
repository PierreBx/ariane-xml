#!/bin/bash
# Stop running ariane-xml applications

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

echo "========================================="
echo "Stopping Ariane-XML Applications"
echo "========================================="
echo ""

# Stop Jupyter if running (check for jupyter processes in container)
echo "Stopping Jupyter Lab processes..."
docker compose exec -T ariane-xml pkill -f "jupyter" 2>/dev/null || true

echo ""
echo "✓ Applications stopped"
echo ""
echo "Note: Containers are still running. Use 'Environment > Stop containers' to stop them."
