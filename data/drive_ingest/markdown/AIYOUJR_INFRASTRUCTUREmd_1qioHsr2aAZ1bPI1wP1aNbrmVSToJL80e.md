# ShadowTag-v2JR Claude Code Infrastructure

**Version:** 1.0.0
**Created:** 2025-11-15
**Purpose:** Complete Claude Code infrastructure with ShadowTag-v2JR governance framework
**Based on:** diet103 patterns + ShadowTagAi Cor.X frameworks

---

## What Is This?

Production-grade Claude Code infrastructure that automatically enforces:
- **Security standards** (AES-256, TLS 1.3, zero-trust)
- **Strategic gates** (ROI ≥3×, LTV:CAC ≥4:1, NPV ≥70%)
- **Development patterns** (Backend/Frontend best practices)
- **Risk management** (Army RM Stage IV protocols)

**The Result:** Your "160-IQ board" built into Claude's workflow. Every feature is validated against strategic goals before implementation.

---

## Directory Structure

```
.claude/
├── skills/                     # Domain expertise (4 core skills)
│   ├── security-enforcement/   # Blocks insecure code (CRITICAL)
│   │   ├── SKILL.md
│   │   └── resources/
│   │       ├── encryption.md
│   │       ├── secrets-management.md
│   │       └── tls-config.md
│   ├── ShadowTag-v2jr-judge/          # Strategic gates (HIGH)
│   │   ├── SKILL.md
│   │   └── resources/
│   │       └── monte-carlo-templates.md
│   ├── backend-dev-guidelines/ # Node.js/TypeScript patterns
│   │   └── SKILL.md
│   ├── frontend-dev-guidelines/# React/TanStack patterns
│   │   └── SKILL.md
│   └── skill-rules.json        # Auto-activation config (CRITICAL)
├── hooks/                      # Automation scripts
│   └── (to be implemented)
├── agents/                     # Specialized task handlers
│   └── (to be implemented)
└── commands/                   # Slash commands
    └── (to be implemented)

dev/
├── active/                     # Current work (dev docs)
└── completed/                  # Archived tasks

ecosystem.config.js             # PM2 microservices config
```

---

## The Four Core Skills

### 1. Security Enforcement (CRITICAL)

**What it does:** Blocks code that violates ShadowTagAi security requirements

**Auto-activates when you:**
- Work with auth, APIs, databases, secrets
- Edit `.ts`, `.py`, `.env` files
- Use keywords like `password`, `token`, `encrypt`

**Mandatory requirements:**
- AES-256-GCM encryption for data at rest
- TLS 1.3 for all API traffic (no TLS 1.2)
- Zero-trust auth (every service call authenticated)
- No secrets in code (Google Secret Manager)
- All errors logged to Sentry

**Example:**
```typescript
// ❌ BLOCKED
const apiKey = 'sk-1234567890';

// ✅ APPROVED
const apiKey = process.env.API_KEY;
```

### 2. ShadowTag-v2JR Judge (HIGH)

**What it does:** Enforces Purpose • Reasons • Brakes framework before implementation

**Auto-activates when you:**
- Plan/design features
- Work with ARCHITECTURE.md or PLAN.md files
- Use keywords like `feature`, `implement`, `deploy`

**Three Gates:**

**Purpose:** Does this serve founder goals?
- Aligns with ActiveShield exit (Y5-Y7) OR SHADOWTAGAI long-term
- Documented in Cor.X framework
- Classification: Mission-critical / High-value / Nice-to-have

**Reasons:** Will this make money?
- ROI ≥3× in 18 months
- LTV:CAC ≥4:1 in 12-18 months
- NPV ≥70% positive probability (Monte Carlo)

**Brakes:** Can we reverse if it fails?
- Rollback steps documented
- Blast radius assessed
- Kill-switch triggers defined
- Test coverage ≥98%
- Security review passed

**Example Decision Matrix:**
```
Feature: Add MFA to ActiveShield

PURPOSE: ✅ PASS (security vertical, mission-critical)
REASONS: ✅ PASS (4.2× ROI, 5.1:1 LTV:CAC, 84% NPV)
BRAKES: ✅ PASS (rollback <5min, low blast radius)

→ DECISION: GO - Implement immediately
```

### 3. Backend Dev Guidelines

**What it does:** Enforces Node.js/TypeScript/Express patterns

**Auto-activates when you:**
- Work in `backend/**/*.ts` files
- Create routes, controllers, services
- Use keywords like `api`, `endpoint`, `prisma`

**Key patterns:**
- Architecture: Routes → Controllers → Services → Repositories
- Error handling: Try-catch with Sentry
- Testing: Jest ≥98% coverage
- Package manager: pnpm (not npm/yarn)
- Database: Prisma ORM (parameterized queries)

### 4. Frontend Dev Guidelines

**What it does:** Enforces React 19 + TypeScript patterns

**Auto-activates when you:**
- Work in `frontend/**/*.tsx` files
- Create components, pages
- Use keywords like `react`, `component`, `tanstack`

**Key patterns:**
- React 19 with TypeScript strict mode
- TanStack Query v5 for data fetching
- TanStack Router for routing
- MUI v7 for components
- React Hook Form + Zod for forms

---

## Auto-Activation System

**How it works:**

1. You type a prompt (e.g., "Create API endpoint for user login")
2. Claude checks `skill-rules.json` for matching keywords/patterns
3. Matching skills load automatically
4. Claude follows skill guidelines while coding

**Keyword Triggers (Examples):**
- `auth` → security-enforcement + backend-dev-guidelines
- `feature` → ShadowTag-v2jr-judge
- `encrypt` → security-enforcement
- `component` → frontend-dev-guidelines

**File Triggers (Examples):**
- Editing `.env` → security-enforcement
- Editing `PLAN.md` → ShadowTag-v2jr-judge
- Editing `backend/**/*.ts` → backend-dev-guidelines + security-enforcement

---

## Quick Start

### 1. Verify Installation

Check that files were created correctly:

```bash
ls -la .claude/skills/
# Should show: ShadowTag-v2jr-judge, backend-dev-guidelines, frontend-dev-guidelines, security-enforcement, skill-rules.json

ls -la .claude/skills/skill-rules.json
# Should exist (this is critical for auto-activation)
```

### 2. Test Skill Activation

Start Claude Code in this directory and try:

```bash
# Test 1: Security skill activation
You: "Create an API endpoint that stores user passwords"

# Expected: security-enforcement skill should activate
# Claude should warn about password hashing requirements

# Test 2: ShadowTag-v2JR judge activation
You: "I want to build a new feature for customer analytics"

# Expected: ShadowTag-v2jr-judge skill should activate
# Claude should ask about ROI, LTV:CAC, strategic alignment

# Test 3: Backend skill activation
You: "Create a REST API endpoint for user registration"

# Expected: backend-dev-guidelines + security-enforcement should activate
# Claude should follow layered architecture (Routes → Controllers → Services)
```

### 3. Create Dev Docs for a Feature

When planning a large feature:

```bash
# 1. Create dev/active directory if not exists
mkdir -p dev/active

# 2. Ask Claude to create dev docs
You: "Create dev docs for adding OAuth 2.0 authentication"

# 3. Claude should create:
# dev/active/oauth-auth/
#   ├── oauth-auth-plan.md       # Strategic plan with ShadowTag-v2JR gates
#   ├── oauth-auth-context.md    # Key decisions, file paths
#   └── oauth-auth-tasks.md      # Execution checklist
```

### 4. Run PM2 Microservices (Optional)

If you have microservices configured:

```bash
# Install PM2 globally
npm install -g pm2

# Start all services
pnpm pm2:start

# Check status
pm2 status

# View logs
pm2 logs auth-service

# Stop all
pm2 stop all
```

---

## Usage Examples

### Example 1: Security Violation Caught

```typescript
You: "Create a function to connect to the database"

// ❌ Claude writes:
const db = await pg.connect('postgresql://REDACTED_USER:REDACTED_PASS@localhost:5432/db');

// ✅ Security skill activates and corrects:
const db = await pg.connect(process.env.DATABASE_URL!);
// Password now loaded from environment variable
```

### Example 2: Feature Fails Reasons Gate

```markdown
You: "Build a custom CRM for lead management"

// ShadowTag-v2JR Judge runs analysis:

PURPOSE: ⚠️ CONDITIONAL (internal tool, not core product)
REASONS: ❌ FAIL
  - ROI: 1.2× (below 3× threshold)
  - Investment: $80k (custom dev)
  - Revenue: $16k (time savings)
BRAKES: ✅ PASS

→ DECISION: NO-GO
→ RECOMMENDATION: Use HubSpot ($50/mo) instead
→ SAVINGS: $79k vs. custom build
```

### Example 3: Backend Pattern Enforcement

```typescript
You: "Create user registration endpoint"

// ❌ Bad pattern (business logic in route):
app.post('/register', async (req, res) => {
  const hashed = await bcrypt.hash(req.body.password, 10);
  await db.user.create({ ...req.body, password: hashed });
});

// ✅ Backend skill guides correct pattern:
// routes/user.routes.ts → controller → service → repository
// - Route defines endpoint
// - Controller handles request/response
// - Service contains business logic
// - Repository handles database operations
```

---

## ShadowTag-v2JR Strategic Framework

### Purpose • Reasons • Brakes

Every feature must pass three gates:

**Purpose:** Strategic alignment
- Does this serve ActiveShield exit or SHADOWTAGAI long-term?
- Documented in which Cor.X framework?
- Mission-critical vs. nice-to-have?

**Reasons:** Financial validation
- ROI ≥3× in 18 months?
- LTV:CAC ≥4:1 in 12-18 months?
- NPV ≥70% positive probability?

**Brakes:** Risk management
- Rollback steps documented?
- Blast radius assessed?
- Kill-switch triggers defined?
- Test coverage ≥98%?

**Decision Matrix:**
| Purpose | Reasons | Brakes | Decision |
|---------|---------|--------|----------|
| ✅ | ✅ | ✅ | **GO** - Implement |
| ✅ | ✅ | ⚠️ | **CONDITIONAL** - Fix brakes first |
| ✅ | ❌ | * | **NO-GO** - Pivot to higher ROI |
| ❌ | * | * | **STOP** - Not strategic |

---

## ShadowTagAi Tech Stack Reference

### Backend
- **Runtime:** Node.js 20+
- **Language:** TypeScript 5+
- **Framework:** Express.js
- **Database:** PostgreSQL + Prisma ORM
- **Package Manager:** pnpm
- **Process Manager:** PM2
- **Testing:** Jest
- **Monitoring:** Sentry

### Frontend
- **Framework:** React 19
- **Language:** TypeScript 5+
- **Data Fetching:** TanStack Query v5
- **Routing:** TanStack Router
- **UI:** MUI v7
- **Forms:** React Hook Form + Zod
- **Build:** Vite

### Python (Cognitive Stack)
- **Runtime:** Python 3.11+
- **Framework:** FastAPI
- **Package Manager:** uv
- **API Server:** Uvicorn

### Security Standards
- **Encryption:** AES-256-GCM
- **Transport:** TLS 1.3 only
- **Auth:** Zero-trust architecture
- **Secrets:** Google Secret Manager
- **Hashing:** Argon2id

---

## Troubleshooting

### Skills Not Auto-Activating

**Symptom:** You use keywords but skills don't load

**Fix:**
1. Check `.claude/skills/skill-rules.json` exists
2. Verify keywords in your prompt match those in skill-rules.json
3. Ask Claude directly: "Load security-enforcement skill"

### Gates Always Failing

**Symptom:** Every feature fails Reasons gate

**Fix:**
- Calibrate thresholds for early-stage features
- Use "CONDITIONAL GO" for MVPs
- Document assumptions clearly (dev time, customer count, pricing)

### PM2 Services Not Starting

**Symptom:** `pm2 status` shows "errored"

**Fix:**
```bash
# Check logs
pm2 logs [service-name] --err

# Verify paths in ecosystem.config.js
# Make sure service directories exist

# Restart
pm2 restart all
```

---

## Customization

### Add New Skill

1. Create directory: `.claude/skills/my-skill/`
2. Create `SKILL.md` with guidelines (<500 lines)
3. Add to `skill-rules.json`:

```json
{
  "my-skill": {
    "type": "domain",
    "enforcement": "suggest",
    "priority": "high",
    "promptTriggers": {
      "keywords": ["keyword1", "keyword2"],
      "intentPatterns": ["pattern.*"]
    }
  }
}
```

### Modify Thresholds

Edit thresholds in `.claude/skills/ShadowTag-v2jr-judge/SKILL.md`:

```markdown
# Change from default
- ROI ≥3× in 18 months  →  ROI ≥2× in 24 months (for long-term projects)
- LTV:CAC ≥4:1          →  LTV:CAC ≥3:1 (for early-stage)
```

---

## Success Metrics

Track these to measure effectiveness:

### Code Quality
- Security violations prevented: [count]
- Test coverage maintained: ≥98%
- Build errors caught pre-commit: [%]

### Strategic Alignment
- Features passing all gates on first try: [%]
- Gate-prevented waste: [$saved from NO-GO decisions]
- Kill-switch triggers hit: [count]

### Productivity
- Time saved per feature: [hours]
- Context resets handled smoothly: [%]
- Skill activation accuracy: [%]

---

## Resources

### diet103 Original Work
- GitHub: https://github.com/diet103/claude-code-infrastructure-showcase
- Reddit Post: "Claude Code is a Beast – Tips from 6 Months of Hardcore Use"
- Achievement: Solo rewrote 300k LOC in 6 months with consistent quality

### ShadowTagAi Internal
- Cor.X Strategic Frameworks
- ShadowTag-v2JR Decision Framework Documentation
- Security Standards (Army RM Stage IV)

---

## Maintenance

### Weekly
- Review skill activation logs
- Check for false positives
- Update skill-rules.json based on usage

### Monthly
- Analyze gate pass/fail rates
- Refine Monte Carlo assumptions based on actuals
- Update cost estimates
- Review security patterns (new threats?)

### Quarterly
- Full system audit
- Update skills with new best practices
- Review and archive old dev docs
- Team retro on effectiveness

---

## Next Steps

1. **Test the system** - Try the quick start examples above
2. **Create your first dev docs** - Plan a feature with ShadowTag-v2JR gates
3. **Customize for your workflow** - Adjust thresholds, add skills
4. **Share with team** - Onboard others to the infrastructure

---

**The Goal:** Scale your decision-making. Instead of manually reviewing every line of code, codify your 160-IQ board decisions into skills that activate automatically.

This is how you solo rewrite 300k LOC in 6 months while maintaining sanity and quality.

Good luck.

---

**Version:** 1.0.0
**Last Updated:** 2025-11-15
**Maintained By:** ShadowTagAi Engineering (Erik)
**License:** Proprietary (ShadowTagAi internal use only)