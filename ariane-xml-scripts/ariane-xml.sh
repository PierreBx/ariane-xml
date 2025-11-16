#!/bin/bash
# ariane-xml.sh - Transparent wrapper for ariane-xml Docker container
# This script automatically manages a persistent Docker container and runs
# ariane-xml inside it, making it feel like a native command.

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONTAINER_NAME="ariane-xml_container"
CONTAINER_BUILD_DIR="/app/ariane-xml-c-kernel/build"
CONTAINER_BINARY="${CONTAINER_BUILD_DIR}/ariane-xml"

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
    if ! docker images -q ariane-xml_image | grep -q .; then
        echo "[ariane-xml] Building Docker image (first time setup)..." >&2
        docker compose build >&2
        echo "[ariane-xml] Docker image built." >&2
    fi

    # Start the container in detached mode
    echo "[ariane-xml] Starting ariane-xml container..." >&2
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
    if ! docker compose exec -T ariane-xml test -f "${CONTAINER_BINARY}" 2>/dev/null; then
        echo "[ariane-xml] Compiling ariane-xml binary..." >&2

        # Clean build directory to ensure fresh build with correct binary name
        docker compose exec -T ariane-xml bash -c \
            "rm -rf ${CONTAINER_BUILD_DIR} && mkdir -p ${CONTAINER_BUILD_DIR} && cd ${CONTAINER_BUILD_DIR} && cmake .. >/dev/null 2>&1 && make >/dev/null 2>&1" >&2

        if docker compose exec -T ariane-xml test -f "${CONTAINER_BINARY}" 2>/dev/null; then
            echo "[ariane-xml] Compilation successful." >&2
        else
            echo "Error: Failed to compile ariane-xml." >&2
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
    # -T: No TTY (for non-interactive/piped input)
    # -i: Keep stdin open (needed for interactive readline)
    if [ -t 0 ] && [ -t 1 ]; then
        TTY_FLAG="-i"
    else
        TTY_FLAG="-T"
    fi

    # Map host path to container path
    # User's home directory is mounted at /host_home in container
    HOST_CWD="$(pwd)"

    # Normalize paths to handle case-insensitive filesystems
    HOST_CWD_REAL="$(realpath "${HOST_CWD}" 2>/dev/null || echo "${HOST_CWD}")"
    HOME_REAL="$(realpath "${HOME}" 2>/dev/null || echo "${HOME}")"

    CONTAINER_CWD="${HOST_CWD_REAL/${HOME_REAL}/\/host_home}"

    # Run ariane-xml inside the persistent container:
    # - Use docker compose exec to reuse running container
    # - Change to the mapped directory
    # - Pass through all arguments
    # - Preserve exit code
    cd "${PROJECT_ROOT}"

    docker compose exec ${TTY_FLAG} \
        ariane-xml \
        bash -c "cd '${CONTAINER_CWD}' 2>/dev/null && exec ${CONTAINER_BINARY} $(printf '%q ' "$@")"

    local EXIT_CODE=$?

    # If directory doesn't exist in container, show helpful error
    if [ $EXIT_CODE -ne 0 ] && [ -z "$(docker compose exec -T ariane-xml test -d "${CONTAINER_CWD}" 2>/dev/null)" ]; then
        echo "Error: Current directory '${HOST_CWD_REAL}' is not accessible in container." >&2
        echo "       Only directories under ${HOME_REAL} are accessible." >&2
        exit 1
    fi

    exit $EXIT_CODE
}

# Run main function with all arguments
main "$@"
