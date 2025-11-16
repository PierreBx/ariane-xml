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

    echo -e "${COLOR_GREEN}=== Docker management ===${COLOR_RESET}"
    echo "  7. Containers"
    echo "  8. Images"
    echo "  9. Docker"
    echo ""

    echo -e "${COLOR_GREEN}=== Apps ===${COLOR_RESET}"
    echo " 10. Start ariane-xml CLI"
    echo " 11. Start ariane-xml in Jupyter"
    echo " 12. Stop running apps"
    echo ""

    echo -e "${COLOR_GREEN}=== Tests ===${COLOR_RESET}"
    echo " 13. Run light test suite (Docker)"
    echo " 14. Run hard test suite (Docker)"
    echo " 15. Run hardest test suite (Docker)"
    echo ""

    echo -e "${COLOR_GREEN}=== Version history & files summary ===${COLOR_RESET}"
    echo " 17. Show version history"
    echo " 18. Show files summary"
    echo ""

    echo -e "${COLOR_YELLOW}  0. Exit${COLOR_RESET}"
    echo ""
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
            "${MANAGER_DIR}/docker-containers.sh"
            ;;
        8)
            "${MANAGER_DIR}/docker-images.sh"
            ;;
        9)
            "${MANAGER_DIR}/docker-system.sh"
            ;;
        10)
            # Exit manager and launch CLI (replaces manager process)
            exec "${MANAGER_DIR}/app-start-cli.sh"
            ;;
        11)
            "${MANAGER_DIR}/app-start-jupyter.sh"
            ;;
        12)
            "${MANAGER_DIR}/app-stop.sh"
            ;;
        13)
            "${MANAGER_DIR}/test-light-docker.sh"
            ;;
        14)
            "${MANAGER_DIR}/test-hard-docker.sh"
            ;;
        15)
            "${MANAGER_DIR}/test-hardest-docker.sh"
            ;;
        17)
            "${MANAGER_DIR}/version-show-history.sh"
            ;;
        18)
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
                echo "  $0                   Interactive menu"
                echo "  $0 --install         Run full installation"
                echo "  $0 --check-env       Check environment"
                echo "  $0 --cli             Start CLI"
                echo "  $0 --jupyter         Start Jupyter"
                echo "  $0 --test-light      Run light tests (Docker mode - recommended)"
                echo "  $0 --test-light-local Run light tests (local mode)"
                echo "  $0 --test-hard       Run hard tests"
                echo "  $0 --test-hardest    Run hardest tests"
                echo "  $0 --version-history Show version history"
                echo "  $0 --files-summary   Show files summary (cloc)"
                echo "  $0 --help            Show this help"
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
        read -p "Enter your choice [0-15, 17-18]: " choice
        echo ""

        execute_option "$choice"

        # Pause after each operation (except for exit)
        if [ "$choice" != "0" ]; then
            echo ""
            read -p "Press Enter to continue..."
        fi
    done
}

# Run main function
main "$@"
