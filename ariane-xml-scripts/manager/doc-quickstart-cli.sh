#!/bin/bash
# Display CLI quick start guide

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

DOC_FILE="${PROJECT_ROOT}/ariane-xml-documentation/01a_Quick_Start_CLI.md"

if command -v less &> /dev/null; then
    less "${DOC_FILE}"
elif command -v more &> /dev/null; then
    more "${DOC_FILE}"
else
    cat "${DOC_FILE}"
fi
