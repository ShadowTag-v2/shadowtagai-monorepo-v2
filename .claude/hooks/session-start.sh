#!/bin/bash
# ShadowTag-v2JR Session Start Hook
# SOP-A: Upload Triage - Automated checks on session start
# Purpose: 2× speed, −90% errors

set -e

echo "🚀 ShadowTag-v2JR Development Environment"
echo "=================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Track overall status
CRITICAL_ISSUES=0
WARNINGS=0

# Function to print status
print_status() {
    local status=$1
    local message=$2

    if [ "$status" == "ok" ]; then
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" == "warn" ]; then
        echo -e "${YELLOW}⚠${NC} $message"
        WARNINGS=$((WARNINGS + 1))
    elif [ "$status" == "error" ]; then
        echo -e "${RED}✗${NC} $message"
        CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
    fi
}

# Check if Python is installed
echo "📋 Environment Checks"
echo "-------------------"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_status "ok" "Python $PYTHON_VERSION"
else
    print_status "error" "Python 3 not found"
fi

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    print_status "warn" "Not in virtual environment (recommended: python -m venv venv)"
else
    print_status "ok" "Virtual environment: $VIRTUAL_ENV"
fi

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    print_status "ok" "requirements.txt found"

    # Check if dependencies are installed (if venv active)
    if [ -n "$VIRTUAL_ENV" ]; then
        # Try to import key packages
        python3 -c "import fastapi" 2>/dev/null && \
            print_status "ok" "FastAPI installed" || \
            print_status "warn" "FastAPI not installed (run: pip install -r requirements.txt)"

        python3 -c "import pytest" 2>/dev/null && \
            print_status "ok" "pytest installed" || \
            print_status "warn" "pytest not installed"
    fi
else
    print_status "warn" "requirements.txt not found (create one for dependency management)"
fi

echo ""
echo "🔒 Security Checks"
echo "-----------------"

# Check for .env file (should exist but not be in git)
if [ -f ".env" ]; then
    print_status "ok" ".env file exists"

    # Check if .env is in .gitignore
    if grep -q "^\.env$" .gitignore 2>/dev/null; then
        print_status "ok" ".env excluded from git"
    else
        print_status "error" ".env NOT in .gitignore (secrets may be exposed!)"
    fi
else
    print_status "warn" ".env file not found (copy .env.example if available)"
fi

# Check if .env.example exists
if [ -f ".env.example" ]; then
    print_status "ok" ".env.example exists (template available)"
fi

# Check for common secret files
for secret_file in "credentials.json" "service-account.json" ".secret" "secrets.yaml"; do
    if [ -f "$secret_file" ]; then
        if grep -q "$secret_file" .gitignore 2>/dev/null; then
            print_status "ok" "$secret_file excluded from git"
        else
            print_status "error" "$secret_file found but NOT in .gitignore!"
        fi
    fi
done

# Run security scan if bandit is available
if command -v bandit &> /dev/null; then
    if [ -d "app" ]; then
        echo ""
        echo "Running security scan..."
        BANDIT_OUTPUT=$(bandit -r app -f txt 2>&1 || true)

        # Check for high or medium severity issues
        if echo "$BANDIT_OUTPUT" | grep -q "Severity: High"; then
            print_status "error" "High severity security issues found (run: bandit -r app)"
        elif echo "$BANDIT_OUTPUT" | grep -q "Severity: Medium"; then
            print_status "warn" "Medium severity security issues found (run: bandit -r app)"
        else
            print_status "ok" "No critical security issues"
        fi
    fi
else
    print_status "warn" "bandit not installed (recommended: pip install bandit)"
fi

# Check dependency vulnerabilities if safety is available
if command -v safety &> /dev/null; then
    echo ""
    echo "Checking dependency vulnerabilities..."
    SAFETY_OUTPUT=$(safety check --json 2>&1 || true)

    if echo "$SAFETY_OUTPUT" | grep -q '"vulnerabilities":'; then
        VULN_COUNT=$(echo "$SAFETY_OUTPUT" | grep -o '"vulnerabilities": [0-9]*' | grep -o '[0-9]*')
        if [ "$VULN_COUNT" -gt 0 ]; then
            print_status "error" "$VULN_COUNT vulnerable dependencies found (run: safety check)"
        else
            print_status "ok" "No known vulnerabilities in dependencies"
        fi
    fi
else
    print_status "warn" "safety not installed (recommended: pip install safety)"
fi

echo ""
echo "📊 Code Quality"
echo "--------------"

# Check if mypy is available
if command -v mypy &> /dev/null; then
    if [ -d "app" ]; then
        print_status "ok" "mypy available for type checking"
    fi
else
    print_status "warn" "mypy not installed (recommended: pip install mypy)"
fi

# Check if ruff is available
if command -v ruff &> /dev/null; then
    if [ -d "app" ]; then
        print_status "ok" "ruff available for linting"
    fi
else
    print_status "warn" "ruff not installed (recommended: pip install ruff)"
fi

# Check for tests directory
if [ -d "tests" ]; then
    TEST_COUNT=$(find tests -name "test_*.py" -o -name "*_test.py" | wc -l)
    print_status "ok" "Test directory exists ($TEST_COUNT test files)"
else
    print_status "warn" "tests/ directory not found (TDD requires tests!)"
fi

echo ""
echo "📚 Documentation"
echo "---------------"

# Check for README
if [ -f "README.md" ]; then
    print_status "ok" "README.md exists"
else
    print_status "warn" "README.md not found"
fi

# Check for API documentation
if [ -f "docs/api.md" ] || [ -f "API.md" ]; then
    print_status "ok" "API documentation exists"
fi

# Check for custom skills
if [ -d ".claude/skills" ]; then
    SKILL_COUNT=$(find .claude/skills -name "SKILL.md" | wc -l)
    print_status "ok" "$SKILL_COUNT custom skills available"
fi

echo ""
echo "🔧 Git Status"
echo "------------"

# Check if in git repo
if git rev-parse --git-dir > /dev/null 2>&1; then
    print_status "ok" "Git repository"

    # Check current branch
    BRANCH=$(git branch --show-current)
    if [ "$BRANCH" == "main" ] || [ "$BRANCH" == "master" ]; then
        print_status "warn" "On $BRANCH branch (consider working on feature branch)"
    else
        print_status "ok" "On branch: $BRANCH"
    fi

    # Check for uncommitted changes
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        print_status "ok" "Working directory clean"
    else
        print_status "warn" "Uncommitted changes present"
    fi

    # Check for untracked files that might be secrets
    UNTRACKED=$(git ls-files --others --exclude-standard)
    if echo "$UNTRACKED" | grep -qE "\.(env|key|pem|p12|pfx|secret)$"; then
        print_status "error" "Untracked files with secret-like extensions found!"
    fi
else
    print_status "warn" "Not a git repository"
fi

echo ""
echo "=================================="

# Final summary
if [ $CRITICAL_ISSUES -gt 0 ]; then
    echo -e "${RED}⚠ CRITICAL ISSUES: $CRITICAL_ISSUES${NC}"
    echo -e "${RED}▸ Address critical issues before proceeding${NC}"
    echo ""
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ Warnings: $WARNINGS${NC}"
    echo ""
fi

if [ $CRITICAL_ISSUES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready to code.${NC}"
    echo ""
fi

# Display SOPs reminder
echo "📖 Quick Reference:"
echo "  • Development Workflow: .claude/DEVELOPMENT_WORKFLOW.md"
echo "  • Skills: .claude/skills/"
echo "  • SOP-A (Upload Triage): Automated checks (this)"
echo "  • SOP-B (Change & Release): Deployment procedures"
echo "  • SOP-C (Decision Protocol): Risk assessment"
echo "  • SOP-D (Code Review): Review checklist"
echo ""

# Display doctrine reminder
echo "🎯 Operating Doctrine:"
echo "  • Security Absolute: 100% non-negotiable"
echo "  • Revenue Aware: Every feature evaluated"
echo "  • Test-Driven: Tests first, implement second"
echo "  • Boy Scout Rule: Leave cleaner than found"
echo "  • Bootstrap Discipline: ROI ≥3×, LTV:CAC ≥4:1"
echo ""

echo "Happy coding! 🚀"
