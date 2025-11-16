#!/bin/bash
#
# Ariane-XML Jupyter Kernel Installation Script
#
# Usage:
#   ./install_kernel.sh          # Install the kernel
#   ./install_kernel.sh --uninstall  # Uninstall the kernel
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Ariane-XML Jupyter Kernel Installer"
echo "=================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.8 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed."
    echo "Please install pip3."
    exit 1
fi
echo "✓ Found pip3"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install --user ipykernel jupyter-client

# Install the kernel package in development mode
echo ""
echo "Installing Ariane-XML kernel package..."
cd "${PROJECT_ROOT}"
pip3 install --user -e .

# Run the kernel installation script
echo ""
python3 -m ariane_xml_jupyter_kernel.install "$@"

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Start Jupyter: jupyter notebook  (or jupyter lab)"
echo "  2. Create a new notebook and select 'Ariane-XML' kernel"
echo "  3. Try the example notebook: ariane-xml-examples/Ariane-XML_Demo.ipynb"
