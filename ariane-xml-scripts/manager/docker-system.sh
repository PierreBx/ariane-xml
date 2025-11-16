#!/bin/bash
# Docker System Management

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Color codes
COLOR_RESET='\033[0m'
COLOR_BOLD='\033[1m'
COLOR_CYAN='\033[0;36m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[0;33m'
COLOR_RED='\033[0;31m'

cd "${PROJECT_ROOT}"

# Display sub-menu
echo -e "${COLOR_BOLD}${COLOR_CYAN}"
echo "╔════════════════════════════════════════════╗"
echo "║           DOCKER MANAGEMENT                ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${COLOR_RESET}"
echo ""
echo "  1. Restart Docker server"
echo "  2. Check Docker status"
echo "  3. Check Docker proxy settings"
echo ""
echo -e "${COLOR_YELLOW}  0. Back to main menu${COLOR_RESET}"
echo ""

read -p "Enter your choice [0-3]: " choice
echo ""

case "$choice" in
    1)
        echo "========================================="
        echo "Restart Docker Server"
        echo "========================================="
        echo ""
        echo -e "${COLOR_YELLOW}⚠ This operation requires sudo privileges${COLOR_RESET}"
        echo ""
        echo "To restart the Docker server, please run the following command:"
        echo ""
        echo -e "${COLOR_BOLD}${COLOR_GREEN}sudo systemctl restart docker${COLOR_RESET}"
        echo ""
        echo "Note: This will restart the Docker daemon and may interrupt running containers."
        ;;
    2)
        echo "========================================="
        echo "Docker Status"
        echo "========================================="
        echo ""

        echo -e "${COLOR_BOLD}Docker Service Status:${COLOR_RESET}"
        echo ""
        if command -v systemctl &> /dev/null; then
            systemctl status docker --no-pager || true
        else
            echo "systemctl not available. Checking Docker info instead..."
        fi

        echo ""
        echo -e "${COLOR_BOLD}Docker Version:${COLOR_RESET}"
        docker version

        echo ""
        echo -e "${COLOR_BOLD}Docker System Info:${COLOR_RESET}"
        docker info
        ;;
    3)
        echo "========================================="
        echo "Docker Proxy Settings"
        echo "========================================="
        echo ""

        # Check systemd proxy configuration
        PROXY_CONF="/etc/systemd/system/docker.service.d/http-proxy.conf"
        if [ -f "$PROXY_CONF" ]; then
            echo -e "${COLOR_BOLD}Systemd proxy configuration:${COLOR_RESET}"
            echo "File: $PROXY_CONF"
            echo ""
            cat "$PROXY_CONF"
            echo ""
        else
            echo "No systemd proxy configuration found at $PROXY_CONF"
            echo ""
        fi

        # Check Docker daemon configuration
        DAEMON_JSON="/etc/docker/daemon.json"
        if [ -f "$DAEMON_JSON" ]; then
            echo -e "${COLOR_BOLD}Docker daemon configuration:${COLOR_RESET}"
            echo "File: $DAEMON_JSON"
            echo ""
            if grep -q "proxy" "$DAEMON_JSON" 2>/dev/null; then
                cat "$DAEMON_JSON"
            else
                echo "No proxy settings found in daemon.json"
            fi
            echo ""
        else
            echo "No Docker daemon configuration found at $DAEMON_JSON"
            echo ""
        fi

        # Check environment variables
        echo -e "${COLOR_BOLD}Proxy environment variables:${COLOR_RESET}"
        echo ""
        env | grep -i proxy || echo "No proxy environment variables set"
        echo ""

        # Check Docker info for proxy settings
        echo -e "${COLOR_BOLD}Docker info proxy settings:${COLOR_RESET}"
        echo ""
        docker info | grep -i proxy || echo "No proxy information in Docker info"
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
