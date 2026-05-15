#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}///▞ ANTIGRAVITY SWARM :: SONAR AUDIT${NC}"

# 1. Check Token
if [ -z "$SONAR_TOKEN" ]; then
    echo -e "${RED}❌ SONAR_TOKEN is not set.${NC}"
    echo "Please run: export SONAR_TOKEN=your_token"
    exit 1
fi

# 2. Infrastructure Check
echo -e "\n${YELLOW}🔍 Checking Infrastructure...${NC}"
./scripts/setup_sonar_integration.sh

# 3. Run Analysis
echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
rm -rf .scannerwork

echo -e "\n${YELLOW}🐛 Debugging File Content...${NC}"
grep -A 10 "orchestrator.execute" src/api/unified.py

echo -e "\n${YELLOW}🐛 Debugging Container Mount...${NC}"
docker run --rm -v "$PWD:/usr/src" alpine cat /usr/src/src/api/unified.py | grep -A 5 "orchestrator.execute"

echo -e "\n${YELLOW}🚀 Running SonarScanner...${NC}"
docker run --rm \
    -e SONAR_HOST_URL="http://host.docker.internal:9000" \
    -e SONAR_TOKEN="$SONAR_TOKEN" \
    -v "$PWD:/usr/src" \
    sonarsource/sonar-scanner-cli \
    -Dsonar.projectKey=ShadowTag-v2-fastapi-services \
    -Dsonar.sources=. \
    -Dsonar.scm.disabled=true \
    -Dsonar.exclusions="**/venv/**,**/node_modules/**,**/__pycache__/**,**/.git/**" \
    -Dsonar.python.version=3.10,3.11,3.12

# 4. Fetch Results
echo -e "\n${YELLOW}📊 Fetching Quality Gate Status...${NC}"
# Give SonarQube a moment to process the report
echo "Waiting for background processing..."
sleep 20
python3 -m app.quality.sonar_client check-gate

echo -e "\n${YELLOW}🐛 Fetching Critical Issues...${NC}"
python3 -m app.quality.sonar_client fetch-issues --severity=BLOCKER,CRITICAL

echo -e "\n${GREEN}✅ Audit Complete.${NC}"
