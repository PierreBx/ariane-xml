#!/bin/bash
# Check environment for ariane-xml requirements

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "========================================="
echo "Ariane-XML Environment Check"
echo "========================================="
echo ""

# Check Docker
echo -n "Docker:           "
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    echo "✓ Installed (${DOCKER_VERSION})"
else
    echo "✗ NOT INSTALLED"
    echo "  Please install Docker: https://docs.docker.com/get-docker/"
fi

# Check Docker Compose V2
echo -n "Docker Compose:   "
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_VERSION=$(docker compose version --short)
    echo "✓ Installed (${COMPOSE_VERSION})"
else
    echo "✗ NOT INSTALLED"
    echo "  Please update Docker to get Compose V2"
fi

# Check Docker daemon
echo -n "Docker daemon:    "
if docker ps &> /dev/null 2>&1; then
    echo "✓ Running"
else
    echo "✗ NOT RUNNING"
    echo "  Please start the Docker daemon"
fi

# Check for Docker image
echo -n "Ariane-XML image: "
if docker images -q ariane-xml_image | grep -q .; then
    IMAGE_SIZE=$(docker images ariane-xml_image --format "{{.Size}}")
    echo "✓ Built (${IMAGE_SIZE})"
else
    echo "✗ Not built"
    echo "  Run 'Setup > Build containers' to create the image"
fi

# Check for running container
echo -n "Container status: "
if docker ps -q -f name=ariane-xml_container -f status=running | grep -q .; then
    echo "✓ Running"
elif docker ps -a -q -f name=ariane-xml_container | grep -q .; then
    echo "⚠ Exists but stopped"
else
    echo "○ Not created"
fi

# Check if binary is compiled
echo -n "Binary compiled:  "
if docker compose exec -T ariane-xml test -f /app/ariane-xml-c-kernel/build/ariane-xml 2>/dev/null; then
    echo "✓ Yes"
else
    echo "✗ No"
    echo "  Will be compiled automatically on first use"
fi

# Check Jupyter kernel
echo -n "Jupyter kernel:   "
if docker compose exec -T ariane-xml jupyter kernelspec list 2>/dev/null | grep -q ariane-xml; then
    echo "✓ Installed"
else
    echo "✗ Not installed"
    echo "  Will be installed automatically when starting Jupyter"
fi

echo ""
echo "========================================="
echo "Environment check complete"
echo "========================================="
