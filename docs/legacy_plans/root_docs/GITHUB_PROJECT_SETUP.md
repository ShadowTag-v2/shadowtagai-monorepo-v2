# PNKLN CORE STACK™ - GITHUB PROJECT SETUP GUIDE

**Date:** 2025-11-15
**Version:** 1.0

---

## OVERVIEW

This guide provides step-by-step instructions for creating a GitHub Project to track the PNKLN Core Stack™ implementation across both components (Judge #6 + Gemini Ingestion Layer).

**Project Structure:**

- **2 Components:** Judge #6 (Enforcement), Gemini Ingestion Layer (Collection)
- **4 Phases:** Foundation (Weeks 1-3), Enhancement (4-6), Production (7-9), Scale (10-12)
- **32 Issues:** 16 per component
- **3 Integration Milestones:** Week 3, 6, 9

---

## STEP 1: CREATE GITHUB PROJECT

### Option A: Using GitHub Web UI

1. Navigate to: `https://github.com/ehanc69/ShadowTag-v2-fastapi-services`
2. Click **"Projects"** tab
3. Click **"New project"**
4. Select **"Board"** template
5. Name: `PNKLN Core Stack™ - Implementation`
6. Description: `Judge #6 + Gemini Ingestion Layer - 12 Week Development Roadmap`
7. Click **"Create project"**

### Option B: Using GitHub CLI

```bash
gh project create \
  --owner ehanc69 \
  --title "PNKLN Core Stack™ - Implementation" \
  --body "Judge #6 + Gemini Ingestion Layer - 12 Week Development Roadmap"
```

---

## STEP 2: CONFIGURE PROJECT BOARD

### Create Custom Columns

**Default columns to create:**

1. **Backlog** - Not yet started
2. **Week 1-3 (Foundation)** - In progress (Phase 1)
3. **Week 4-6 (Enhancement)** - In progress (Phase 2)
4. **Week 7-9 (Production)** - In progress (Phase 3)
5. **Week 10-12 (Scale)** - In progress (Phase 4)
6. **Blocked** - Waiting on dependencies
7. **In Review** - PR submitted, awaiting review
8. **Done** - Completed

### Add Custom Fields

Add these custom fields to track metadata:

1. **Component** (Single select)
   - Judge #6
   - Gemini Ingestion Layer
   - Integration
   - Shared Infrastructure

2. **Phase** (Single select)
   - Phase 1: Foundation (Weeks 1-3)
   - Phase 2: Enhancement (Weeks 4-6)
   - Phase 3: Production (Weeks 7-9)
   - Phase 4: Scale (Weeks 10-12)

3. **Effort** (Number)
   - Person-weeks (e.g., 1, 2, 3)

4. **Priority** (Single select)
   - Critical
   - High
   - Medium
   - Low

5. **Week Target** (Number)
   - 1-12 (target completion week)

6. **Assignee** (Person)
   - Backend Eng 1, 2, 3, 4, 5
   - DevOps
   - Data Scientist

---

## STEP 3: CREATE LABELS

### Component Labels

```bash
gh label create "component: judge-6" --color "0052CC" --description "Judge #6 (Enforcement Layer)"
gh label create "component: ingestion" --color "00875A" --description "Gemini Ingestion Layer (Collection)"
gh label create "component: integration" --color "FF5630" --description "Integration between components"
gh label create "component: infrastructure" --color "6554C0" --description "Shared infrastructure (GKE, PostgreSQL, Redis)"
```

### Phase Labels

```bash
gh label create "phase-1: foundation" --color "FFF0B3" --description "Weeks 1-3"
gh label create "phase-2: enhancement" --color "FFE380" --description "Weeks 4-6"
gh label create "phase-3: production" --color "FFC400" --description "Weeks 7-9"
gh label create "phase-4: scale" --color "FF8B00" --description "Weeks 10-12"
```

### Priority Labels

```bash
gh label create "priority: critical" --color "DE350B" --description "Critical priority"
gh label create "priority: high" --color "FF5630" --description "High priority"
gh label create "priority: medium" --color "FFAB00" --description "Medium priority"
gh label create "priority: low" --color "36B37E" --description "Low priority"
```

### Type Labels

```bash
gh label create "type: feature" --color "0052CC" --description "New feature"
gh label create "type: enhancement" --color "00875A" --description "Enhancement to existing feature"
gh label create "type: bug" --color "DE350B" --description "Bug fix"
gh label create "type: documentation" --color "5E6C84" --description "Documentation"
gh label create "type: infrastructure" --color "6554C0" --description "Infrastructure work"
```

---

## STEP 4: CREATE MILESTONES

### Integration Milestones

```bash
# Milestone 1: Week 3 - First Integration
gh milestone create \
  --title "Week 3: First Integration" \
  --description "First data flow: Ingestion (280 items/day) → Judge #6 (35% coverage)" \
  --due-date 2025-12-06

# Milestone 2: Week 6 - Feedback Loop
gh milestone create \
  --title "Week 6: Feedback Loop Operational" \
  --description "Ingestion (620 items/day) → Judge #6 (78% coverage) → Feedback signals" \
  --due-date 2025-12-27

# Milestone 3: Week 9 - Production Launch
gh milestone create \
  --title "Week 9: Production Launch" \
  --description "PNKLN Core Stack™ v1.0: 850 items/day, 94% coverage, ATP 5-19 certified" \
  --due-date 2026-01-17

# Milestone 4: Week 12 - v1.0 Release
gh milestone create \
  --title "Week 12: v1.0 Release" \
  --description "$500K ARR booked, full feature set, handoff to operations" \
  --due-date 2026-02-07
```

---

## STEP 5: CREATE ISSUES (32 Total)

### Judge #6 Issues (16)

#### PHASE 1: Foundation (Weeks 1-3)

**Issue #1: JR Engine Core Framework**

```bash
gh issue create \
  --title "[JUDGE-6] JR Engine Core Framework (Purpose/Reasons/Brakes)" \
  --body-file .github/ISSUE_TEMPLATE/judge_six_implementation.md \
  --label "component: judge-6,phase-1: foundation,priority: critical,type: feature" \
  --milestone "Week 3: First Integration" \
  --assignee "backend-eng-3"
```

**Issue #2: ATP 5-19 Policy Schema**

```bash
gh issue create \
  --title "[JUDGE-6] ATP 5-19 Policy Schema (44 Threat Categories)" \
  --body "Define ATP 5-19 policy schema (JSON format) covering 44 threat categories..." \
  --label "component: judge-6,phase-1: foundation,priority: critical,type: feature" \
  --milestone "Week 3: First Integration"
```

**Issue #3: Gemini API Integration**

```bash
gh issue create \
  --title "[JUDGE-6] Gemini Flash 2.0 API Integration" \
  --body "Integrate Gemini Flash 2.0 for AI-powered policy validation..." \
  --label "component: judge-6,phase-1: foundation,priority: high,type: feature" \
  --milestone "Week 3: First Integration"
```

**Issue #4: Validation API Endpoints**

```bash
gh issue create \
  --title "[JUDGE-6] FastAPI Validation Endpoints" \
  --body "Build REST API endpoints: POST /api/v1/validate, /api/v1/validate/batch..." \
  --label "component: judge-6,phase-1: foundation,priority: high,type: feature" \
  --milestone "Week 3: First Integration"
```

#### PHASE 2: Enhancement (Weeks 4-6)

**Issue #5: Hybrid Enforcement (Gemini + PyTorch)**

```bash
gh issue create \
  --title "[JUDGE-6] Hybrid Enforcement (Gemini + PyTorch Fallback)" \
  --body "Add PyTorch local models as fallback for Gemini API failures..." \
  --label "component: judge-6,phase-2: enhancement,priority: high,type: feature" \
  --milestone "Week 6: Feedback Loop Operational"
```

**Issue #6-8:** Performance Optimization, Extended Policies, Audit Logging
_(Repeat pattern with appropriate titles/labels)_

#### PHASE 3: Production (Weeks 7-9)

**Issue #9-12:** Multi-Framework Compliance, Custom Policies, Dashboard, SLA
_(Repeat pattern with milestone "Week 9: Production Launch")_

#### PHASE 4: Scale (Weeks 10-12)

**Issue #13-16:** Horizontal Scaling, Analytics, Rate Limiting, Reports
_(Repeat pattern with milestone "Week 12: v1.0 Release")_

---

### Gemini Ingestion Layer Issues (16)

#### PHASE 1: Foundation (Weeks 1-3)

**Issue #17: GKE Cluster Setup**

```bash
gh issue create \
  --title "[INGESTION] GKE Cluster Provisioning (3 nodes, n1-standard-2)" \
  --body "Provision GKE cluster for nightly CronJob orchestration..." \
  --label "component: ingestion,phase-1: foundation,priority: critical,type: infrastructure" \
  --milestone "Week 3: First Integration" \
  --assignee "devops-engineer"
```

**Issue #18: Core CronJob Manifest**

```bash
gh issue create \
  --title "[INGESTION] Kubernetes CronJob Manifest (Multi-Container)" \
  --body "Create CronJob manifest for nightly ingestion (3:00 AM daily)..." \
  --label "component: ingestion,phase-1: foundation,priority: critical,type: infrastructure" \
  --milestone "Week 3: First Integration"
```

**Issue #19-23:** YouTube Collector, Twitter Collector, PostgreSQL Schema, Tier Classification, AM Briefing
_(Repeat pattern)_

#### PHASE 2-4: Similar pattern for Issues #24-32

---

## STEP 6: QUICK ISSUE CREATION SCRIPT

### Automated Issue Creation

Save this as `scripts/create_github_issues.sh`:

```bash
#!/bin/bash

# PNKLN Core Stack™ - GitHub Issue Creation Script

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Creating PNKLN Core Stack™ GitHub Issues...${NC}"

# Judge #6 Issues (Phase 1)
echo -e "${GREEN}Creating Judge #6 Phase 1 issues...${NC}"

gh issue create --title "[JUDGE-6] JR Engine Core Framework" \
  --body "**Component:** Judge #6
**Phase:** Foundation (Weeks 1-3)
**Effort:** 3 weeks

Implement core Purpose/Reasons/Brakes validation framework.

**Acceptance Criteria:**
- [ ] Purpose validator (business objective alignment)
- [ ] Reasons validator (evidence-based justification)
- [ ] Brakes validator (security/compliance risk detection)
- [ ] Unit tests ≥85% coverage
- [ ] Documentation: JR Engine philosophy guide

**Files to Create:**
- \`src/judge_six/jr_engine.py\`
- \`src/judge_six/validators/purpose.py\`
- \`src/judge_six/validators/reasons.py\`
- \`src/judge_six/validators/brakes.py\`

**Dependencies:** None" \
  --label "component: judge-6,phase-1: foundation,priority: critical" \
  --milestone "Week 3: First Integration"

gh issue create --title "[JUDGE-6] ATP 5-19 Policy Schema" \
  --body "**Component:** Judge #6
**Phase:** Foundation (Weeks 1-3)
**Effort:** 1 week

Define ATP 5-19 policy schema (JSON) covering 44 threat categories.

**Acceptance Criteria:**
- [ ] JSON schema (OpenAPI-compatible)
- [ ] 44 threat categories defined
- [ ] 20+ example policies
- [ ] Schema validation logic

**Files:**
- \`schemas/atp_5_19_policy_schema.json\`
- \`policies/security/injection.json\`
- \`policies/compliance/data_residency.json\`" \
  --label "component: judge-6,phase-1: foundation,priority: critical" \
  --milestone "Week 3: First Integration"

# Continue for all 32 issues...

echo -e "${GREEN}✓ All issues created!${NC}"
```

---

## STEP 7: ORGANIZE PROJECT BOARD

### Drag Issues to Columns

**Backlog:**

- All Phase 4 issues (Weeks 10-12)

**Week 1-3 (Foundation):**

- Issue #1-4 (Judge #6 Phase 1)
- Issue #17-23 (Ingestion Phase 1)

**Week 4-6 (Enhancement):**

- Issue #5-8 (Judge #6 Phase 2)
- Issue #24-29 (Ingestion Phase 2)

**Week 7-9 (Production):**

- Issue #9-12 (Judge #6 Phase 3)
- Issue #30-32 (Ingestion Phase 3)

**Week 10-12 (Scale):**

- Issue #13-16 (Judge #6 Phase 4)

---

## STEP 8: CREATE PROJECT VIEWS

### View 1: By Component

**Filter:** Group by `Component` field
**Sort:** By `Priority` (Critical → Low)

### View 2: By Phase

**Filter:** Group by `Phase` field
**Sort:** By `Week Target`

### View 3: By Assignee

**Filter:** Group by `Assignee`
**Sort:** By `Priority`

### View 4: Integration Milestones

**Filter:** Only issues with milestone = "Week 3", "Week 6", or "Week 9"
**Highlight:** Critical integration tasks

---

## STEP 9: SET UP AUTOMATION

### GitHub Actions Workflow

Create `.github/workflows/project-automation.yml`:

```yaml
name: Project Board Automation

on:
  pull_request:
    types: [opened, reopened, closed]
  issues:
    types: [opened, closed]

jobs:
  update-project:
    runs-on: ubuntu-latest
    steps:
      - name: Move issue to "In Progress" when PR is opened
        if: github.event_name == 'pull_request' && github.event.action == 'opened'
        run: |
          # Move linked issue to "In Review" column
          echo "Moving issue to In Review"

      - name: Move issue to "Done" when PR is merged
        if: github.event_name == 'pull_request' && github.event.pull_request.merged == true
        run: |
          # Move linked issue to "Done" column
          echo "Moving issue to Done"
```

---

## STEP 10: WEEKLY STANDUP TEMPLATE

### Create Issue Template for Standup Notes

`.github/ISSUE_TEMPLATE/weekly_standup.md`:

```markdown
---
name: Weekly Standup
about: Weekly team standup notes
title: "Standup: Week [X] - [Date]"
labels: "standup"
---

## Week [X] Standup - [Date]

### Completed This Week

- [ ] Issue #X: [Title]
- [ ] Issue #Y: [Title]

### In Progress

- [ ] Issue #Z: [Title] (60% complete)

### Blocked

- [ ] Issue #A: [Title] - Waiting on [Dependency]

### Next Week Priorities

1. Issue #B: [Title]
2. Issue #C: [Title]

### Metrics

- **Issues Closed:** X/Y
- **Velocity:** Z story points
- **Budget Burn:** $X/$Y remaining

### Risks & Mitigations

- **Risk:** [Description]
- **Mitigation:** [Action plan]

### Demo This Week

- **What:** [Feature demo]
- **When:** [Date/Time]
- **Audience:** [Stakeholders]
```

---

## STEP 11: PROJECT METRICS DASHBOARD

### Track These KPIs Weekly

| Metric                      | Week 1   | Week 2   | Week 3 | ... | Week 12 |
| --------------------------- | -------- | -------- | ------ | --- | ------- |
| **Issues Closed**           | 0/32     | X/32     | Y/32   | ... | 32/32   |
| **Velocity (person-weeks)** | 0/60     | X/60     | Y/60   | ... | 60/60   |
| **Budget Burn**             | $0/$370K | $X/$370K | ...    | ... | $370K   |
| **Ingestion Items/Day**     | 0        | 18       | 280    | ... | 850     |
| **Judge #6 Coverage**       | 0%       | 10%      | 35%    | ... | 94%     |

---

## APPENDIX: FULL ISSUE LIST

### Judge #6 (16 Issues)

**Phase 1 (Weeks 1-3):**

1. JR Engine Core Framework
2. ATP 5-19 Policy Schema
3. Gemini API Integration
4. Validation API Endpoints

**Phase 2 (Weeks 4-6):** 5. Hybrid Enforcement (Gemini + PyTorch) 6. Performance Optimization 7. Extended Policy Categories (40+ Threats) 8. Audit Logging System

**Phase 3 (Weeks 7-9):** 9. Multi-Framework Compliance (SOC 2, HIPAA) 10. Custom Policy Authoring 11. Real-Time Dashboard 12. SLA Guarantees (99.2%)

**Phase 4 (Weeks 10-12):** 13. Horizontal Scaling Architecture 14. Advanced Analytics (Threat Trends) 15. API Rate Limiting & Quotas 16. Customer-Facing Compliance Reports

---

### Gemini Ingestion Layer (16 Issues)

**Phase 1 (Weeks 1-3):** 17. GKE Cluster Setup 18. Core CronJob Manifest 19. YouTube Collector Container 20. Twitter Collector Container 21. PostgreSQL Database Schema 22. Basic Tier Classification (Rule-Based) 23. Minimal AM Briefing (Email-Only)

**Phase 2 (Weeks 4-6):** 24. Gemini 2.0 Pro NLP Integration 25. Expanded Sources (News APIs) 26. RSS Feed Collector 27. Reddit Collector 28. Ethical Compliance Module 29. Performance Optimization

**Phase 3 (Weeks 7-9):** 30. Multi-Source Coverage Complete (24+ Sources) 31. AM Briefing Automation (Slack + PDF + Dashboard) 32. Quality Gates Enforcement

---

## NEXT STEPS

1. **Create Project:** Follow Step 1
2. **Create Labels & Milestones:** Run commands from Steps 3-4
3. **Create Issues:** Use script from Step 6 or manually create
4. **Organize Board:** Drag issues to appropriate columns (Step 7)
5. **Weekly Review:** Use standup template (Step 10)
6. **Track Metrics:** Update KPI dashboard weekly (Step 11)

---

**VERSION:** 1.0
**STATUS:** Ready for GitHub Project creation
**LAST UPDATED:** 2025-11-15

---

**END OF GITHUB PROJECT SETUP GUIDE**
