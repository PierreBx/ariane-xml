#!/bin/bash
# Ariane-XML Manager - Unified management interface
# This script provides an interactive menu for all ariane-xml operations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGER_DIR="${SCRIPT_DIR}/ariane-xml-scripts/manager"

# Color codes for better UX
COLOR_RESET='\033[0m'
COLOR_BOLD='\033[1m'
COLOR_CYAN='\033[0;36m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[0;33m'

# Display the main menu
show_menu() {
    clear
    echo -e "${COLOR_BOLD}${COLOR_CYAN}"
    echo "╔════════════════════════════════════════════╗"
    echo "║      ARIANE-XML MANAGEMENT CONSOLE         ║"
    echo "╚════════════════════════════════════════════╝"
    echo -e "${COLOR_RESET}"
    echo ""

    echo -e "${COLOR_GREEN}=== Setup ===${COLOR_RESET}"
    echo "  1. Run full installation"
    echo "  2. Check environment"
    echo ""

    echo -e "${COLOR_GREEN}=== Documentation ===${COLOR_RESET}"
    echo "  3. Quick start guide - CLI"
    echo "  4. Quick start guide - Jupyter"
    echo "  5. Quick start guide - Encryption"
    echo "  6. Full documentation index"
    echo ""

    echo -e "${COLOR_GREEN}=== Infrastructure ===${COLOR_RESET}"
    echo "  7. Docker / Images / Containers / Jupyter"
    echo ""

    echo -e "${COLOR_GREEN}=== Apps ===${COLOR_RESET}"
    echo "  8. Start ariane-xml CLI"
    echo "  9. Start ariane-xml in Jupyter"
    echo " 10. Stop running apps"
    echo ""

    echo -e "${COLOR_GREEN}=== Tests ===${COLOR_RESET}"
    echo " 11. Run light test suite (Docker)"
    echo " 12. Run hard test suite (Docker)"
    echo " 13. Run hardest test suite (Docker)"
    echo " 14. Run DSN mode test suite (Docker)"
    echo ""

    echo -e "${COLOR_GREEN}=== Version history & files summary ===${COLOR_RESET}"
    echo " 15. Show version history"
    echo " 16. Show files summary"
    echo ""

    echo -e "${COLOR_YELLOW}  0. Exit${COLOR_RESET}"
    echo ""
}

# Display Infrastructure submenu
show_infrastructure_menu() {
    clear
    echo -e "${COLOR_BOLD}${COLOR_CYAN}"
    echo "╔════════════════════════════════════════════╗"
    echo "║       INFRASTRUCTURE MANAGEMENT            ║"
    echo "╚════════════════════════════════════════════╝"
    echo -e "${COLOR_RESET}"
    echo ""
    echo "  1. Docker"
    echo "  2. Images"
    echo "  3. Containers"
    echo "  4. Jupyter server"
    echo ""
    echo -e "${COLOR_YELLOW}  0. Back to main menu${COLOR_RESET}"
    echo ""
}

# Display component action submenu
show_component_menu() {
    local component="$1"
    clear
    echo -e "${COLOR_BOLD}${COLOR_CYAN}"
    echo "╔════════════════════════════════════════════╗"
    echo "║      ${component^^} MANAGEMENT                    ║"
    echo "╚════════════════════════════════════════════╝"
    echo -e "${COLOR_RESET}"
    echo ""
    echo "  1. Status"
    echo "  2. Kill and clean"
    echo "  3. Build"
    echo ""
    echo -e "${COLOR_YELLOW}  0. Back${COLOR_RESET}"
    echo ""
}

# Handle infrastructure component actions
handle_infrastructure_action() {
    local component="$1"
    local action="$2"

    case "$component-$action" in
        # Docker actions
        docker-status)
            echo "========================================="
            echo "Docker System Status"
            echo "========================================="
            echo ""
            echo -e "${COLOR_BOLD}Docker Version:${COLOR_RESET}"
            docker version
            echo ""
            echo -e "${COLOR_BOLD}Docker System Info:${COLOR_RESET}"
            docker info
            echo ""
            echo -e "${COLOR_BOLD}Docker Compose Status:${COLOR_RESET}"
            docker compose ps
            ;;
        docker-clean)
            echo "========================================="
            echo "Clean Docker System"
            echo "========================================="
            echo ""
            echo "⚠ This will:"
            echo "  - Stop all ariane-xml containers"
            echo "  - Remove all stopped containers"
            echo "  - Prune unused resources"
            echo ""
            read -p "Continue? [y/N] " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker compose down
                docker system prune -f
                echo ""
                echo "✓ Docker system cleaned"
            else
                echo "Cancelled."
            fi
            ;;
        docker-build)
            echo "========================================="
            echo "Rebuild Docker Environment"
            echo "========================================="
            echo ""
            docker compose build --no-cache
            echo ""
            echo "✓ Docker build completed"
            ;;

        # Images actions
        images-status)
            echo "========================================="
            echo "Ariane-XML Related Images"
            echo "========================================="
            echo ""
            docker images | head -1
            docker images | grep -i ariane || echo "No ariane-xml related images found."
            echo ""
            ;;
        images-clean)
            echo "========================================="
            echo "Delete Ariane-XML Images"
            echo "========================================="
            echo ""
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
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    echo ""
                    echo "$IMAGES" | while read -r image; do
                        echo "Deleting $image..."
                        docker rmi "$image" || echo "Warning: Could not remove $image"
                    done
                    echo ""
                    echo "✓ Image deletion completed"
                else
                    echo "Cancelled."
                fi
            fi
            ;;
        images-build)
            echo "========================================="
            echo "Build Ariane-XML Image"
            echo "========================================="
            echo ""
            docker compose build ariane-xml --no-cache
            echo ""
            echo "✓ Image build completed"
            ;;

        # Containers actions
        containers-status)
            echo "========================================="
            echo "Ariane-XML Containers Status"
            echo "========================================="
            echo ""
            docker compose ps
            echo ""
            ;;
        containers-clean)
            echo "========================================="
            echo "Stop and Remove Containers"
            echo "========================================="
            echo ""
            echo "⚠ This will:"
            echo "  - Stop all running containers"
            echo "  - Remove all containers"
            echo "  - Data in containers will be lost"
            echo ""
            read -p "Continue? [y/N] " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker compose down
                echo ""
                echo "✓ Containers stopped and removed"
            else
                echo "Cancelled."
            fi
            ;;
        containers-build)
            echo "========================================="
            echo "Build and Start Containers"
            echo "========================================="
            echo ""
            docker compose up -d --build
            echo ""
            echo "✓ Containers built and started"
            ;;

        # Jupyter actions
        jupyter-status)
            echo "========================================="
            echo "Jupyter Server Status"
            echo "========================================="
            echo ""
            if docker compose ps jupyter 2>/dev/null | grep -q "Up"; then
                echo "✓ Jupyter server is running"
                echo ""
                docker compose exec jupyter jupyter server list 2>/dev/null || echo "Could not retrieve server list"
            else
                echo "✗ Jupyter server is not running"
            fi
            echo ""
            ;;
        jupyter-clean)
            echo "========================================="
            echo "Kill and Clean Jupyter"
            echo "========================================="
            echo ""
            "${MANAGER_DIR}/jupyter-kill.sh"
            echo ""
            "${MANAGER_DIR}/jupyter-clean.sh"
            echo ""
            echo "✓ Jupyter cleaned"
            ;;
        jupyter-build)
            echo "========================================="
            echo "Build and Start Jupyter"
            echo "========================================="
            echo ""
            docker compose build jupyter --no-cache
            docker compose up -d jupyter
            echo ""
            echo "✓ Jupyter built and started"
            ;;

        *)
            echo -e "${COLOR_YELLOW}Invalid action${COLOR_RESET}"
            ;;
    esac
}

# Infrastructure menu loop
infrastructure_menu() {
    while true; do
        show_infrastructure_menu
        read -p "Enter your choice [0-4]: " component_choice
        echo ""

        case "$component_choice" in
            0)
                return
                ;;
            1|2|3|4)
                local component_name
                case "$component_choice" in
                    1) component_name="Docker" ;;
                    2) component_name="Images" ;;
                    3) component_name="Containers" ;;
                    4) component_name="Jupyter" ;;
                esac

                while true; do
                    show_component_menu "$component_name"
                    read -p "Enter your choice [0-3]: " action_choice
                    echo ""

                    case "$action_choice" in
                        0)
                            break
                            ;;
                        1)
                            handle_infrastructure_action "${component_name,,}" "status"
                            read -p "Press Enter to continue..."
                            ;;
                        2)
                            handle_infrastructure_action "${component_name,,}" "clean"
                            read -p "Press Enter to continue..."
                            ;;
                        3)
                            handle_infrastructure_action "${component_name,,}" "build"
                            read -p "Press Enter to continue..."
                            ;;
                        *)
                            echo -e "${COLOR_YELLOW}Invalid option. Please try again.${COLOR_RESET}"
                            read -p "Press Enter to continue..."
                            ;;
                    esac
                done
                ;;
            *)
                echo -e "${COLOR_YELLOW}Invalid option. Please try again.${COLOR_RESET}"
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Execute the selected option
execute_option() {
    case $1 in
        1)
            "${MANAGER_DIR}/setup-install.sh"
            ;;
        2)
            "${MANAGER_DIR}/setup-check-env.sh"
            ;;
        3)
            "${MANAGER_DIR}/doc-quickstart-cli.sh"
            ;;
        4)
            "${MANAGER_DIR}/doc-quickstart-jupyter.sh"
            ;;
        5)
            "${MANAGER_DIR}/doc-encryption.sh"
            ;;
        6)
            "${MANAGER_DIR}/doc-index.sh"
            ;;
        7)
            infrastructure_menu
            ;;
        8)
            # Exit manager and launch CLI (replaces manager process)
            exec "${MANAGER_DIR}/app-start-cli.sh"
            ;;
        9)
            "${MANAGER_DIR}/app-start-jupyter.sh"
            ;;
        10)
            "${MANAGER_DIR}/app-stop.sh"
            ;;
        11)
            "${MANAGER_DIR}/test-light-docker.sh"
            ;;
        12)
            "${MANAGER_DIR}/test-hard-docker.sh"
            ;;
        13)
            "${MANAGER_DIR}/test-hardest-docker.sh"
            ;;
        14)
            "${MANAGER_DIR}/test-dsn-docker.sh"
            ;;
        15)
            "${MANAGER_DIR}/version-show-history.sh"
            ;;
        16)
            "${MANAGER_DIR}/version-show-files-summary.sh"
            ;;
        0)
            echo ""
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo ""
            echo -e "${COLOR_YELLOW}Invalid option. Please try again.${COLOR_RESET}"
            ;;
    esac
}

# Main loop
main() {
    # Check if running with command-line arguments (non-interactive mode)
    if [ $# -gt 0 ]; then
        case "$1" in
            --install)
                "${MANAGER_DIR}/setup-install.sh"
                ;;
            --check-env)
                "${MANAGER_DIR}/setup-check-env.sh"
                ;;
            --cli)
                exec "${MANAGER_DIR}/app-start-cli.sh"
                ;;
            --jupyter)
                "${MANAGER_DIR}/app-start-jupyter.sh"
                ;;
            --test-light)
                "${MANAGER_DIR}/test-light-docker.sh"
                ;;
            --test-light-local)
                "${MANAGER_DIR}/test-light.sh"
                ;;
            --test-hard)
                "${MANAGER_DIR}/test-hard.sh"
                ;;
            --test-hardest)
                "${MANAGER_DIR}/test-hardest.sh"
                ;;
            --test-dsn)
                "${MANAGER_DIR}/test-dsn-docker.sh"
                ;;
            --test-dsn-local)
                "${MANAGER_DIR}/test-dsn.sh"
                ;;
            --version-history)
                "${MANAGER_DIR}/version-show-history.sh"
                ;;
            --files-summary)
                "${MANAGER_DIR}/version-show-files-summary.sh"
                ;;
            --help)
                echo "Ariane-XML Manager"
                echo ""
                echo "Usage:"
                echo "  $0                     Interactive menu"
                echo "  $0 --install           Run full installation"
                echo "  $0 --check-env         Check environment"
                echo "  $0 --cli               Start CLI"
                echo "  $0 --jupyter           Start Jupyter"
                echo "  $0 --test-light        Run light tests (Docker mode - recommended)"
                echo "  $0 --test-light-local  Run light tests (local mode)"
                echo "  $0 --test-hard         Run hard tests"
                echo "  $0 --test-hardest      Run hardest tests"
                echo "  $0 --test-dsn          Run DSN mode tests (Docker mode - recommended)"
                echo "  $0 --test-dsn-local    Run DSN mode tests (local mode)"
                echo "  $0 --version-history   Show version history"
                echo "  $0 --files-summary     Show files summary (cloc)"
                echo "  $0 --help              Show this help"
                echo ""
                echo "Note: Interactive mode now includes Infrastructure menu for managing"
                echo "      Docker, Images, Containers, and Jupyter server."
                ;;
            *)
                echo "Unknown option: $1"
                echo "Run '$0 --help' for usage information"
                exit 1
                ;;
        esac
        exit 0
    fi

    # Interactive mode
    while true; do
        show_menu
        read -p "Enter your choice [0-16]: " choice
        echo ""

        execute_option "$choice"

        # Pause after each operation (except for exit)
        if [ "$choice" != "0" ] && [ "$choice" != "8" ]; then
            echo ""
            read -p "Press Enter to continue..."
        fi
    done
}

# Run main function
main "$@"
