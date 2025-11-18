#!/bin/bash
#
# Ariane-XML Jupyter Lab Startup Script
#
# This script starts Jupyter Lab in the Docker container with proper configuration
# for the Ariane-XML kernel integration.
#

set -e

echo "========================================="
echo "Ariane-XML Jupyter Lab Environment"
echo "========================================="
echo ""

# Verify Ariane-XML binary is available
DOCKER_BINARY="/app/ariane-xml-c-kernel/build/ariane-xml"
HOST_BINARY="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/ariane-xml-c-kernel/build/ariane-xml"

if [ -f "$DOCKER_BINARY" ]; then
    echo "✓ Ariane-XML binary found at $DOCKER_BINARY"
elif [ -f "$HOST_BINARY" ]; then
    echo "✓ Ariane-XML binary found at $HOST_BINARY"
else
    echo "ERROR: Ariane-XML binary not found"
    echo "Checked locations:"
    echo "  - $DOCKER_BINARY (Docker)"
    echo "  - $HOST_BINARY (Host)"
    echo ""
    echo "To build the binary:"
    echo "  cd $(dirname "$HOST_BINARY")"
    echo "  cmake .. && make"
    exit 1
fi

# Verify the kernel is installed
if ! jupyter kernelspec list | grep -q ariane-xml; then
    echo "ERROR: Ariane-XML kernel not installed"
    echo "Installing the kernel now..."
    python3 -m ariane_xml_jupyter_kernel.install
fi

echo "✓ Ariane-XML Jupyter kernel is installed"
echo ""

# Display kernel information
echo "Available Jupyter kernels:"
jupyter kernelspec list
echo ""

# Kill any existing Jupyter servers on port 8888
echo "Checking for existing Jupyter servers on port 8888..."
JUPYTER_PID=$(lsof -ti:8888 2>/dev/null || true)
if [ -n "$JUPYTER_PID" ]; then
    echo "⚠ Found existing process on port 8888 (PID: $JUPYTER_PID)"
    echo "  Terminating to avoid port conflict..."
    kill -9 $JUPYTER_PID 2>/dev/null || true
    sleep 1
    echo "✓ Port 8888 is now available"
else
    echo "✓ Port 8888 is available"
fi
echo ""

# Generate Jupyter configuration if it doesn't exist
JUPYTER_CONFIG_DIR="${HOME}/.jupyter"
mkdir -p "${JUPYTER_CONFIG_DIR}"

if [ ! -f "${JUPYTER_CONFIG_DIR}/jupyter_lab_config.py" ]; then
    echo "Generating Jupyter Lab configuration..."
    jupyter lab --generate-config
fi

# Configure JupyterLab settings for dark mode
JUPYTER_LAB_SETTINGS_DIR="${JUPYTER_CONFIG_DIR}/lab/user-settings/@jupyterlab"
THEME_SETTINGS_DIR="${JUPYTER_LAB_SETTINGS_DIR}/apputils-extension"
mkdir -p "${THEME_SETTINGS_DIR}"

# Create theme settings file to enable dark mode
cat > "${THEME_SETTINGS_DIR}/themes.jupyterlab-settings" <<'EOF'
{
    "theme": "JupyterLab Dark"
}
EOF

echo "✓ JupyterLab configured with dark mode"
echo ""

# Start Jupyter Lab
echo "========================================="
echo "Starting Jupyter Lab..."
echo "========================================="
echo ""
echo "Access Jupyter Lab at: http://localhost:8888"
echo ""
echo "The demo notebook is available at:"
echo "  ariane-xml-examples/Ariane-XML_Demo.ipynb"
echo ""
echo "Press Ctrl+C to stop Jupyter Lab"
echo ""

# Start Jupyter Lab with appropriate settings
exec jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root \
    --NotebookApp.token='' \
    --NotebookApp.password='' \
    --NotebookApp.allow_origin='*' \
    --NotebookApp.base_url='/'
