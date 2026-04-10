# /sonar-audit - SonarQube Quality Audit

Runs a comprehensive SonarQube analysis and quality gate check using the Antigravity Swarm infrastructure.

## Usage

```
/sonar-audit [options]
```

### Options
- `--fix`: Attempt to fix issues using SonarLint suggestions (not yet implemented)
- `--verbose`: Show full analysis logs

## What It Does

1.  **Infrastructure Check**
    - Verifies SonarQube server is running (Docker).
    - Auto-starts `ShadowTag-v2-sonarqube` container if offline.
    - Verifies `SONAR_TOKEN` authentication.

2.  **Analysis Execution**
    - Runs `sonar-scanner` (via Docker) on the codebase.
    - Uploads report to local SonarQube instance.

3.  **Quality Gate Verification**
    - Checks the project's Quality Gate status.
    - Fails if status is `ERROR`.

4.  **Issue Reporting**
    - Fetches `BLOCKER` and `CRITICAL` issues.
    - Displays them with file locations and rule descriptions.

## Prerequisites

- Docker Desktop must be installed and running.
- `SONAR_TOKEN` environment variable must be set.

## Execution Steps (Agent Instructions)

When this command is invoked:

1.  **Check Token**:
    If `SONAR_TOKEN` is missing, ask the user to provide it or run:
    ```bash
    export SONAR_TOKEN=your_token_here
    ```

2.  **Run Integration Script**:
    Execute the swarm-audited setup script to ensure environment readiness:
    ```bash
    ./scripts/setup_sonar_integration.sh
    ```

3.  **Run Analysis (if needed)**:
    If the user requests a fresh scan or if the project is missing, run the scanner:
    ```bash
    docker run --rm \
        -e SONAR_HOST_URL="http://host.docker.internal:9000" \
        -e SONAR_TOKEN="$SONAR_TOKEN" \
        -v "$PWD:/usr/src" \
        sonarsource/sonar-scanner-cli \
        -Dsonar.projectKey=ShadowTag-v2-fastapi-services \
        -Dsonar.sources=. \
        -Dsonar.exclusions="**/venv/**,**/node_modules/**,**/__pycache__/**,**/.git/**"
    ```

4.  **Fetch Results**:
    Use the Python client to get the final verdict:
    ```bash
    python3 -m app.quality.sonar_client check-gate
    python3 -m app.quality.sonar_client fetch-issues --severity=BLOCKER,CRITICAL
    ```

## Example Output

```markdown
# SonarQube Audit Report

## Infrastructure
✅ SonarQube Server: UP (http://localhost:9000)
✅ Docker Container: ShadowTag-v2-sonarqube (Healthy)

## Quality Gate
❌ FAILED
- Coverage: 65.0% (Threshold: 80.0%)
- Duplicated Lines: 4.2% (Threshold: 3.0%)

## Critical Issues
🔴 [CRITICAL] python:S1234 - Function has too many parameters
  📍 app/services/complex_service.py:42
  💬 Refactor this function to reduce parameters from 8 to 7.

## Recommendation
- Run unit tests to improve coverage.
- Refactor `complex_service.py`.
```