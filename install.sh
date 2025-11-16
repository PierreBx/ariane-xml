#!/bin/bash
# Backward compatibility wrapper - calls the actual install script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/scripts/install.sh" "$@"
