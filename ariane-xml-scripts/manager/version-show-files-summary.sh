#!/bin/bash
# Display Ariane-XML files summary using cloc

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/../.."

# Color codes
COLOR_RESET='\033[0m'
COLOR_BOLD='\033[1m'
COLOR_CYAN='\033[0;36m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[0;33m'

# Clear screen (if terminal is available)
if [ -t 1 ] && [ -n "$TERM" ]; then
    clear
fi

echo -e "${COLOR_BOLD}${COLOR_CYAN}"
echo "================================================================================"
echo "                    ARIANE-XML FILES SUMMARY (CLOC)"
echo "================================================================================"
echo -e "${COLOR_RESET}"
echo ""

# Check if we're inside a Docker container
if [ -f /.dockerenv ]; then
    # We're inside the container, run cloc directly
    cd /app
    cloc . \
        --exclude-dir=build,.git,__pycache__,.pytest_cache,.ipynb_checkpoints,node_modules \
        --exclude-ext=.pyc,.pyo,.class,.o,.so,.a \
        --quiet
else
    # We're outside the container, run cloc via docker exec
    echo -e "${COLOR_YELLOW}Running cloc inside ariane-xml container...${COLOR_RESET}"
    echo ""
    docker compose exec -T ariane-xml bash -c "cd /app && cloc . \
        --exclude-dir=build,.git,__pycache__,.pytest_cache,.ipynb_checkpoints,node_modules \
        --exclude-ext=.pyc,.pyo,.class,.o,.so,.a \
        --quiet"
fi

echo ""
echo -e "${COLOR_GREEN}Summary complete.${COLOR_RESET}"
