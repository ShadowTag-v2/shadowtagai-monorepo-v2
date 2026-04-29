# COR.53 Option C: Quick Start Guide

**You selected:** Full Stack (Balanced Velocity + Compliance) ✅

---

## 🚀 Next 30 Minutes

### 1. Get to Vertex AI Workbench

```bash
# SSH or open JupyterLab at:
# https://console.cloud.google.com/vertex-ai/workbench
```

### 2. Clone Repository

```bash
cd /home/jupyter/
git clone https://github.com/ehanc69/shadowtag_v4-fastapi-services.git
cd shadowtag_v4-fastapi-services
git checkout claude/cor-integration-deployment-01H68gzv26893rqrchCFHTww
```

### 3. Install Dependencies

```bash
pip install anthropic google-generativeai pyautogen --break-system-packages
```

### 4. Set API Keys

```bash
export ANTHROPIC_API_KEY = "REDACTED_API_KEY"
export GOOGLE_API_KEY="AIza-YOUR-KEY-HERE"  # Optional
```

### 5. Run Validation

```bash
python DEPLOYMENT_CHECKLIST.py
```

**Expected:** ✅ READY FOR PRODUCTION (25/25 checks passed)

---

## 🎯 First Production Task (Next 12 hours)

### Healthcare GTM Strategy

**Create:** `healthcare_gtm.py`

```python
from cor53_integration_guide import initialize_cor53, TaskRequest

# Initialize COR.53
cor = initialize_cor53(strict_mode=True)

# Define task
task = TaskRequest(
    task_id="GTM_TELEHEALTH_001",
    description="Develop comprehensive go-to-market strategy for telehealth vertical "
                "including market sizing, competitive analysis, HIPAA compliance, "
                "customer segmentation, pricing strategy, and 90-day execution plan",
    justification="Enables PNKLN's 30-vertical expansion. $50B TAM, zero capital, "
                 "48-hour completion. Creates replicable template for 29 remaining verticals.",
    requester="strategic_planning",
    priority="high",
    estimated_hours=12,
    cost_estimate=0,
    compliance_requirements=["HIPAA"]
)

# Execute
result = cor['process_task'](task)

# Results
print(f"Status: {result.overall_status}")
print(f"Violations: {len(result.validation.violations)}")

if result.overall_status == "COMPLETED":
    with open('telehealth_gtm_strategy.md', 'w') as f:
        f.write(result.execution_output['response'])
    print("✓ Strategy saved to telehealth_gtm_strategy.md")

# Export audit
cor['export_report']('execution_report.json')
```

**Run:**

```bash
python healthcare_gtm.py
```

**Expected:** Completes in 2-12 hours, generates telehealth GTM strategy with ShadowTag watermark

---

## 📊 Validation Checkpoints

After first task completion:

- [ ] Status = "COMPLETED" or "REVIEW_REQUIRED" (not "BLOCKED")
- [ ] Violation Level = V0_COMPLIANT or V1_MINOR (not V3/V4)
- [ ] Purpose Score ≥ 0.7
- [ ] Reasons Score ≥ 0.7
- [ ] Brakes Triggered = False
- [ ] ShadowTag watermark present in output
- [ ] Execution time < 48 hours
- [ ] API cost < $15

---

## 🔥 If Something Goes Wrong

### Task Blocked (V4_CRITICAL)?

**Check:** `result.validation.violations`
**Fix:** Improve justification, set `ra1_approval=True` if RA-1 operation

### "API Key Not Set"?

```bash
echo $ANTHROPIC_API_KEY  # Should show your key
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Import Errors?

```bash
pip install anthropic google-generativeai pyautogen --break-system-packages
# Restart Python kernel
```

### RA-1 Operations Not Blocked?

**CRITICAL:** Run `python Cor.Claude_Code_6_enforcement.py` - Test 2 MUST show "BLOCKED"
If not blocked, DO NOT deploy to production - fix BrakesGate first

---

## 📈 Scaling to 30 Verticals

Once first vertical succeeds, scale with batch processing:

```python
from cor53_integration_guide import initialize_cor53, TaskRequest

cor = initialize_cor53(strict_mode=True)

# 5 verticals at a time
verticals = [
    ('telehealth', 'HIPAA'),
    ('fintech', 'SEC'),
    ('legaltech', 'ABA'),
    ('edtech', 'FERPA'),
    ('manufacturing', 'ISO9001')
]

tasks = [
    TaskRequest(
        task_id=f"VERTICAL_GTM_{i+1:03d}",
        description=f"Develop GTM strategy for {vert} with {comp} compliance",
        justification=f"Part of 30-vertical expansion. Zero capital, doctrine-compliant.",
        requester="strategic_planning",
        priority="high",
        estimated_hours=10,
        cost_estimate=0,
        compliance_requirements=[comp]
    )
    for i, (vert, comp) in enumerate(verticals)
]

# Batch execute
results = cor['batch_process'](tasks)

# Summary
completed = sum(1 for r in results if r.overall_status == "COMPLETED")
print(f"Completed: {completed}/{len(results)} verticals")
```

**Timeline:** 5 verticals every 24-48 hours = 30 verticals in 6-12 days

---

## 💰 Cost Tracking

**Per Vertical:**

- Anthropic API: $3-15 (depends on strategy depth)
- Gemini API: $0 (free tier)
- Infrastructure: $0 (Vertex AI free tier)

**30 Verticals Total:** ~$90-450

**Cost Reduction:**

- Use Anthropic free tier credits
- Disable Gemini for low-risk tasks
- Cache validation results

---

## 📚 Full Documentation

- **Complete Guide:** `OPTION_C_DEPLOYMENT_GUIDE.md` (you are here - Quick Start)
- **Deployment Validation:** `DEPLOYMENT_CHECKLIST.py`
- **Component Docs:** Docstrings in each `.py` file

---

## ✅ Success = Ready for Next Vertical

When you see:

```
Status: COMPLETED
Violation Level: V0_COMPLIANT
Purpose Score: 1.00
Reasons Score: 0.90
✓ Strategy saved to telehealth_gtm_strategy.md
✓ Audit trail exported
```

**You're ready to scale to 30 verticals! 🎉**

---

**Questions? Issues?**

- Check `deployment_report.json` for detailed diagnostics
- Review `Cor.Claude_Code_6_audit_log.json` for violation patterns
- See `OPTION_C_DEPLOYMENT_GUIDE.md` for full troubleshooting guide

**Good luck with your deployment!** 🚀
