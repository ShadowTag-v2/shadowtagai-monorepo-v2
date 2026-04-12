#!/bin/bash
set -e

echo "⏪ Rolling back deployment..."

# Configuration
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
REGISTRY="${REGISTRY:-ghcr.io}"
IMAGE_NAME="${IMAGE_NAME:-ShadowTag-v2-fastapi-services}"
PREVIOUS_VERSION="${1:-latest}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

main() {
    log_info "Rolling back to version: $PREVIOUS_VERSION"

    # Get current container ID for backup
    CURRENT_CONTAINER=$(docker-compose -f "$COMPOSE_FILE" ps -q app-prod 2>/dev/null || echo "")

    if [ -n "$CURRENT_CONTAINER" ]; then
        log_info "Current container ID: $CURRENT_CONTAINER"
    fi

    # Try to pull previous version
    log_info "Pulling previous image..."
    docker pull "$REGISTRY/$IMAGE_NAME:$PREVIOUS_VERSION" 2>/dev/null || log_warn "Could not pull image from registry"

    # Stop current containers
    log_info "Stopping current containers..."
    docker-compose -f "$COMPOSE_FILE" --profile production down

    # Start previous version
    log_info "Starting previous version..."
    docker-compose -f "$COMPOSE_FILE" --profile production up -d

    # Wait for startup
    log_info "Waiting for application to start..."
    sleep 10

    # Health check
    if ./deployment/scripts/health-check.sh; then
        log_info "✅ Rollback successful!"
        log_info "Now running version: $PREVIOUS_VERSION"
    else
        log_error "❌ Rollback failed!"
        log_error "Application is not healthy after rollback"

        # Show logs
        docker-compose -f "$COMPOSE_FILE" logs --tail=50
        return 1
    fi
}

main "$@"
