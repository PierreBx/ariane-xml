#!/bin/bash
# Run full installation process

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "========================================="
echo "Ariane-XML Installation"
echo "========================================="
echo ""

# Call the main install script
exec "${PROJECT_ROOT}/ariane-xml-scripts/install.sh" "$@"
