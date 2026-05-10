import os
import sys

# Add current directory to sys.path
sys.path.append(os.getcwd())

try:
    print("Attempting to import pnkln.core.cor_orchestrator")
    from pnkln.core import cor_orchestrator

    print("Import successful")
    print(f"numpy version via module: {cor_orchestrator.np.__version__}")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback

    traceback.print_exc()
