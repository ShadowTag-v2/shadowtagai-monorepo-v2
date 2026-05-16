# Advanced Prompt Engineering for Cost Optimization

**The 16th Habit: Engineer prompts strategically to match model capabilities and minimize token usage**

Strategic prompt engineering can save 50-90% on costs by ensuring you use the right model with the right instructions for each task.

---

## Table of Contents

1. [Why Prompt Engineering Matters for Cost](#why-prompt-engineering-matters-for-cost)
2. [Model-Specific Prompt Design](#model-specific-prompt-design)
3. [Case Study: Gemini Ingestion Layer Analysis](#case-study-gemini-ingestion-layer-analysis)
4. [Prompt Optimization Techniques](#prompt-optimization-techniques)
5. [Prompt Templates for Common Tasks](#prompt-templates-for-common-tasks)
6. [Measuring Prompt Efficiency](#measuring-prompt-efficiency)

---

## Why Prompt Engineering Matters for Cost

**The Problem:**
- Vague prompts → multiple back-and-forth rounds → 3x cost
- Wrong model for the task → overpaying for capabilities you don't need
- Overly verbose prompts → unnecessary token usage
- Generic prompts → low-quality outputs requiring rework

**The Solution:**
Strategic prompt engineering that:
- Matches model capabilities to task requirements
- Provides precise, targeted instructions
- Minimizes token usage while maximizing quality
- Gets the desired output in one shot

**Cost Impact:**

| Approach | Cost | Quality | Time |
|----------|------|---------|------|
| Generic prompt on Sonnet | $5.00 | Medium | 3 rounds |
| Optimized prompt on Haiku | $0.50 | High | 1 round |
| **Savings** | **90%** | **Better** | **3x faster** |

---

## Model-Specific Prompt Design

### Haiku: Fast & Efficient for Routine Tasks

**Best For:**
- Bug fixes
- Code formatting
- Simple refactoring
- File reads/searches
- Routine analysis

**Prompt Strategy:**
- Be specific about file and line numbers
- Provide exact error messages
- Use concrete examples
- Keep context minimal

**Example:**

```
❌ Expensive (vague, on Sonnet)
"Help me fix this authentication issue"

✅ Cheap (specific, on Haiku)
"Fix TypeError in auth.ts:234 - 'user.token is undefined'.
Add null check before accessing user.token."
```

**Cost:** $0.10 vs $0.50 = **80% savings**

---

### Sonnet: Strategic for Complex Tasks

**Best For:**
- Multi-file refactoring
- System architecture
- Complex debugging
- Learning new codebases
- Strategic planning

**Prompt Strategy:**
- Provide architectural context
- Define success criteria clearly
- Break down into phases
- Request detailed analysis

**Example:**

```
✅ Optimized for Sonnet
"Analyze the authentication system across these 5 files:
- auth.ts (core logic)
- session.ts (state management)
- api.ts (endpoints)
- database.ts (persistence)
- types.ts (interfaces)

Goal: Identify security vulnerabilities and propose fixes.
Focus on: JWT validation, session expiry, CSRF protection.
Output: Prioritized list with code examples."
```

**Why This Works:**
- Leverages Sonnet's multi-file reasoning
- Clear scope prevents wandering analysis
- Specific output format ensures actionable results

---

### Gemini: Specialized for Domain Analysis

**Best For:**
- Large-scale data analysis
- Document comprehension
- Pattern recognition
- Cross-system integration
- Ethical/compliance review

**Prompt Strategy:**
- Provide rich contextual documentation
- Define domain-specific metrics
- Request structured outputs
- Set realistic confidence thresholds

---

## Case Study: Gemini Ingestion Layer Analysis

### Background

The PNKLN Core Stack™ includes a Gemini Ingestion Layer—a nightly batch system that crawls multiple sources (YouTube, Twitter, news) to collect intelligence data. The team adapted a "Judge #6" validation prompt to create an analysis prompt for this ingestion system.

**Challenge:**
- Pre-production system (no real metrics yet)
- Multiple quality dimensions to analyze
- Ethical compliance critical
- Need actionable insights from specs alone

**Solution:**
Strategic prompt engineering tailored to Gemini 2.0 Pro's strengths.

---

### Direct Replacements: Keeping It Domain-Relevant

These swaps repurposed the prompt without losing core structure:

| Original (Judge #6) | New (Ingestion Layer) | Why |
|---------------------|----------------------|-----|
| "Judge #6" | "Gemini Ingestion Layer" | Domain focus |
| `judge_six.py` | Pipeline docs & arch specs | Broader scope for distributed system |
| p99 ≤90ms | ~45 min/night runtime | Batch vs real-time metrics |
| 98% coverage | Quality gates (items, sources, costs, scores) | Multifaceted quality vs binary threshold |

**Cost Insight:**
By using architecture docs instead of requiring the model to read all code files, this approach saves ~80% in token costs while providing better analysis of the system's design.

---

### Context-Specific Adaptations: Tailoring to Function

The prompt evolved from a reactive validator to a proactive collector:

| Dimension | Judge #6 (Validator) | Ingestion Layer (Collector) | Impact |
|-----------|---------------------|----------------------------|---------|
| **Architecture** | Hybrid Gemini+PyTorch | GKE CronJob Multi-Container | Emphasizes orchestration |
| **Key Metrics** | Latency, throughput, block rate | Items/day, sources, cost/item | Volume/diversity over speed |
| **Integration** | Calls services in 4 namespaces | Called by services in 4 namespaces | Foundation layer |
| **Unique Features** | ATP 5-19, JR validation | Ethical crawling, tier classification | Compliance focus |
| **Cost Model** | API calls per validation | Monthly operational ~$77 | Batch-friendly |
| **Quality Focus** | FP/FN rates | Relevance, timeliness, completeness | Holistic data quality |

**Why This Matters for Cost:**

1. **Right Metrics = Right Model:**
   - Validator needs real-time → use faster model with latency focus
   - Ingestion is batch → use deeper analysis model with efficiency focus

2. **Prevent Over-Engineering:**
   - Don't optimize for latency if you run once per night
   - Don't track FP/FN rates if you're collecting, not validating

3. **Focused Prompts = One-Shot Results:**
   - Each dimension maps to specific analysis
   - No generic "analyze this system" that requires clarification

**Estimated Savings:**
- Generic analysis: 5-7 rounds × $2/round = **$10-14**
- Tailored prompt: 1 round × $2 = **$2**
- **Savings: 80-85%**

---

### New Sections Added: Enhancing Depth

Adding these sections addressed gaps and made analysis comprehensive:

#### 1. Ethical Compliance Model
```
Analyze adherence to:
- robots.txt compliance
- Rate limiting (requests/second by source)
- Transparency (disclosure of crawling purpose)
- Attribution requirements
```

**Why Added:**
- Prevents legal/reputation costs (invaluable)
- Demonstrates responsible engineering
- Surfaces risks before production

**Cost Benefit:**
Catching one compliance issue before deployment saves:
- Legal review: $5,000+
- Remediation: $10,000+
- Reputation damage: Priceless

**ROI of prompt section: 5000x+**

---

#### 2. Multi-Source Coverage Analysis
```
Evaluate diversity across:
- YouTube (video transcripts, metadata)
- Twitter (real-time feeds, threads)
- News (articles, RSS)
- [Other sources]

Metrics:
- Items per source per day
- Source reliability scores
- Coverage gaps
```

**Why Added:**
- Prevents over-reliance on single source
- Identifies blind spots
- Balances acquisition costs

**Cost Optimization:**
If analysis reveals 80% items from one expensive source, you can:
- Diversify to cheaper sources
- Negotiate better rates
- Reduce redundancy

**Example Savings:**
- Before: 10,000 items/day × $0.01/item = $100/day
- After: Shift 50% to free sources = $50/day
- **Monthly savings: $1,500**

---

#### 3. Tier Classification Metrics
```
Analyze distribution:
- Tier 1: High-value intelligence (target: 20%)
- Tier 2: Moderate value (target: 50%)
- Tier 3: Low value/noise (target: 30%)

Identify:
- Current distribution
- Tier drift over time
- Cost per tier
```

**Why Added:**
- Focuses resources on high-value data
- Prevents "garbage in, garbage out"
- Enables ROI tracking

**Cost Optimization:**
If you're spending 60% of compute on Tier 3 data:
- Filter aggressively at ingestion
- Reduce Tier 3 processing depth
- Reallocate to Tier 1 enhancement

**Example Savings:**
- 60% of $77/month on low-value = $46 wasted
- Optimize to 30% = **$23/month savings**
- Annual: **$276 saved**

---

#### 4. AM Briefing Delivery Effectiveness
```
Evaluate output quality:
- Format clarity
- Timeliness (ready by 6 AM?)
- Completeness (all sources represented?)
- Actionability (insights vs raw data)
```

**Why Added:**
- End-to-end validation
- User experience matters
- Catches pipeline failures

**Cost Benefit:**
If briefings arrive late or incomplete:
- Users run manual queries → $5/session
- 20 users × 5 days/week = 100 sessions
- **Wasted: $500/week**

Good delivery effectiveness analysis prevents this.

---

### Confidence Adjustments: Realistic Expectations

**Change:** Lowered target confidence from ≥70% (Judge #6) to ≥60% (Ingestion Layer)

**Reasoning:**
- Pre-production = no real telemetry
- Analysis based on specs/docs = more assumptions
- Setting achievable bars prevents false negatives

**Cost Implication:**

| Confidence Target | Gemini Analysis Depth | Token Usage | Cost |
|-------------------|----------------------|-------------|------|
| 90% (unrealistic) | 3x deeper probing | 15,000 tokens | $6.00 |
| 70% (production) | Standard depth | 8,000 tokens | $3.20 |
| 60% (pre-prod) | Spec-focused | 5,000 tokens | $2.00 |

**By setting realistic expectations:**
- Avoid expensive over-analysis
- Get useful insights faster
- Bump up later when metrics available

**Savings: $4.00 per analysis** (vs unrealistic 90% target)

---

## Prompt Optimization Techniques

### 1. Scope Reduction
```
❌ Expensive
"Analyze the entire codebase for issues"

✅ Cheap
"Analyze auth.ts:100-200 for JWT validation issues"
```

**Savings: 95%** (5,000 lines → 100 lines)

---

### 2. Output Format Specification
```
❌ Vague (requires follow-up)
"What are the problems?"

✅ Structured (one-shot)
"List problems in this format:
1. File:line - Issue - Severity - Fix
2. ..."
```

**Savings: 2x** (one round vs two)

---

### 3. Context Prioritization
```
❌ Over-contextualized
[Provides entire git history, all related files, full documentation]

✅ Targeted
[Only provides: current file, error message, relevant config]
```

**Savings: 80%** in token costs

---

### 4. Model Selection Guidance
Include in your prompts:

```
For this task:
- If routine bug fix → use Haiku
- If multi-file refactor → use Sonnet
- If data/compliance analysis → use Gemini
```

**Savings: 5x** (using right tool for job)

---

### 5. Confidence Calibration
```
❌ Default (often 95%+)
"Analyze this system thoroughly"

✅ Calibrated
"Analyze based on specs. Target 60% confidence.
Flag assumptions clearly."
```

**Savings: 40%** (less deep-diving)

---

### 6. Incremental Refinement
```
Round 1 (Haiku): "Identify top 5 issues in auth.ts"
[Review results]
Round 2 (Haiku): "Fix issues #1 and #3"
[Only if needed]
Round 3 (Sonnet): "Refactor auth flow for issues #2, #4, #5"
```

**vs:**

```
Single Round (Sonnet): "Fix all auth issues"
```

**Savings: 50%** (3x Haiku + 1x Sonnet < 3x Sonnet)

---

## Prompt Templates for Common Tasks

### Template 1: Bug Fix (Haiku)
```
Fix [ERROR_TYPE] in [FILE]:[LINE]

Error: [EXACT_ERROR_MESSAGE]

Expected behavior: [WHAT_SHOULD_HAPPEN]
Actual behavior: [WHAT_HAPPENS]

Context:
- [KEY_VARIABLE_1]: [VALUE]
- [KEY_VARIABLE_2]: [VALUE]

Return: Code fix with 1-line explanation
```

**Cost: $0.10**

---

### Template 2: Refactoring Plan (Haiku → Sonnet)
```
Round 1 (Haiku):
Create a plan to [GOAL] in these files:
- [FILE_1]: [ROLE]
- [FILE_2]: [ROLE]
- [FILE_3]: [ROLE]

Constraints:
- [CONSTRAINT_1]
- [CONSTRAINT_2]

Output: 5-step plan with risk assessment

[Review plan]

Round 2 (Sonnet):
Implement step [N] of the plan above.
[PASTE_PLAN_STEP]

Files to modify:
- [FILE_1]
- [FILE_2]

Output: Complete code changes
```

**Cost: $0.50 + $2.00 = $2.50** (vs $5.00 for unplanned Sonnet refactor)

---

### Template 3: System Analysis (Gemini)
```
Analyze [SYSTEM_NAME] based on [DOCS/SPECS].

Focus areas:
1. [AREA_1]: [SPECIFIC_METRICS]
2. [AREA_2]: [SPECIFIC_METRICS]
3. [AREA_3]: [SPECIFIC_METRICS]

Output format:
## [AREA_1]
- Metric: [VALUE]
- Assessment: [GOOD/CONCERN]
- Recommendation: [ACTION]

## [AREA_2]
...

Target confidence: [60/70/90]%
Flag assumptions clearly.
```

**Cost: $2.00** (vs $6.00 for generic "analyze everything")

---

### Template 4: Code Search (Haiku)
```
Search [DIRECTORY] for [PATTERN]

Criteria:
- [CRITERION_1]
- [CRITERION_2]

Limit: First 50 results
Sort by: [RELEVANCE/DATE/FILE]

Output: File:line for each match
```

**Cost: $0.05** (vs $0.50 for unlimited search)

---

### Template 5: Multi-Source Data Analysis (Gemini)
```
Analyze data quality across sources:

Sources:
- [SOURCE_1]: [DESCRIPTION]
- [SOURCE_2]: [DESCRIPTION]
- [SOURCE_3]: [DESCRIPTION]

Metrics per source:
- Volume: Items/day
- Quality: [QUALITY_METRIC]
- Cost: $/item
- Timeliness: Lag from event to ingestion

Identify:
1. Coverage gaps
2. Cost outliers
3. Quality issues
4. Optimization opportunities

Output: Table + 3 top recommendations
```

**Cost: $2.50** (high value for multi-source insight)

---

## Measuring Prompt Efficiency

### Key Metrics

1. **Token Usage per Task**
   - Measure: Input + output tokens
   - Target: Minimize while maintaining quality
   - Tool: Claude Code cost tracker

2. **Rounds per Task**
   - Measure: How many back-and-forths?
   - Target: 1 round for routine tasks, ≤3 for complex
   - Indicator: Prompt specificity

3. **Model Match Score**
   - Measure: % tasks on optimal model
   - Target: 80%+ on Haiku, 15% on Sonnet, 5% on Gemini
   - Tool: Weekly review

4. **Rework Rate**
   - Measure: % outputs requiring revision
   - Target: <10%
   - Indicator: Prompt clarity

5. **Cost per Task Type**
   - Measure: Average cost by category
   - Target: Trend downward as prompts improve
   - Tool: Cost tracker with tags

### Example Dashboard

```
Week 1 (Before Optimization):
- Bug fixes: $1.20/task (Sonnet, 2 rounds)
- Refactors: $8.00/task (Sonnet, 4 rounds)
- Analysis: $10.00/task (Sonnet, generic)
Total: $152/week

Week 4 (After Optimization):
- Bug fixes: $0.15/task (Haiku, 1 round)
- Refactors: $2.50/task (Haiku plan + Sonnet impl)
- Analysis: $2.00/task (Gemini, targeted)
Total: $25/week

Savings: 84%
```

---

## Iterative Improvement Process

### Step 1: Baseline
Track current prompts and costs for 1 week.

### Step 2: Identify Patterns
Which tasks cost the most? Which take multiple rounds?

### Step 3: Templatize
Create reusable templates for top 5 task types.

### Step 4: Test
Run A/B test: Generic vs optimized prompts.

### Step 5: Measure
Compare:
- Cost per task
- Rounds per task
- Output quality

### Step 6: Refine
Adjust templates based on results.

### Step 7: Scale
Share templates with team, update documentation.

---

## Integration with Core Optimization Habits

Prompt engineering amplifies the original 15 habits:

| Habit | Prompt Engineering Enhancement |
|-------|-------------------------------|
| #1: Use Haiku 80% | Template prompts for Haiku-suitable tasks |
| #2: Search first | Prompt for exact search criteria |
| #6: Plan first | Two-stage prompts (plan → implement) |
| #9: Be specific | Structured prompt templates |
| #11: Create checklists | Prompt for checklist generation first |

---

## Real-World Results: Gemini Ingestion Layer

**Before Optimization:**
- Generic "analyze this system" prompt
- 7 rounds of clarification
- Mixed Sonnet/Gemini usage
- Cost: ~$15 per analysis

**After Strategic Prompt Engineering:**
- Targeted prompt with 6 analysis dimensions
- 1 round (occasionally 2 for edge cases)
- Gemini 2.0 Pro (right tool for docs/compliance)
- Cost: ~$2 per analysis

**Savings: 87%**

**Quality improvement:**
- Added ethical compliance review (invaluable)
- Multi-source coverage insights
- Tier classification metrics
- End-to-end delivery validation

**Result:**
Better analysis at 1/7 the cost, in 1/7 the time.

---

## Next Steps

1. **Audit Your Current Prompts**
   - Review last 20 Claude Code sessions
   - Identify repetitive patterns
   - Calculate cost per pattern

2. **Create Your Top 5 Templates**
   - Start with most frequent tasks
   - Use examples in this guide
   - Test and refine

3. **Set Up Tracking**
   - Tag tasks by type
   - Monitor cost trends
   - A/B test templates

4. **Share Knowledge**
   - Document team's best prompts
   - Run lunch-and-learn
   - Iterate based on feedback

5. **Continuous Improvement**
   - Weekly: Review outlier costs
   - Monthly: Update templates
   - Quarterly: Benchmark against baseline

---

## Resources

- Main guide: [CLAUDE_CODE_COST_OPTIMIZATION.md](./CLAUDE_CODE_COST_OPTIMIZATION.md)
- Quick reference: [CLAUDE_COST_CHEATSHEET.md](./CLAUDE_COST_CHEATSHEET.md)
- Setup: [setup-cost-optimization.sh](./setup-cost-optimization.sh)

---

## Appendix: Gemini Ingestion Layer Prompt (Excerpt)

```
# Gemini Ingestion Layer Analysis

## System Context
Analyze the PNKLN Gemini Ingestion Layer based on provided
architecture specifications and documentation.

## Architecture
- Platform: GKE CronJob Multi-Container
- Schedule: Nightly batch (target: ~45 min runtime)
- Sources: YouTube, Twitter, News, [others]
- Output: Structured intelligence data for downstream services

## Analysis Dimensions

### 1. Ethical Compliance Model
Evaluate adherence to:
- robots.txt compliance across all sources
- Rate limiting (requests/second by source)
- Transparency and attribution
- Data retention policies

Metrics:
- Compliance score: [0-100]
- Violations flagged: [count]
- Risk level: [Low/Medium/High]

### 2. Multi-Source Coverage Analysis
Assess diversity:
- Items per source per day (target: balanced distribution)
- Source reliability scores
- Coverage gaps by topic/geography
- Redundancy rate

Metrics:
- Source count: [N]
- Diversity index: [0-1]
- Gap analysis: [list]

### 3. Tier Classification Metrics
Analyze data value distribution:
- Tier 1 (high-value): [%] (target: 20%)
- Tier 2 (moderate): [%] (target: 50%)
- Tier 3 (low-value): [%] (target: 30%)

Identify:
- Cost per tier
- Tier drift trends
- Optimization opportunities

### 4. Cost Model
Monthly operational: ~$77 (target)
Breakdown by:
- Compute: [%]
- Storage: [%]
- API calls: [%]
- Network: [%]

Sensitivity: What if volume doubles?

### 5. Quality Focus
Evaluate ingested data on:
- Relevance: Does it match intelligence goals?
- Timeliness: Lag from event to ingestion
- Completeness: Missing fields/metadata

Metrics:
- Relevance score: [0-100]
- Avg lag: [minutes]
- Completeness: [%]

### 6. AM Briefing Delivery Effectiveness
Assess output:
- Format clarity
- Timeliness (ready by 6 AM?)
- Completeness (all sources represented?)
- Actionability (insights vs raw data)

Metrics:
- Delivery success rate: [%]
- User satisfaction: [qualitative]

## Output Format
For each dimension:
1. Current assessment
2. Key findings
3. Recommendations (prioritized)

## Confidence Target
≥60% (pre-production, specs-based analysis)
Flag all assumptions clearly.

## Integration Context
Called by services in 4 namespaces:
[List namespaces and trigger patterns]

Analyze upstream triggers and downstream handoffs.
```

**Why This Works:**
- Clear structure → Gemini knows what to analyze
- Specific metrics → Quantitative outputs
- Realistic confidence → Avoids over-analysis
- Context provided → Better recommendations

**Cost: $2.00** for comprehensive analysis that would cost $15+ with generic prompt.

---

**Conclusion:**
Strategic prompt engineering is the "force multiplier" for cost optimization. Combined with the 15 core habits, it can push savings from 90% to 95%+, while improving output quality and speed.

**Your turn:** Pick one repetitive task, create an optimized template, and measure the difference. Share your results with the team!
