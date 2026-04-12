
#!/bin/bash
echo "Verifying Omega System Status..."
echo "------------------------------"

echo "1. Checking Frontend (Port 3001)..."
curl -I http://localhost:3001 || echo "⚠️ Frontend Unreachable"

echo "\n2. Checking Backend (Port 8080)..."
# ADK usually exposes routes. Let's try basic root.
curl -v http://localhost:8080/ || echo "⚠️ Backend Unreachable"

echo "\n3. Checking specific ADK endpoint (if applicable)..."
curl -X POST http://localhost:8080/copilotkit/v1/info || echo "⚠️ ADK Info Endpoint Unreachable"

echo "\nDone."
