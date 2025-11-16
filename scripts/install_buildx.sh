#!/bin/bash
# Install Docker Buildx for improved build performance

set -e

echo "Installing Docker Buildx..."
echo ""

# Check Docker version
DOCKER_VERSION=$(docker version --format '{{.Server.Version}}')
echo "Current Docker version: $DOCKER_VERSION"

# Create Docker CLI plugins directory
mkdir -p ~/.docker/cli-plugins

# Download latest buildx
BUILDX_VERSION=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep '"tag_name"' | sed -E 's/.*"v([^"]+)".*/\1/')
echo "Latest Buildx version: v$BUILDX_VERSION"

# Download buildx binary
echo "Downloading buildx..."
curl -sSL "https://github.com/docker/buildx/releases/download/v${BUILDX_VERSION}/buildx-v${BUILDX_VERSION}.linux-amd64" \
  -o ~/.docker/cli-plugins/docker-buildx

# Make it executable
chmod +x ~/.docker/cli-plugins/docker-buildx

# Verify installation
echo ""
echo "Verifying installation..."
docker buildx version

echo ""
echo "✓ Buildx installed successfully!"
echo ""
echo "The warning should now disappear when running docker compose build."
