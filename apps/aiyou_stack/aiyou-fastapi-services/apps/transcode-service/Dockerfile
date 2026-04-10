# Multi-stage Dockerfile for transcode-service
# Stage 1: Build Rust application
# Stage 2: Runtime with FFmpeg 7.0 + NVIDIA support

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage 1: Builder
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FROM rust:1.82-bookworm AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    libclang-dev \
    clang \
    cmake \
    nasm \
    && rm -rf /var/lib/apt/lists/*

# Install FFmpeg dev libraries for ffmpeg-next bindings
RUN apt-get update && apt-get install -y \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libavfilter-dev \
    libavdevice-dev \
    libswscale-dev \
    libswresample-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy manifests
COPY Cargo.toml Cargo.lock ./

# Create dummy src to cache dependencies
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
RUN rm -rf src

# Copy actual source
COPY src ./src

# Build release binary
RUN touch src/main.rs && cargo build --release

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage 2: Runtime with FFmpeg
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FROM nvidia/cuda:12.3.1-runtime-ubuntu22.04

# Install FFmpeg with NVIDIA support
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec59 \
    libavformat59 \
    libavutil57 \
    libavfilter8 \
    libswscale6 \
    libswresample4 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r transcode && useradd -r -g transcode transcode

# Create directories
RUN mkdir -p /tmp/transcode && chown transcode:transcode /tmp/transcode

# Copy binary from builder
COPY --from=builder /app/target/release/transcode-service /usr/local/bin/

# Set ownership
RUN chown transcode:transcode /usr/local/bin/transcode-service

# Switch to non-root user
USER transcode

# Health check ports
EXPOSE 8080 9090

# Environment defaults
ENV TRANSCODE_LISTEN_ADDR="0.0.0.0:8080" \
    TRANSCODE_METRICS_ADDR="0.0.0.0:9090" \
    TRANSCODE_TEMP_DIR="/tmp/transcode" \
    TRANSCODE_SEGMENT_DURATION="6" \
    TRANSCODE_MAX_CONCURRENT_JOBS="2" \
    TRANSCODE_ENABLE_NVENC="true" \
    RUST_LOG="transcode_service=info"

ENTRYPOINT ["/usr/local/bin/transcode-service"]
