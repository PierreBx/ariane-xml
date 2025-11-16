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
    echo "Running docker compose exec ariane-xml bash..."
    docker compose exec ariane-xml bash -c "cd /app && bash install_encryption_in_container.sh"
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
echo "Step 4: Installing Ariane-XML kernel..."
echo ""

cd /app
pip3 install -e .
python3 -m ariane-xml_kernel.install

echo ""
echo "Step 5: Installing Ariane-XML encryption module..."
echo ""

pip3 install -e ./ariane-xml_crypto

echo ""
echo "============================================"
echo "Installation Complete!"
echo "============================================"
echo ""

# Verify installation
echo "Verifying installation..."
echo ""

if command -v ariane-xml-encrypt &> /dev/null; then
    echo "✓ ariane-xml-encrypt command is available"
    ariane-xml-encrypt --help | head -10
else
    echo "✗ ariane-xml-encrypt command not found"
    echo "  Trying to find it..."
    find /usr/local -name "ariane-xml-encrypt" 2>/dev/null || echo "  Not found in /usr/local"
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
echo "   ariane-xml-encrypt encrypt sample_data.xml encrypted.xml -c ../../encryption_config.example.yaml"
echo ""
echo "2. Read the documentation:"
echo "   cat /app/ENCRYPTION_QUICKSTART.md"
echo ""
