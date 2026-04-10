# Base image with Node.js 20
FROM node:20-bookworm

# Install essential packages and tools
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    # Core utilities
    git \
    curl \
    wget \
    ca-certificates \
    # Shell and productivity tools
    zsh \
    fzf \
    ripgrep \
    # Network tools for firewall
    iptables \
    iputils-ping \
    dnsutils \
    net-tools \
    # Python and pip
    python3 \
    python3-pip \
    python3-venv \
    # Build tools
    build-essential \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Set up Python symlinks
RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# Install Oh My Zsh for better shell experience
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Configure ZSH
RUN echo 'export ZSH="$HOME/.oh-my-zsh"' >> ~/.zshrc && \
    echo 'ZSH_THEME="robbyrussell"' >> ~/.zshrc && \
    echo 'plugins=(git node npm python fzf)' >> ~/.zshrc && \
    echo 'source $ZSH/oh-my-zsh.sh' >> ~/.zshrc && \
    echo 'export HISTFILE=/commandhistory/.zsh_history' >> ~/.zshrc && \
    echo 'export HISTSIZE=10000' >> ~/.zshrc && \
    echo 'export SAVEHIST=10000' >> ~/.zshrc

# Set ZSH as default shell
RUN chsh -s $(which zsh)

# Install global npm packages
RUN npm install -g \
    typescript \
    ts-node \
    prettier \
    eslint \
    @anthropic-ai/claude-code

# Install Python packages for Claude Agent SDK
RUN pip3 install --no-cache-dir \
    claude-agent-sdk \
    pytest \
    black \
    pylint \
    mypy

# Copy firewall initialization script
COPY .devcontainer/init-firewall.sh /usr/local/bin/init-firewall.sh
RUN chmod +x /usr/local/bin/init-firewall.sh

# Create directory for command history
RUN mkdir -p /commandhistory && chmod 777 /commandhistory

# Set working directory
WORKDIR /workspace

# Default command
CMD ["/bin/zsh"]
