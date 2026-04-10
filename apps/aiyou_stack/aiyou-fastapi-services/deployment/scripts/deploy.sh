#!/bin/bash
set -e

echo "🚀 Deploying to production..."

# Configuration
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
HEALTH_URL="${HEALTH_URL:-http://localhost:8000/health}"
MAX_RETRIES=30
RETRY_DELAY=2

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

health_check() {
    local url=$1
    local retries=$2
    local delay=$3

    log_info "Checking health at $url"

    for i in $(seq 1 $retries); do
        if curl -f -s "$url" > /dev/null 2>&1; then
            log_info "Application is healthy!"
            return 0
        fi
        log_warn "Attempt $i/$retries failed, retrying in ${delay}s..."
        sleep "$delay"
    done

    log_error "Health check failed after $retries attempts"
    return 1
}

# Main deployment flow
main() {
    log_info "Starting deployment process..."

    # Pull latest changes
    log_info "Pulling latest changes..."
    git pull origin main || log_warn "Not a git repository or no changes"

    # Install dependencies
    log_info "Installing dependencies..."
    npm ci

    # Run tests
    log_info "Running tests..."
    npm test || log_warn "No tests found or tests failed"

    # Build application
    log_info "Building application..."
    npm run build || log_warn "No build script found"

    # Build Docker image
    log_info "Building Docker image..."
    docker-compose -f "$COMPOSE_FILE" build

    # Stop old containers
    log_info "Stopping old containers..."
    docker-compose -f "$COMPOSE_FILE" --profile production down

    # Start new containers
    log_info "Starting new containers..."
    docker-compose -f "$COMPOSE_FILE" --profile production up -d

    # Wait for startup
    log_info "Waiting for application to start..."
    sleep 10

    # Health check
    if health_check "$HEALTH_URL" "$MAX_RETRIES" "$RETRY_DELAY"; then
        log_info "✅ Deployment successful!"

        # Show running containers
        log_info "Running containers:"
        docker-compose -f "$COMPOSE_FILE" ps

        return 0
    else
        log_error "❌ Deployment failed - health check unsuccessful!"
        log_error "Showing recent logs:"
        docker-compose -f "$COMPOSE_FILE" logs --tail=50

        # Optionally rollback
        read -p "Do you want to rollback? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Initiating rollback..."
            ./deployment/scripts/rollback.sh
        fi

        return 1
    fi
}

# Run main function
main "$@"
