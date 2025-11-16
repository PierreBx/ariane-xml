#!/bin/bash
# Display Ariane-XML version history

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION_HISTORY_FILE="${SCRIPT_DIR}/../../ariane-xml-config/VERSION_HISTORY.txt"

# Color codes
COLOR_RESET='\033[0m'
COLOR_BOLD='\033[1m'
COLOR_CYAN='\033[0;36m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[0;33m'

# Check if version history file exists
if [ ! -f "$VERSION_HISTORY_FILE" ]; then
    echo -e "${COLOR_YELLOW}Error: Version history file not found at $VERSION_HISTORY_FILE${COLOR_RESET}"
    exit 1
fi

# Clear screen and display header (if terminal is available)
if [ -t 1 ] && [ -n "$TERM" ]; then
    clear
fi

echo -e "${COLOR_BOLD}${COLOR_CYAN}"
cat "$VERSION_HISTORY_FILE"
echo -e "${COLOR_RESET}"
