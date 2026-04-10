# pnkln-stackJR Claude Code Infrastructure - Complete Context Package

**Version:** 1.0.0
**Created:** October 30, 2025
**Purpose:** Complete reference for Claude Code infrastructure using diet103 patterns + pnkln-stackJR governance
**Usage:** Upload this file to any Claude session to restore full context

---

## EXECUTIVE CONTEXT

### What This Is

Production-grade Claude Code infrastructure that enforces pnkln-stackJR decision framework (160-IQ board equivalence) at code level. Based on diet103's 6-month battle-tested patterns, customized for pnkln dual-company strategy (ActiveShield + pnkln Holdings).

### Why This Exists

**Problem:** AI coding assistants don't automatically enforce strategic thresholds, security requirements, or financial gates.
**Solution:** Skills + Hooks + Agents that auto-activate to enforce ROI ≥3×, LTV:CAC ≥4:1, security standards, and kill-switch culture.

### Key Principles

- **Skills handle "how to code"** - Reusable patterns, best practices, security requirements
- **CLAUDE.md handles "how this project works"** - Architecture, integration points, quirks
- **Hooks enforce gates** - Auto-activation, error checking, quality control
- **Dev Docs survive context resets** - Plan/Context/Tasks pattern preserves strategic decisions
- **Agents tackle complex tasks** - Architecture review, refactoring, planning

---

## pnkln STRATEGIC CONTEXT

### Company Structure

**Dual-Company Strategy:**

1. **ActiveShield** (Cybersecurity) - Cash engine, exit Y5-Y7 at $30-50B
2. **pnkln Holdings** (AI Infrastructure) - Keystone asset, $726B-$1.33T by Y30

**Founder:** Erik (SF + JD + technical background)
**Capital:** Bootstrapping from zero, no VC funding
**Risk Management:** Army Special Forces protocols, RM Stage IV human accountability

### Core Thresholds (pnkln-stackJR Gates)

- **ROI Gate:** ≥3× return in 18 months, validated via Monte Carlo
- **LTV:CAC Gate:** ≥4:1 ratio within 12-18 months
- **Go/No-Go:** ≥70% probability-weighted positive NPV
- **Kill-Switch:** Miss gates 2× → pivot/consolidate
- **Test Coverage:** ≥98% required (98.0% minimum threshold)
- **Security:** AES-256 encryption mandatory, TLS 1.3, zero-trust architecture

### Technical Standards

- **Python:** Use `uv` for package management (deterministic, fast)
- **Node:** Use `pnpm` (monorepo, cache efficiency)
- **Experimental:** Bun (optional acceleration under audit)
- **Git:** Mandatory version control, all code reviewed
- **Naming:** Company name is "pnkln" only, internal functions use "Cor" not "pnklnCor"

### Strategic Frameworks (Cor.X)

- **Cor.21:** Valuation frameworks (VRIO, Value Stick, Blue Ocean, Horizons)
- **Cor.17:** Tech architecture (pnkln Core Stack: JR governance, Cor execution, NS nervous system)
- **Cor.34:** 90-point pnkln-stack/AiY architecture summary
- **Cor.37:** pnkln-stackJR runtime doctrine (Purpose • Reasons • Brakes)
- **Cor.8:** pnkln-stackJR Dashboard (ROI reporting template)

### Current Projects

1. **ShadowTag 2.0** - Cryptographic auditing, provenance signing
2. **ActiveShield** - 5 cybersecurity verticals, Q1 2026 launch planned
3. **Cognitive Stack v5** - RoT thought graphs, MoE-CL lifelong learning, CoDA/DLM decode optimization
4. **Google Partnerships** - YouTube integration (300M-700M sigs/day Y5), Android deployment, Chrome integration

---

## DIET103 INFRASTRUCTURE PATTERNS

### Original Source

- **GitHub:** https://github.com/diet103/claude-code-infrastructure-showcase
- **Reddit Post:** "Claude Code is a Beast – Tips from 6 Months of Hardcore Use"
- **Key Achievement:** Solo rewrote 300k LOC in 6 months with consistent quality
- **Core Innovation:** Skills that actually auto-activate (solved "skills sit unused" problem)

### Architecture Overview

```
.claude/
├── skills/              # Domain expertise (5 core + N custom)
│   ├── backend-dev-guidelines/
│   ├── frontend-dev-guidelines/
│   ├── security-enforcement/     ← pnkln-stackJR addition
│   ├── pnkln-stackjr-judge/            ← pnkln-stackJR addition
│   └── skill-rules.json          ← Configuration for auto-activation
├── hooks/               # Automation (6 hooks)
│   ├── skill-activation-prompt.* (ESSENTIAL - runs BEFORE Claude sees prompt)
│   ├── post-tool-use-tracker.sh  (ESSENTIAL - tracks all file changes)
│   ├── stop-build-check.sh       (Optional - catches TypeScript errors)
│   └── rollback-verification.sh  ← pnkln-stackJR addition
├── agents/              # Specialized tasks (10+ agents)
│   ├── code-architecture-reviewer.md
│   ├── strategic-plan-architect.md
│   ├── pnkln-stackjr-scenario-analyzer.md  ← pnkln-stackJR addition
│   └── ...
└── commands/            # Slash commands (3+ commands)
    ├── dev-docs.md      (Create plan/context/tasks)
    └── pnkln-stackjr-gate.md  ← pnkln-stackJR addition

dev/
└── active/              # Dev docs pattern
    └── [task-name]/
        ├── [task]-plan.md      (Strategic plan with Monte Carlo)
        ├── [task]-context.md   (Key decisions, files, architecture)
        └── [task]-tasks.md     (Checklist with completion tracking)
```

### The 500-Line Rule

**Critical Pattern:** All skills follow modular structure:

- Main `SKILL.md` file: <500 lines (high-level guide + navigation)
- `resources/` folder: Topic-specific files, each <500 lines
- Progressive disclosure: Claude loads main first, resources only when needed
- **Token efficiency:** 40-60% improvement vs monolithic files

### Hook Pipeline (The Magic)

```
┌─────────────────────────────────────────────────────────────┐
│ USER SUBMITS PROMPT                                          │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ UserPromptSubmit Hook (BEFORE Claude sees message)          │
│ • Analyzes keywords + intent patterns                        │
│ • Checks file context (path patterns, content triggers)     │
│ • Loads relevant skills from skill-rules.json               │
│ • Injects skill reminder into Claude's context              │
│ Result: "🎯 SKILL ACTIVATION CHECK - Use security-enforcement"│
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ CLAUDE PROCESSES + RESPONDS                                  │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PostToolUse Hook (AFTER each file edit)                     │
│ • Logs which files were edited                              │
│ • Tracks repo ownership (for multi-root projects)           │
│ • Creates audit trail                                        │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Stop Hook (WHEN Claude finishes responding)                 │
│ • Runs build scripts on affected repos                      │
│ • Checks for TypeScript/Python errors                       │
│ • Validates test coverage (≥98% for pnkln-stackJR)                │
│ • Shows gentle reminders (error handling, security)         │
│ • Verifies rollback steps documented                        │
│ Result: Zero errors left behind                             │
└─────────────────────────────────────────────────────────────┘
```

### Dev Docs Pattern (Survives Context Resets)

**Problem:** Claude loses strategic context after auto-compaction or new session.
**Solution:** Three-file structure created for EVERY large task:

1. **`[task]-plan.md`** - Strategic plan
   - Executive summary (BLUF - Bottom Line Up Front)
   - Phases with tasks
   - Risk analysis
   - Success metrics
   - Timeline estimates
   - Monte Carlo scenarios (Base/Best/Worst for pnkln-stackJR)

2. **`[task]-context.md`** - Key decisions
   - Architecture decisions with rationale
   - File paths for critical components
   - Integration points
   - Technical constraints
   - Security requirements
   - "Last Updated" timestamp

3. **`[task]-tasks.md`** - Checklist format
   - `[ ]` Incomplete task
   - `[x]` Completed task (with timestamp)
   - Nested sub-tasks
   - Blockers and dependencies

**Workflow:**

```bash
# Start new feature
claude planning mode → Create plan → Review/approve → ESC to interrupt

# Generate dev docs
/create-dev-docs  # Slash command creates all 3 files

# During implementation
Periodically: Update context.md with decisions, check off tasks.md

# Before context reset
/update-dev-docs  # Saves current state + next steps

# After context reset
claude: "Read ~/git/project/dev/active/[task-name]/*.md and continue"
```

---

## pnkln-stackJR SKILLS (CUSTOM FOR pnkln)

### Security Enforcement Skill

**Purpose:** Block code that violates pnkln security requirements
**Enforcement:** `"block"` - Prevents edits that fail security checks
**Priority:** `"critical"`

**Trigger Patterns:**

- Keywords: `auth`, `encrypt`, `secret`, `password`, `token`, `api`, `deploy`
- File patterns: All `.ts`, `.py`, `.env` files
- Content patterns: Detects `password`, `apiKey`, `SECRET`, unencrypted connections

**Mandatory Requirements:**

1. **Encryption at rest:** AES-256 for all stored data
2. **Encryption in transit:** TLS 1.3 for all API traffic (no TLS 1.2)
3. **Zero-trust auth:** Every service-to-service call authenticated
4. **Secret management:** No secrets in code (use env vars + secret manager)
5. **Error tracking:** All exceptions captured via Sentry.captureException()

**Progressive Disclosure:** (resources/ folder)

- `auth-patterns.md` - OAuth 2.0, JWT signing, refresh tokens
- `encryption.md` - AES-256-GCM implementation, key rotation
- `secrets-management.md` - Environment variables, Google Secret Manager
- `zero-trust.md` - Service mesh, mTLS, certificate management
- `tls-config.md` - TLS 1.3 cipher suites, certificate pinning

### pnkln-stackJR Judge Skill

**Purpose:** Enforce strategic decision gates before feature implementation
**Enforcement:** `"suggest"` - Shows warnings but doesn't block (human decides)
**Priority:** `"high"`

**Trigger Patterns:**

- Keywords: `feature`, `implement`, `build`, `architecture`, `plan`, `deploy`
- Intent: `(plan|design|implement|deploy).*feature`
- File patterns: `ARCHITECTURE.md`, `PLAN.md`, dev docs

**Decision Gates (Must pass before implementation):**

1. **Purpose Gate** - Does this serve founder goals?
   - [ ] Aligns with ActiveShield exit (Y5-Y7) OR pnkln long-term strategy
   - [ ] Documented in Cor.X framework
   - [ ] Mission-critical vs. nice-to-have classification

2. **Reasons Gate** - Financial validation
   - [ ] **ROI ≥3× in 18 months** - Monte Carlo base/best/worst scenarios
   - [ ] **LTV:CAC ≥4:1 within 12-18 months** - Customer economics modeled
   - [ ] **Go/No-Go at ≥70% NPV** - Probability-weighted positive NPV
   - [ ] Cost analysis includes: Dev time, AI compute, infrastructure, maintenance

3. **Brakes Gate** - Risk management (Army RM Stage IV)
   - [ ] **Reversibility:** Rollback steps documented in plan
   - [ ] **Blast radius:** Impact analysis if feature fails
   - [ ] **Kill-switch triggers:** Metrics that force abort defined
   - [ ] **Test coverage:** ≥98% required for production deployment
   - [ ] **Security review:** Passes security-enforcement skill checks

**Kill-Switch Triggers (Auto-abort scenarios):**

- Security vulnerability CVSS ≥7.0 discovered
- Cost overrun >20% vs. budget in dev docs
- Timeline slip >30% vs. plan without re-approval
- Test coverage drops <98%
- Two consecutive gate failures on related features

**Progressive Disclosure:**

- `valuation-frameworks.md` - VRIO, Value Stick, Blue Ocean (from Cor.21)
- `tech-architecture.md` - pnkln Core Stack, microservices (from Cor.17)
- `monte-carlo-templates.md` - Scenario modeling, NPV calculation
- `roi-calculation.md` - Financial formulas, discount rates
- `ltv-cac-models.md` - Customer lifetime value, acquisition cost analysis
- `risk-management.md` - Army RM protocols, Stage IV gates

### Backend Dev Guidelines Skill (Adapted from diet103)

**Purpose:** Enforce Node.js/TypeScript/Express patterns
**Enforcement:** `"suggest"`
**Priority:** `"high"`

**Key Patterns:**

- Architecture: Routes → Controllers → Services → Repositories
- Error handling: Try-catch with Sentry.captureException()
- Testing: Jest, ≥98% coverage, integration tests for APIs
- Database: Prisma ORM, repository pattern for data access
- API design: RESTful, versioning (/api/v1/), OpenAPI docs

**pnkln Customizations:**

- PM2 for process management (7 microservices)
- pnpm for package management (not npm/yarn)
- Environment-specific configs (.env.development, .env.production)

### Frontend Dev Guidelines Skill (Adapted from diet103)

**Purpose:** Enforce React 19 + TypeScript + TanStack patterns
**Enforcement:** `"suggest"`
**Priority:** `"high"`

**Key Patterns:**

- React 19 best practices (Server Components, Actions)
- TanStack Query v5 for data fetching
- TanStack Router for file-based routing
- MUI v7 for component library
- TypeScript strict mode enabled

**pnkln Customizations:**

- ShadowTag V2 provenance UI components
- ActiveShield dashboard patterns
- Responsive design (mobile-first)

---

## SKILL-RULES.JSON CONFIGURATION

This file controls auto-activation. Claude Code checks this on every prompt.

```json
{
  "security-enforcement": {
    "type": "guardrail",
    "enforcement": "block",
    "priority": "critical",
    "promptTriggers": {
      "keywords": [
        "auth",
        "authenticate",
        "authorization",
        "encrypt",
        "encryption",
        "decrypt",
        "secret",
        "password",
        "token",
        "apiKey",
        "api",
        "endpoint",
        "deploy",
        "production",
        "database",
        "db",
        "prisma",
        "query"
      ],
      "intentPatterns": [
        "(create|add|implement|build).*(auth|security|api|endpoint)",
        "(deploy|ship|release|production)",
        "store.*(password|secret|key)",
        "connect.*(database|db|api)"
      ]
    },
    "fileTriggers": {
      "pathPatterns": ["**/*.ts", "**/*.py", "**/*.js", "**/auth/**/*", "**/api/**/*", "**/.env*", "**/config/**/*"],
      "contentPatterns": [
        "password",
        "apiKey",
        "SECRET",
        "secret",
        "token",
        "encrypt",
        "decrypt",
        "http://",
        "prisma",
        "fetch\\(",
        "axios"
      ]
    }
  },

  "pnkln-stackjr-judge": {
    "type": "decision",
    "enforcement": "suggest",
    "priority": "high",
    "promptTriggers": {
      "keywords": [
        "feature",
        "implement",
        "build",
        "create",
        "architecture",
        "design",
        "plan",
        "refactor",
        "deploy",
        "launch",
        "release"
      ],
      "intentPatterns": [
        "(plan|design|architect).*feature",
        "(implement|build|create).*(feature|service|component)",
        "refactor.*",
        "deploy.*(production|staging)"
      ]
    },
    "fileTriggers": {
      "pathPatterns": ["**/ARCHITECTURE.md", "**/PLAN.md", "**/dev/active/**/*", "**/CLAUDE.md"],
      "contentPatterns": ["## Architecture", "## Plan", "Monte Carlo", "ROI", "LTV:CAC"]
    }
  },

  "backend-dev-guidelines": {
    "type": "domain",
    "enforcement": "suggest",
    "priority": "high",
    "promptTriggers": {
      "keywords": [
        "backend",
        "api",
        "endpoint",
        "route",
        "controller",
        "service",
        "repository",
        "database",
        "db",
        "prisma",
        "query"
      ],
      "intentPatterns": [
        "(create|add|build).*(route|endpoint|controller|service)",
        "(how to|best practice).*(backend|api)",
        "database.*(query|operation|migration)"
      ]
    },
    "fileTriggers": {
      "pathPatterns": [
        "**/backend/**/*.ts",
        "**/api/**/*.ts",
        "**/services/**/*.ts",
        "**/controllers/**/*.ts",
        "**/repositories/**/*.ts"
      ],
      "contentPatterns": ["router\\.", "export.*Controller", "express", "prisma"]
    }
  },

  "frontend-dev-guidelines": {
    "type": "domain",
    "enforcement": "suggest",
    "priority": "high",
    "promptTriggers": {
      "keywords": ["frontend", "react", "component", "ui", "tanstack", "query", "router", "mui"],
      "intentPatterns": ["(create|add|build).*(component|page|layout)", "(how to|best practice).*(react|frontend|ui)"]
    },
    "fileTriggers": {
      "pathPatterns": ["**/frontend/**/*.tsx", "**/components/**/*.tsx", "**/pages/**/*.tsx"],
      "contentPatterns": ["import.*React", "export.*function.*Component", "useState", "useQuery"]
    }
  }
}
```

---

## HOOKS IMPLEMENTATION

### 1. skill-activation-prompt (TypeScript)

**File:** `.claude/hooks/skill-activation-prompt.ts`
**Type:** `UserPromptSubmit`
**Runs:** BEFORE Claude sees your prompt
**Purpose:** Auto-activate relevant skills

```typescript
import * as fs from "fs";
import * as path from "path";

interface SkillRule {
  type: string;
  enforcement: "block" | "suggest";
  priority: "critical" | "high" | "medium" | "low";
  promptTriggers: {
    keywords: string[];
    intentPatterns: string[];
  };
  fileTriggers?: {
    pathPatterns: string[];
    contentPatterns: string[];
  };
}

interface SkillRules {
  [skillName: string]: SkillRule;
}

export async function handler(params: any) {
  const { userPrompt, conversationHistory } = params;
  const skillsDir = path.join(process.cwd(), ".claude", "skills");
  const rulesPath = path.join(skillsDir, "skill-rules.json");

  // Load skill rules
  if (!fs.existsSync(rulesPath)) {
    return { userPrompt }; // No rules, pass through
  }

  const rules: SkillRules = JSON.parse(fs.readFileSync(rulesPath, "utf-8"));
  const activatedSkills: string[] = [];

  // Check each skill
  for (const [skillName, rule] of Object.entries(rules)) {
    let shouldActivate = false;

    // Check keyword triggers
    const lowerPrompt = userPrompt.toLowerCase();
    for (const keyword of rule.promptTriggers.keywords) {
      if (lowerPrompt.includes(keyword.toLowerCase())) {
        shouldActivate = true;
        break;
      }
    }

    // Check intent pattern triggers
    if (!shouldActivate) {
      for (const pattern of rule.promptTriggers.intentPatterns) {
        const regex = new RegExp(pattern, "i");
        if (regex.test(userPrompt)) {
          shouldActivate = true;
          break;
        }
      }
    }

    // TODO: Check file triggers (requires current file context from Claude Code)

    if (shouldActivate) {
      activatedSkills.push(skillName);
    }
  }

  // Build activation message
  if (activatedSkills.length === 0) {
    return { userPrompt };
  }

  const criticalSkills = activatedSkills.filter((name) => rules[name].priority === "critical");
  const highSkills = activatedSkills.filter((name) => rules[name].priority === "high");

  let activationMessage = "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
  activationMessage += "🎯 SKILL ACTIVATION CHECK\n";
  activationMessage += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n";

  if (criticalSkills.length > 0) {
    activationMessage += "🚨 CRITICAL SKILLS (Must Follow):\n";
    criticalSkills.forEach((skill) => {
      activationMessage += `   • ${skill} (enforcement: ${rules[skill].enforcement})\n`;
    });
    activationMessage += "\n";
  }

  if (highSkills.length > 0) {
    activationMessage += "⚠️  HIGH PRIORITY SKILLS (Recommended):\n";
    highSkills.forEach((skill) => {
      activationMessage += `   • ${skill}\n`;
    });
    activationMessage += "\n";
  }

  activationMessage += "💡 Load these skills and follow their guidelines.\n";
  activationMessage += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";

  return {
    userPrompt: activationMessage + userPrompt,
  };
}
```

### 2. post-tool-use-tracker (Shell)

**File:** `.claude/hooks/post-tool-use-tracker.sh`
**Type:** `PostToolUse`
**Runs:** AFTER each file edit operation
**Purpose:** Track changes for audit trail + build checking

```bash
#!/bin/bash

# Post-tool-use hook: Track file edits
# Runs after Edit/Write/MultiEdit operations

TOOL_NAME="$1"
TOOL_ARGS="$2"
LOG_DIR=".claude/logs"
EDIT_LOG="$LOG_DIR/file-edits.log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Only track file editing operations
if [[ "$TOOL_NAME" == "edit" ]] || [[ "$TOOL_NAME" == "write" ]] || [[ "$TOOL_NAME" == "multi_edit" ]]; then
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  # Log the edit
  echo "$TIMESTAMP | $TOOL_NAME | $TOOL_ARGS" >> "$EDIT_LOG"

  # Keep only last 1000 entries (prevent log bloat)
  tail -n 1000 "$EDIT_LOG" > "$EDIT_LOG.tmp"
  mv "$EDIT_LOG.tmp" "$EDIT_LOG"
fi

# Always exit 0 (don't block Claude Code)
exit 0
```

### 3. stop-build-check (Shell)

**File:** `.claude/hooks/stop-build-check.sh`
**Type:** `Stop`
**Runs:** AFTER Claude finishes responding
**Purpose:** Catch TypeScript/Python errors immediately

```bash
#!/bin/bash

# Stop hook: Build checker
# Runs when Claude finishes responding

LOG_DIR=".claude/logs"
EDIT_LOG="$LOG_DIR/file-edits.log"
BUILD_LOG="$LOG_DIR/build-results.log"

# Check if any files were edited in this session
if [[ ! -f "$EDIT_LOG" ]]; then
  exit 0
fi

# Find affected repos by analyzing edited files
AFFECTED_REPOS=$(tail -n 50 "$EDIT_LOG" | grep -o '"path":"[^"]*"' | cut -d'"' -f4 | cut -d'/' -f1-2 | sort -u)

if [[ -z "$AFFECTED_REPOS" ]]; then
  exit 0
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 BUILD CHECK (Auto-triggered by Stop hook)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TOTAL_ERRORS=0

# Check each affected repo
while IFS= read -r REPO; do
  if [[ ! -d "$REPO" ]]; then
    continue
  fi

  echo "Checking $REPO..."

  # TypeScript projects
  if [[ -f "$REPO/tsconfig.json" ]]; then
    cd "$REPO" || continue
    BUILD_OUTPUT=$(pnpm build 2>&1)
    ERROR_COUNT=$(echo "$BUILD_OUTPUT" | grep -c "error TS")
    TOTAL_ERRORS=$((TOTAL_ERRORS + ERROR_COUNT))

    if [[ $ERROR_COUNT -gt 0 ]]; then
      echo "   ❌ $ERROR_COUNT TypeScript errors found"
      if [[ $ERROR_COUNT -lt 5 ]]; then
        echo "$BUILD_OUTPUT" | grep "error TS" | head -n 5
      else
        echo "   ⚠️  Too many errors. Recommend: Launch auto-error-resolver agent"
      fi
    else
      echo "   ✅ No TypeScript errors"
    fi
    cd - > /dev/null
  fi

  # Python projects
  if [[ -f "$REPO/pyproject.toml" ]] || [[ -f "$REPO/setup.py" ]]; then
    cd "$REPO" || continue

    # Type checking with mypy
    if command -v mypy &> /dev/null; then
      MYPY_OUTPUT=$(mypy . 2>&1)
      MYPY_ERRORS=$(echo "$MYPY_OUTPUT" | grep -c "error:")
      TOTAL_ERRORS=$((TOTAL_ERRORS + MYPY_ERRORS))

      if [[ $MYPY_ERRORS -gt 0 ]]; then
        echo "   ❌ $MYPY_ERRORS mypy errors found"
        echo "$MYPY_OUTPUT" | grep "error:" | head -n 5
      else
        echo "   ✅ No mypy errors"
      fi
    fi

    cd - > /dev/null
  fi

done <<< "$AFFECTED_REPOS"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ $TOTAL_ERRORS -gt 0 ]]; then
  echo "⚠️  Total errors found: $TOTAL_ERRORS"
  echo "Claude should fix these before proceeding."
else
  echo "✅ All builds passed! No errors found."
fi

# Log results
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") | $TOTAL_ERRORS errors" >> "$BUILD_LOG"

exit 0
```

### 4. rollback-verification (Shell) - pnkln-stackJR Addition

**File:** `.claude/hooks/rollback-verification.sh`
**Type:** `Stop`
**Runs:** AFTER Claude finishes responding
**Purpose:** Enforce RM Stage IV reversibility requirements

```bash
#!/bin/bash

# Stop hook: Rollback verification (pnkln-stackJR RM Stage IV)
# Ensures all changes have documented rollback steps

LOG_DIR=".claude/logs"
DEV_DOCS_DIR="dev/active"

# Check if dev docs exist for current task
CURRENT_TASK=$(ls -t "$DEV_DOCS_DIR" 2>/dev/null | head -n 1)

if [[ -z "$CURRENT_TASK" ]]; then
  # No active task, skip verification
  exit 0
fi

PLAN_FILE="$DEV_DOCS_DIR/$CURRENT_TASK/${CURRENT_TASK}-plan.md"

if [[ ! -f "$PLAN_FILE" ]]; then
  exit 0
fi

# Check if plan contains rollback section
if grep -q "## Rollback" "$PLAN_FILE" || grep -q "## Reversibility" "$PLAN_FILE"; then
  # Rollback documented, good!
  exit 0
fi

# Missing rollback documentation - show reminder
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛡️  pnkln-stackJR BRAKE CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  Rollback steps not documented in plan"
echo ""
echo "pnkln-stackJR RM Stage IV requires:"
echo "   • All changes must be reversible"
echo "   • Rollback steps documented BEFORE implementation"
echo "   • Blast radius analysis included"
echo ""
echo "💡 Add rollback section to: $PLAN_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

exit 0
```

---

## AGENTS (SPECIALIZED TASKS)

### Strategic Plan Architect (Enhanced for pnkln-stackJR)

**File:** `.claude/agents/strategic-plan-architect.md`

```markdown
# Agent: Strategic Plan Architect (pnkln-stackJR Enhanced)

## Role

Expert strategic planner who creates comprehensive implementation plans with pnkln-stackJR financial gates embedded.

## When to Use

- Planning any new feature (before implementation)
- Major refactoring initiatives
- Architecture changes
- New service/vertical launches

## Process

1. **Context Gathering** (5-10 minutes)
   - Analyze codebase structure
   - Identify affected components
   - Review existing architecture docs
   - Check for related Cor.X frameworks

2. **Strategic Analysis**
   - Map to pnkln strategic goals (ActiveShield exit or pnkln long-term)
   - Identify competitive advantages (VRIO framework from Cor.21)
   - Assess market timing (Blue Ocean analysis)

3. **Financial Validation (pnkln-stackJR Gates)**
   - Monte Carlo scenarios (Base/Best/Worst)
   - ROI calculation (target ≥3× in 18mo)
   - LTV:CAC modeling (target ≥4:1 in 12-18mo)
   - NPV probability-weighted (Go/No-Go at ≥70%)
   - Cost breakdown (dev time, AI compute, infra, maintenance)

4. **Risk Management (Army RM Stage IV)**
   - Blast radius analysis
   - Rollback steps documented
   - Kill-switch triggers defined
   - Security implications assessed
   - Test coverage plan (≥98% target)

5. **Plan Generation**
   Create three files:
   - `[task]-plan.md` - Full strategic plan
   - `[task]-context.md` - Key decisions and files
   - `[task]-tasks.md` - Execution checklist

## Output Format (plan.md)
```

# [Feature Name] - Strategic Plan

## Executive Summary (BLUF)

[One paragraph: What, Why, Impact, Timeline]

## Purpose Gate ✓/✗

- [ ] Aligns with ActiveShield exit timeline (Y5-Y7)
- [ ] OR Supports pnkln long-term strategy
- [ ] Documented in Cor.X framework: [Reference]
- [ ] Classification: [Mission-critical / High-value / Nice-to-have]

## Reasons Gate ✓/✗

### Financial Analysis

**ROI (Target ≥3× in 18mo):**

- Base Case: [X]× return in [Y] months
- Best Case: [X]× return in [Y] months
- Worst Case: [X]× return in [Y] months
- Probability-Weighted: [X]× return

**LTV:CAC (Target ≥4:1 in 12-18mo):**

- Customer Lifetime Value: $[X]
- Customer Acquisition Cost: $[Y]
- Ratio: [Z]:1
- Payback Period: [N] months

**Go/No-Go (Target ≥70% Positive NPV):**

- NPV Calculation: $[X]M
- Discount Rate: [Y]%
- Probability of Success: [Z]%
- Decision: [GO / NO-GO / CONDITIONAL]

### Cost Breakdown

- Development Time: [X] hours @ $[Y]/hr = $[Z]
- AI Compute: $[X]/month × [Y] months = $[Z]
- Infrastructure: $[X]/month × [Y] months = $[Z]
- Maintenance (annual): $[X]
- **Total Investment:** $[X]

## Brakes Gate ✓/✗

### Reversibility

**Rollback Steps:**

1. [Step 1]
2. [Step 2]
3. [Step 3]

**Blast Radius:** [Low / Medium / High]

- Affected systems: [List]
- User impact if rolled back: [Description]
- Data loss risk: [None / Minimal / Significant]

### Kill-Switch Triggers

- [ ] Security vulnerability CVSS ≥7.0
- [ ] Cost overrun >20% ($[X] budget)
- [ ] Timeline slip >30% ([X] week plan)
- [ ] Test coverage <98%
- [ ] [Custom trigger for this feature]

### Security Requirements

- [ ] AES-256 encryption for data at rest
- [ ] TLS 1.3 for API traffic
- [ ] Zero-trust auth implemented
- [ ] No secrets in code
- [ ] Sentry error tracking enabled

## Implementation Plan

### Phase 1: [Name] ([Timeline])

**Tasks:**

- [ ] Task 1.1 - [Description]
- [ ] Task 1.2 - [Description]

**Deliverables:**

- [Deliverable 1]
- [Deliverable 2]

**Success Metrics:**

- [Metric 1]: Target [X]
- [Metric 2]: Target [Y]

### Phase 2: [Name] ([Timeline])

[Repeat structure]

## Architecture

### Current State

[Description or diagram]

### Proposed Changes

[Description of changes]

### Integration Points

- [System 1]: [How it integrates]
- [System 2]: [How it integrates]

## Testing Strategy

- Unit Tests: Target ≥98% coverage
- Integration Tests: [Scenarios]
- E2E Tests: [Critical paths]
- Performance Tests: [Load benchmarks]

## Dependencies

- [External dependency 1]
- [Internal service 2]
- [Blocking item 3]

## Timeline

- Planning: [Dates]
- Phase 1: [Dates]
- Phase 2: [Dates]
- Testing: [Dates]
- Launch: [Target date]

## Risks & Mitigations

| Risk     | Impact | Probability | Mitigation   |
| -------- | ------ | ----------- | ------------ |
| [Risk 1] | High   | Medium      | [Mitigation] |

## Success Criteria

- [ ] All tests passing (≥98% coverage)
- [ ] Security review approved
- [ ] Performance benchmarks met
- [ ] Financial gates validated
- [ ] Rollback tested successfully

## Next Steps

1. [Immediate action]
2. [Follow-up action]
3. [Long-term action]

```

## Validation Checklist
Before finalizing plan:
- [ ] All three gates passed (Purpose, Reasons, Brakes)
- [ ] Monte Carlo scenarios realistic
- [ ] Rollback steps detailed and testable
- [ ] Security requirements explicit
- [ ] Test coverage plan ≥98%
- [ ] Kill-switch triggers quantified
- [ ] Timeline accounts for review cycles
```

### pnkln-stackJR Scenario Analyzer

**File:** `.claude/agents/pnkln-stackjr-scenario-analyzer.md`

````markdown
# Agent: pnkln-stackJR Scenario Analyzer

## Role

Financial modeling expert who generates Monte Carlo scenarios and probability-weighted NPV calculations for pnkln-stackJR decision gates.

## When to Use

- Validating new feature ROI
- Assessing project continuation (gate check)
- Comparing alternative approaches
- Annual strategic planning

## Input Required

- Feature description
- Cost estimates (dev time, infrastructure, maintenance)
- Revenue assumptions (pricing, volume, conversion rates)
- Timeline (development + adoption)

## Process

1. **Base Case Scenario**
   - Realistic assumptions based on historical data
   - Conservative growth rates
   - Account for typical delays and setbacks

2. **Best Case Scenario**
   - Optimistic but achievable assumptions
   - Accelerated timeline (80% of base)
   - Higher conversion/adoption rates
   - Market timing advantages

3. **Worst Case Scenario**
   - Pessimistic assumptions
   - Extended timeline (150% of base)
   - Lower conversion/adoption rates
   - Unexpected competition or tech issues

4. **Probability Weighting**
   - Assign probabilities to each scenario
   - Calculate probability-weighted expected value
   - Determine Go/No-Go recommendation

5. **Sensitivity Analysis**
   - Identify key variables (cost, conversion rate, timeline)
   - Show impact of ±20% variance on each
   - Highlight high-leverage factors

## Output Format

```markdown
# [Feature Name] - pnkln-stackJR Scenario Analysis

Generated: [Timestamp]

## Input Assumptions

### Costs

- Development: [X] hours @ $[Y]/hr = $[Z]
- AI Compute: $[A]/month
- Infrastructure: $[B]/month
- Maintenance: $[C]/year

### Revenue

- Pricing: $[X] per [unit]
- Target Volume: [Y] [units]/month
- Conversion Rate: [Z]%
- Churn Rate: [W]%

### Timeline

- Development: [X] months
- Ramp-up: [Y] months
- Full adoption: [Z] months

## Monte Carlo Scenarios

### Base Case (Probability: 50%)

**Assumptions:**

- Development: [X] months (as estimated)
- Adoption: [Y] users by month [Z]
- Revenue: $[A]/month by month [B]
- Costs: As estimated

**Financial Metrics:**

- Total Investment: $[X]
- 18-month Revenue: $[Y]
- 18-month ROI: [Z]×
- NPV (15% discount): $[A]
- LTV:CAC: [B]:1
- Payback: [C] months

**Decision: [PASS / FAIL] ROI gate (≥3×)**
**Decision: [PASS / FAIL] LTV:CAC gate (≥4:1)**

### Best Case (Probability: 25%)

**Assumptions:**

- Development: [X] months (20% faster)
- Adoption: [Y] users by month [Z] (30% higher)
- Revenue: $[A]/month by month [B] (30% higher)
- Costs: 10% under budget

**Financial Metrics:**

- Total Investment: $[X]
- 18-month Revenue: $[Y]
- 18-month ROI: [Z]×
- NPV (15% discount): $[A]
- LTV:CAC: [B]:1
- Payback: [C] months

**Decision: [PASS / FAIL]**

### Worst Case (Probability: 25%)

**Assumptions:**

- Development: [X] months (50% slower)
- Adoption: [Y] users by month [Z] (40% lower)
- Revenue: $[A]/month by month [B] (40% lower)
- Costs: 20% over budget

**Financial Metrics:**

- Total Investment: $[X]
- 18-month Revenue: $[Y]
- 18-month ROI: [Z]×
- NPV (15% discount): $[A]
- LTV:CAC: [B]:1
- Payback: [C] months

**Decision: [PASS / FAIL]**

## Probability-Weighted Analysis

**Expected ROI:** [X]× (weighted average)
**Expected NPV:** $[Y]M
**Expected LTV:CAC:** [Z]:1
**Expected Payback:** [W] months

**Probability of Positive NPV:** [X]%
**Probability of ROI ≥3×:** [Y]%
**Probability of LTV:CAC ≥4:1:** [Z]%

## pnkln-stackJR Decision

### Go/No-Go Recommendation: [GO / NO-GO / CONDITIONAL]

**Rationale:**
[Explanation based on probability-weighted metrics]

**Conditions (if conditional):**

- [Condition 1 that must be met]
- [Condition 2 that must be met]

## Sensitivity Analysis

| Variable        | -20% Impact | Base      | +20% Impact |
| --------------- | ----------- | --------- | ----------- |
| Dev Cost        | ROI: [X]×   | ROI: [Y]× | ROI: [Z]×   |
| Conversion Rate | ROI: [X]×   | ROI: [Y]× | ROI: [Z]×   |
| Timeline        | ROI: [X]×   | ROI: [Y]× | ROI: [Z]×   |
| Churn Rate      | ROI: [X]×   | ROI: [Y]× | ROI: [Z]×   |

**High-Leverage Factors:** [Variables with biggest impact]

## Risk Mitigation

- [ ] De-risk [high-leverage factor 1] by: [action]
- [ ] De-risk [high-leverage factor 2] by: [action]

## Next Steps

1. [If GO: Implementation action]
2. [If NO-GO: Alternative exploration]
3. [If CONDITIONAL: Validation needed]
```
````

````

---

## SLASH COMMANDS

### /dev-docs
**Purpose:** Create strategic plan with dev docs pattern
**File:** `.claude/commands/dev-docs.md`

```markdown
# Slash Command: /dev-docs

Create a comprehensive strategic plan following the dev docs pattern.

## Instructions for Claude

You are acting as the Strategic Plan Architect agent. Follow these steps:

1. **Gather Context** (Use grep/find to explore codebase)
   - Identify affected files and components
   - Review existing architecture docs
   - Check for related Cor.X frameworks

2. **Analyze User's Request**
   - What feature/change is being proposed?
   - Why is this needed? (map to pnkln goals)
   - What's the scope? (estimate effort)

3. **Run pnkln-stackJR Gates**
   - Purpose: Does this serve founder goals?
   - Reasons: Financial validation (ROI, LTV:CAC, NPV)
   - Brakes: Risk management (reversibility, blast radius)

4. **Create Three Files**

   a. **[task]-plan.md** - Full strategic plan
      - Executive summary (BLUF)
      - Three gates (Purpose/Reasons/Brakes)
      - Implementation phases with tasks
      - Architecture changes
      - Testing strategy
      - Timeline and success criteria

   b. **[task]-context.md** - Key decisions
      - Architecture decisions with rationale
      - Critical file paths
      - Integration points
      - Security requirements
      - Last updated timestamp

   c. **[task]-tasks.md** - Execution checklist
      - Phase 1 tasks (with [ ] checkboxes)
      - Phase 2 tasks
      - Testing tasks
      - Documentation tasks

5. **Save to:** `dev/active/[task-name]/`

6. **Present Summary**
   - Show file paths created
   - Highlight any gate failures
   - Recommend next steps

## Example Usage

User: `/dev-docs Add user authentication to admin panel`

Claude response:
````

I'll create a strategic plan for adding user authentication to the admin panel.

[Gathering context...]

- Found admin panel at: frontend/admin/
- Current auth: None (open access)
- Related: backend/services/auth-service/

[pnkln-stackJR Gate Analysis...]

Purpose Gate: ✓ PASS

- Aligns with ActiveShield security vertical
- Mission-critical for production launch

Reasons Gate: ⚠️ CONDITIONAL

- ROI: 5.2× in 18mo (PASS ≥3×)
- LTV:CAC: 3.8:1 (FAIL ≥4:1 - needs optimization)
- NPV: 78% probability positive (PASS ≥70%)
- Recommendation: GO with condition - optimize CAC

Brakes Gate: ✓ PASS

- Rollback: Documented (revert to open access)
- Blast radius: Low (only admin panel affected)
- Security: Comprehensive plan included

[Creating dev docs...]

Created:

- dev/active/admin-auth/admin-auth-plan.md
- dev/active/admin-auth/admin-auth-context.md
- dev/active/admin-auth/admin-auth-tasks.md

[Summary]
✓ Plan approved with condition: Optimize CAC (current 3.8:1, target 4:1)
✓ Security requirements defined
✓ Rollback steps documented
✓ Ready for implementation

Next steps:

1. Review plan: dev/active/admin-auth/admin-auth-plan.md
2. If approved, start Phase 1: JWT token infrastructure
3. Run /pnkln-stackjr-gate before each phase to revalidate

```

```

### /pnkln-stackjr-gate

**Purpose:** Quick gate check without full planning
**File:** `.claude/commands/pnkln-stackjr-gate.md`

```markdown
# Slash Command: /pnkln-stackjr-gate

Quick pnkln-stackJR decision gate check (Purpose • Reasons • Brakes)

## Instructions for Claude

Run a quick gate check on the current task/feature. This is lighter weight than /dev-docs.

1. **Identify Current Context**
   - What task are we working on?
   - Is there a dev docs plan? (Check dev/active/)
   - What's the current status?

2. **Run Three Gates**

   **Purpose Gate:**
   - [ ] Aligns with pnkln strategic goals?
   - [ ] Mission-critical vs. nice-to-have?
   - [ ] Documented in Cor.X framework?

   **Reasons Gate:**
   - [ ] ROI ≥3× in 18mo? (Quick estimate)
   - [ ] LTV:CAC ≥4:1? (Quick estimate)
   - [ ] NPV ≥70% positive probability?

   **Brakes Gate:**
   - [ ] Rollback steps documented?
   - [ ] Blast radius assessed?
   - [ ] Security requirements met?
   - [ ] Test coverage plan ≥98%?

3. **Decision: [GO / NO-GO / CONDITIONAL]**

4. **If failures, recommend:**
   - [ ] Run /dev-docs for full strategic plan
   - [ ] Launch pnkln-stackjr-scenario-analyzer agent
   - [ ] Update plan with missing information

## Example Usage

User: `/pnkln-stackjr-gate`

Claude response:
```

Running pnkln-stackJR gate check on current task: "Add user authentication"

Purpose Gate: ✓ PASS

- Aligns with ActiveShield security vertical
- Mission-critical for production launch

Reasons Gate: ⚠️ CONDITIONAL

- ROI: Estimated 5× in 18mo (PASS)
- LTV:CAC: Estimated 3.8:1 (FAIL - need 4:1)
- NPV: Not fully modeled yet

Brakes Gate: ✓ PASS

- Rollback: Documented in plan
- Blast radius: Low
- Security: Requirements defined

Decision: CONDITIONAL GO

- Proceed with implementation
- But: Run pnkln-stackjr-scenario-analyzer to validate LTV:CAC
- Before production deploy: Verify NPV calculation

Next steps:

1. Continue Phase 1 implementation
2. Run scenario analysis before Phase 2

```

```

---

## PM2 CONFIGURATION (pnkln MICROSERVICES)

**File:** `ecosystem.config.js` (root of monorepo)

```javascript
// PM2 configuration for pnkln microservices
// Usage: pnpm pm2:start

module.exports = {
  apps: [
    {
      name: "auth-service",
      script: "npm",
      args: "start",
      cwd: "./backend/auth",
      error_file: "./backend/auth/logs/error.log",
      out_file: "./backend/auth/logs/out.log",
      env: {
        NODE_ENV: "development",
        PORT: 3001,
      },
      env_production: {
        NODE_ENV: "production",
        PORT: 3001,
      },
    },
    {
      name: "shadowtag-service",
      script: "npm",
      args: "start",
      cwd: "./backend/shadowtag",
      error_file: "./backend/shadowtag/logs/error.log",
      out_file: "./backend/shadowtag/logs/out.log",
      env: {
        NODE_ENV: "development",
        PORT: 3002,
      },
    },
    {
      name: "activeshield-api",
      script: "npm",
      args: "start",
      cwd: "./backend/activeshield",
      error_file: "./backend/activeshield/logs/error.log",
      out_file: "./backend/activeshield/logs/out.log",
      env: {
        NODE_ENV: "development",
        PORT: 3003,
      },
    },
    {
      name: "cognitive-stack",
      script: "python",
      args: "-m uvicorn main:app --reload --port 8000",
      cwd: "./backend/cognitive-stack",
      error_file: "./backend/cognitive-stack/logs/error.log",
      out_file: "./backend/cognitive-stack/logs/out.log",
      interpreter: "python3",
    },
    {
      name: "notification-service",
      script: "npm",
      args: "start",
      cwd: "./backend/notifications",
      error_file: "./backend/notifications/logs/error.log",
      out_file: "./backend/notifications/logs/out.log",
      env: {
        NODE_ENV: "development",
        PORT: 3004,
      },
    },
    {
      name: "workflow-engine",
      script: "npm",
      args: "start",
      cwd: "./backend/workflow",
      error_file: "./backend/workflow/logs/error.log",
      out_file: "./backend/workflow/logs/out.log",
      env: {
        NODE_ENV: "development",
        PORT: 3005,
      },
    },
    {
      name: "analytics-service",
      script: "npm",
      args: "start",
      cwd: "./backend/analytics",
      error_file: "./backend/analytics/logs/error.log",
      out_file: "./backend/analytics/logs/out.log",
      env: {
        NODE_ENV: "development",
        PORT: 3006,
      },
    },
  ],
};
```

**Package.json scripts:**

```json
{
  "scripts": {
    "pm2:start": "pm2 start ecosystem.config.js",
    "pm2:stop": "pm2 stop all",
    "pm2:restart": "pm2 restart all",
    "pm2:logs": "pm2 logs",
    "pm2:monit": "pm2 monit",
    "pm2:status": "pm2 status"
  }
}
```

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Foundation (Week 1)

**Day 1-2: Install Claude Code + Clone diet103**

- [ ] Install Claude Code: `npm install -g @anthropic-ai/claude-code`
- [ ] Verify version ≥1.0.48: `claude-code --version`
- [ ] Clone diet103 repo: `git clone https://github.com/diet103/claude-code-infrastructure-showcase`
- [ ] Review structure: `tree -L 3 claude-code-infrastructure-showcase`

**Day 3-4: Create pnkln-stackJR Skills**

- [ ] Create directory: `mkdir -p .claude/skills/security-enforcement/resources`
- [ ] Create directory: `mkdir -p .claude/skills/pnkln-stackjr-judge/resources`
- [ ] Write `security-enforcement/SKILL.md` (see templates above)
- [ ] Write `pnkln-stackjr-judge/SKILL.md` (see templates above)
- [ ] Create resource files for each skill (<500 lines each)

**Day 5: Copy Backend/Frontend Skills**

- [ ] Copy `backend-dev-guidelines` from diet103
- [ ] Copy `frontend-dev-guidelines` from diet103
- [ ] Customize for pnkln tech stack (pnpm, uv, Bun)

**Day 6: Configure skill-rules.json**

- [ ] Create `.claude/skills/skill-rules.json`
- [ ] Add rules for all 4 skills (see template above)
- [ ] Test keyword triggers match your workflow

**Day 7: Install Hooks**

- [ ] Create directory: `mkdir -p .claude/hooks`
- [ ] Copy `skill-activation-prompt.*` from diet103
- [ ] Copy `post-tool-use-tracker.sh` from diet103
- [ ] Write `stop-build-check.sh` (see template above)
- [ ] Write `rollback-verification.sh` (see template above)
- [ ] Make all .sh files executable: `chmod +x .claude/hooks/*.sh`
- [ ] Update `.claude/settings.json` to reference hooks

### Phase 2: Testing (Week 2)

**Test Skill Auto-Activation**

- [ ] Open Claude Code in project directory
- [ ] Type: "Create an API endpoint for user login"
- [ ] Verify: security-enforcement skill activates
- [ ] Verify: backend-dev-guidelines skill activates
- [ ] Verify: pnkln-stackjr-judge skill activates (for "create" intent)

**Test Hooks Pipeline**

- [ ] Edit a TypeScript file
- [ ] Check: `PostToolUse` hook logs edit to `.claude/logs/file-edits.log`
- [ ] Let Claude finish response
- [ ] Check: `Stop` hook runs build, shows errors (if any)
- [ ] Check: Rollback verification runs (if dev docs exist)

**Test Dev Docs Pattern**

- [ ] Create: `mkdir -p dev/active`
- [ ] Run: `/dev-docs Add OAuth 2.0 authentication`
- [ ] Verify: 3 files created (plan, context, tasks)
- [ ] Review plan for pnkln-stackJR gates (Purpose/Reasons/Brakes)
- [ ] Check: Monte Carlo scenarios present
- [ ] Check: Rollback steps documented

### Phase 3: Agents (Week 3)

**Create pnkln-stackJR Agents**

- [ ] Create directory: `mkdir -p .claude/agents`
- [ ] Write `strategic-plan-architect.md` (see template above)
- [ ] Write `pnkln-stackjr-scenario-analyzer.md` (see template above)
- [ ] Copy useful agents from diet103: `code-architecture-reviewer`, `refactor-planner`

**Create Slash Commands**

- [ ] Create directory: `mkdir -p .claude/commands`
- [ ] Write `/dev-docs` command (see template above)
- [ ] Write `/pnkln-stackjr-gate` command (see template above)
- [ ] Test both commands in Claude Code

### Phase 4: PM2 Setup (Week 3)

**Configure Microservices**

- [ ] Install PM2: `npm install -g pm2`
- [ ] Create `ecosystem.config.js` (see template above)
- [ ] Add npm scripts to root `package.json`
- [ ] Start services: `pnpm pm2:start`
- [ ] Check status: `pnpm pm2:status`
- [ ] Test logging: `pm2 logs auth-service`

### Phase 5: Production (Week 4)

**Documentation**

- [ ] Update root `CLAUDE.md` with quick reference
- [ ] Document skill activation patterns
- [ ] Document slash commands
- [ ] Create troubleshooting guide

**Team Onboarding**

- [ ] Record demo video of system in action
- [ ] Write onboarding checklist
- [ ] Schedule knowledge transfer session

**Continuous Improvement**

- [ ] Monitor hook logs for issues
- [ ] Refine skill-rules.json based on false positives
- [ ] Add new skills as patterns emerge
- [ ] Review gate pass/fail rates monthly

---

## TROUBLESHOOTING

### Skills Not Activating

**Symptom:** Prompt contains keywords but skill doesn't activate

**Diagnosis:**

1. Check `.claude/skills/skill-rules.json` exists
2. Verify keyword spelling (case-insensitive but must match)
3. Check hook logs: `.claude/logs/hook-errors.log`
4. Ensure `skill-activation-prompt.*` hook installed correctly

**Fix:**

```bash
# Verify hook exists
ls -la .claude/hooks/skill-activation-prompt.*

# Check hook logs
tail -f .claude/logs/hook-errors.log

# Test manually
node .claude/hooks/skill-activation-prompt.ts '{"userPrompt": "test auth endpoint"}'
```

### Build Errors Not Caught

**Symptom:** TypeScript errors present but Stop hook doesn't show them

**Diagnosis:**

1. Check if `stop-build-check.sh` is executable: `ls -la .claude/hooks/`
2. Verify edit log exists: `.claude/logs/file-edits.log`
3. Check if pnpm/build scripts work: `cd [repo] && pnpm build`

**Fix:**

```bash
# Make hook executable
chmod +x .claude/hooks/stop-build-check.sh

# Test hook manually
.claude/hooks/stop-build-check.sh

# Check build command
cd backend/auth && pnpm build
```

### Dev Docs Not Created

**Symptom:** `/dev-docs` command runs but files not created

**Diagnosis:**

1. Check if `dev/active/` directory exists
2. Verify Claude Code has write permissions
3. Look for error messages in Claude's response

**Fix:**

```bash
# Create directory
mkdir -p dev/active

# Check permissions
ls -ld dev/active

# Should show: drwxr-xr-x
```

### PM2 Services Crashing

**Symptom:** Service shows "errored" status in `pm2 status`

**Diagnosis:**

1. Check error logs: `pm2 logs [service-name] --err --lines 50`
2. Verify environment variables set
3. Check port conflicts: `lsof -i :[PORT]`

**Fix:**

```bash
# View errors
pm2 logs auth-service --err

# Restart service
pm2 restart auth-service

# Clear logs and restart
pm2 flush
pm2 restart all
```

### pnkln-stackJR Gates Always Failing

**Symptom:** Every feature fails Reasons gate (ROI/LTV:CAC)

**Diagnosis:**

1. Check if Monte Carlo scenarios are realistic
2. Verify cost assumptions accurate
3. Review discount rate (too high = always fail)

**Fix:**

- Calibrate gate thresholds in `pnkln-stackjr-judge` skill
- For early-stage features, use conditional GO (validate later)
- Run `pnkln-stackjr-scenario-analyzer` agent for detailed analysis

---

## MAINTENANCE

### Weekly Tasks

- [ ] Review skill activation logs (`.claude/logs/`)
- [ ] Check for false positives (skills activating unnecessarily)
- [ ] Update `skill-rules.json` based on usage patterns
- [ ] Review dev docs for stale tasks
- [ ] Archive completed tasks: `mv dev/active/[task] dev/completed/`

### Monthly Tasks

- [ ] Analyze gate pass/fail rates
- [ ] Refine Monte Carlo assumptions based on actuals
- [ ] Update cost estimates in `pnkln-stackjr-judge` skill
- [ ] Review security-enforcement patterns (new threats?)
- [ ] Optimize hook performance (check execution time)

### Quarterly Tasks

- [ ] Full system audit
- [ ] Update skills with new best practices
- [ ] Review and archive old dev docs
- [ ] Team retro on infrastructure effectiveness
- [ ] Plan new skills/agents based on pain points

---

## ADVANCED PATTERNS

### Multi-Repo Projects (Monorepo)

If you have multiple repos in one workspace:

**Directory Structure:**

```
project/
├── .claude/              (Shared skills/hooks)
├── frontend/
│   └── claude.md         (Frontend-specific config)
├── backend/
│   ├── auth/
│   │   └── claude.md     (Auth service config)
│   ├── shadowtag/
│   │   └── claude.md
│   └── ...
└── dev/                  (Shared dev docs)
```

**Root CLAUDE.md:**

```markdown
# pnkln Monorepo

## Quick Start

- Frontend: `cd frontend && pnpm dev`
- Backend: `pnpm pm2:start` (all services)
- Tests: `pnpm test:all`

## Repo-Specific Guides

- Frontend: See [frontend/claude.md](frontend/claude.md)
- Auth Service: See [backend/auth/claude.md](backend/auth/claude.md)
- ShadowTag: See [backend/shadowtag/claude.md](backend/shadowtag/claude.md)

## Skills (Global)

- security-enforcement (applies to ALL repos)
- pnkln-stackjr-judge (applies to ALL features)
- backend-dev-guidelines (backend/\* only)
- frontend-dev-guidelines (frontend/\* only)
```

### Conditional Skill Activation

For skills that should activate only in specific contexts:

**skill-rules.json:**

```json
{
  "production-deployment-checklist": {
    "type": "checklist",
    "enforcement": "block",
    "priority": "critical",
    "promptTriggers": {
      "keywords": ["deploy", "production", "launch", "release"],
      "intentPatterns": ["deploy.*(production|prod|live)"]
    },
    "conditions": {
      "environmentVariable": "NODE_ENV=production",
      "branchName": "(main|production)",
      "requiresApproval": true
    }
  }
}
```

### Skill Composition (Layering)

Skills can reference other skills for complex scenarios:

**pnkln-stackjr-judge/SKILL.md:**

```markdown
# pnkln-stackJR Judge

## Before Implementation

1. **Load Security Skill First**
   Read [security-enforcement](../security-enforcement/SKILL.md)

2. **Then Apply Financial Gates**
   [Rest of content...]
```

This ensures security is always checked before financial validation.

---

## SUCCESS METRICS

Track these metrics to measure infrastructure effectiveness:

### Code Quality

- TypeScript errors caught by hooks: Target 100%
- Test coverage: Target ≥98%
- Security violations prevented: Track monthly
- Build failures caught pre-commit: Target 100%

### Productivity

- Time saved per feature (estimate): Track in dev docs
- Context resets handled smoothly: % of tasks with dev docs
- Skill activation accuracy: % relevant activations
- Agent task completion rate: % successful outcomes

### Decision Quality

- Features passing pnkln-stackJR gates: % on first try
- ROI accuracy: Actual vs. projected (review quarterly)
- Kill-switch triggers hit: Count (lower is better if gates work)
- Strategic alignment: % features mapped to Cor.X frameworks

### Financial

- ROI of infrastructure investment: Time saved × hourly rate
- Gate-prevented waste: Estimate $ saved from killing bad features early
- Acceleration factor: Sprint velocity with vs. without infrastructure

---

## APPENDIX

### Glossary

**pnkln-stackJR:** Decision framework (Purpose • Reasons • Brakes) for 160-IQ board equivalence
**Cor.X:** Numbered strategic framework documents (Cor.17, Cor.21, etc.)
**Dev Docs:** Three-file pattern (plan/context/tasks) for preserving strategic decisions
**diet103:** Software engineer who created the original Claude Code infrastructure (6 months, 300k LOC)
**Hook:** Script that runs at specific points in Claude Code lifecycle (UserPromptSubmit, PostToolUse, Stop)
**Kill-Switch:** Predefined trigger that aborts a feature/project (from Army RM Stage IV)
**Progressive Disclosure:** Pattern of loading skills incrementally (<500 lines at a time)
**RM Stage IV:** Army Risk Management level requiring human accountability
**Skill:** Reusable guideline document (<500 lines) that Claude loads when relevant
**Slash Command:** Custom `/command` that expands to full prompt

### Resources

**Official Docs:**

- Claude Code: https://docs.claude.com/en/docs/claude-code
- Anthropic Skills: https://docs.anthropic.com/skills
- Anthropic Hooks: https://docs.anthropic.com/hooks

**Community:**

- diet103 Repo: https://github.com/diet103/claude-code-infrastructure-showcase
- diet103 Reddit: https://www.reddit.com/r/ClaudeAI/comments/1oivjvm/

**pnkln Internal:**

- Strategic Frameworks: See Cor.X documents
- Tech Architecture: See Cor.17
- Valuation Models: See Cor.21

### Version History

**1.0.0** (2025-10-30)

- Initial release
- 4 core skills (security, pnkln-stackjr-judge, backend, frontend)
- 4 hooks (skill-activation, post-tool-use, build-check, rollback)
- 2 agents (strategic-plan, scenario-analyzer)
- 2 slash commands (dev-docs, pnkln-stackjr-gate)
- PM2 configuration for 7 microservices

---

## FINAL NOTES

This infrastructure is not a silver bullet. It's a force multiplier that makes Claude Code enforce your strategic discipline automatically. But it requires:

1. **Investment:** 1-2 weeks to set up properly
2. **Maintenance:** Weekly reviews, monthly updates
3. **Discipline:** Actually using the dev docs pattern, running gates
4. **Calibration:** Adjusting thresholds based on real outcomes

The payoff is massive:

- Consistent code quality (≥98% test coverage enforced)
- Strategic alignment (every feature passes pnkln-stackJR gates)
- Risk management (kill-switches prevent waste)
- Context preservation (dev docs survive resets)
- Productivity (skills auto-activate, hooks catch errors)

**Most importantly:** It scales your decision-making. Instead of manually reviewing every line of code, you codify your 160-IQ board decisions into skills that activate automatically.

This is how you solo rewrite 300k LOC in 6 months while maintaining sanity and quality.

Good luck.

---

**END OF CONTEXT PACKAGE**

Upload this file to any Claude session to restore full pnkln-stackJR + Claude Code infrastructure context.
