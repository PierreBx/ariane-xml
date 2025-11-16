#!/bin/bash
# expocli.sh - Transparent wrapper for expocli Docker container
# This script automatically manages a persistent Docker container and runs
# expocli inside it, making it feel like a native command.

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONTAINER_NAME="expocli_container"
CONTAINER_BUILD_DIR="/app/build"
CONTAINER_BINARY="${CONTAINER_BUILD_DIR}/expocli"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first." >&2
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null 2>&1; then
    echo "Error: Docker Compose V2 is not available. Please update Docker." >&2
    exit 1
fi

# Check if container is running, start if needed
ensure_container_running() {
    cd "${PROJECT_ROOT}"

    # Check if container exists and is running
    if docker ps -q -f name="${CONTAINER_NAME}" -f status=running | grep -q .; then
        return 0
    fi

    # Check if image exists, build if not
    if ! docker images -q expocli_image | grep -q .; then
        echo "[expocli] Building Docker image (first time setup)..." >&2
        docker compose build >&2
        echo "[expocli] Docker image built." >&2
    fi

    # Start the container in detached mode
    echo "[expocli] Starting expocli container..." >&2
    docker compose up -d >&2

    # Wait a moment for container to be ready
    sleep 1

    # Verify container is running
    if ! docker ps -q -f name="${CONTAINER_NAME}" -f status=running | grep -q .; then
        echo "Error: Failed to start container." >&2
        exit 1
    fi
}

# Check if binary exists and build if needed
check_and_build_binary() {
    cd "${PROJECT_ROOT}"
    if ! docker compose exec -T expocli test -f "${CONTAINER_BINARY}" 2>/dev/null; then
        echo "[expocli] Compiling expocli binary (first time)..." >&2
        docker compose exec -T expocli bash -c \
            "mkdir -p ${CONTAINER_BUILD_DIR} && cd ${CONTAINER_BUILD_DIR} && cmake .. >/dev/null 2>&1 && make >/dev/null 2>&1" >&2

        if docker compose exec -T expocli test -f "${CONTAINER_BINARY}" 2>/dev/null; then
            echo "[expocli] Compilation successful." >&2
        else
            echo "Error: Failed to compile expocli." >&2
            exit 1
        fi
    fi
}

# Main execution
main() {
    # Ensure container is running
    ensure_container_running

    # Ensure binary is compiled
    check_and_build_binary

    # Determine if we need TTY (interactive mode)
    TTY_FLAG="-T"
    if [ -t 0 ] && [ -t 1 ]; then
        TTY_FLAG=""
    fi

    # Map host path to container path
    # User's home directory is mounted at /host_home in container
    HOST_CWD="$(pwd)"
    CONTAINER_CWD="${HOST_CWD/${HOME}/\/host_home}"

    # Run expocli inside the persistent container:
    # - Use docker compose exec to reuse running container
    # - Change to the mapped directory
    # - Pass through all arguments
    # - Preserve exit code
    cd "${PROJECT_ROOT}"

    docker compose exec ${TTY_FLAG} \
        expocli \
        bash -c "cd '${CONTAINER_CWD}' 2>/dev/null && ${CONTAINER_BINARY} $(printf '%q ' "$@")"

    local EXIT_CODE=$?

    # If directory doesn't exist in container, show helpful error
    if [ $EXIT_CODE -ne 0 ] && [ -z "$(docker compose exec -T expocli test -d "${CONTAINER_CWD}" 2>/dev/null)" ]; then
        echo "Error: Current directory '${HOST_CWD}' is not accessible in container." >&2
        echo "       Only directories under ${HOME} are accessible." >&2
        exit 1
    fi

    exit $EXIT_CODE
}

# Run main function with all arguments
main "$@"
