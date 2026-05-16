# Claude Code in Vertex AI Workbench: Enterprise Implementation Guide

**Claude Code is Anthropic's terminal-based agentic coding assistant that understands codebases and accelerates development through natural language commands.** This production-ready guide provides complete installation, configuration, and optimization procedures for integrating Claude Code with Google Cloud Vertex AI Workbench for enterprise AI infrastructure development. Vertex AI Workbench provides managed JupyterLab environments with two-disk architecture (ephemeral boot disk, persistent data disk at `/home/jupyter/`), requiring specific configuration patterns to ensure tools persist across instance restarts. The guide covers authentication via Google Cloud Secret Manager, multi-repository workspace management, and security best practices for enterprise deployments.

## Installing Claude Code in Vertex AI Workbench terminal

**Native binary installation is recommended** over npm for better performance and no Node.js dependency. The installation process must account for Vertex AI Workbench's persistence model where only `/home/jupyter/` survives restarts.

### Installation procedure

Access your Vertex AI Workbench terminal (File > New > Terminal or SSH via `gcloud compute ssh`) and execute the native installer:

```bash
# Install Claude Code stable version
curl -fsSL https://claude.ai/install.sh | bash

# Verify installation
claude doctor

# Check installation location
which claude
```

The installer places binaries in `~/.local/bin/claude` (persistent location). **Critical**: The installer automatically adds `~/.local/bin` to your PATH in `~/.bashrc` or `~/.zshrc`, which persists across restarts since shell configuration files reside in `/home/jupyter/`.

### Handling Alpine Linux environments

For Container-Optimized OS custom containers (Alpine-based):

```bash
# Install required dependencies first
sudo apk add libgcc libstdc++ ripgrep

# Set environment variable to use system ripgrep
echo 'export USE_BUILTIN_RIPGREP=0' >> ~/.bashrc
source ~/.bashrc

# Then install Claude Code
curl -fsSL https://claude.ai/install.sh | bash
```

### Post-installation verification

```bash
# Test Claude Code
claude --version

# Run diagnostic check
claude doctor

# Test basic functionality
claude -p "What is Claude Code?"
```

### Migration from npm installation

If you previously installed via npm:

```bash
# Migrate to native installer
claude install

# Or explicitly migrate
claude migrate-installer

# Uninstall npm version after verification
npm uninstall -g @anthropic-ai/claude-code
```

## Configuring authentication tokens for persistent sessions

Claude Code supports three authentication methods with different trade-offs for Vertex AI Workbench deployments.

### Authentication method comparison

| Method | Persistence | Cost Model | Security | Best For |
|--------|-------------|------------|----------|----------|
| **API Key (env var)** | Requires configuration | Pay-per-use | Requires secure storage | Automated workflows, CI/CD |
| **Claude Console OAuth** | Browser-based, survives restarts | Creates dedicated workspace | Linked to user account | Individual developers |
| **Pro/Max Subscription** | Browser-based, survives restarts | Fixed monthly ($20-$100) | Linked to user account | Regular heavy usage |

### Method 1: API Key with Google Cloud Secret Manager (recommended for production)

**Never store API keys in plaintext**. Use Google Cloud Secret Manager for secure token storage:

```bash
# Step 1: Create secret in Secret Manager (one-time setup)
# In Cloud Console: Secret Manager > Create Secret
# - Name: anthropic-api-key
# - Value: your-api-key-sk-ant-xxxxx

# Step 2: Grant Workbench service account access to secret
# Get your instance's service account email
gcloud workbench instances describe INSTANCE_NAME \
  --project=PROJECT_ID \
  --location=ZONE \
  --format="value(gceSetup.serviceAccounts[0].email)"

# Grant Secret Manager Secret Accessor role
gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/secretmanager.secretAccessor" \
  --project=PROJECT_ID

# Step 3: Create persistent startup script to fetch secret
cat > ~/fetch_claude_key.py << 'EOF'
from google.cloud import secretmanager
import os

def get_secret(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID")
api_key = get_secret(project_id, "anthropic-api-key")
print(api_key)
EOF

chmod +x ~/fetch_claude_key.py

# Step 4: Add to shell profile for persistence
cat >> ~/.bashrc << 'EOF'

# Claude Code API Key (from Secret Manager)
if command -v python3 &> /dev/null && [ -f ~/fetch_claude_key.py ]; then
    export ANTHROPIC_API_KEY=$(python3 ~/fetch_claude_key.py 2>/dev/null)
fi
EOF

source ~/.bashrc

# Step 5: Verify authentication
claude /status
```

### Method 2: OAuth authentication (simplest for individual developers)

```bash
# Launch Claude Code - will trigger browser OAuth
claude

# Follow browser prompts to authenticate with Claude Console
# Authentication persists in ~/.claude/credentials.json (persistent location)

# Verify authentication status
claude /status
```

### Method 3: Subscription authentication

For teams using Claude Pro/Max subscriptions:

```bash
# Launch Claude Code
claude

# Select subscription authentication when prompted
# Log in with claude.ai account credentials
# Authentication persists automatically

# Check subscription usage
# Visit console.anthropic.com/workspaces
```

### Disabling auto-updates (optional)

For controlled enterprise environments:

```bash
# Add to ~/.bashrc for persistence
echo 'export DISABLE_AUTOUPDATER=1' >> ~/.bashrc
source ~/.bashrc
```

## Integrating Claude Code with GitHub repositories

Vertex AI Workbench includes the `jupyterlab-git` extension preinstalled, providing seamless integration between Git workflows and Claude Code.

### GitHub authentication setup

**Personal Access Token (PAT) method** (required since password authentication was removed August 2021):

```bash
# Step 1: Create GitHub PAT
# Visit: https://github.com/settings/tokens
# Generate new token (classic) with 'repo' scope

# Step 2: Store PAT in Secret Manager (recommended)
# Create secret 'github-pat' in Secret Manager

# Step 3: Configure Git with cached credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
git config --global credential.helper 'store --file ~/.git-credentials'

# Step 4: Clone repository (will prompt for PAT)
cd ~/repos
git clone https://github.com/your-org/your-repo.git

# Enter username and PAT when prompted
# Credentials cached in ~/.git-credentials (persistent)
```

**SSH key authentication** (more secure for production):

```bash
# Step 1: Generate SSH key in Vertex AI Workbench
ssh-keygen -t ed25519 -C "your.email@company.com" -f ~/.ssh/id_ed25519
# Press Enter for no passphrase (or use passphrase)

# Step 2: Display public key and add to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy output and add to GitHub: Settings > SSH and GPG keys > New SSH key

# Step 3: Configure SSH
cat >> ~/.ssh/config << 'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
EOF

chmod 600 ~/.ssh/config

# Step 4: Test SSH connection
ssh -T git@github.com

# Step 5: Clone repositories using SSH URLs
git clone git@github.com:your-org/your-repo.git
```

### Claude Code Git workflow integration

Claude Code provides native Git capabilities:

```bash
# Navigate to repository
cd ~/repos/your-project

# Launch Claude Code in repository context
claude

# Claude Code Git commands (within interactive session):
# - Automatic commit message generation
# - PR creation and management
# - Merge conflict resolution
# - Branch operations
# - Git history search

# Example: Create feature with automatic commits
claude "Create a new authentication module with tests"
# Claude Code writes code, creates commits, can create PR

# Example: Find relevant commits
claude "Which commit added tests for markdown in December?"

# Example: Handle merge conflicts
claude "Rebase on main and resolve merge conflicts"
```

### Multi-repository workspace setup

```bash
# Create organized repository structure
mkdir -p ~/repos/{backend,frontend,infrastructure,shared-libs}

# Clone multiple repositories
cd ~/repos/backend
git clone git@github.com:org/api-service.git
cd ~/repos/frontend
git clone git@github.com:org/web-app.git
cd ~/repos/infrastructure
git clone git@github.com:org/terraform-configs.git

# Launch Claude Code with multiple directories
claude --add-dir ~/repos/backend/api-service \
       --add-dir ~/repos/frontend/web-app \
       --add-dir ~/repos/infrastructure/terraform-configs

# Or add directories during session
/add-dir ~/repos/shared-libs/common-utils
```

## Setting up Claude Code with Jupyter notebooks

**Claude Code is fundamentally a terminal tool** and cannot be directly embedded into Jupyter notebook cells. However, effective integration patterns exist for using Claude Code alongside Jupyter workflows.

### Integration pattern 1: Side-by-side terminal and notebook

**Recommended approach** for interactive development:

```bash
# In Vertex AI Workbench JupyterLab:
# 1. Open your notebook in main editor pane
# 2. File > New > Terminal (opens terminal in split pane)
# 3. In terminal, navigate to notebook directory:
cd ~/repos/your-project

# 4. Launch Claude Code
claude

# 5. Reference .ipynb files in Claude Code prompts:
"Review the analysis in notebook.ipynb and suggest optimizations"
"Create a new notebook implementing the model training pipeline"
"Debug the error in cell 5 of data_processing.ipynb"
```

**Claude Code can read and generate .ipynb files** since notebooks are JSON format. Example workflows:

```bash
# Inside Claude Code session:
claude "Analyze anomalies_analysis.ipynb and create a cleaned version"
claude "Convert the Python script model.py into a Jupyter notebook"
claude "Add markdown documentation to all cells in pipeline.ipynb"
```

### Integration pattern 2: Jupyter AI extension (alternative AI coding assistant)

For **in-notebook AI assistance**, use Jupyter AI instead of Claude Code:

```bash
# Install Jupyter AI in persistent location
pip install --user jupyter-ai

# Configure with Anthropic provider
# In JupyterLab: Settings > Settings Editor > Jupyter AI
# Add Anthropic API key (fetch from Secret Manager)

# Usage in notebooks:
%load_ext jupyter_ai_magics

%%ai anthropic:claude-sonnet-4
Generate a function to preprocess time series data
```

### Integration pattern 3: VS Code extension (if using VS Code instead of JupyterLab)

Claude Code has a VS Code extension for richer IDE integration:

```bash
# Install VS Code Server in Vertex AI Workbench
curl -fsSL https://code-server.dev/install.sh | sh
code-server --bind-addr 0.0.0.0:8081

# Access via port forwarding
gcloud compute ssh INSTANCE_NAME \
  --project=PROJECT_ID \
  --zone=ZONE \
  -- -L 8081:localhost:8081

# Install Claude Code VS Code extension
# Open http://localhost:8081
# Extensions > Search "Claude Code" > Install

# Launch: Cmd+Esc (Mac) or Ctrl+Esc (Windows/Linux)
```

### Best practices for Claude Code + Jupyter workflows

1. **Use Claude Code for code generation**, then copy results into notebook cells
2. **Use Jupyter for experimentation**, then ask Claude Code to refactor into production code
3. **Let Claude Code handle file operations** (creating notebooks, organizing project structure)
4. **Use notebook outputs as context**: "Based on the output in cell 10, optimize the algorithm"
5. **Leverage Claude Code's TDD capabilities**: "Write tests for the notebook functions, then create a .py module"

## Configuring Claude Code as standalone terminal tool

Claude Code operates as a standalone CLI tool with both interactive REPL mode and non-interactive print mode for automation.

### Interactive REPL mode configuration

```bash
# Launch in project directory
cd ~/repos/your-project
claude

# Key interactive commands:
/init          # Analyze project, create CLAUDE.md context file
/clear         # Clear context window (use frequently between tasks)
/config        # Interactive configuration menu
/permissions   # Manage tool execution permissions
/model         # Switch between models (Sonnet 4.5, Opus 4.1, Haiku 3.5)
/status        # Check authentication and configuration
/rewind        # Restore previous code state (double Esc)
/add-dir       # Add directories to context mid-session
/help          # Show all commands
```

### Non-interactive print mode for automation

**Print mode** allows scriptable Claude Code usage:

```bash
# Basic print mode usage
claude -p "Explain the main function in app.py"

# JSON output for parsing
claude -p "List all API endpoints" --output-format json

# Pipe input to Claude Code
cat error_logs.txt | claude -p "Analyze these errors and suggest fixes"

# Continue most recent conversation
claude -c "Now implement the fix"

# Resume specific session
claude -r "session-id" "Complete the remaining tasks"

# Set maximum conversation turns
claude -p --max-turns 3 "Refactor the authentication module"

# Skip permission prompts (use with caution)
claude -p --dangerously-skip-permissions "Run all tests"
```

### Custom slash commands for team workflows

Create reusable commands for common tasks:

```bash
# Create commands directory (project-specific)
mkdir -p ~/repos/your-project/.claude/commands

# Create custom command: test.md
cat > ~/repos/your-project/.claude/commands/test.md << 'EOF'
# Test Command
Run the full test suite with coverage reporting.
Execute: pytest --cov=src --cov-report=html tests/
Analyze failures and suggest fixes.
$ARGUMENTS
EOF

# Create custom command: deploy.md
cat > ~/repos/your-project/.claude/commands/deploy.md << 'EOF'
# Deploy Command
1. Run linting and type checking
2. Execute test suite
3. Build Docker container
4. If all checks pass, provide gcloud deployment command
Environment: $ARGUMENTS
EOF

# Usage in Claude Code:
/project:test
/project:deploy staging

# Create personal commands (available in all sessions)
mkdir -p ~/.claude/commands

cat > ~/.claude/commands/review.md << 'EOF'
# Code Review
Perform comprehensive code review checking:
- Code quality and style
- Security vulnerabilities
- Performance issues
- Test coverage
Files: $ARGUMENTS
EOF

# Usage:
/personal:review src/auth.py
```

### Model Context Protocol (MCP) integration

Extend Claude Code with external tools and data sources:

```bash
# Configure MCP servers
claude mcp

# Example: Configure filesystem server
# ~/.claude/mcp.json or project .mcp.json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/docs"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx"
      }
    }
  }
}

# Debug MCP connections
claude --mcp-debug
```

## Best practices for persistent configuration across restarts

Vertex AI Workbench's two-disk architecture requires specific strategies to ensure configurations survive instance restarts.

### Understanding persistence in Vertex AI Workbench

**Persistent (Data Disk - `/home/jupyter/`):**
- User files and notebooks
- `~/.bashrc`, `~/.zshrc` shell configurations
- `~/.local/` user-installed binaries and libraries
- `~/.claude/` Claude Code configuration
- `~/.ssh/` SSH keys
- `~/.gitconfig` Git configuration
- Conda environments in `/home/jupyter/envs/`

**Ephemeral (Boot Disk - lost on upgrades/restarts):**
- System packages installed via `apt-get`
- `/opt/conda` base environment modifications
- Framework versions

### Configuration file locations

```bash
# Claude Code persistent configuration locations:
~/.claude/settings.json          # User settings
~/.claude/credentials.json        # Authentication (persists)
~/.claude/commands/               # Personal slash commands
~/.claude.json                    # Alternative config location (recommended)

# Project-specific configuration:
~/repos/project/.claude/          # Project settings
~/repos/project/.claude/commands/ # Project slash commands
~/repos/project/.mcp.json         # MCP server configuration
~/repos/project/CLAUDE.md         # Project context (/init generated)
```

### Shell profile configuration

Add persistent environment variables and PATH modifications:

```bash
# Edit ~/.bashrc (bash) or ~/.zshrc (zsh)
cat >> ~/.bashrc << 'EOF'

# ============= Claude Code Configuration =============

# Authentication (fetch from Secret Manager)
if command -v python3 &> /dev/null && [ -f ~/fetch_claude_key.py ]; then
    export ANTHROPIC_API_KEY=$(python3 ~/fetch_claude_key.py 2>/dev/null)
fi

# Model selection (optional)
export ANTHROPIC_MODEL="claude-sonnet-4-5-20250929"

# Disable auto-updates in controlled environments (optional)
# export DISABLE_AUTOUPDATER=1

# Custom workspace directory
export CLAUDE_WORKSPACE=~/repos

# Ensure Claude Code binary in PATH (installer adds this automatically)
export PATH="$HOME/.local/bin:$PATH"

# ============= Git Configuration =============
# Git editor
export GIT_EDITOR=nano

# Git credential caching
git config --global credential.helper 'store --file ~/.git-credentials'

# ============= Project Aliases =============
alias cdproject='cd ~/repos/your-main-project'
alias claude-project='cd ~/repos/your-main-project && claude'

EOF

# Apply immediately
source ~/.bashrc
```

### Post-startup script for advanced persistence

Create a Cloud Storage-based startup script for system-level configurations:

```bash
# Step 1: Create startup script
cat > /tmp/claude-code-startup.sh << 'EOF'
#!/bin/bash
# Claude Code Vertex AI Workbench Startup Script

set -e

# Log file
LOGFILE=/home/jupyter/startup-script.log
exec > >(tee -a ${LOGFILE}) 2>&1
echo "=== Claude Code Startup Script - $(date) ==="

# Install additional system dependencies if missing
if ! command -v ripgrep &> /dev/null; then
    echo "Installing ripgrep..."
    sudo apt-get update -qq
    sudo apt-get install -y ripgrep
fi

# Ensure Google Cloud Secret Manager client installed
pip install --user --quiet google-cloud-secret-manager

# Verify Claude Code installation
su - jupyter -c "claude doctor || curl -fsSL https://claude.ai/install.sh | bash"

echo "=== Startup script completed successfully ==="
EOF

# Step 2: Upload to Cloud Storage
gsutil mb gs://YOUR-PROJECT-ID-config || true
gsutil cp /tmp/claude-code-startup.sh gs://YOUR-PROJECT-ID-config/

# Step 3: Configure instance to use startup script
gcloud workbench instances update INSTANCE_NAME \
  --project=PROJECT_ID \
  --location=ZONE \
  --metadata=post-startup-script=gs://YOUR-PROJECT-ID-config/claude-code-startup.sh,post-startup-script-behavior=run_every_start
```

### Custom container for guaranteed persistence

For production environments requiring **complete reproducibility**:

```dockerfile
# Dockerfile
FROM us-docker.pkg.dev/deeplearning-platform-release/gcr.io/workbench-container:latest

# Install Claude Code during build
RUN curl -fsSL https://claude.ai/install.sh | bash

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    ripgrep \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create default configuration directory
RUN mkdir -p /home/jupyter/.claude/commands

# Copy team-specific Claude Code configurations
COPY claude-config/.claude.json /home/jupyter/.claude.json
COPY claude-config/commands/ /home/jupyter/.claude/commands/

# Set ownership
RUN chown -R jupyter:jupyter /home/jupyter/.claude

# Install Python Secret Manager client
RUN pip install --user google-cloud-secret-manager

# Environment variables
ENV PATH="/home/jupyter/.local/bin:$PATH"
ENV DISABLE_AUTOUPDATER=1

# Add startup helper script
COPY startup-helper.sh /startup-helper.sh
RUN chmod +x /startup-helper.sh

CMD ["/startup-helper.sh"]
```

```bash
# Build and deploy custom container
docker build -t us-west1-docker.pkg.dev/PROJECT_ID/containers/claude-workbench:v1 .
docker push us-west1-docker.pkg.dev/PROJECT_ID/containers/claude-workbench:v1

# Create instance with custom container
gcloud workbench instances create claude-instance \
  --project=PROJECT_ID \
  --location=us-west1-a \
  --container-repository=us-west1-docker.pkg.dev/PROJECT_ID/containers/claude-workbench \
  --container-tag=v1 \
  --machine-type=n1-standard-4 \
  --service-account=SERVICE_ACCOUNT_EMAIL
```

## Google Cloud authentication and IAM permissions

Vertex AI Workbench instances require specific IAM roles for Claude Code to access external APIs and Google Cloud resources securely.

### Service account configuration

**Every Vertex AI Workbench instance runs with a service account**. Default is the Compute Engine default service account, but custom service accounts are recommended for production.

```bash
# Create custom service account for Vertex AI Workbench
gcloud iam service-accounts create claude-workbench-sa \
  --display-name="Claude Code Workbench Service Account" \
  --project=PROJECT_ID

# Grant necessary roles
# 1. Secret Manager Secret Accessor (for API keys)
gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:claude-workbench-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=PROJECT_ID

# 2. Storage Object Viewer (for reading Cloud Storage data)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:claude-workbench-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# 3. Vertex AI User (if using Vertex AI APIs)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:claude-workbench-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# 4. BigQuery Data Viewer (if accessing BigQuery)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:claude-workbench-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"
```

### IAM roles for Workbench instance management

Users managing Vertex AI Workbench instances need appropriate permissions:

```bash
# Grant user ability to create/manage instances
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:developer@company.com" \
  --role="roles/notebooks.admin"

# Or more restricted: instance user role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:developer@company.com" \
  --role="roles/notebooks.runner"
```

### Application Default Credentials (ADC)

Vertex AI Workbench instances automatically use ADC, allowing code to authenticate to Google Cloud APIs without explicit credentials:

```python
# Python code automatically uses instance service account
from google.cloud import secretmanager

# No explicit credentials needed - uses ADC
client = secretmanager.SecretManagerServiceClient()
name = f"projects/{project_id}/secrets/anthropic-api-key/versions/latest"
response = client.access_secret_version(request={"name": name})
api_key = response.payload.data.decode("UTF-8")
```

```bash
# Verify ADC configuration
gcloud auth application-default print-access-token

# Check which service account is active
gcloud auth list
```

### Security best practices

**Principle of least privilege:**

```bash
# Instead of Editor role, create custom role with specific permissions
gcloud iam roles create VertexAIWorkbenchMinimal \
  --project=PROJECT_ID \
  --title="Vertex AI Workbench Minimal" \
  --permissions="compute.instances.start,compute.instances.stop,notebooks.instances.use" \
  --stage=GA

# Apply custom role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:claude-workbench-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="projects/PROJECT_ID/roles/VertexAIWorkbenchMinimal"
```

**Network security:**

```bash
# Create instance without external IP (use Cloud NAT for outbound)
gcloud workbench instances create secure-instance \
  --project=PROJECT_ID \
  --location=ZONE \
  --machine-type=n1-standard-4 \
  --network=projects/PROJECT_ID/global/networks/VPC_NAME \
  --subnet=projects/PROJECT_ID/regions/REGION/subnetworks/SUBNET_NAME \
  --no-public-ip \
  --service-account=claude-workbench-sa@PROJECT_ID.iam.gserviceaccount.com
```

**Audit logging:**

```bash
# View audit logs
gcloud logging read "resource.type=notebooks_instance" --project=PROJECT_ID --limit=50
```

## Workspace configuration for multi-repository projects

Enterprise AI development often involves multiple interdependent repositories requiring coordinated workspace management.

### Directory structure best practices

```bash
# Recommended project organization
/home/jupyter/
├── repos/
│   ├── backend/
│   │   ├── api-service/
│   │   ├── data-pipeline/
│   │   └── ml-models/
│   ├── frontend/
│   │   ├── web-app/
│   │   └── mobile-app/
│   ├── infrastructure/
│   │   ├── terraform/
│   │   ├── kubernetes/
│   │   └── ci-cd/
│   └── shared/
│       ├── proto-definitions/
│       ├── common-utils/
│       └── ml-libraries/
├── notebooks/
│   ├── exploration/
│   ├── experiments/
│   └── production/
├── data/
│   ├── raw/
│   ├── processed/
│   └── models/
└── docs/
    ├── architecture/
    └── runbooks/
```

### Multi-repository Claude Code configuration

```bash
# Create workspace initialization script
cat > ~/init-workspace.sh << 'EOF'
#!/bin/bash
# Initialize multi-repo workspace for Claude Code

set -e

WORKSPACE_ROOT=~/repos

# Clone all repositories
echo "Cloning repositories..."
mkdir -p $WORKSPACE_ROOT/{backend,frontend,infrastructure,shared}

# Backend repositories
cd $WORKSPACE_ROOT/backend
[ ! -d "api-service" ] && git clone git@github.com:org/api-service.git
[ ! -d "data-pipeline" ] && git clone git@github.com:org/data-pipeline.git
[ ! -d "ml-models" ] && git clone git@github.com:org/ml-models.git

# Frontend repositories
cd $WORKSPACE_ROOT/frontend
[ ! -d "web-app" ] && git clone git@github.com:org/web-app.git

# Infrastructure
cd $WORKSPACE_ROOT/infrastructure
[ ! -d "terraform" ] && git clone git@github.com:org/terraform.git

# Shared libraries
cd $WORKSPACE_ROOT/shared
[ ! -d "proto-definitions" ] && git clone git@github.com:org/proto-definitions.git

echo "Workspace initialized successfully"

# Create launch script for Claude Code with all repos
cat > ~/launch-full-workspace.sh << 'LAUNCH_EOF'
#!/bin/bash
claude --add-dir ~/repos/backend/api-service \
       --add-dir ~/repos/backend/data-pipeline \
       --add-dir ~/repos/backend/ml-models \
       --add-dir ~/repos/frontend/web-app \
       --add-dir ~/repos/infrastructure/terraform \
       --add-dir ~/repos/shared/proto-definitions
LAUNCH_EOF

chmod +x ~/launch-full-workspace.sh

echo "Launch Claude Code with: ~/launch-full-workspace.sh"
EOF

chmod +x ~/init-workspace.sh
~/init-workspace.sh
```

### Project-specific Claude Code configuration

Create `.claude/` configuration in each repository:

```bash
# Example: API Service repository configuration
cd ~/repos/backend/api-service

mkdir -p .claude/commands

# Create project context file
cat > CLAUDE.md << 'EOF'
# API Service Project

## Overview
FastAPI-based REST API service for ML model serving.

## Tech Stack
- Python 3.11, FastAPI, SQLAlchemy, PostgreSQL, Redis, Docker

## Key Files
- `app/main.py` - Application entry point
- `app/api/` - API route definitions
- `tests/` - Test suite

## Development Commands
```bash
uvicorn app.main:app --reload  # Run locally
pytest tests/ --cov=app         # Run tests
```
EOF

# Create project-specific commands
cat > .claude/commands/test.md << 'EOF'
# Test Suite
Run comprehensive test suite:
1. Unit tests: `pytest tests/unit/ -v`
2. Integration tests: `pytest tests/integration/ -v`
3. Generate coverage report
$ARGUMENTS
EOF

# Commit configuration to repository
git add .claude/ CLAUDE.md
git commit -m "Add Claude Code project configuration"
git push
```

## Performance optimization for Vertex AI Workbench

### Instance sizing recommendations

```bash
# Development workloads (single developer)
# n1-standard-4: 4 vCPUs, 15 GB RAM
gcloud workbench instances create dev-instance \
  --machine-type=n1-standard-4 \
  --no-public-ip \
  --data-disk-size=100GB \
  --data-disk-type=pd-ssd \
  --metadata="idle-timeout-seconds=3600"

# ML training workloads (heavy computation)
# n1-highmem-8 + GPU: 8 vCPUs, 52 GB RAM, 1x Tesla T4
gcloud workbench instances create ml-instance \
  --machine-type=n1-highmem-8 \
  --accelerator-type=NVIDIA_TESLA_T4 \
  --accelerator-core-count=1 \
  --install-gpu-driver \
  --data-disk-size=500GB \
  --data-disk-type=pd-ssd
```

### Disk performance optimization

```bash
# SSD provides better IOPS for Claude Code operations
# pd-ssd: 30 IOPS/GB (read/write) - recommended
# pd-standard: 0.75 IOPS/GB (read) - adequate for basic use

# Increase data disk size for better IOPS
gcloud workbench instances update INSTANCE_NAME \
  --project=PROJECT_ID \
  --location=ZONE \
  --data-disk-size=500GB
```

### Claude Code performance tuning

```bash
# Use smaller models for faster responses
claude --model haiku  # Fastest
claude --model sonnet  # Balanced (default)
claude --model opus    # Most capable, slower

# Clear context frequently for responsiveness
# In Claude Code session:
/clear

# Limit context size for faster processing
claude --add-dir ~/repos/api-service/app  # Specific subdirectory
```

### Network performance optimization

```bash
# Deploy in region closest to your location
# US-based: us-west1, us-central1, us-east1
# Europe: europe-west1, europe-west4
# Asia: asia-northeast1, asia-southeast1

gcloud workbench instances create optimized-instance \
  --location=us-west1-a

# Use Private Google Access for faster API calls
gcloud compute networks subnets update SUBNET_NAME \
  --region=REGION \
  --enable-private-ip-google-access
```

### Caching and data access patterns

```bash
# Mount Cloud Storage buckets for large datasets
mkdir -p ~/gcs-data
gcsfuse --implicit-dirs BUCKET_NAME ~/gcs-data

# Cache frequently accessed data locally
mkdir -p ~/cache/datasets
gsutil -m cp -r gs://bucket/hot-dataset ~/cache/datasets/
```

### Auto-scaling and cost optimization

```bash
# Enable idle shutdown to reduce costs
gcloud workbench instances update INSTANCE_NAME \
  --project=PROJECT_ID \
  --location=ZONE \
  --metadata="idle-timeout-seconds=1800"  # 30 minutes

# Create VM schedule for predictable workloads
gcloud compute resource-policies create instance-schedule work-hours-schedule \
  --region=REGION \
  --vm-start-schedule="0 9 * * MON-FRI" \
  --vm-stop-schedule="0 18 * * MON-FRI" \
  --timezone="America/Los_Angeles"

# Attach schedule to instance
gcloud compute instances add-resource-policies INSTANCE_NAME \
  --resource-policies=work-hours-schedule \
  --zone=ZONE
```

### Monitoring and profiling

```bash
# Enable system health reporting
gcloud workbench instances create monitored-instance \
  --location=ZONE \
  --metadata="report-system-health=true"

# Inside instance, monitor performance:
iostat -x 5  # Disk I/O statistics
vmstat 5     # Virtual memory statistics
htop         # Interactive process viewer
```

## Security considerations for API token storage

### Secret Manager integration (production standard)

**Never store API keys in code, notebooks, or environment files**. Use Google Cloud Secret Manager:

```bash
# 1. Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com --project=PROJECT_ID

# 2. Create secret for Anthropic API key
gcloud secrets create anthropic-api-key \
  --replication-policy="automatic" \
  --project=PROJECT_ID

# 3. Add secret value
echo -n "sk-ant-api03-XXXX" | gcloud secrets versions add anthropic-api-key \
  --data-file=- \
  --project=PROJECT_ID

# 4. Grant Workbench service account access
SERVICE_ACCOUNT=$(gcloud workbench instances describe INSTANCE_NAME \
  --project=PROJECT_ID \
  --location=ZONE \
  --format="value(gceSetup.serviceAccounts[0].email)")

gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor" \
  --project=PROJECT_ID

# 5. Verify access
gcloud secrets get-iam-policy anthropic-api-key --project=PROJECT_ID
```

### Secure credential retrieval

```python
# Create ~/fetch_claude_key.py (persists in home directory)
"""
Securely fetch Anthropic API key from Secret Manager
"""
from google.cloud import secretmanager
import os
import sys

def get_secret(project_id: str, secret_id: str, version_id: str = "latest") -> str:
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error retrieving secret: {e}", file=sys.stderr)
        return ""

if __name__ == "__main__":
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID")
    api_key = get_secret(project_id, "anthropic-api-key")
    if api_key:
        print(api_key)
    else:
        sys.exit(1)
```

```bash
# Make script executable
chmod +x ~/fetch_claude_key.py

# Add to shell profile (automatic authentication)
cat >> ~/.bashrc << 'EOF'

# Claude Code Authentication (via Secret Manager)
if command -v python3 &> /dev/null && [ -f ~/fetch_claude_key.py ]; then
    export ANTHROPIC_API_KEY=$(python3 ~/fetch_claude_key.py 2>/dev/null)
fi
EOF

source ~/.bashrc

# Verify Claude Code can authenticate
claude /status
```

### Security best practices checklist

**API Key Management:**
- ✅ Use Secret Manager for production
- ✅ Never commit keys to Git repositories
- ✅ Rotate keys regularly (every 90 days minimum)
- ✅ Use separate keys for dev/staging/prod
- ❌ Never hardcode keys in notebooks or scripts
- ❌ Never share keys via email/Slack

**Access Control:**
```bash
# Implement least privilege
gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

# Audit secret access
gcloud logging read "resource.type=secretmanager_secret" \
  --limit=50 \
  --format=json
```

**Network Security:**
```bash
# Create private instance (no external IP)
gcloud workbench instances create secure-instance \
  --no-public-ip \
  --network=VPC_NAME \
  --subnet=SUBNET_NAME
```

**Credential Rotation:**
```bash
# Update Secret Manager with new key
echo -n "sk-ant-api03-NEW_KEY" | gcloud secrets versions add anthropic-api-key \
  --data-file=- \
  --project=PROJECT_ID

# Test new key
python3 ~/fetch_claude_key.py
claude /status

# Disable old key version
gcloud secrets versions disable VERSION_ID \
  --secret=anthropic-api-key \
  --project=PROJECT_ID
```

### Customer-Managed Encryption Keys (CMEK)

For regulated industries requiring additional encryption control:

```bash
# Create Cloud KMS key
gcloud kms keyrings create vertex-ai-keyring \
  --location=REGION \
  --project=PROJECT_ID

gcloud kms keys create vertex-ai-key \
  --location=REGION \
  --keyring=vertex-ai-keyring \
  --purpose=encryption \
  --project=PROJECT_ID

# Grant Vertex AI service account access
SERVICE_AGENT="service-PROJECT_NUMBER@gcp-sa-notebooks.iam.gserviceaccount.com"

gcloud kms keys add-iam-policy-binding vertex-ai-key \
  --location=REGION \
  --keyring=vertex-ai-keyring \
  --member="serviceAccount:${SERVICE_AGENT}" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter" \
  --project=PROJECT_ID

# Create instance with CMEK encryption
gcloud workbench instances create cmek-instance \
  --location=ZONE \
  --boot-disk-encryption=CMEK \
  --boot-disk-kms-key=projects/PROJECT_ID/locations/REGION/keyRings/vertex-ai-keyring/cryptoKeys/vertex-ai-key \
  --data-disk-encryption=CMEK \
  --data-disk-kms-key=projects/PROJECT_ID/locations/REGION/keyRings/vertex-ai-keyring/cryptoKeys/vertex-ai-key
```

## Production deployment checklist

**✅ Installation & Configuration:**
- [ ] Claude Code installed via native installer
- [ ] `claude doctor` passes all checks
- [ ] Authentication configured via Secret Manager
- [ ] Shell profile configured with API key retrieval

**✅ Security:**
- [ ] API keys stored in Secret Manager
- [ ] Service account follows least privilege
- [ ] Audit logging enabled
- [ ] Network configured appropriately
- [ ] Key rotation procedure documented

**✅ Persistence:**
- [ ] All configurations in `/home/jupyter/`
- [ ] Post-startup script created and configured
- [ ] Git SSH keys configured
- [ ] Custom conda environments in persistent location

**✅ Multi-Repository Setup:**
- [ ] Repository directory structure created
- [ ] All repositories cloned
- [ ] Project-specific `.claude/` configurations created
- [ ] Custom slash commands created

**✅ Performance:**
- [ ] Instance machine type appropriate
- [ ] Data disk sized appropriately (SSD recommended)
- [ ] Idle shutdown configured
- [ ] Monitoring enabled

**✅ Testing:**
- [ ] Test API key retrieval from Secret Manager
- [ ] Test Claude Code authentication
- [ ] Test GitHub SSH access
- [ ] Test multi-repository workspace
- [ ] Test instance restart persistence

## Conclusion

This comprehensive guide provides production-ready procedures for integrating Claude Code with Google Cloud Vertex AI Workbench. **Key success factors** include proper authentication via Secret Manager, understanding Vertex AI Workbench's persistence model, implementing least-privilege IAM policies, and creating team-specific workflow configurations. For updates and community support, consult the official Claude Code documentation at docs.claude.com and engage with the Claude Developers Discord community.
