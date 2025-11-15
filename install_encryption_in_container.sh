#!/bin/bash
#
# Install encryption module in existing Docker container
# This is a workaround until the Docker proxy issue is fixed
#

set -e

echo "============================================"
echo "Installing Encryption Module in Container"
echo "============================================"
echo ""

# Check if we're inside a container
if [ ! -f /.dockerenv ]; then
    echo "This script should be run inside the Docker container."
    echo "Running docker compose exec expocli bash..."
    docker compose exec expocli bash -c "cd /app && bash install_encryption_in_container.sh"
    exit 0
fi

echo "Step 1: Installing Python and pip..."
echo ""

# Install Python packages manager
apt-get update
apt-get install -y python3-pip python3-venv

echo ""
echo "Step 2: Installing Python dependencies..."
echo ""

# Install encryption dependencies
pip3 install --no-cache-dir \
    cryptography \
    pyyaml \
    faker \
    lxml \
    ff3

echo ""
echo "Step 3: Installing Jupyter dependencies..."
echo ""

pip3 install --no-cache-dir \
    jupyterlab \
    notebook \
    ipykernel \
    jupyter-client

echo ""
echo "Step 4: Installing ExpoCLI kernel..."
echo ""

cd /app
pip3 install -e .
python3 -m expocli_kernel.install

echo ""
echo "Step 5: Installing ExpoCLI encryption module..."
echo ""

pip3 install -e . -f setup_crypto.py

echo ""
echo "============================================"
echo "Installation Complete!"
echo "============================================"
echo ""

# Verify installation
echo "Verifying installation..."
echo ""

if command -v expocli-encrypt &> /dev/null; then
    echo "✓ expocli-encrypt command is available"
    expocli-encrypt --help | head -10
else
    echo "✗ expocli-encrypt command not found"
    echo "  Trying to find it..."
    find /usr/local -name "expocli-encrypt" 2>/dev/null || echo "  Not found in /usr/local"
    echo ""
    echo "  You may need to add it to PATH:"
    echo "  export PATH=\"\$PATH:/usr/local/bin\""
fi

echo ""
echo "Testing Python imports..."
if python3 -c "import cryptography, faker, lxml, yaml; print('✓ All packages imported successfully')" 2>/dev/null; then
    echo "✓ All encryption packages available"
else
    echo "✗ Some packages missing"
fi

echo ""
echo "Testing Jupyter..."
if command -v jupyter &> /dev/null; then
    echo "✓ Jupyter is available"
    jupyter --version
else
    echo "✗ Jupyter not found"
fi

echo ""
echo "Next steps:"
echo "1. Test encryption with sample data:"
echo "   cd /app/tests/encryption"
echo "   expocli-encrypt encrypt sample_data.xml encrypted.xml -c ../../encryption_config.example.yaml"
echo ""
echo "2. Read the documentation:"
echo "   cat /app/ENCRYPTION_QUICKSTART.md"
echo ""
