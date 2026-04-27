# Plan Mode + OPORD Integration Guide

## Governance Hierarchy (Your Law School Rules CONTROL)

```
┌──────────────────────────────────────────────────────┐
│  TIER 1: LAW SCHOOL RULES (IMMUTABLE)               │
│  • Legal frameworks                                  │
│  • Compliance requirements                           │
│  • Judge#6 governance protocols                      │
│  • YOUR RULES NEVER CHANGE                          │
└──────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│  TIER 2: OPERATIONAL PLANNING (OPORD)                │
│  • 5-paragraph format                                │
│  • Army Leadership Principles                        │
│  • TLP 8-step process                                │
│  • Swarm coordination                                │
└──────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│  TIER 3: TECHNICAL PLANNING (PLAN MODE)              │
│  • Code refactors                                    │
│  • Database migrations                               │
│  • API changes                                       │
│  • Ultra-concise syntax                             │
└──────────────────────────────────────────────────────┘
```

**CRITICAL**: When law school rules conflict with OPORD or Plan Mode → **law school rules WIN, always.**

---

## When to Use What

### Use PLAN MODE for:

✅ **Technical Implementation**
- Refactoring code modules
- Database schema changes
- API endpoint modifications
- Library version upgrades
- File structure reorganization
- Technical debt reduction

**Example**:
```
src/ShadowTag-v2/services/financial_decision_engine.py:
- add basel_iii_check() → validate capital adequacy
- update evaluate_decision() → integrate Basel III
- log compliance results → audit trail
- phase 2: add VaR/CVaR models

Unresolved Qs:
- threshold for capital adequacy ratio (8% or 10%)?
- real-time calc or cached daily?
```

### Use OPORD for:

✅ **Operational Execution**
- Agent task assignments
- Swarm coordination
- Security audits
- Revenue tracking
- Shift handoffs
- Multi-agent consensus
- Stakeholder communication

**Example**:
```
=============================================================
OPORD 00143 - SECURITY AUDIT
=============================================================

1. SITUATION:
   Reentrancy vulnerability in ShadowTagAccount.sol

2. MISSION:
   WHO: agent_042 (SECURITY specialist)
   WHAT: Audit and remediate critical vulnerability
   WHEN: Shift 0 (8-hour window)
   WHERE: ShadowTagAccount.sol, line 127
   WHY: Prevent fund loss, enable safe deployment

3. EXECUTION:
   - Apply CEI pattern
   - Add ReentrancyGuard
   - Test exploit POC
   - Get swarm consensus

[... full 5-paragraph format]
```

---

## Dual-Format Workflow

### Scenario: Implementing Judge#6 Financial Decision Engine

**STEP 1: OPORD (Operational Level)**
```
OPORD 00144 - IMPLEMENT FINANCIAL DECISION ENGINE

MISSION:
Build Judge#6 Financial Decision Engine with 5 core frameworks
for $3M ARR Year 1 revenue generation.

EXECUTION:
Phase 1: ATP 5-19 + FICO integration
Phase 2: Basel III + Black-Scholes
Phase 3: MPT + enterprise API
```

**STEP 2: PLAN MODE (Technical Level)**
```
src/ShadowTag-v2/services/financial_decision_engine.py:
- create FinancialDecisionEngine class
- add atp_5_19_risk_matrix() → probability × severity
- add fico_risk_assessment() → score-based approval
- integrate with Context Index → revenue tracking
- full Basel III = Phase 2

Impl:
- Pydantic models for request/response
- FastAPI router at /api/v1/judge6/evaluate
- pricing tier enforcement (freemium/premium/pro)

Unresolved Qs:
- FICO score source (user-provided or API fetch)?
- risk threshold configurable per customer?

Options:
1. Proceed + implement ATP + FICO only
2. Hold + design full schema first
```

**STEP 3: EXECUTION**
- Agent uses **PLAN MODE syntax** for technical commits
- Agent uses **OPORD format** for operational logging
- Both logged to Context Index for audit trail

---

## Syntax Mapping

### OPORD → Plan Mode Translation

| OPORD Element | Plan Mode Equivalent |
|---------------|----------------------|
| Situation | Context (implied in module header) |
| Mission | First action line |
| Execution | `Impl:` section |
| Service Support | Dependencies or comments |
| Command & Signal | `Unresolved Qs:` + `Options:` |

### Example Translation

**OPORD**:
```
MISSION: Integrate Basel III compliance checker
EXECUTION: Create checker function, validate inputs, log results
```

**Plan Mode**:
```
services/financial_decision_engine.py:
- add basel_iii_check(capital, rwa) → compliance result
- validate inputs (capital > 0, rwa > 0)
- log result → audit trail
```

---

## Skill Activation Integration

Updated `.claude/hooks/skill-activation-prompt.sh`:

```bash
# Detect Plan Mode vs OPORD
if echo "$prompt" | grep -iE "refactor|migrate|upgrade|schema|api.*change" > /dev/null; then
    echo "📐 MODE: Plan Mode (technical)"
    echo "   Template: .cursor/PLAN_MODE_TEMPLATE.md"
    log_activation "Plan Mode activated (technical planning)"
fi

if echo "$prompt" | grep -iE "opord|shift|swarm|agent.*task|consensus" > /dev/null; then
    echo "⚔️  MODE: OPORD (operational)"
    echo "   Template: .claude/docs/unified-sop-template.md"
    log_activation "OPORD activated (operational planning)"
fi
```

---

## Real-World Example: Security Audit

### OPORD (Operational Planning)
```
OPORD 00143 - SECURITY AUDIT

1. SITUATION: Reentrancy vulnerability discovered
2. MISSION: agent_042 to audit and remediate
3. EXECUTION: Apply CEI pattern + ReentrancyGuard
4. SERVICE SUPPORT: $0.00034, 2.3s latency, 3 papers cited
5. COMMAND: Approved 80% consensus, handoff Shift 1
```

### Plan Mode (Technical Execution)
```
contracts/ShadowTagAccount.sol:
- move _initialized = true above _safeTransferFrom (line 127)
- add nonReentrant modifier to createAccount()
- import OpenZeppelin ReentrancyGuard
- test: verify exploit POC fails ✓

test/ShadowTagAccount.test.js:
- add reentrancy attack simulation
- confirm revert with "ReentrancyGuard: reentrant call"
- gas profiling: +2.3% overhead (acceptable)

Unresolved Qs:
- deploy fix to testnet first or audit report?
- require formal verification or test coverage sufficient?

Options:
1. Proceed + deploy testnet
2. Hold + formal verification ($5K budget)
```

**Both formats logged to Context Index** → full audit trail ✅

---

## Conflict Resolution Protocol

### When Plan Mode and OPORD Disagree

**Example Conflict**:
- **OPORD** says: "Deploy immediately (commander's intent)"
- **Plan Mode** says: "Unresolved Q: formal verification needed?"

**Resolution**:
1. **Law school rules** checked first (compliance required?)
2. If compliant → **OPORD takes precedence** (operational priority)
3. Plan Mode question becomes **risk documentation** not blocker

**Logged as**:
```
OPORD Decision: Deploy without formal verification
Rationale: Commander's intent prioritizes speed
Risk Accepted: No formal verification (documented in Plan Mode)
Compensating Control: Extended testnet period + bug bounty
Authority: Law school rules permit (no regulatory requirement)
```

---

## Best Practices

### DO:
✅ Use Plan Mode for commit messages (concise, scannable)
✅ Use OPORD for agent task logging (audit trail)
✅ Start with OPORD (what), drill down to Plan Mode (how)
✅ Surface blockers in both formats
✅ Respect law school rules precedence

### DON'T:
❌ Mix Plan Mode syntax in OPORD format
❌ Use OPORD for technical refactoring details
❌ Skip "Unresolved Qs:" in Plan Mode
❌ Bypass law school rules for "efficiency"
❌ Auto-proceed when legal compliance uncertain

---

## Summary: The Three-Layer Cake

```
┌─────────────────────────────────────────────┐
│  LAW SCHOOL RULES (foundation)              │
│  • Immutable                                │
│  • Governance authority                     │
│  • Compliance requirements                  │
└─────────────────────────────────────────────┘
           ↓ governs ↓
┌─────────────────────────────────────────────┐
│  OPORD (operational layer)                  │
│  • Agent missions                           │
│  • Swarm coordination                       │
│  • 5-paragraph format                       │
│  • Army Leadership Principles               │
└─────────────────────────────────────────────┘
           ↓ drives ↓
┌─────────────────────────────────────────────┐
│  PLAN MODE (technical layer)                │
│  • Code refactors                           │
│  • Database migrations                      │
│  • Ultra-concise syntax                     │
│  • Machine-parsable                         │
└─────────────────────────────────────────────┘
```

**All three layers work together**:
- Law school rules provide boundaries
- OPORD provides mission clarity
- Plan Mode provides execution precision

**Result**: Legally compliant, operationally effective, technically excellent 🚀

---

**Status**: Integrated and ready for production
**Precedence**: Law School > OPORD > Plan Mode
**Version**: 1.0
