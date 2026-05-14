# PNKLN Analysis Prompts

This directory contains comprehensive analysis prompts for PNKLN Core Stack™ components, designed for use with large language models (primarily Gemini 2.0 Pro).

## Directory Structure

```
prompts/
├── README.md (this file)
└── analysis/
    ├── gemini-ingestion-layer-analysis.md
    └── (future: judge-6-analysis.md, autogen-analysis.md, etc.)
```

## Available Prompts

### 1. Gemini Ingestion Layer Analysis
**File**: `analysis/gemini-ingestion-layer-analysis.md`
**Target Model**: Gemini 2.0 Pro
**Status**: ✅ Ready for Execution
**Version**: 1.0
**Date**: 2025-11-15

#### Purpose
Comprehensive pre-production analysis of the Gemini Ingestion Layer, PNKLN's intelligence collection pipeline.

#### Key Features
- **Architecture Review**: GKE CronJob multi-container orchestration
- **Performance Analysis**: ~45 min/night runtime efficiency target
- **Quality Gates**: Multi-dimensional (items, sources, costs, scores)
- **Ethical Compliance**: robots.txt, rate limiting, transparency
- **Multi-Source Coverage**: YouTube, Twitter, News, Reddit, etc.
- **Tier Classification**: Tier 1/2/3 distribution and optimization
- **AM Briefing Delivery**: 6:00 AM SLA effectiveness
- **Cost Model**: Monthly operational budget (~$77)

#### Confidence Target
≥60% (pre-production, specifications-based analysis)

#### Expected Analysis Time
10-15 minutes (Gemini 2.0 Pro)

#### Required Supporting Documents
- GKE CronJob specifications
- Container orchestration configs
- Source configuration matrix
- Cost breakdown spreadsheet
- Integration API contracts
- Ethical compliance policy docs

#### Success Criteria
- Identify ≥3 architectural risks before production
- Validate 45-minute runtime assumption
- Assess ethical compliance robustness
- Recommend ≥5 cost optimizations
- Provide go/no-go recommendation

#### Documentation
See `docs/prompts/gemini-ingestion-layer-prompt-design.md` for:
- Design rationale
- Comparison to Judge #6 prompt
- Implementation notes
- Iteration guidelines

---

## Prompt Design Philosophy

### Shared Structural Framework
All PNKLN analysis prompts follow a consistent structure:
1. **Executive Summary Request**: Overview of system role and analysis scope
2. **System Context**: Architecture, metrics, integration points, unique features
3. **Detailed Analysis Sections**: Component-specific deep dives
4. **Output Format**: Executive summary, findings, recommendations, clarifications
5. **Confidence Calibration**: Realistic targets based on available data
6. **Success Criteria**: Measurable outcomes for analysis quality

### Component-Specific Customization
Each prompt is tailored to the component's role in PNKLN:
- **Enforcement Systems** (Judge #6): Latency, accuracy, real-time validation
- **Collection Systems** (Ingestion Layer): Volume, diversity, batch efficiency
- **Orchestration Systems** (AutoGen): Coordination, fault tolerance, state management
- **Processing Systems** (Cognitive): Reasoning depth, context handling

### Confidence Targets
- **≥70%**: Production systems with telemetry (logs, metrics, user feedback)
- **≥60%**: Pre-production systems with specs only
- **≥50%**: Conceptual designs without implementation details

---

## Usage Instructions

### 1. Select Appropriate Prompt
Choose based on:
- **Component**: Which PNKLN system are you analyzing?
- **Stage**: Pre-production (specs) vs production (telemetry)?
- **Goal**: Architecture review, performance optimization, cost analysis, etc.

### 2. Gather Supporting Documents
Each prompt specifies required inputs:
- Architecture specifications
- Configuration files
- Cost models
- Integration contracts
- Performance benchmarks (if available)

### 3. Execute Analysis
**With Gemini 2.0 Pro**:
```python
import google.generativeai as genai

# Load prompt
with open('prompts/analysis/gemini-ingestion-layer-analysis.md', 'r') as f:
    prompt = f.read()

# Configure model
model = genai.GenerativeModel('gemini-2.0-pro-exp')

# Add supporting documents to prompt
full_prompt = f"{prompt}\n\n## Supporting Documents\n\n{your_docs_here}"

# Generate analysis
response = model.generate_content(full_prompt)
print(response.text)
```

**With Claude Code / Agent SDK**:
```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Load prompt
with open('prompts/analysis/gemini-ingestion-layer-analysis.md', 'r') as f:
    prompt = f.read()

# Execute (if using Claude for meta-analysis)
async for message in query(
    prompt=f"Review this analysis prompt and suggest improvements:\n\n{prompt}",
    options=ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code"}
    )
):
    print(message)
```

### 4. Review Outputs
Expected deliverables:
- **Executive Summary**: Go/no-go, top strengths/risks
- **Detailed Findings**: Per-section analysis with confidence levels
- **Prioritized Recommendations**: Critical, important, strategic actions
- **Clarifications Needed**: Missing information to improve confidence

### 5. Iterate
- Address clarification questions
- Add missing documentation
- Re-run analysis with updated inputs
- Compare findings across iterations

---

## Prompt Comparison Matrix

| Prompt | System Role | Architecture | Key Metrics | Confidence | Status |
|--------|-------------|--------------|-------------|------------|--------|
| **Ingestion Layer** | Collection (upstream) | GKE CronJob | Items/day, sources, cost/item | ≥60% | ✅ Ready |
| **Judge #6** | Enforcement (downstream) | Hybrid AI (3-layer) | p99 latency, FP/FN rates | ≥70% | 🔄 Planned |
| **AutoGen** | Orchestration | Multi-agent LLM | Coordination latency, success rate | TBD | 📋 Future |
| **Cognitive** | Processing | LangGraph state machine | Reasoning depth, context retention | TBD | 📋 Future |
| **ShadowTag** | Watermarking | Embedding pipeline | Detection rate, robustness | TBD | 📋 Future |

---

## Best Practices

### 1. Use Appropriate Model
- **Gemini 2.0 Pro**: Long-context analysis (architecture reviews, multi-doc synthesis)
- **Claude Sonnet 4**: Deep reasoning, code review, security analysis
- **GPT-4**: Baseline comparison, alternative perspective

### 2. Provide Sufficient Context
- Don't rely on prompt alone - attach specs, configs, metrics
- More documentation = higher confidence analysis
- Flag missing information early

### 3. Calibrate Expectations
- Pre-prod prompts (≥60%) will have more assumptions
- Production prompts (≥70%) should be grounded in data
- Don't force confidence - flag uncertainties honestly

### 4. Iterate Based on Findings
- Initial analysis identifies gaps → fill gaps → re-analyze
- Use recommendations to prioritize next documentation efforts
- Track confidence improvement across iterations

### 5. Cross-Reference Prompts
- Compare findings across PNKLN components
- Look for integration bottlenecks (Ingestion → Judge #6)
- Use combined prompts for end-to-end flow analysis

---

## Contribution Guidelines

### Adding New Prompts
1. **Create File**: `analysis/[component-name]-analysis.md`
2. **Follow Template**: Use Ingestion Layer as structural reference
3. **Customize Sections**: Adapt to component's unique role
4. **Set Confidence Target**: Match available data (specs vs telemetry)
5. **Document Design**: Add rationale doc in `docs/prompts/`
6. **Update README**: Add entry to prompt comparison matrix

### Prompt Quality Checklist
- [ ] Clear system context (architecture, metrics, integration)
- [ ] ≥8 detailed analysis sections (tailored to component)
- [ ] Specified output format (summary, findings, recommendations)
- [ ] Realistic confidence target with calibration notes
- [ ] ≥10 measurable success criteria
- [ ] Required supporting documents listed
- [ ] Expected analysis time estimated
- [ ] Comparison to related prompts (optional)

### Versioning
- **Version 1.0**: Initial release
- **Version 1.x**: Minor updates (clarifications, typo fixes)
- **Version 2.0**: Major revisions (new sections, restructured)

---

## Examples & Templates

### Quick Start: Run Ingestion Layer Analysis

```bash
# 1. Prepare supporting documents
mkdir -p analysis-inputs/ingestion-layer
cp ~/gke-cronJob-spec.yaml analysis-inputs/ingestion-layer/
cp ~/source-matrix.csv analysis-inputs/ingestion-layer/
cp ~/cost-model.xlsx analysis-inputs/ingestion-layer/

# 2. Run analysis (example with Gemini API)
python << 'EOF'
import google.generativeai as genai
import glob

genai.configure(api_key='YOUR_API_KEY')
model = genai.GenerativeModel('gemini-2.0-pro-exp')

# Load prompt
with open('prompts/analysis/gemini-ingestion-layer-analysis.md', 'r') as f:
    prompt = f.read()

# Load supporting docs
docs = ""
for file in glob.glob('analysis-inputs/ingestion-layer/*'):
    with open(file, 'r') as f:
        docs += f"\n\n### {file}\n\n```\n{f.read()}\n```"

# Generate analysis
response = model.generate_content(f"{prompt}\n\n## Supporting Documents{docs}")

# Save results
with open('analysis-outputs/ingestion-layer-results.md', 'w') as f:
    f.write(response.text)

print("✅ Analysis complete: analysis-outputs/ingestion-layer-results.md")
EOF

# 3. Review results
cat analysis-outputs/ingestion-layer-results.md
```

---

## Resources

### Documentation
- **Design Rationale**: `docs/prompts/gemini-ingestion-layer-prompt-design.md`
- **Migration Guide**: `MIGRATION.md` (Claude Agent SDK)

### Related Projects
- **PNKLN Core Stack**: (repository links)
- **Claude Code Optimization**: `setup-claude-gke.sh`

### External References
- [Gemini 2.0 Pro Documentation](https://ai.google.dev/gemini-api/docs)
- [Claude Agent SDK](https://docs.claude.com/en/api/agent-sdk/overview)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)

---

## Support & Feedback

### Issues
Report issues with prompts:
- Unclear instructions
- Missing sections
- Incorrect assumptions
- Model compatibility problems

### Enhancements
Suggest improvements:
- New analysis sections
- Additional prompts for other components
- Better output formatting
- Visualization templates

### Contact
- **Project**: PNKLN Core Stack Team
- **Repository**: `aiyou-fastapi-services`
- **Documentation**: `docs/prompts/`

---

**Last Updated**: 2025-11-15
**Maintainer**: PNKLN Core Stack Team
**Status**: ✅ Active Development
