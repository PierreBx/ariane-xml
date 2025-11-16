#!/bin/bash
# Rebuild Docker containers from scratch

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

echo "========================================="
echo "Rebuilding Ariane-XML Containers"
echo "========================================="
echo ""
echo "⚠ This will stop and remove existing containers"
echo "⚠ All data in containers will be lost"
echo ""
read -p "Continue? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Stopping containers..."
docker compose down

echo ""
echo "Rebuilding images..."
docker compose build --no-cache

echo ""
echo "Starting containers..."
docker compose up -d

echo ""
echo "✓ Containers rebuilt successfully"
