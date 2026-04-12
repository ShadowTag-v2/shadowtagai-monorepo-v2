#!/bin/bash
# Skill Activation Hook - UserPromptSubmit
# Analyzes prompt and context to auto-inject skill reminders

set -euo pipefail

# Read configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$(dirname "$SCRIPT_DIR")"
RULES_FILE="$CLAUDE_DIR/skill-rules.json"
PROMPT_FILE="${1:-/dev/stdin}"

#!/bin/bash
# .claude/hooks/skill-activation-prompt.sh
# Pre-prompt hook that analyzes user input and injects relevant skill reminders + SOP frameworks

PROMPT=$(cat "$PROMPT_FILE")
SKILL_RULES_FILE=".claude/skill-rules.json"
SKILLS_DIR=".claude/skills"
SOP_TEMPLATE=".claude/docs/unified-sop-template.md"

log_activation() {
    mkdir -p "$(dirname ".claude/logs/skill-activation.log")"
    echo "[$(date +%Y-%m-%dT%H:%M:%S)] $1" >> .claude/logs/skill-activation.log
}

# Function to detect SOP framework needed based on prompt type
detect_sop_framework() {
    local prompt="$1"
    local framework=""

    # Mission planning indicators → R-I-S-E
    if echo "$prompt" | grep -iE "plan|design|architect|strategy|roadmap|how.*should" > /dev/null; then
        framework="R-I-S-E"
        log_activation "SOP Framework: R-I-S-E (mission planning detected)"
    fi

    # Task execution indicators → T-A-G
    if echo "$prompt" | grep -iE "implement|build|create|develop|execute|fix|audit" > /dev/null; then
        framework="${framework} T-A-G"
        log_activation "SOP Framework: T-A-G (task execution detected)"
    fi

    # Problem analysis indicators → B-A-B + Is/Is Not
    if echo "$prompt" | grep -iE "problem|issue|bug|error|why.*fail|debug|troubleshoot" > /dev/null; then
        framework="${framework} B-A-B"
        log_activation "SOP Framework: B-A-B (problem analysis detected)"
    fi

    # Stakeholder communication indicators → C-A-R-E
    if echo "$prompt" | grep -iE "explain|document|report|summary|stakeholder|communicate" > /dev/null; then
        framework="${framework} C-A-R-E"
        log_activation "SOP Framework: C-A-R-E (communication detected)"
    fi

    # Review/improvement indicators → R-T-F + AAR
    if echo "$prompt" | grep -iE "review|improve|optimize|lessons.*learn|retrospect|after.*action" > /dev/null; then
        framework="${framework} R-T-F"
        log_activation "SOP Framework: R-T-F (improvement detected)"
    fi

    echo "$framework"
}

# Function to check if prompt matches any skill activation pattern
check_skill_activation() {
    local prompt="$1"
    local activated_skills=""

    # Read activation rules from skill-rules.json
    if [ -f "$SKILL_RULES_FILE" ]; then
        # Check for FastAPI/backend patterns
        if echo "$prompt" | grep -iE "fastapi|endpoint|route|api|pydantic|database" > /dev/null; then
            activated_skills="${activated_skills}backend-dev-guidelines "
            log_activation "Triggered: backend-dev-guidelines (pattern: fastapi/api)"
        fi

        # Check for Solidity/blockchain patterns
        if echo "$prompt" | grep -iE "solidity|smart contract|erc-|blockchain|web3|hardhat" > /dev/null; then
            activated_skills="${activated_skills}blockchain-dev-guidelines "
            log_activation "Triggered: blockchain-dev-guidelines (pattern: solidity/blockchain)"
        fi

        # Check for agent/orchestration patterns (auto-loads SOP)
        if echo "$prompt" | grep -iE "agent|swarm|opord|orchestrat|flying.*monk|shift|consensus" > /dev/null; then
            activated_skills="${activated_skills}agent-orchestration "
            log_activation "Triggered: agent-orchestration (pattern: agent/swarm) + Unified SOP"
        fi
    fi

    echo "$activated_skills"
}

# Get activated skills and SOP frameworks
ACTIVATED_SKILLS=$(check_skill_activation "$PROMPT")
SOP_FRAMEWORKS=$(detect_sop_framework "$PROMPT")

# If skills or frameworks are activated, inject them into context
if [ -n "$ACTIVATED_SKILLS" ] || [ -n "$SOP_FRAMEWORKS" ]; then
    echo "🎯 SKILL ACTIVATION CHECK"
    echo "========================"

    # Inject skills
    for skill in $ACTIVATED_SKILLS; do
        skill_file="$SKILLS_DIR/$skill/SKILL.md"
        if [ -f "$skill_file" ]; then
            echo "📋 Skill: $skill"
            echo "   Location: $skill_file"
            log_activation "Activated skill: $skill"
        fi
    done

    # Inject SOP frameworks
    if [ -n "$SOP_FRAMEWORKS" ]; then
        echo ""
        echo "📐 SOP Frameworks: $SOP_FRAMEWORKS"
        echo "   Template: $SOP_TEMPLATE"
        log_activation "SOP Frameworks activated: $SOP_FRAMEWORKS"

        # Provide quick reference based on framework
        for framework in $SOP_FRAMEWORKS; do
            case $framework in
                "R-I-S-E")
                    echo "   → R-I-S-E: Define Role, Input, Steps (TLP), Expectation"
                    ;;
                "T-A-G")
                    echo "   → T-A-G: Task definition, Action execution, Goal validation"
                    ;;
                "B-A-B")
                    echo "   → B-A-B: Before state, After state, Bridge (action plan)"
                    ;;
                "C-A-R-E")
                    echo "   → C-A-R-E: Context, Action, Result, Example"
                    ;;
                "R-T-F")
                    echo "   → R-T-F: Role (AAR facilitator), Task (extract lessons), Format (OPORD)"
                    ;;
            esac
        done
    fi

    echo "========================"
    echo ""
fi

# Check for open files that might indicate context
if [ -n "$CLAUDE_OPEN_FILES" ]; then
    log_activation "Open files: $CLAUDE_OPEN_FILES"
fi

# Army Leadership reminder for agent tasks
if echo "$ACTIVATED_SKILLS" | grep -q "agent-orchestration"; then
    echo "⚔️  ARMY LEADERSHIP PRINCIPLES ACTIVE"
    echo "   → Know yourself and seek self-improvement"
    echo "   → Make sound and timely decisions"
    echo "   → Accomplish every mission"
    echo ""
fi

# Output original prompt
echo "$PROMPT"
