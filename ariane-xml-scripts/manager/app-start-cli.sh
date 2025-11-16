#!/bin/bash
# Start ariane-xml CLI in interactive mode

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "========================================="
echo "Starting Ariane-XML CLI"
echo "========================================="
echo ""
echo "Type your SQL-like queries at the prompt"
echo "Press Ctrl+D or type 'exit' to quit"
echo ""

# Run the CLI wrapper script in interactive mode
exec "${PROJECT_ROOT}/ariane-xml-scripts/ariane-xml.sh"
