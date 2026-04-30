# PNKLN Core Stack™ - Analysis Prompts

This directory contains Gemini 2.0 Pro analysis prompts for comprehensive evaluation of PNKLN Core Stack components. These prompts enable structured, evidence-based analysis to identify strengths, weaknesses, risks, and optimization opportunities.

---

## 📋 Available Prompts

| Prompt                        | Target Component          | Phase          | Confidence Target | File                                                           |
| ----------------------------- | ------------------------- | -------------- | ----------------- | -------------------------------------------------------------- |
| **Gemini Ingestion Analysis** | Gemini Ingestion Layer    | Pre-production | ≥60%              | [gemini_ingestion_analysis.md](./gemini_ingestion_analysis.md) |
| **Judge 6 Analysis**         | Judge 6 Validation Layer | Production     | ≥70%              | [judge_six_analysis.md](./judge_six_analysis.md)               |

---

## 🎯 What Are These Prompts?

These are **comprehensive analysis frameworks** designed for Gemini 2.0 Pro to evaluate PNKLN Core Stack components across 8 key dimensions:

### Common Analysis Dimensions

Both prompts analyze:

1. **Architecture & Design** - System structure, scalability, resilience
2. **Performance** - Runtime efficiency or real-time latency
3. **Core Functionality** - Tier classification (Ingestion) or validation accuracy (Judge 6)
4. **Quality & Testing** - Code coverage, monitoring, quality gates
5. **Integration** - Cross-service communication and handoffs
6. **Cost Model** - Operational costs and efficiency
7. **Decision Quality** - Tier distribution or block rate effectiveness
8. **End-to-End Impact** - AM Briefing delivery or user experience

### Analysis Output Format

Each dimension receives:

- ✅ **Strengths**: What's working well
- ⚠️ **Weaknesses**: Gaps or issues
- 🔴 **Risks**: Potential production concerns
- 💡 **Recommendations**: Actionable improvements
- 📊 **Confidence Score**: 0-100% with reasoning

---

## 🚀 Quick Start Guide

### Step 1: Choose Your Prompt

**For Pre-Production Systems** (specs only, no telemetry):

- Use: [Gemini Ingestion Analysis](./gemini_ingestion_analysis.md)
- Confidence Target: ≥60%
- Best for: Architecture review, design validation, pre-deployment checks

**For Production Systems** (with real data):

- Use: [Judge 6 Analysis](./judge_six_analysis.md)
- Confidence Target: ≥70%
- Best for: Performance tuning, cost optimization, production health checks

---

### Step 2: Gather Context Documents

#### For Gemini Ingestion Layer Analysis

Required:

- [ ] [GEMINI_INGESTION_LAYER.md](../architecture/GEMINI_INGESTION_LAYER.md) (full specifications)
- [ ] GKE deployment manifests (CronJob YAML, container configs)
- [ ] Source integration documentation (API configs, crawler specs)

Optional (if available):

- [ ] Cost model spreadsheets
- [ ] Architecture diagrams
- [ ] Ethical crawling compliance docs

#### For Judge 6 Analysis

Required:

- [ ] Judge 6 source code (judge_six.py and related files)
- [ ] Production metrics:
  - Latency distributions (p50, p95, p99, p99.9)
  - Throughput data (validations/second)
  - Error rates and logs
  - FP/FN analysis reports
  - Cost breakdown (monthly bills, per-validation costs)
- [ ] Test coverage reports (HTML or JSON)

Optional (if available):

- [ ] Incident post-mortems
- [ ] Service dependency graphs
- [ ] User feedback on validation quality
- [ ] Dashboard screenshots

---

### Step 3: Run the Analysis

#### Using Gemini 2.0 Pro (Web Interface)

1. **Open Gemini**:
   - Visit: https://ai.google.dev/gemini
   - Or use Google AI Studio: https://aistudio.google.com/

2. **Create New Conversation**:
   - Start with: "I'm providing context documents for PNKLN Core Stack analysis."

3. **Upload Context**:
   - Method A: Paste full text of context documents
   - Method B: Upload files directly (Gemini supports PDFs, images, text)
   - For large codebases: Create a consolidated context file

   ```bash
   # Example: Consolidate context for Ingestion Layer
   cat docs/architecture/GEMINI_INGESTION_LAYER.md > /tmp/ingestion_context.txt
   echo "\n\n--- GKE Deployment Manifest ---\n" >> /tmp/ingestion_context.txt
   cat deployment/gke/ingestion-cronjob.yaml >> /tmp/ingestion_context.txt
   # Upload /tmp/ingestion_context.txt to Gemini
   ```

4. **Submit the Prompt**:
   - Open the relevant prompt file (e.g., `gemini_ingestion_analysis.md`)
   - Copy the **entire prompt** from the code block (starts with "You are a senior...")
   - Paste into Gemini

5. **Wait for Analysis**:
   - Gemini will process for 2-7 minutes depending on context size
   - Watch for structured output following the 8-dimension format

#### Using Gemini 2.0 Pro (API)

```python
import google.generativeai as genai

# Configure API
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.0-pro')

# Load context and prompt
with open('docs/architecture/GEMINI_INGESTION_LAYER.md', 'r') as f:
    context = f.read()

with open('docs/prompts/gemini_ingestion_analysis.md', 'r') as f:
    # Extract prompt from markdown (the text in the code block)
    prompt_content = extract_prompt_from_markdown(f.read())

# Combine and send
full_prompt = f"{context}\n\n{prompt_content}"
response = model.generate_content(full_prompt)

# Save results
with open('docs/prompts/results/gemini_ingestion_2025-11-15.md', 'w') as f:
    f.write(response.text)

print("Analysis complete! Results saved.")
```

---

### Step 4: Review the Output

Gemini's analysis should include:

```
**Dimension 1: Architecture & Design**

Strengths:
- [Bullet points with evidence]

Weaknesses:
- [Bullet points with evidence]

Risks:
- [Bullet points with probability/impact]

Recommendations:
- [Actionable items with expected impact]

Confidence Score: X%
Reasoning: [Why this confidence level]

---

[Dimensions 2-8 follow same format]

---

**Overall Summary**

Overall Strengths: [Top 3-5]
Overall Weaknesses: [Top 3-5]
Critical Risks: [Top 3]
Top Recommendations: [Top 5, prioritized]
Overall Confidence Score: X%

Pre-Production Readiness Assessment / Production Health Assessment:
[Detailed assessment with must-fix items]
```

---

### Step 5: Take Action

1. **Extract Action Items**:
   - Create a spreadsheet or GitHub issues for top recommendations
   - Prioritize by impact and effort (use Gemini's estimates)

2. **Address Must-Fix Items**:
   - For pre-production: Fix critical issues before deployment
   - For production: Schedule high-priority improvements

3. **Track Improvements**:
   - Re-run the analysis after implementing recommendations
   - Measure before/after (e.g., latency improvement, cost reduction)

4. **Archive Results**:
   - Save Gemini's full output to `results/` directory
   - Format: `{component}_{YYYY-MM-DD}.md`

---

## 📊 Comparison: Ingestion vs. Judge 6 Prompts

| Aspect               | Gemini Ingestion Prompt                     | Judge 6 Prompt                                         |
| -------------------- | ------------------------------------------- | ------------------------------------------------------- |
| **Target**           | Gemini Ingestion Layer                      | Judge 6 Validation Layer                               |
| **Phase**            | Pre-production (specs)                      | Production (telemetry)                                  |
| **Data Source**      | Architecture docs, manifests                | Source code, metrics, logs                              |
| **Confidence**       | ≥60% (limited data)                         | ≥70% (rich data)                                        |
| **Focus**            | Design validation, feasibility              | Performance tuning, optimization                        |
| **Key Metrics**      | Items/day, sources, cost/item, tier scores  | Latency, FP/FN, coverage, block rate                    |
| **Dimensions**       | Ethics, multi-source, tier classification   | Validation accuracy, test coverage, service integration |
| **Output Use**       | Pre-deployment checklist, design refinement | Performance fixes, cost optimization                    |
| **Update Frequency** | Once pre-prod, then quarterly               | Quarterly or after incidents                            |

**Complementary**: Run both to get full pipeline insight (collection + validation).

---

## 🎨 Customizing Prompts

### Adapting for Your Stack

If your stack differs from PNKLN, modify prompts:

1. **Change Component Names**:
   - Replace "Gemini Ingestion Layer" with your component
   - Update file references (e.g., "judge_six.py" → "your_validator.py")

2. **Adjust Metrics**:
   - Replace "Items/day" with your volume metric
   - Update latency targets (e.g., p99 ≤90ms → p99 ≤50ms)

3. **Modify Dimensions**:
   - Add stack-specific dimensions (e.g., "Fairness & Bias" for ML models)
   - Remove irrelevant ones (e.g., "Ethical Crawling" if not crawling)

4. **Update Confidence Targets**:
   - Pre-production: 50-60% (specs)
   - Early production: 60-70% (limited data)
   - Mature production: 70-80% (rich data)

### Example: Creating a New Prompt

```markdown
# My Custom Component - Analysis Prompt

## Meta Information

- **Target**: My Custom Component
- **Phase**: [Pre-production | Production]
- **Confidence Target**: ≥[60|70]%

## ANALYSIS PROMPT

You are a senior [role] conducting analysis of [component] in [system].

### Context

[Describe component, its role, what you have access to]

### Your Task

Analyze across [N] dimensions:

#### 1. [Dimension Name]

**Focus**: [What to evaluate]

**Evaluate**:

- [Question 1]
- [Question 2]
  ...

**Key Documents**: [List documents]

**Output Format**:
```

**Dimension 1: [Name]**
Strengths: ...
Weaknesses: ...
Risks: ...
Recommendations: ...
Confidence: X%
Reasoning: ...

```
...

[Repeat for all dimensions]

### Overall Summary
[Instructions for final summary]
```

---

## 📁 Results Archive

Save analysis outputs to `results/` directory:

```
docs/prompts/results/
├── gemini_ingestion_2025-11-15.md    # First pre-prod analysis
├── gemini_ingestion_2026-01-15.md    # Post-deployment analysis
├── gemini_ingestion_2026-04-15.md    # Quarterly review
├── judge_six_2025-11-15.md           # Production health check
├── judge_six_2026-02-15.md           # Post-optimization review
└── README.md                          # Results index
```

### Results README Template

```markdown
# Analysis Results Archive

## Gemini Ingestion Layer

| Date       | Phase      | Confidence | Key Findings                                              | Actions Taken              |
| ---------- | ---------- | ---------- | --------------------------------------------------------- | -------------------------- |
| 2025-11-15 | Pre-prod   | 62%        | Runtime feasible, cost model solid, need Gemini fallback  | Added caching (2025-12-01) |
| 2026-01-15 | Prod (1mo) | 68%        | Runtime stable at 43min, cost $73/mo, Tier 1 at 18% (low) | Tuned tier thresholds      |

## Judge 6

| Date       | Phase      | Confidence | Key Findings                                          | Actions Taken                          |
| ---------- | ---------- | ---------- | ----------------------------------------------------- | -------------------------------------- |
| 2025-11-15 | Production | 74%        | p99 violation (118ms vs 90ms), Gemini caching needed  | Implemented caching, re-run in 2 weeks |
| 2025-12-01 | Post-fix   | 76%        | p99 now 92ms (improved but still over), cost down 15% | Async validation added                 |
```

---

## 🔄 Analysis Workflow

### Quarterly Review Cycle

```
┌─────────────────────────────────────────────────────┐
│ Quarterly Analysis Workflow                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. Gather Latest Data                              │
│     - Update architecture docs                      │
│     - Pull production metrics (last 90 days)        │
│     - Collect incident reports                      │
│                                                      │
│  2. Run Analysis Prompt                             │
│     - Submit to Gemini 2.0 Pro                      │
│     - Review output for completeness                │
│                                                      │
│  3. Extract Action Items                            │
│     - Create GitHub issues for recommendations      │
│     - Prioritize by ROI (Gemini's estimates)        │
│                                                      │
│  4. Implement Improvements                          │
│     - Fix high-priority issues                      │
│     - Track progress (% complete)                   │
│                                                      │
│  5. Re-Run Analysis (Post-Fix)                      │
│     - Validate improvements                         │
│     - Measure impact (before/after metrics)         │
│                                                      │
│  6. Archive Results                                 │
│     - Save to results/ directory                    │
│     - Update results index                          │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Ad-Hoc Analysis Triggers

Run analysis immediately after:

- Major architecture changes
- Production incidents (P0/P1)
- Significant metric degradation (e.g., latency spike, cost increase)
- New component deployment
- Quarterly business reviews

---

## 💡 Best Practices

### For Pre-Production Analysis

1. **Be Thorough with Specs**: The more detailed your specs, the higher Gemini's confidence
2. **Include Diagrams**: Upload architecture diagrams for visual context
3. **Document Assumptions**: Call out estimates explicitly (e.g., "assuming 1,600 items/day")
4. **Focus on Design**: Ask Gemini to stress-test architecture choices
5. **Iterate**: Re-run analysis after design changes

### For Production Analysis

1. **Use Real Data**: Provide actual metrics, not projections
2. **Include Time Series**: Show trends (e.g., latency over last 30 days)
3. **Add Context**: Explain anomalies (e.g., "spike on Nov 3 due to Black Friday traffic")
4. **Root Cause Logs**: Include error logs for issues Gemini should diagnose
5. **Track Improvements**: Re-run after fixes to validate impact

### General Tips

- **Separate Concerns**: Run one prompt per component; don't mix Ingestion + Judge 6
- **Version Control**: Commit analysis results to git for history
- **Cross-Reference**: Compare analyses over time to track trends
- **Automate**: Script the analysis process for consistency
- **Share**: Circulate results with the team; discuss in retrospectives

---

## 🛠️ Troubleshooting

### Issue: Gemini's Analysis is Too Brief

**Solution**: Ask follow-up questions

```
"Please expand Dimension 3 with more specific examples from the specs."
"Can you provide code-level recommendations for the caching strategy?"
```

### Issue: Low Confidence Scores

**Causes**:

- Insufficient context documents
- Missing production data
- Vague specifications

**Solutions**:

- Add more detailed specs or metrics
- Clarify assumptions in the prompt
- Accept lower confidence for pre-production (60% is OK)

### Issue: Recommendations are Vague

**Solution**: Request specificity

```
"Can you make Recommendation #2 more actionable? Include specific implementation steps."
"What is the expected latency improvement from adding caching, based on the call patterns?"
```

### Issue: Gemini Misinterprets Data

**Solution**: Provide clarification

```
"The p99 graph shows spikes to 120ms during peak hours (14:00-16:00 UTC), not a constant 120ms."
"Cost/item should be calculated as monthly_cost / (items_per_day * 30), not as shown."
```

---

## 📞 Support & Feedback

### Questions?

- **Prompt structure**: See examples in `gemini_ingestion_analysis.md` and `judge_six_analysis.md`
- **Gemini API**: https://ai.google.dev/gemini-api/docs
- **Analysis methodology**: Based on structured component analysis best practices

### Improving the Prompts

Found a gap or improvement?

1. Update the relevant prompt file
2. Document changes in the version history table
3. Re-run the analysis to validate improvements
4. Share findings with the team

### Related Resources

- [PNKLN Core Stack Architecture](../architecture/PNKLN_CORE_STACK.md)
- [Gemini Ingestion Layer Specs](../architecture/GEMINI_INGESTION_LAYER.md)
- [Main Documentation README](../README.md)

---

## 📅 Maintenance Schedule

| Task                                  | Frequency              | Owner               |
| ------------------------------------- | ---------------------- | ------------------- |
| Update prompts for new dimensions     | As needed              | Architecture team   |
| Run pre-production analysis           | Before each deployment | Deployment lead     |
| Run production analysis               | Quarterly              | SRE team            |
| Review and prioritize recommendations | Quarterly              | Engineering manager |
| Archive old results                   | Quarterly              | Documentation team  |

---

**Directory Maintained By**: PNKLN Analysis Team
**Review Cycle**: Quarterly or after major component updates
**Last Updated**: 2025-11-15

---

## 🗺️ Next Steps

1. **Run Your First Analysis**:
   - Choose [Gemini Ingestion Analysis](./gemini_ingestion_analysis.md) or [Judge 6 Analysis](./judge_six_analysis.md)
   - Follow the Quick Start Guide above
   - Save results to `results/` directory

2. **Create Results Index**:
   - Add a `results/README.md` to track all analyses
   - Include: Date, component, confidence, key findings, actions taken

3. **Set Up Recurring Analysis**:
   - Schedule quarterly reviews
   - Automate data gathering if possible
   - Track improvement trends over time

4. **Share Insights**:
   - Present findings in team meetings
   - Use recommendations to inform roadmap
   - Celebrate wins when metrics improve!

---

**Happy Analyzing! 🚀**
