#!/bin/bash
echo "/// SHADOWTAG OMEGA // IGNITION SEQUENCE ///"
echo "> CHECKING ARMOR (Dependencies)..."
pip install -q fastapi uvicorn websockets google-cloud-billing
echo "> IGNITING KERNEL..."
echo "> ACCESS DASHBOARD AT: http://localhost:8000"
echo "---------------------------------------------------"
# Updated path to match repo structure: src/omega/omega_kernel.py
python3 src/omega/omega_kernel.py
