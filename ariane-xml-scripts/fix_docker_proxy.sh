#!/bin/bash
#
# Script to fix Docker proxy configuration
#

set -e

echo "============================================"
echo "Docker Proxy Configuration Fix"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}This script needs sudo privileges.${NC}"
    echo "Restarting with sudo..."
    exec sudo bash "$0" "$@"
fi

echo "Step 1: Checking current Docker daemon configuration..."
echo ""

if [ -f /etc/docker/daemon.json ]; then
    echo "Current /etc/docker/daemon.json:"
    cat /etc/docker/daemon.json
    echo ""

    # Backup the current configuration
    echo "Creating backup at /etc/docker/daemon.json.backup..."
    cp /etc/docker/daemon.json /etc/docker/daemon.json.backup
    echo -e "${GREEN}✓ Backup created${NC}"
    echo ""
else
    echo "No existing /etc/docker/daemon.json found"
    echo ""
fi

echo "Step 2: Creating new Docker daemon configuration without proxy..."
echo ""

# Create new daemon.json without proxy
cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

echo "New /etc/docker/daemon.json:"
cat /etc/docker/daemon.json
echo ""
echo -e "${GREEN}✓ Configuration file updated${NC}"
echo ""

echo "Step 3: Restarting Docker daemon..."
echo ""

systemctl restart docker
sleep 2

if systemctl is-active --quiet docker; then
    echo -e "${GREEN}✓ Docker daemon restarted successfully${NC}"
else
    echo -e "${RED}✗ Docker daemon failed to restart${NC}"
    echo "Restoring backup..."
    if [ -f /etc/docker/daemon.json.backup ]; then
        mv /etc/docker/daemon.json.backup /etc/docker/daemon.json
        systemctl restart docker
    fi
    exit 1
fi

echo ""
echo "Step 4: Verifying proxy configuration..."
echo ""

PROXY_INFO=$(docker info 2>&1 | grep -A 3 -i "HTTP Proxy" || echo "No proxy configured")
echo "$PROXY_INFO"
echo ""

if echo "$PROXY_INFO" | grep -q "localhost:3128"; then
    echo -e "${RED}✗ Proxy still configured - additional steps may be needed${NC}"
else
    echo -e "${GREEN}✓ Proxy configuration removed${NC}"
fi

echo ""
echo "============================================"
echo "Configuration complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Navigate to your Ariane-XML directory:"
echo "   cd /home/ipro0800/Documents/projets-perso/prod-projects/ariane-xml"
echo ""
echo "2. Stop any running containers:"
echo "   docker compose down"
echo ""
echo "3. Rebuild the Docker image:"
echo "   docker compose build"
echo ""
echo "4. Start the services:"
echo "   docker compose up -d"
echo ""
echo "5. Check Jupyter logs:"
echo "   docker compose logs jupyter"
echo ""
