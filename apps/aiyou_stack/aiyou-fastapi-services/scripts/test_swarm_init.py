import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

try:
    print("t_ 🧪 Testing Swarm Import...")
    from src.antigravity.swarm import SwarmOrchestrator

    print("   ✅ Import Successful: src.antigravity.swarm.SwarmOrchestrator")

    orchestrator = SwarmOrchestrator()
    print("   ✅ Initialization Successful")
    print(f"   🤖 Available Agents: {orchestrator.available_agents()}")
except ImportError as e:
    print(f"   ❌ Import Failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Initialization Failed: {e}")
    sys.exit(1)
