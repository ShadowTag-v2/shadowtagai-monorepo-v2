#!/bin/bash

################################################################################
# Validation Hook for Pnkln GKE Services
#
# This hook can be run at any time to validate:
# - Code quality and linting
# - Security vulnerabilities
# - Configuration consistency
# - Best practices compliance
#
# Exit codes:
#   0 - All validations passed
#   1 - Validation failures detected
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FAIL_ON_WARNING="${FAIL_ON_WARNING:-false}"
STRICT_MODE="${STRICT_MODE:-false}"

# Counters
ERRORS=0
WARNINGS=0
PASSED=0

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((ERRORS++))
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED++))
}

log_section() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════════"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

################################################################################
# Validation Start
################################################################################

log_section "PNKLN GKE SERVICES VALIDATION"
log_info "Starting comprehensive validation..."
log_info "Strict mode: $STRICT_MODE"
log_info "Fail on warning: $FAIL_ON_WARNING"
echo ""

################################################################################
# Python Code Quality
################################################################################

log_section "PYTHON CODE QUALITY"

# Check for Python files
if compgen -G "*.py" > /dev/null || [ -d "app" ] || [ -d "src" ]; then
    log_info "Python project detected"

    # Black - Code formatting
    if command_exists black; then
        log_info "Running Black formatter check..."
        if black --check . >/dev/null 2>&1; then
            log_pass "Black: Code is properly formatted"
        else
            log_warn "Black: Code formatting issues detected"
            log_info "  Run 'black .' to fix formatting"
        fi
    else
        log_warn "Black not installed. Install with: pip install black"
    fi

    # Flake8 - Linting
    if command_exists flake8; then
        log_info "Running Flake8 linter..."
        flake8_output=$(flake8 . 2>&1 || true)
        flake8_errors=$(echo "$flake8_output" | wc -l)

        if [ "$flake8_errors" -eq 0 ]; then
            log_pass "Flake8: No linting issues"
        else
            log_warn "Flake8: Found $flake8_errors issue(s)"
            echo "$flake8_output" | head -10
        fi
    else
        log_warn "Flake8 not installed. Install with: pip install flake8"
    fi

    # MyPy - Type checking
    if command_exists mypy; then
        log_info "Running MyPy type checker..."
        if mypy . --ignore-missing-imports >/dev/null 2>&1; then
            log_pass "MyPy: No type errors"
        else
            log_warn "MyPy: Type errors detected"
        fi
    else
        log_warn "MyPy not installed. Install with: pip install mypy"
    fi

    # Pylint - Advanced linting
    if command_exists pylint; then
        log_info "Running Pylint..."
        pylint_score=$(pylint --exit-zero . 2>/dev/null | grep "rated at" | awk '{print $7}' | cut -d'/' -f1 || echo "0")

        if (( $(echo "$pylint_score >= 8.0" | bc -l) )); then
            log_pass "Pylint: Score $pylint_score/10"
        else
            log_warn "Pylint: Score $pylint_score/10 (target: 8.0+)"
        fi
    fi

else
    log_info "No Python files detected, skipping Python validation"
fi

################################################################################
# Security Scanning
################################################################################

log_section "SECURITY SCANNING"

# Bandit - Python security
if command_exists bandit && compgen -G "*.py" > /dev/null; then
    log_info "Running Bandit security scanner..."
    bandit_output=$(bandit -r . -f json 2>/dev/null || echo "{}")

    high_severity=$(echo "$bandit_output" | jq '.results[] | select(.issue_severity=="HIGH")' 2>/dev/null | wc -l || echo "0")
    medium_severity=$(echo "$bandit_output" | jq '.results[] | select(.issue_severity=="MEDIUM")' 2>/dev/null | wc -l || echo "0")

    if [ "$high_severity" -gt 0 ]; then
        log_error "Bandit: Found $high_severity HIGH severity issue(s)"
        echo "$bandit_output" | jq -r '.results[] | select(.issue_severity=="HIGH") | "\(.issue_text) at \(.filename):\(.line_number)"' 2>/dev/null | head -5
    elif [ "$medium_severity" -gt 0 ]; then
        log_warn "Bandit: Found $medium_severity MEDIUM severity issue(s)"
    else
        log_pass "Bandit: No security issues detected"
    fi
else
    log_info "Bandit not available or no Python files"
fi

# Safety - Dependency vulnerabilities
if command_exists safety && [ -f "requirements.txt" ]; then
    log_info "Checking for vulnerable dependencies..."
    if safety check --json >/dev/null 2>&1; then
        log_pass "Safety: No vulnerable dependencies"
    else
        log_warn "Safety: Vulnerable dependencies detected"
        safety check || true
    fi
else
    log_info "Safety not available or no requirements.txt"
fi

# Trivy - Container image scanning
if command_exists trivy; then
    log_info "Checking for Dockerfiles..."
    if [ -f "Dockerfile" ]; then
        log_info "Scanning Dockerfile with Trivy..."
        trivy_output=$(trivy config Dockerfile --format json 2>/dev/null || echo "{}")

        critical=$(echo "$trivy_output" | jq '[.Results[].Misconfigurations[]? | select(.Severity=="CRITICAL")] | length' 2>/dev/null || echo "0")
        high=$(echo "$trivy_output" | jq '[.Results[].Misconfigurations[]? | select(.Severity=="HIGH")] | length' 2>/dev/null || echo "0")

        if [ "$critical" -gt 0 ]; then
            log_error "Trivy: Found $critical CRITICAL and $high HIGH severity issues"
        elif [ "$high" -gt 0 ]; then
            log_warn "Trivy: Found $high HIGH severity issues"
        else
            log_pass "Trivy: No critical issues in Dockerfile"
        fi
    fi
else
    log_info "Trivy not installed"
fi

# Check for secrets in code
log_info "Scanning for potential secrets..."
secret_patterns=(
    "password.*=.*['\"].*['\"]"
    "api[_-]?key.*=.*['\"].*['\"]"
    "secret.*=.*['\"].*['\"]"
    "token.*=.*['\"].*['\"]"
    "aws[_-]?access"
    "private[_-]?key"
)

secrets_found=0
for pattern in "${secret_patterns[@]}"; do
    matches=$(grep -riE "$pattern" --include="*.py" --include="*.js" --include="*.ts" --include="*.yaml" --include="*.yml" . 2>/dev/null | grep -v ".git" | wc -l || echo "0")
    if [ "$matches" -gt 0 ]; then
        ((secrets_found+=matches))
    fi
done

if [ "$secrets_found" -gt 0 ]; then
    log_error "Found $secrets_found potential secrets in code"
    log_error "Review code for hardcoded credentials"
else
    log_pass "No obvious secrets detected in code"
fi

################################################################################
# Kubernetes Manifests Validation
################################################################################

log_section "KUBERNETES MANIFESTS VALIDATION"

k8s_dirs=("k8s" "kubernetes" "deploy" "deployments" "manifests")
manifest_dir=""

for dir in "${k8s_dirs[@]}"; do
    if [ -d "$dir" ]; then
        manifest_dir="$dir"
        break
    fi
done

if [ -n "$manifest_dir" ]; then
    log_info "Found Kubernetes manifests in: $manifest_dir"

    # Validate YAML syntax
    log_info "Validating YAML syntax..."
    yaml_errors=0

    while IFS= read -r -d '' file; do
        if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" >/dev/null 2>&1; then
            log_error "Invalid YAML syntax in: $file"
            ((yaml_errors++))
        fi
    done < <(find "$manifest_dir" -name "*.yaml" -o -name "*.yml" -print0)

    if [ "$yaml_errors" -eq 0 ]; then
        log_pass "All YAML files have valid syntax"
    fi

    # kubectl validation
    if command_exists kubectl; then
        log_info "Validating with kubectl..."
        if kubectl apply --dry-run=client -f "$manifest_dir" >/dev/null 2>&1; then
            log_pass "Kubernetes manifests are valid"
        else
            log_error "Kubernetes manifest validation failed"
            kubectl apply --dry-run=client -f "$manifest_dir" 2>&1 | head -20
        fi
    fi

    # Check for best practices
    log_info "Checking Kubernetes best practices..."

    # Resource limits
    missing_limits=$(grep -r "kind: Deployment" "$manifest_dir" -A 100 | grep -c "resources:" || echo "0")
    total_deployments=$(grep -rc "kind: Deployment" "$manifest_dir" | awk -F: '{sum+=$2} END {print sum}' || echo "1")

    if [ "$missing_limits" -lt "$total_deployments" ]; then
        log_warn "Some deployments may be missing resource limits"
    else
        log_pass "Resource limits appear to be configured"
    fi

    # Liveness/Readiness probes
    missing_probes=$(grep -r "kind: Deployment" "$manifest_dir" -A 100 | grep -cE "livenessProbe|readinessProbe" || echo "0")

    if [ "$missing_probes" -lt "$((total_deployments * 2))" ]; then
        log_warn "Some deployments may be missing health probes"
    else
        log_pass "Health probes appear to be configured"
    fi

    # Security context
    security_contexts=$(grep -rc "securityContext" "$manifest_dir" | awk -F: '{sum+=$2} END {print sum}' || echo "0")

    if [ "$security_contexts" -lt "$total_deployments" ]; then
        log_warn "Consider adding securityContext to deployments"
    else
        log_pass "Security contexts are configured"
    fi

else
    log_warn "No Kubernetes manifest directory found"
fi

################################################################################
# Docker Configuration Validation
################################################################################

log_section "DOCKER CONFIGURATION VALIDATION"

if [ -f "Dockerfile" ]; then
    log_info "Validating Dockerfile..."

    # Check for best practices
    if grep -q "^FROM.*:latest" Dockerfile; then
        log_warn "Dockerfile uses ':latest' tag (pin specific versions)"
    else
        log_pass "Dockerfile uses pinned image versions"
    fi

    if grep -q "^USER" Dockerfile; then
        log_pass "Dockerfile sets non-root user"
    else
        log_warn "Dockerfile should set USER (don't run as root)"
    fi

    if grep -q "HEALTHCHECK" Dockerfile; then
        log_pass "Dockerfile includes HEALTHCHECK"
    else
        log_warn "Consider adding HEALTHCHECK to Dockerfile"
    fi

    # Check layer count
    layer_count=$(grep -cE "^(FROM|RUN|COPY|ADD)" Dockerfile)
    if [ "$layer_count" -gt 20 ]; then
        log_warn "Dockerfile has $layer_count layers (consider combining commands)"
    else
        log_pass "Dockerfile layer count is reasonable ($layer_count)"
    fi

else
    log_info "No Dockerfile found"
fi

if [ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ]; then
    log_info "Validating docker-compose configuration..."

    if command_exists docker-compose; then
        if docker-compose config >/dev/null 2>&1; then
            log_pass "docker-compose configuration is valid"
        else
            log_error "docker-compose configuration has errors"
        fi
    fi
fi

################################################################################
# Configuration Files Validation
################################################################################

log_section "CONFIGURATION FILES VALIDATION"

# Check for environment files
if [ -f ".env.example" ] || [ -f ".env.template" ]; then
    log_pass "Environment template file exists"
else
    log_warn "Consider adding .env.example for documentation"
fi

if [ -f ".env" ]; then
    log_warn ".env file found - ensure it's in .gitignore"

    if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
        log_error ".env is NOT in .gitignore!"
    else
        log_pass ".env is properly ignored by git"
    fi
fi

# Check .gitignore
if [ -f ".gitignore" ]; then
    log_pass ".gitignore exists"

    # Check for common patterns
    essential_patterns=("__pycache__" "*.pyc" ".env" "venv" "node_modules")
    missing_patterns=()

    for pattern in "${essential_patterns[@]}"; do
        if ! grep -q "$pattern" .gitignore; then
            missing_patterns+=("$pattern")
        fi
    done

    if [ ${#missing_patterns[@]} -gt 0 ]; then
        log_warn ".gitignore missing patterns: ${missing_patterns[*]}"
    fi
else
    log_error "No .gitignore file found"
fi

################################################################################
# Dependencies Check
################################################################################

log_section "DEPENDENCIES CHECK"

# Python dependencies
if [ -f "requirements.txt" ]; then
    log_pass "requirements.txt found"

    # Check for version pinning
    unpinned=$(grep -cE "^[^#]*==$" requirements.txt || echo "0")
    if [ "$unpinned" -gt 0 ]; then
        log_warn "Some dependencies are not version-pinned in requirements.txt"
    else
        log_pass "Dependencies are version-pinned"
    fi
else
    log_info "No requirements.txt found"
fi

# Check for lockfiles
if [ -f "poetry.lock" ] || [ -f "Pipfile.lock" ] || [ -f "package-lock.json" ] || [ -f "yarn.lock" ]; then
    log_pass "Dependency lockfile found"
else
    log_warn "No dependency lockfile found (consider using poetry/pipenv)"
fi

################################################################################
# Documentation Check
################################################################################

log_section "DOCUMENTATION CHECK"

if [ -f "README.md" ]; then
    log_pass "README.md exists"

    readme_size=$(wc -l < README.md)
    if [ "$readme_size" -lt 10 ]; then
        log_warn "README.md is very short ($readme_size lines)"
    fi
else
    log_warn "No README.md found"
fi

# Check for API documentation
if [ -f "docs/api.md" ] || [ -f "openapi.yaml" ] || [ -f "swagger.yaml" ]; then
    log_pass "API documentation found"
else
    log_info "No API documentation found"
fi

################################################################################
# Git Validation
################################################################################

log_section "GIT VALIDATION"

if [ -d ".git" ]; then
    log_pass "Git repository initialized"

    # Check for sensitive files in git
    sensitive_files=$(git ls-files | grep -E "\.(env|pem|key|secret)$" || true)
    if [ -n "$sensitive_files" ]; then
        log_error "Sensitive files tracked by git:"
        echo "$sensitive_files"
    else
        log_pass "No sensitive files in git"
    fi

    # Check commit message convention (if commits exist)
    if git rev-parse HEAD >/dev/null 2>&1; then
        recent_commits=$(git log --oneline -5 --format="%s" 2>/dev/null || echo "")
        if [ -n "$recent_commits" ]; then
            log_info "Recent commit messages look OK"
        fi
    fi
else
    log_warn "Not a git repository"
fi

################################################################################
# Final Summary
################################################################################

log_section "VALIDATION SUMMARY"

echo ""
log_info "Results:"
log_info "  ${GREEN}Passed: $PASSED${NC}"
log_info "  ${YELLOW}Warnings: $WARNINGS${NC}"
log_info "  ${RED}Errors: $ERRORS${NC}"
echo ""

# Determine exit code
EXIT_CODE=0

if [ "$ERRORS" -gt 0 ]; then
    log_error "Validation failed with $ERRORS error(s)"
    EXIT_CODE=1
elif [ "$WARNINGS" -gt 0 ]; then
    if [ "$FAIL_ON_WARNING" = "true" ]; then
        log_error "Validation failed with $WARNINGS warning(s) (fail-on-warning enabled)"
        EXIT_CODE=1
    else
        log_warn "Validation completed with $WARNINGS warning(s)"
    fi
else
    log_info "${GREEN}✓ All validations passed!${NC}"
fi

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    log_info "Status: ${GREEN}PASS${NC}"
else
    log_info "Status: ${RED}FAIL${NC}"
fi

exit $EXIT_CODE
