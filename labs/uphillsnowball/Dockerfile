# UphillSnowball ANE-Optimized OrbStack Container
# Architecture: linux/arm64 (Apple Silicon Native)
# Role: Glass House Sentinel (Relay + Tree-Sitter Pruning Engine)

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# 1. Install System Dependencies & Pruning Prerequisites
# OrbStack handles network and mounts via VirtioFS natively.
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    clang \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/uphillsnowball

# 2. Setup Node.js Relay & Context Pruning (Tree-sitter WASM)
# Tree-sitter CLI installed globally for rapid AST sharding
RUN npm install -g pnpm pm2 tree-sitter-cli

# Copy Node manifests (assuming they exist or will be generated)
COPY package*.json ./
RUN if [ -f package.json ]; then npm install; fi

# 3. Setup Agentic Python Core (Akit/Jetski)
RUN python3 -m venv /opt/uphillsnowball/.venv
ENV PATH="/opt/uphillsnowball/.venv/bin:$PATH"

COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# 4. Copy the Core Intelligence Code
COPY . /opt/uphillsnowball/

# 5. Export Communication Ports
# 3000: Node.js Antigravity WebSocket Relay
# 53410: Language Server Orchestrator (Jetski)
EXPOSE 3000
EXPOSE 53410

# 6. Ignite the Triad
# Boot the central nervous system via PM2 to ensure automatic restart if an agent crashes the thread
CMD ["pm2-runtime", "start", "relay.js", "--name", "uphillsnowball-relay"]
