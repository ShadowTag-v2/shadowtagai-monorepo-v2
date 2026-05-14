# PNKLN Prompt Templates

**Copy-paste ready prompts for instant workflow automation**

---

## Quick Navigation

| # | Template | Use When | Time Saved |
|---|----------|----------|------------|
| 01 | [Deep Research](#01-deep-research) | Need comprehensive analysis | 80% (2-4 hrs → 15-30 min) |
| 02 | [Design Critique](#02-design-critique) | Reviewing UI/UX | 75% (30-60 min → 5-15 min) |
| 03 | [High-Converting Copy](#03-high-converting-copy) | Creating marketing copy | 85% (1-2 hrs → 5-10 min) |
| 04 | [Monetization Strategy](#04-monetization-strategy) | Designing pricing | 85% (2-3 hrs → 10-20 min) |
| 05 | [Workflow Optimization](#05-workflow-optimization) | Simplifying processes | 80% (1-2 hrs → 10-20 min) |
| 06 | [Prompt Engineering](#06-prompt-engineering) | Creating AI prompts | 80% (30-60 min → 5-10 min) |
| 07 | [New Product Launch](#07-new-product-launch) | Launching products | 90% (2-3 days → 4-6 hrs) |
| 08 | [Marketing Campaign](#08-marketing-campaign) | Running campaigns | 85% (1-2 days → 3-4 hrs) |
| 09 | [Revenue Optimization](#09-revenue-optimization) | Optimizing existing revenue | 85% (2-3 hrs → 10-20 min) |
| 10 | [Quick Reference](#10-quick-reference) | Fast lookup | Always useful |

---

## How to Use These Templates

### Step 1: Choose Your Template
Pick the template that matches your goal from the table above.

### Step 2: Open the Template File
```bash
# Example
cat pnkln/templates/01-deep-research.md
```

### Step 3: Copy the Prompt
Find the "Copy-Paste Prompt" section and copy it.

### Step 4: Fill in Your Details
Replace placeholders with your specific information:
- `[YOUR TOPIC]` → Your actual topic
- `[X]` → Your numbers
- `[$Y]` → Your prices
- etc.

### Step 5: Execute
Paste into your PNKLN-enabled system and let the agents work.

---

## Template Details

### 01: Deep Research
**File**: `01-deep-research.md`
**Activates**: ResearchAgent + ResearchExplorerSkill
**Perfect for**:
- Market research
- Competitive analysis
- Assumption validation
- Multi-perspective exploration

**Example**:
```
@research AI agent orchestration frameworks for 2025
Depth: Exhaustive
Challenge assumptions about Python dominance
```

---

### 02: Design Critique
**File**: `02-design-critique.md`
**Activates**: DesignAgent + DesignCriticSkill
**Perfect for**:
- UI/UX review
- Design simplification
- Jobs-style critique
- Visual feedback

**Example**:
```
@design-critique ./landing-page.png
Ruthlessness: Jobs-Level
Focus: Simplicity and function over decoration
```

---

### 03: High-Converting Copy
**File**: `03-high-converting-copy.md`
**Activates**: CopyAgent + CopyConverterSkill
**Perfect for**:
- Landing pages
- Email sequences
- Ad copy
- CTAs

**Example**:
```
@copy Landing Page for AI workflow tool
Target: CTOs at Series A startups
Benefit: Ship 3x more features without hiring
```

---

### 04: Monetization Strategy
**File**: `04-monetization-strategy.md`
**Activates**: RevenueAgent + MonetizationArchitectSkill
**Perfect for**:
- Pricing strategy
- Revenue model design
- Subscription tiers
- Payment systems

**Example**:
```
@revenue Design monetization for developer API
Stage: Pre-launch
Target: $50K MRR in 6 months
```

---

### 05: Workflow Optimization
**File**: `05-workflow-optimization.md`
**Activates**: WorkflowRefinerSkill
**Perfect for**:
- Process simplification
- Bottleneck removal
- Automation discovery
- Efficiency gains

**Example**:
```
Optimize: Feature development workflow
Current: 4 days, 22 hours of work
Goal: 50% time reduction
```

---

### 06: Prompt Engineering
**File**: `06-prompt-engineering.md`
**Activates**: PromptCraftSkill
**Perfect for**:
- AI prompt creation
- Instruction optimization
- Few-shot examples
- LLM task design

**Example**:
```
@prompt Create prompt for technical → customer copy
Model: Claude
Output: Benefit-focused feature descriptions
```

---

### 07: New Product Launch
**File**: `07-new-product-launch.md`
**Activates**: ProjectDeepAgent (orchestrates all agents)
**Perfect for**:
- Complete product launches
- Go-to-market execution
- Multi-phase projects
- End-to-end workflows

**Example**:
```
@project-deep Launch AgentFlow platform
Timeline: 30 days
Goal: 1,000 signups, 100 paying customers
```

---

### 08: Marketing Campaign
**File**: `08-marketing-campaign.md`
**Activates**: ProjectDeepAgent + CopyAgent + ResearchAgent
**Perfect for**:
- Multi-channel campaigns
- Product announcements
- Lead generation
- Brand awareness

**Example**:
```
Create marketing campaign:
- Product Hunt launch
- Email + Twitter + LinkedIn
- Goal: 1,000 signups in 4 weeks
```

---

### 09: Revenue Optimization
**File**: `09-revenue-optimization.md`
**Activates**: RevenueAgent + ResearchAgent
**Perfect for**:
- Optimizing existing pricing
- Reducing churn
- Expansion revenue
- ARPU increase

**Example**:
```
Optimize revenue:
Current MRR: $15K, Churn: 8%
Goal MRR: $50K, Churn: 3%
Timeline: 6 months
```

---

### 10: Quick Reference
**File**: `10-quick-reference.md`
**Activates**: N/A (Reference guide)
**Perfect for**:
- Fast command lookup
- Common patterns
- Troubleshooting
- Pro tips

---

## Template Selection Guide

### "I'm researching..."
→ **Template 01**: Deep Research

### "I need feedback on this design..."
→ **Template 02**: Design Critique

### "I need to write marketing copy..."
→ **Template 03**: High-Converting Copy

### "How should I price my product?"
→ **Template 04**: Monetization Strategy

### "This workflow is too slow..."
→ **Template 05**: Workflow Optimization

### "I need to create an AI prompt..."
→ **Template 06**: Prompt Engineering

### "I'm launching a new product..."
→ **Template 07**: New Product Launch

### "I need to run a marketing campaign..."
→ **Template 08**: Marketing Campaign

### "I want to grow revenue..."
→ **Template 09**: Revenue Optimization

### "I just need a quick reference..."
→ **Template 10**: Quick Reference

---

## Customization Tips

### Making Templates Your Own

1. **Add Your Context**
   - Include your industry-specific terminology
   - Reference your brand guidelines
   - Add your success metrics

2. **Adjust Depth/Ruthlessness**
   - For quick tasks: Set depth to "surface" or "medium"
   - For critical decisions: Set depth to "exhaustive"
   - For gentle feedback: Reduce ruthlessness level

3. **Combine Templates**
   - Research (01) → Monetization (04) → Copy (03)
   - Design (02) → Copy (03) for landing pages
   - Workflow (05) → Prompt (06) for automation

4. **Create Your Own**
   - Copy existing template structure
   - Modify for your specific use case
   - Save as `custom-[name].md`

---

## Common Workflows

### Launch Workflow
```
1. Template 01: Research market
2. Template 04: Design pricing
3. Template 03: Write landing page copy
4. Template 02: Review landing page design
5. Template 08: Create launch campaign
```

### Optimization Workflow
```
1. Template 05: Optimize internal workflow
2. Template 09: Optimize revenue
3. Template 03: Update messaging
4. Template 08: Re-engage customers
```

### Content Creation Workflow
```
1. Template 01: Research topic
2. Template 06: Create content prompts
3. Template 03: Write copy
4. Template 02: Review visuals
```

---

## Pro Tips

### 1. Start Simple
Don't fill in every optional field. Start with required fields and iterate.

### 2. Use Examples
Each template has example usage. Copy and modify those first.

### 3. Chain Templates
For complex projects, use Template 07 or 08 which orchestrate multiple skills.

### 4. Save Your Variations
When you customize a template, save it for reuse.

### 5. Track Results
Note which templates save you the most time for your work.

---

## Template Format

All templates follow this structure:

```markdown
# Template XX: [Name]

## Purpose
[What this template does]

## When to Use
[Specific use cases]

## Copy-Paste Prompt
[Ready-to-use prompt with placeholders]

## Example Usage
[Real example with filled-in values]

## Expected Output Structure
[What you'll get back]

## Tips for Best Results
[How to get better outputs]

## Related Templates
[Other templates that might help]
```

---

## Getting Started

**New to PNKLN?**
1. Start with Template 10 (Quick Reference)
2. Try Template 01 (Deep Research) on a simple topic
3. Experiment with Template 03 (High-Converting Copy)
4. Graduate to Template 07 (New Product Launch) for full workflows

**Already familiar?**
- Jump to the template you need
- Customize for your specific use case
- Chain templates for complex projects

---

## Support

- **Full Integration Guide**: See `/pnkln/integration-guide.md`
- **Skills Reference**: See `/pnkln/skills-registry.yaml`
- **Agents Reference**: See `/pnkln/agents-registry.yaml`
- **Activation Rules**: See `/pnkln/skill-rules.json`

---

## Contributing

Found a better way to phrase a template? Have a new template to add?

1. Copy an existing template
2. Modify for your use case
3. Share with the community

---

**Version**: 1.0.0
**Last Updated**: 2025-11-15
**Total Templates**: 10

---

**Happy automating! 🚀**
