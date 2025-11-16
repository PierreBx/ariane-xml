#!/bin/bash
# Docker Images Management

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
echo "║           IMAGES MANAGEMENT                ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${COLOR_RESET}"
echo ""
echo "  1. Delete images"
echo "  2. List images"
echo ""
echo -e "${COLOR_YELLOW}  0. Back to main menu${COLOR_RESET}"
echo ""

read -p "Enter your choice [0-2]: " choice
echo ""

case "$choice" in
    1)
        echo "========================================="
        echo "Deleting Ariane-XML Images"
        echo "========================================="
        echo ""

        # Get ariane-xml related images
        IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -i ariane || true)

        if [ -z "$IMAGES" ]; then
            echo "No ariane-xml related images found."
        else
            echo "Found the following ariane-xml images:"
            echo "$IMAGES"
            echo ""
            echo "⚠ This will permanently remove these images"
            echo ""
            read -p "Continue? [y/N] " -n 1 -r
            echo ""

            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Cancelled."
                exit 0
            fi

            echo ""
            echo "$IMAGES" | while read -r image; do
                echo "Deleting $image..."
                docker rmi "$image" || echo "Warning: Could not remove $image (might be in use)"
            done
            echo ""
            echo "✓ Image deletion completed"
        fi
        ;;
    2)
        echo "========================================="
        echo "Ariane-XML Related Images"
        echo "========================================="
        echo ""
        docker images | head -1  # Header
        docker images | grep -i ariane || echo "No ariane-xml related images found."
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
