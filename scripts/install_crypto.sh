#!/bin/bash
# Installation script for Ariane-XML Encryption Module

set -e

echo "============================================"
echo "Ariane-XML Encryption Module - Installation"
echo "============================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 is required"; exit 1; }

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install --user cryptography pyyaml faker lxml ff3

# Install the encryption module
echo ""
echo "Installing Ariane-XML encryption module..."
pip3 install --user -e ./ariane-xml_crypto

echo ""
echo "============================================"
echo "Installation completed successfully!"
echo "============================================"
echo ""
echo "The 'ariane-xml-encrypt' command is now available."
echo ""
echo "Quick start:"
echo "  1. Copy the example configuration:"
echo "     cp config/encryption_config.example.yaml my_config.yaml"
echo ""
echo "  2. Edit the configuration to match your needs:"
echo "     nano my_config.yaml"
echo ""
echo "  3. Encrypt a file:"
echo "     ariane-xml-encrypt encrypt input.xml output.xml -c my_config.yaml"
echo ""
echo "  4. View help:"
echo "     ariane-xml-encrypt --help"
echo ""
echo "See ENCRYPTION_MODULE.md for full documentation."
echo ""
