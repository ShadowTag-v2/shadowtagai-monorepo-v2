# ============================================
# STAGE 1: Build Environment
# ============================================
FROM rust:1.82-slim-bookworm AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy manifest files for dependency caching
COPY Cargo.toml Cargo.lock* ./

# Create dummy src for dependency compilation
RUN mkdir src && echo "fn main() {}" > src/main.rs

# Build dependencies only (cache layer)
RUN cargo build --release && rm -rf src

# Copy actual source code
COPY src ./src

# Build the application
RUN touch src/main.rs && cargo build --release

# ============================================
# STAGE 2: Runtime (Minimal)
# ============================================
FROM gcr.io/distroless/cc-debian12:nonroot

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/target/release/media-edge /app/media-edge

# Security: Run as non-root (UID 1001 matches K8s security context)
USER 1001:1001

# Expose ports
# 8080: HTTP traffic
# 9090: Prometheus metrics
EXPOSE 8080 9090

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD ["/app/media-edge", "--health-check"] || exit 1

# Entry point
ENTRYPOINT ["/app/media-edge"]
