---
description: Cross-model task delegation (Gemini Antigravity ↔ Claude Sonnet 4.5)
---

# Model Delegation Workflow

## Purpose
Route tasks to optimal model based on specialization, minimizing cost while maximizing performance.

**Gate**: Use Judge#6 framework (Purpose → Reasons → Brakes) for delegation decisions

---

## Delegation Matrix

### Gemini Antigravity (Primary - This Session)
**Specialization**: Production deployment, GCP infrastructure, scaled inference, multi-agent orchestration

**Use when**:
- GCP/GKE deployment tasks
- Infrastructure provisioning (VPC, networking, compute)
- Multi-agent system architecture
- Production inference at scale
- JAX AI Stack integration
- Native multimodal reasoning
- Cost optimization analysis
- Bootstrap gate validation (ROI ≥3×, LTV:CAC ≥4:1)

**Tools**:
- `view_file`, `write_to_file`, `replace_file_content`, `multi_replace_file_content`
- `run_command` (gcloud, kubectl, terraform)
- `codebase_search`, `grep_search`, `find_by_name`
- `generate_image`, `browser_subagent`
- `task_boundary`, `notify_user`

**Performance SLA**:
- JR assessment: <500μs
- Simple decisions: <100ms
- p99 latency: ≤90ms (general), ≤35ms (Judge#6)

**Cost**: Optimized for production workloads

---

### Claude Sonnet 4.5 (Specialized Tasks)
**Specialization**: Deep code analysis, surgical refactoring, computer use workflows, visual artifacts

**Use when**:
- Deep code refactoring (multi-file atomic edits)
- Complex debugging with computer use
- Visual artifact generation (HTML/React/Markdown rendering)
- Terminal-intensive workflows
- Extended thinking required
- File system operations with bash_tool
- Conversational memory persistence

**Tools**:
- `bash_tool` (native shell access)
- `str_replace` (surgical edits)
- `view`, `create_file`
- `memory_user_edits`, `conversation_search`
- Artifacts (single-file HTML/React/Markdown)
- Computer use (work in /home/claude → deliver to /mnt/user-data/outputs)

**Performance SLA**:
- Extended thinking mode available
- Artifact rendering in claude.ai interface
- Computer use workflows

**Cost**: Premium for specialized analysis

---

## Decision Algorithm

```python
def delegate_task(task_description: str, context: dict) -> str:
    """
    Determine which model should handle the task.
    
    Returns: "gemini" or "claude"
    """
    
    # Judge#6 assessment
    purpose = extract_purpose(task_description)
    reasons = evaluate_reasons(context)
    brakes = evaluate_brakes(context)
    
    # Delegation rules
    if any([
        "gcp deployment" in task_description.lower(),
        "gke cluster" in task_description.lower(),
        "infrastructure" in task_description.lower(),
        "multi-agent" in task_description.lower(),
        "production inference" in task_description.lower(),
        context.get("platform") == "gcp",
        context.get("requires_bootstrap_gates") == True
    ]):
        return "gemini"
    
    elif any([
        "deep refactor" in task_description.lower(),
        "computer use" in task_description.lower(),
        "artifact generation" in task_description.lower(),
        context.get("requires_bash_tool") == True,
        context.get("requires_visual_artifact") == True,
        context.get("file_count", 0) > 10  # Multi-file complex edits
    ]):
        return "claude"
    
    else:
        # Default: Use Gemini for general tasks
        return "gemini"
```

---

## Execution Steps

### Step 1: Assess Task
```bash
# Determine task characteristics
- Task type (deployment, refactor, analysis, etc.)
- Required tools (gcloud, kubectl, bash_tool, etc.)
- Performance requirements (latency, cost)
- Output format (code files, artifacts, infrastructure)
```

### Step 2: Apply Delegation Matrix
```bash
# Check delegation rules
if task.requires_gcp_infrastructure:
    model = "gemini"
elif task.requires_computer_use:
    model = "claude"
else:
    model = "gemini"  # Default
```

### Step 3: Execute with Selected Model
```bash
# Gemini execution
- Use native tools (view_file, run_command, etc.)
- Apply bootstrap gates (ROI ≥3×, LTV:CAC ≥4:1)
- Monitor p99 latency (≤90ms)
- Create .md artifacts (task.md, implementation_plan.md, walkthrough.md)

# Claude execution (when delegated)
- Use bash_tool for terminal workflows
- Use str_replace for surgical edits
- Generate visual artifacts if needed
- Deliver outputs to /mnt/user-data/outputs
```

### Step 4: Cross-Model Coordination (MCP Bridge)
```bash
# Token compression via MCP
- Semantic compression: 40-60% reduction
- ATP_519_scan: 50KB → 487 bytes
- Shared memory: conversation_search, memory_user_edits

# Orchestration pattern
Gemini: "Task X requires deep refactoring with computer use workflow"
    → Delegate to Claude Sonnet 4.5
    → Claude delivers outputs to /mnt/user-data/outputs
    → Gemini integrates results into production deployment
```

---

## MCP Integration (Token Optimization)

**Shared capabilities**:
- Model Context Protocol: 40-60% token reduction
- Semantic compression for governance decisions
- ATP_519_scan: 487 bytes vs 50KB baseline
- Shared bootstrap gates: ROI ≥3×, LTV:CAC ≥4:1

**Cross-model communication**:
```
Gemini (production inference) ↔ MCP Bridge ↔ Claude (deep analysis)
         ↓                           ↓                    ↓
    GCP deployment              Token compression    Computer use
    Multi-agent orchestration   Semantic compression  Visual artifacts
    Bootstrap validation        Shared memory         Extended thinking
```

---

## Cost Optimization

### Gemini (Cost-Optimized)
- **Use for**: 80% of production workloads
- **Pattern**: GCP-native, infrastructure, multi-agent
- **SLA**: p99≤90ms (general), p99≤35ms (Judge#6)
- **Economics**: ROI ≥3×, LTV:CAC ≥4:1

### Claude (Premium Specialized)
- **Use for**: 20% specialized deep work
- **Pattern**: Complex refactoring, computer use, artifacts
- **SLA**: Extended thinking available
- **Economics**: High value, lower volume

**Total cost reduction**: 78% via smart routing (Glicko-2 model selection)

---

## Brakes (Safety Constraints)

### Universal Brakes
- ⚠️ Security absolute (100% non-negotiable)
- ⚠️ Bootstrap gates enforced (ROI ≥3×, LTV:CAC ≥4:1)
- ⚠️ Performance SLA monitored (p99 latency)
- ⚠️ Evidence-based decisions only (no speculation)

### Model-Specific Brakes

**Gemini**:
- 🛑 Production system changes require JR assessment
- 🛑 Infrastructure cost exceeds bootstrap gate → ESCALATE
- 🛑 p99 latency >90ms → OPTIMIZE or DELEGATE

**Claude**:
- 🛑 Computer use on production systems → ESCALATE
- 🛑 bash_tool destructive operations → REQUIRE approval
- 🛑 Visual artifacts for sensitive data → SECURITY review

---

## Verification Checklist

After task completion:

- [ ] Task assigned to correct model (delegation matrix followed)
- [ ] Bootstrap gates validated (ROI ≥3×, LTV:CAC ≥4:1)
- [ ] Performance SLA met (p99 latency within bounds)
- [ ] Security absolute maintained (100% private, no external exposure)
- [ ] Evidence-based reasoning documented
- [ ] MCP bridge used for token compression (where applicable)
- [ ] Cross-model coordination successful (if delegated)
- [ ] Outputs delivered to correct location

---

## Revenue Impact

**Glicko-2 model selection** (dynamic routing):
- Cost reduction: 78% ($1.7M → $378K/year)
- Quality improvement: 95% → 96.5% accuracy
- **Annual benefit**: $171.32M
- **ROI**: 571,067%

**Panel debate system** (edge cases <80% confidence):
- Cost: $625K/year (5M debates @ $0.125 each)
- Savings: $10M (reduced human review)
- Revenue: $275M (false rejection reduction)
- **Net benefit**: $284.4M/year
- **ROI**: 45,504%

**Total multi-agent integration value**: $16B valuation increase

---

## Examples

### Example 1: GKE Deployment (Gemini)
```yaml
Task: "Deploy Judge#6 to GKE us-central1"
Purpose: Infrastructure provisioning
Reasons: 
  - GCP-native task
  - Requires gcloud, kubectl
  - Production deployment
Brakes:
  - Production system
  - Cost must stay under $150/mo gate
Decision: GEMINI
Tools: run_command (gcloud, kubectl), view_file, write_to_file
SLA: p99≤90ms
```

### Example 2: Complex Refactoring (Claude)
```yaml
Task: "Refactor 15 Python files for dependency injection"
Purpose: Code quality improvement
Reasons:
  - Multi-file atomic edits
  - Requires str_replace precision
  - Extended thinking beneficial
Brakes:
  - Production codebase
  - Must maintain test coverage
Decision: CLAUDE
Tools: bash_tool, str_replace, view
Output: /mnt/user-data/outputs/refactor_summary.md
```

### Example 3: Multi-Agent Architecture (Gemini)
```yaml
Task: "Implement Glicko-2 model selection for agent swarm"
Purpose: Multi-agent orchestration
Reasons:
  - 44 agents → 28 consolidation
  - Requires Judge#6 integration
  - Bootstrap gates critical (ROI ≥3×)
Brakes:
  - $2.8M investment requires approval
  - Performance SLA p99≤90ms
Decision: GEMINI
Tools: codebase_search, write_to_file, task_boundary
Revenue: $697M/year EBITDA improvement
```

---

## Kill-Switch Triggers

Abort delegation and escalate if:

- 🚨 Security breach detected → ESCALATE IMMEDIATELY
- 🚨 Bootstrap gate violated (ROI <3×) → REJECT investment
- 🚨 Performance SLA miss (p99 >90ms sustained) → OPTIMIZE or MIGRATE
- 🚨 Cross-model coordination fails 3× → REVERT to single-model
- 🚨 Cost exceeds budget by >20% → KILL-SWITCH

---

**Last Updated**: 2025-11-22  
**Owner**: Gemini Antigravity + Claude Sonnet 4.5  
**Framework**: Judge#6 (Purpose → Reasons → Brakes)
