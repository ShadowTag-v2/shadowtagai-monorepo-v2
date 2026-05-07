#!/usr/bin/env python3
"""
Omega Loop Health Dashboard
Provides a quick status overview of the autonomous system's health.
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def check_git_status():
    try:
        status = subprocess.check_output(['git', 'status', '--porcelain'], text=True)
        dirty_files = len([line for line in status.splitlines() if line.strip()])
        return dirty_files
    except Exception:
        return "Unknown"

def check_github_auth():
    pem = os.environ.get("SHADOWTAG_PEM")
    if not pem:
        return "MISSING $SHADOWTAG_PEM"
    if not os.path.exists(pem):
        return f"PEM NOT FOUND at {pem}"
    return "Valid PEM Path"

def main():
    print("========================================")
    print("      OMEGA LOOP HEALTH DASHBOARD       ")
    print("========================================")
    print(f"Timestamp:       {datetime.now().isoformat()}")
    
    dirty_files = check_git_status()
    print(f"Dirty Files:     {dirty_files}")
    
    auth_status = check_github_auth()
    print(f"GitHub Auth:     {auth_status}")
    
    # Check Python version
    print(f"Python Version:  {sys.version.split()[0]}")
    
    # Check if Jules is accessible (Dummy check for now)
    print("Jules MCP:       Pending TLS Verification")
    
    print("========================================")
    if dirty_files != 0 and dirty_files != "Unknown":
        print("WARNING: Uncommitted changes detected. Omega Loop may need to run.")
    else:
        print("SYSTEM HEALTHY. Ready for autonomous execution.")

if __name__ == "__main__":
    main()
