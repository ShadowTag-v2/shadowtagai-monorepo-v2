#!/bin/bash
# Install Swarm Intelligence Stack: AgentDB + Claude-Flow + scikit-opt

set -euo pipefail

echo "🚀 Installing Swarm Intelligence Stack"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js 16+"
    exit 1
fi

echo "✓ Prerequisites check passed"
echo ""

# 1. Install AgentDB
echo "📦 Installing AgentDB (96x-164x faster vector search)..."
pip3 install agentdb --quiet || {
    echo "⚠️  AgentDB installation failed, trying with --user flag"
    pip3 install --user agentdb --quiet
}

if python3 -c "import agentdb" 2>/dev/null; then
    VERSION=$(python3 -c "import agentdb; print(agentdb.__version__)" 2>/dev/null || echo "unknown")
    echo "✓ AgentDB ${VERSION} installed"
else
    echo "❌ AgentDB installation failed"
    exit 1
fi

echo ""

# 2. Install Claude-Flow
echo "📦 Installing Claude-Flow (100+ MCP tools)..."
npm install -g claude-flow@alpha 2>&1 | grep -v "npm WARN" || true

if npx claude-flow@alpha --version &> /dev/null; then
    VERSION=$(npx claude-flow@alpha --version 2>/dev/null || echo "unknown")
    echo "✓ Claude-Flow ${VERSION} installed"
else
    echo "❌ Claude-Flow installation failed"
    exit 1
fi

echo ""

# 3. Initialize MCP tools
echo "🔧 Initializing MCP tools..."
npx claude-flow@alpha mcp init --yes 2>&1 | grep -v "npm WARN" || true
echo "✓ MCP tools initialized"

echo ""

# 4. Install scikit-opt
echo "📦 Installing scikit-opt (PSO, GA, ACO, SA, IA, AFSA, DE)..."
pip3 install scikit-opt --quiet || {
    echo "⚠️  scikit-opt installation failed, trying with --user flag"
    pip3 install --user scikit-opt --quiet
}

if python3 -c "from sko.PSO import PSO" 2>/dev/null; then
    echo "✓ scikit-opt installed"
else
    echo "❌ scikit-opt installation failed"
    exit 1
fi

echo ""
echo "✅ Installation Complete!"
echo "========================="
echo ""
echo "Installed Components:"
echo "  • AgentDB: $(python3 -c 'import agentdb; print(agentdb.__version__)' 2>/dev/null || echo 'installed')"
echo "  • Claude-Flow: $(npx claude-flow@alpha --version 2>/dev/null || echo 'installed')"
echo "  • scikit-opt: Installed"
echo ""
echo "Next Steps:"
echo "  1. Test AgentDB: python3 -c 'from agentdb import AgentDB; print(\"AgentDB ready\")'"
echo "  2. List MCP tools: npx claude-flow@alpha mcp list"
echo "  3. Test scikit-opt: python3 -c 'from sko.PSO import PSO; print(\"scikit-opt ready\")'"
echo ""
echo "Integration Docs: .claude/docs/swarm-intelligence-integration.md"
echo ""
echo "Rangers lead the way! 🎯"
