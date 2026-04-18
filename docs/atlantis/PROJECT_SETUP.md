# PROJECT_SETUP - Claude Projects Integration Guide

**Version**: 1.0
**Last Updated**: 2025-11-14
**Purpose**: Guide for setting up and using Pnkln documentation in Claude Projects for rich, persistent context

---

## OVERVIEW

This guide explains how to use the **"heavier" Projects approach** for Pnkln context management, providing rich, full-context documentation across all Claude conversations.

**What You Get**:

- **Full documentation** available in every conversation (no 500-line skill limit)

- **Richer context** vs. skills (complete frameworks, examples, playbooks)

- **Portable source of truth** (Cor_vX.md + supporting docs version-controlled)

- **Token efficient** (load once per project vs. re-explain every session)

**Trade-offs vs. Skills**:

- ✅ No line limits (skills capped at 500 lines)

- ✅ Supports full examples, playbooks, detailed specs

- ✅ Version-controlled in your repository (git history)

- ⚠️ Projects are claude.ai-specific (not API/other platforms)

- ⚠️ Requires manual re-upload for updates (no auto-sync yet)

---

## SETUP INSTRUCTIONS

### Step 1: Create a New Claude Project


1. **Navigate to Claude.ai**: Log in to your claude.ai account

2. **Create Project**: Click "Projects" → "New Project"

3. **Name Project**: "Pnkln Core" (or your preferred name)

4. **Description**: "Pnkln operating system - JR_ENGINE, Bootstrap Gates, Technical SLA, Risk Framework"

### Step 2: Upload Documentation Files

**Upload these files to your project** (in order):


1. **Cor_v1.md** (master framework - upload FIRST)

   - Location: `docs/pnkln/Cor_v1.md`

   - Purpose: Overview and quick reference


2. **JR_ENGINE.md** (decision framework)

   - Location: `docs/pnkln/JR_ENGINE.md`

   - Purpose: PURPOSE → REASONS → BRAKES validation


3. **BOOTSTRAP_GATES.md** (financial constraints)

   - Location: `docs/pnkln/BOOTSTRAP_GATES.md`

   - Purpose: Burn limits, ROI thresholds, LTV:CAC ratios


4. **TECHNICAL_SLA.md** (performance standards)

   - Location: `docs/pnkln/TECHNICAL_SLA.md`

   - Purpose: Judge #6 targets, core stack, architecture principles


5. **RISK_FRAMEWORK.md** (risk management)

   - Location: `docs/pnkln/RISK_FRAMEWORK.md`

   - Purpose: ATP 5-19 gates, kill-switch protocols

**How to Upload**:

- Click "Add Content" in your project

- Select "Upload Files"

- Choose all 5 markdown files

- Confirm upload

### Step 3: Set Project Instructions (Optional)

In the project "Custom Instructions" field, you can add:

```

This project contains Pnkln's operating system documentation.

When working on strategic decisions, use the JR_ENGINE framework (PURPOSE → REASONS → BRAKES).

When evaluating financial decisions, validate against BOOTSTRAP_GATES (burn limit $60-65K, ROI ≥3×, LTV:CAC ≥4:1).

When making technical decisions, check TECHNICAL_SLA compliance (Judge #6 p99≤90ms, core stack requirements).

When assessing risks, apply RISK_FRAMEWORK (ATP 5-19: Identify → Assess → Control → Implement → Supervise).

Always exercise objection duty: challenge assumptions, flag weak evidence, call out scope creep.

```

### Step 4: Test the Project

**Open a new conversation in the project** and test with:

```

Evaluate the decision to build Gulfstream ERCOT integration.
Use the JR_ENGINE framework and validate against all gates.

```

**Expected Response**:

- Claude should reference JR_ENGINE (PURPOSE → REASONS → BRAKES)

- Check BOOTSTRAP_GATES (ROI ≥3×, LTV:CAC ≥4:1, burn constraints)

- Assess via RISK_FRAMEWORK (hazards, probability × severity)

- Provide structured decision output with validation footer

---

## USAGE PATTERNS

### Pattern 1: Strategic Decisions

**Prompt**:

```

I'm considering [decision]. Run this through JR_ENGINE and give me a recommendation.

```

**Example**:

```

I'm considering hiring a full-time designer for $80K/year. Run this through JR_ENGINE and give me a recommendation.

```

**Expected Output**:

```

JR_ENGINE DECISION: Hire Full-Time Designer ($80K/year)
========================================================

PURPOSE: [Revenue-Enabling OR Technical Foundation - Claude analyzes]

REASONS:
[Tier 1] - [Direct evidence from your description]
[Tier 2] - [Secondary evidence Claude infers]
[Tier 3] - [First principles reasoning]
[Tier 4] **FLAG** - [Speculation Claude identifies]

BRAKES:
Bootstrap: FAIL - $80K exceeds total burn budget $60-65K
Technical: N/A
Risk: EXTREME - Depletes all capital, no runway
Strategic: MISALIGNED - Defer until post-revenue

DECISION: REJECT
RATIONALE: Violates bootstrap burn constraint, no path to ROI within capital limits.
ALTERNATIVE: Contract designer ($5K/project) for critical work only.

```

### Pattern 2: Technical Decisions

**Prompt**:

```

Should we [technical choice]? Check against TECHNICAL_SLA requirements.

```

**Example**:

```

Should we migrate from PostgreSQL to MongoDB for Judge #6? Check against TECHNICAL_SLA requirements.

```

**Expected Output**:

```

TECHNICAL_SLA ASSESSMENT: Migrate PostgreSQL → MongoDB
=======================================================

STACK COMPATIBILITY: FAIL

- Requirement: PostgreSQL 15+ (ACID, JSON, proven)

- Proposed: MongoDB (NoSQL, eventual consistency)

- Rationale: PostgreSQL is core stack, avoid churn

PERFORMANCE IMPACT: UNCERTAIN

- Current: p99 = 150ms (PostgreSQL, 67ms over target)

- Claim: MongoDB faster (unvalidated for our workload)

- Risk: Migration could degrade performance further

COMPLEXITY: HIGH

- Data migration effort: 2-4 weeks

- Application refactor: 3-5 weeks

- Learning curve: Moderate (team knows SQL, not NoSQL)

RECOMMENDATION: REJECT
RATIONALE: Violates core stack principle (PostgreSQL preferred), high complexity, unvalidated performance benefit.
ALTERNATIVE: Optimize PostgreSQL (indexes, caching) to reach p99≤90ms target.

```

### Pattern 3: Risk Assessment

**Prompt**:

```

Assess the risk of [scenario] using ATP 5-19 framework.

```

**Example**:

```

Assess the risk of relying on a single cloud provider (AWS) using ATP 5-19 framework.

```

**Expected Output**:

```

RISK ASSESSMENT: Single Cloud Provider Dependency (AWS)
=======================================================

STEP 1: IDENTIFY HAZARD

- Hazard: AWS outage or price increase

- Category: Technical (dependency) + Financial (cost)

STEP 2: ASSESS HAZARD

- Probability: 3 (Occasional) - AWS outages rare but happen

- Severity: 4 (Critical) - Extended downtime, customer SLA breach

- Risk Level: 3 × 4 = 12 (HIGH)

STEP 3: DEVELOP CONTROLS
Strategy: MITIGATE (avoid is too expensive, transfer not practical)

Controls:

1. Multi-region deployment within AWS (reduce outage impact)

2. Portable architecture (use standard tech: Postgres, Docker)

3. Monitor AWS pricing, budget alert if >10% increase

4. Maintain migration plan (documentation, time estimate)

Residual Risk: MODERATE (6: Seldom × Moderate)

STEP 4: IMPLEMENT CONTROLS

- ✅ Portable architecture (already using Postgres, Docker)

- ⏳ Multi-region deferred (until 50 customers, see BOOTSTRAP_GATES)

- ✅ Pricing alerts configured

- ⏳ Migration plan documentation (scheduled Q2 2026)

STEP 5: SUPERVISE & EVALUATE

- Monthly: AWS bill review, pricing trend

- Quarterly: Re-assess multi-region need (customer count, uptime)

DECISION: ACCEPT RESIDUAL RISK (Moderate acceptable for bootstrap phase)

```

### Pattern 4: Financial Gate Checks

**Prompt**:

```

Check if [expense] passes all 5 Bootstrap Gates.

```

**Example**:

```

Check if spending $5K on a marketing campaign targeting 50 prospects passes all 5 Bootstrap Gates.

```

**Expected Output**:

```

BOOTSTRAP GATES ASSESSMENT: $5K Marketing Campaign
===================================================

GATE 1: Budget Fit

- Remaining Capital: $45K (assumed)

- Decision Cost: $5K

- Remaining After: $40K

- Runway: $40K ÷ $10K/mo = 4 months

- STATUS: CONDITIONAL (below 6 months, but acceptable if revenue impact)

GATE 2: ROI Validation

- Expected Conversion: 20% (10 customers from 50 prospects)

- LTV per Customer: $9,000 (assumed)

- Expected Revenue: 10 × $9K = $90K

- ROI: ($90K - $5K) / $5K = 17× ✅ PASS

GATE 3: LTV:CAC Impact

- Current CAC: $2,000

- Campaign CAC: $5K / 10 = $500 per customer

- New Blended CAC: Lower (campaign more efficient)

- LTV:CAC: $9K / $2K = 4.5:1 maintained ✅ PASS

GATE 4: Cheaper Alternative

- Alternative: Manual outreach ($0 cost, 20 hours founder time)

- Analysis: Manual viable but slow (10 prospects/week vs. 50)

- Decision: Campaign justified for speed ✅ PASS

GATE 5: Worst-Case Affordable

- Worst-Case Conversion: 10% (5 customers)

- Worst-Case Revenue: 5 × $9K = $45K

- Worst-Case ROI: ($45K - $5K) / $5K = 8× ✅ PASS

OVERALL: APPROVE (all gates PASS or CONDITIONAL with justification)
CONDITIONS:

- Track conversion weekly, kill-switch if <5% at 25 prospects

- Document campaign learnings for future CAC optimization

```

---

## MAINTENANCE & UPDATES

### When to Update Documentation

**Update Triggers**:

1. **Strategic priorities change**: New product, market pivot, major customer

2. **Financial constraints change**: Funding, revenue milestone, burn rate shift

3. **Technical SLA evolves**: New performance targets, stack changes

4. **Risk landscape shifts**: New hazards, changed probabilities, control failures

5. **Lessons learned**: Quarterly retrospective, major incidents

### How to Update

**Process**:

1. **Edit source files** in your repository (`docs/pnkln/*.md`)

2. **Update version number** in Cor_vX.md (e.g., v1.0 → v1.1)

3. **Document changes** in version history section

4. **Commit to git** with clear message (e.g., "Update BOOTSTRAP_GATES: Increase burn limit to $75K")

5. **Re-upload to Claude Project** (replace old files with new versions)

**Version Numbering**:

- **Major version (v1 → v2)**: Significant framework changes (e.g., new decision model)

- **Minor version (v1.0 → v1.1)**: Updates to targets, constraints, examples

- **Patch version (v1.1.0 → v1.1.1)**: Typos, clarifications, formatting

**Example Update**:

```

# Scenario: Revenue hits $100K ARR, increasing burn budget


1. Edit BOOTSTRAP_GATES.md:

   - Change burn limit: $60-65K → $75-80K

   - Update monthly target: $10K → $12K


2. Edit Cor_v1.md → Cor_v1.1.md:

   - Update BOOTSTRAP_GATES summary

   - Add version history entry:
     "v1.1 (2025-12-15): Increased burn limit to $75-80K based on revenue milestone"


3. Commit:
   git add docs/pnkln/
   git commit -m "Update BOOTSTRAP_GATES: Increase burn limit to $75-80K (revenue milestone)"
   git push


4. Re-upload to Claude Project:

   - Remove old BOOTSTRAP_GATES.md and Cor_v1.md

   - Upload new BOOTSTRAP_GATES.md and Cor_v1.1.md

```

### Sync Checks

**Monthly**:

- Compare project files to repository (are they in sync?)

- Review recent commits (any updates not yet uploaded?)

- Schedule re-upload if drift detected

**Quarterly**:

- Full documentation review (accuracy, relevance, completeness)

- Version bump (even if minor, document "no changes" to confirm review)

- Team alignment (if team >1, ensure everyone uses same version)

---

## ALTERNATIVE APPROACHES

### Comparison: Projects vs. Skills vs. Manual

| Aspect | **Projects** (Heavier) | **Skills** (Lighter) | **Manual** (Baseline) |
|--------|------------------------|----------------------|----------------------|
| **Context Richness** | Full docs (no limits) | 500 lines max | Re-explain each session |
| **Token Efficiency** | High (load once) | High (load once) | Low (repeat context) |
| **Portability** | claude.ai only | claude.ai only | Works everywhere |
| **Update Mechanism** | Manual re-upload | Manual re-upload | N/A (always fresh) |
| **Version Control** | Git-tracked source | Git-tracked source | No tracking |
| **Setup Effort** | Moderate (upload files) | Low (upload 1 file) | Zero |
| **Maintenance** | Moderate (re-upload) | Low (re-upload 1 file) | Zero |
| **Best For** | Rich context, examples | Core framework only | One-off, simple tasks |

**Decision Matrix**:

- **Use Projects** (this approach) IF:

  - You need full documentation, examples, playbooks

  - You work primarily on claude.ai (not API)

  - You're willing to maintain sync (git → project)


- **Use Skills** IF:

  - You can distill framework to <500 lines

  - You want minimal maintenance overhead

  - Core framework is stable (few updates)


- **Use Manual** IF:

  - Context is simple, changes frequently

  - You work across multiple platforms (claude.ai, API, mobile)

  - You want maximum flexibility, no sync burden

### Hybrid Approach

**Combine Projects + Memory** for best results:


1. **Projects**: Upload full documentation (frameworks, playbooks)

2. **Memory**: Claude remembers your preferences, recent decisions, active projects

3. **Benefits**:

   - Projects provide systematic frameworks

   - Memory provides personalized context

   - Together: Rich + relevant context every session

**Example**:

- **Project**: JR_ENGINE, BOOTSTRAP_GATES, etc. (systematic frameworks)

- **Memory**: "Founder working on Gulfstream ERCOT, prefers concise communication, skeptical of premature optimization"

- **Outcome**: Claude applies frameworks with personalized context

---

## TROUBLESHOOTING

### Issue: Claude Not Referencing Documentation

**Symptoms**:

- Claude doesn't use JR_ENGINE framework when asked

- Responses ignore BOOTSTRAP_GATES constraints

- No mention of Cor_vX.md frameworks

**Diagnosis**:

1. **Check project context**: Are you in the "Pnkln Core" project? (top of conversation)

2. **Check file upload**: Are all 5 files uploaded and accessible?

3. **Check file format**: Are files markdown (.md) and properly formatted?

**Fix**:

- Ensure conversation is within project (not general chat)

- Re-upload files if missing or corrupted

- Explicitly prompt: "Use the JR_ENGINE framework from the project docs"

### Issue: Outdated Information in Responses

**Symptoms**:

- Claude references old targets (e.g., p99≤100ms when updated to ≤90ms)

- Old burn limits cited (e.g., $50K when increased to $75K)

**Diagnosis**:

- Project files not synced with latest git commits

- Claude reading old version of documentation

**Fix**:

1. Check git history: When was last update?

2. Check project files: What version is uploaded?

3. Re-upload latest version from repository

### Issue: Responses Too Verbose or Not Verbose Enough

**Symptoms**:

- Claude provides full JR_ENGINE analysis when you wanted quick answer

- Claude gives terse response when you wanted detailed breakdown

**Fix**:

- **For concise**: "Quick gate check: Does this pass BOOTSTRAP_GATES?"

- **For detailed**: "Full JR_ENGINE analysis with examples from documentation"

- **Update custom instructions**: Add verbosity preference to project settings

---

## VALIDATION TEST

**Test your setup works correctly**:

### Test 1: Framework Recognition

**Prompt**:

```

What is the JR_ENGINE framework?

```

**Expected**:

```

JR_ENGINE is Pnkln's decision validation framework with three stages:


1. PURPOSE: What strategic outcome does this serve?

2. REASONS: Evidence hierarchy (Tier 1-4) supporting the decision

3. BRAKES: Constraints and kill-switch criteria

Used for feature prioritization, technical architecture, resource allocation, and strategic pivots.

```

### Test 2: Constraint Application

**Prompt**:

```

What's the burn limit and monthly target?

```

**Expected**:

```

BURN LIMIT: $60,000 - $65,000 (total capital)
MONTHLY TARGET: ≤$10,000/month average
WARNING THRESHOLD: $11,000/month (2 consecutive months)
KILL-SWITCH: $12,000/month (2 consecutive months)

```

### Test 3: Decision Framework

**Prompt**:

```

I want to spend $15K on a new feature. What do I need to validate?

```

**Expected**:

```

Run through BOOTSTRAP_GATES (5 gates):


1. Budget Fit: Does $15K fit within remaining capital?

2. ROI Validation: Is ROI ≥3× measurable within 6 months?

3. LTV:CAC Impact: Does this maintain ratio ≥4:1?

4. Cheaper Alternative: Is there a cheaper validation path?

5. Worst-Case Affordable: Can we afford if revenue assumptions 50% wrong?

Also run JR_ENGINE (PURPOSE → REASONS → BRAKES) and RISK_FRAMEWORK (identify → assess → control).

```

**If all 3 tests pass** → Setup successful ✅

---

## BEST PRACTICES

### 1. Reference Specific Sections

**Instead of**:

```

Use the framework to evaluate this.

```

**Do**:

```

Use JR_ENGINE (PURPOSE → REASONS → BRAKES) to evaluate this. Check BOOTSTRAP_GATES Gate 2 (ROI ≥3×).

```

**Why**: More specific prompts → more accurate application of frameworks

### 2. Combine Frameworks

**Prompt**:

```

Evaluate [decision] using:

1. JR_ENGINE (full decision framework)

2. BOOTSTRAP_GATES (all 5 gates)

3. RISK_FRAMEWORK (ATP 5-19 assessment)

Provide a consolidated recommendation.

```

**Why**: Comprehensive analysis catches issues single framework might miss

### 3. Request Validation Footers

**Prompt**:

```

[Your question]

Include validation footer:

- JR_ENGINE: [assessment]

- GATES: [pass/fail summary]

- RISKS: [level + mitigation]

- DECISION: [recommend/defer/reject]

```

**Why**: Standardized output format, easy to scan, consistent structure

### 4. Challenge Assumptions

**Prompt**:

```

I think we should [decision].

Exercise objection duty: What am I missing? What assumptions are weak? What could go wrong?

```

**Why**: Leverages Claude's analysis to find blind spots, weak reasoning

### 5. Iterate on Evidence

**Prompt**:

```

I want to [decision]. Here's my evidence: [list].

Classify this evidence (Tier 1-4). What's missing? What would strengthen the case?

```

**Why**: Improves decision quality by identifying evidence gaps

---

## TOKEN ECONOMICS

### Estimated Token Usage

**Without Projects** (manual context):

- Per session: ~5-8K tokens explaining frameworks

- 10 sessions: ~50-80K tokens (repeated context)

**With Projects** (this approach):

- Initial load: ~15-20K tokens (full documentation)

- Per session: ~1-2K tokens (references to pre-loaded context)

- 10 sessions: ~15-20K (initial) + ~10-20K (sessions) = ~25-40K tokens

**Savings**: ~40-60% token reduction over manual approach

**Cost Impact**:

- Lower token usage → faster responses

- Pre-loaded context → more consistent framework application

- Reduced need to re-explain → more time on actual problem-solving

---

## NEXT STEPS


1. **Complete Setup** (15 minutes):

   - Create Claude Project "Pnkln Core"

   - Upload all 5 documentation files

   - Set custom instructions

   - Run validation tests


2. **Test Drive** (30 minutes):

   - Run 3-5 real decisions through JR_ENGINE

   - Check gate compliance for recent spending

   - Assess 1-2 risks using ATP 5-19

   - Refine custom instructions based on results


3. **Establish Cadence** (ongoing):

   - Monthly: Sync check (repo vs. project files)

   - Quarterly: Documentation review and version bump

   - Ad-hoc: Update after major changes, incidents


4. **Iterate** (as needed):

   - Adjust custom instructions (verbosity, focus areas)

   - Add new documents (e.g., product specs, customer personas)

   - Prune outdated sections (keep docs lean and relevant)

---

## SUPPORT & FEEDBACK

**Issues with This Guide**:

- File a GitHub issue in your repository

- Tag with "documentation" label

- Describe problem, expected vs. actual behavior

**Improvements to Frameworks**:

- Propose changes via pull request

- Update Cor_vX.md version history

- Sync to Claude Project after merge

**Questions**:

- Ask Claude directly (it has access to this guide!)

- Consult [Claude Code docs](https://docs.claude.com/en/docs/claude-code) for platform features

- Check project "Memory" for past clarifications

---

## SUMMARY

**The Projects Approach** gives you:

- ✅ Full documentation (no limits)

- ✅ Rich context (examples, playbooks, details)

- ✅ Portable source of truth (git-tracked)

- ✅ Token efficient (load once, reference many)

**To succeed**:

1. Upload all docs to Claude Project

2. Reference frameworks explicitly in prompts

3. Maintain sync (git → project monthly)

4. Iterate based on usage (refine, prune, expand)

**You're ready**! Start using Pnkln Core frameworks in every strategic, technical, and operational decision.

---

**END PROJECT_SETUP.md**
