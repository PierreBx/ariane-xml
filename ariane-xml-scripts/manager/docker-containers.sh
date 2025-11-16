#!/bin/bash
# Docker Containers Management

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Color codes
COLOR_RESET='\033[0m'
COLOR_BOLD='\033[1m'
COLOR_CYAN='\033[0;36m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[0;33m'

cd "${PROJECT_ROOT}"

# Display sub-menu
echo -e "${COLOR_BOLD}${COLOR_CYAN}"
echo "╔════════════════════════════════════════════╗"
echo "║         CONTAINERS MANAGEMENT              ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${COLOR_RESET}"
echo ""
echo "  1. Stop containers"
echo "  2. Start containers"
echo "  3. Delete containers"
echo "  4. Check containers status"
echo ""
echo -e "${COLOR_YELLOW}  0. Back to main menu${COLOR_RESET}"
echo ""

read -p "Enter your choice [0-4]: " choice
echo ""

case "$choice" in
    1)
        echo "========================================="
        echo "Stopping Ariane-XML Containers"
        echo "========================================="
        echo ""
        docker compose stop
        echo ""
        echo "✓ Containers stopped successfully"
        ;;
    2)
        echo "========================================="
        echo "Starting Ariane-XML Containers"
        echo "========================================="
        echo ""
        docker compose start
        echo ""
        echo "✓ Containers started successfully"
        ;;
    3)
        echo "========================================="
        echo "Deleting Ariane-XML Containers"
        echo "========================================="
        echo ""
        echo "⚠ This will remove all containers"
        echo "⚠ All data in containers will be lost"
        echo ""
        read -p "Continue? [y/N] " -n 1 -r
        echo ""

        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Cancelled."
            exit 0
        fi

        echo ""
        docker compose down
        echo ""
        echo "✓ Containers deleted successfully"
        ;;
    4)
        echo "========================================="
        echo "Ariane-XML Containers Status"
        echo "========================================="
        echo ""
        docker compose ps
        echo ""
        ;;
    0)
        echo "Returning to main menu..."
        ;;
    *)
        echo -e "${COLOR_YELLOW}Invalid option. Please try again.${COLOR_RESET}"
        exit 1
        ;;
esac
