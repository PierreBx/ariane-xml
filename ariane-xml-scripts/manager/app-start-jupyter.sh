#!/bin/bash
# Start Jupyter Lab with ariane-xml kernel

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

echo "========================================="
echo "Starting Ariane-XML Jupyter Lab"
echo "========================================="
echo ""

# Start containers if not running
if ! docker ps -q -f name=ariane-xml_container -f status=running | grep -q .; then
    echo "Starting containers..."
    docker compose up -d
    sleep 2
fi

echo "Launching Jupyter Lab..."
echo ""
echo "Access at: http://localhost:8888"
echo ""
echo "Press Ctrl+C to stop Jupyter Lab"
echo ""

# Execute the start-jupyter script inside the container
docker compose exec ariane-xml /app/ariane-xml-scripts/start-jupyter.sh
