# PNKLN Core Stack™ Analysis Guide

This guide provides comprehensive documentation for using the PNKLN Stack analysis agents and master prompt framework.

## Overview

The PNKLN Stack analyzer provides specialized tools for analyzing components of the PNKLN Core Stack™, a production-grade intelligence pipeline. It includes:

- **Master Prompt Framework**: Generates specialized analysis prompts for different components
- **Component Analyzers**: Dedicated agents for Judge 6, Gemini Ingestion Layer, and more
- **Comparison Framework**: Compares components and provides migration guidance
- **Integration Analysis**: Analyzes end-to-end data flow across components

## Quick Start

```typescript
import { PNKLNStack, masterPromptFramework, getAgent } from "claude-code-agents";

// Get a PNKLN analyzer
const ingestionAnalyzer = getAgent("gemini-ingestion-analyzer");

// Execute analysis
const result = await ingestionAnalyzer.execute({
  projectPath: "/path/to/pnkln-stack",
  userQuery: "Analyze the Gemini Ingestion Layer for optimization opportunities",
});

console.log(result.output);
console.log(result.recommendations);
```

## Components

### 1. Gemini Ingestion Layer Analyzer

Analyzes the intelligence collection pipeline with focus on:

- **Runtime Efficiency**: ~45 min/night target
- **Ethical Compliance**: robots.txt, rate limiting, transparency
- **Multi-Source Coverage**: YouTube, Twitter, News, APIs, etc.
- **Tier Classification**: Tier 1/2/3 distribution and quality
- **Cost Model**: Monthly operational costs (~$77)
- **Data Quality**: Relevance, timeliness, completeness scores

#### Usage Example

```typescript
import { PNKLNStack } from "claude-code-agents";

const analyzer = new PNKLNStack.GeminiIngestionAnalyzerAgent();

const result = await analyzer.execute({
  projectPath: "/path/to/gemini-ingestion",
  userQuery: "Evaluate ethical compliance and suggest improvements",
  additionalContext: {
    focusAreas: ["ethical-compliance", "tier-classification"],
    includeComparison: true,
  },
});

// Access structured results
console.log("Confidence Score:", result.metrics?.stepsCompleted);
console.log("Recommendations:", result.recommendations);
```

#### Expected Output

```
## Executive Summary
The Gemini Ingestion Layer demonstrates strong ethical compliance with
opportunity for optimization in Tier 1 data acquisition.

## Ethical Compliance ✓
- robots.txt: Fully respected
- Rate Limiting: 2 req/sec (conservative)
- User-Agent: Properly identified
- Data Retention: 90-day policy

## Tier Classification
- Tier 1 (high-value): 15% → Opportunity to increase to 25%
- Tier 2 (medium): 45%
- Tier 3 (low): 40%

## Recommendations
1. [HIGH] Tune classifiers to improve Tier 1 from 15% to 25%
2. [MEDIUM] Parallelize source ingestion (reduce runtime to <30 min)
3. [LOW] Add Redis caching for duplicate detection

Confidence: 85%
```

### 2. Judge 6 Analyzer

Analyzes the real-time validation system with focus on:

- **Latency**: p99 ≤ 90ms target
- **Throughput**: Request capacity and scalability
- **Error Rates**: False positives/negatives
- **Coverage**: 98% validation coverage target
- **Integration**: Calls to 4 namespaces (auth, storage, logging, metrics)
- **Cost Model**: API calls per validation

#### Usage Example

```typescript
import { PNKLNStack } from "claude-code-agents";

const analyzer = new PNKLNStack.JudgeSixAnalyzerAgent();

const result = await analyzer.execute({
  projectPath: "/path/to/judge-six",
  userQuery: "Analyze latency bottlenecks and optimization opportunities",
  constraints: {
    maxTokens: 100000,
    timeoutMs: 300000,
  },
});
```

#### Expected Output

```
## Executive Summary
Judge 6 demonstrates excellent latency (p99: 78ms) with opportunities
to reduce false positives and API costs.

## Performance Assessment ✓
- p50: 45ms (Excellent)
- p95: 68ms (Good)
- p99: 78ms (Meets target <90ms)
- Throughput: 1,250 req/sec

## Quality Metrics
- Coverage: 98.2% ✓
- False Positives: 2.1% (Target: <1%)
- False Negatives: 0.3% ✓

## Recommendations
1. [CRITICAL] Reduce FP rate from 2.1% to <1% via model tuning
2. [HIGH] Cache auth/storage calls (est. 15ms reduction)
3. [HIGH] Retrain PyTorch model (reduce API costs $600/month)

Confidence: 92%
```

### 3. Component Comparison Analyzer

Compares different PNKLN components and provides migration guidance.

#### Usage Example

```typescript
import { PNKLNStack, masterPromptFramework } from "claude-code-agents";

// Generate comparison prompt
const comparisonPrompt = masterPromptFramework.compareComponents("judge-6", "gemini-ingestion");

console.log(comparisonPrompt);

// Or use the agent directly
const analyzer = new PNKLNStack.ComponentComparisonAnalyzerAgent();

const result = await analyzer.compareComponents("judge-6", "gemini-ingestion", {
  projectPath: "/path/to/pnkln-stack",
  userQuery: "Compare and provide adaptation guidance",
});
```

#### Expected Output

```
# Component Comparison: Judge 6 vs Gemini Ingestion Layer

## Architectural Differences
Judge 6 uses Hybrid Gemini+PyTorch while Gemini Ingestion uses GKE CronJob.
This reflects their different positions in the stack: real-time validation vs batch collection.

## Metric Adaptations
- **p99 latency → Runtime efficiency**: Batch processing prioritizes throughput
- **FP/FN rates → Quality scores**: Intelligence requires holistic assessment
- **Caller → Callee**: Integration pattern reflects preventive vs reactive roles

## Key Differences Table
| Aspect | Judge 6 | Gemini Ingestion |
|--------|----------|------------------|
| Purpose | Real-time validation | Intelligence collection |
| Architecture | Hybrid Gemini+PyTorch | GKE CronJob Multi-Container |
| Primary Metric | p99 ≤ 90ms | ~45 min/night |
| Integration | Caller (4 namespaces) | Callee (4 namespaces) |

## Migration Considerations
When adapting analysis from judge-6 to gemini-ingestion, consider:
1. Adjust metrics from latency to runtime efficiency
2. Update integration patterns: Caller → Callee
3. Refocus quality from error rates to holistic scores
4. Adapt confidence thresholds (70% prod → 60% pre-prod)
```

## Master Prompt Framework

The Master Prompt Framework generates specialized analysis prompts for any PNKLN component.

### Generating Custom Prompts

```typescript
import { masterPromptFramework, PNKLNComponent } from "claude-code-agents";

// Generate prompt for a specific component
const prompt = masterPromptFramework.generatePrompt("gemini-ingestion", {
  additionalContext: "Focus on cost optimization and ethical compliance",
});

// Use with Gemini 2.0 Pro or Claude
// ... send prompt to LLM ...
```

### Component-Specific Metrics

Each component has tailored metrics:

#### Judge 6

- Latency (p50, p95, p99)
- Throughput
- Block rate
- FP/FN rates
- API calls per validation

#### Gemini Ingestion

- Runtime (~45 min/night)
- Items per day
- Source diversity
- Cost per item
- Quality scores (relevance, timeliness, completeness)
- Tier distribution (1/2/3)
- Ethical compliance metrics

### Comparison Features

```typescript
// Compare two components
const comparison = masterPromptFramework.compareComponents("judge-6", "gemini-ingestion");

// Analyze integration across components
const integration = masterPromptFramework.analyzeIntegration(["gemini-ingestion", "judge-6", "storage", "api-gateway"]);
```

## Confidence Scoring

All analyses include confidence scores:

- **≥70%**: Production systems with full telemetry
- **≥60%**: Pre-production systems with specs only
- **<60%**: Insufficient data, flag assumptions

```typescript
const result = await analyzer.execute({
  projectPath: "/path/to/component",
  userQuery: "Analyze...",
});

if (result.metrics && result.metrics.tokensUsed) {
  console.log(`Confidence: ${result.metrics.tokensUsed}%`);
}
```

## Advanced Usage

### Custom Analysis Context

```typescript
const result = await analyzer.execute({
  projectPath: "/path/to/component",
  userQuery: "Comprehensive analysis",
  additionalContext: {
    environment: "pre-production",
    focusAreas: ["performance", "cost", "ethics"],
    compareWith: "judge-6",
    includeVisualization: true,
  },
  constraints: {
    maxTokens: 150000,
    timeoutMs: 600000,
    dryRun: false,
  },
});
```

### Batch Analysis

```typescript
import { getAllAgents } from "claude-code-agents";

const pnklnAgents = getAllAgents().filter((agent) => agent.metadata.category === "pnkln-stack");

for (const agent of pnklnAgents) {
  const result = await agent.execute({
    projectPath: `/path/to/${agent.metadata.id}`,
    userQuery: "Comprehensive analysis",
  });

  console.log(`\n=== ${agent.metadata.name} ===`);
  console.log(result.output);
}
```

### Integration with CI/CD

```yaml
# .github/workflows/pnkln-analysis.yml
name: PNKLN Stack Analysis

on:
  push:
    branches: [main, develop]
  schedule:
    - cron: "0 0 * * 0" # Weekly on Sunday

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: "20"

      - name: Install Dependencies
        run: npm install claude-code-agents

      - name: Analyze Gemini Ingestion
        run: |
          node -e "
          const { getAgent } = require('claude-code-agents');
          const analyzer = getAgent('gemini-ingestion-analyzer');
          analyzer.execute({
            projectPath: process.cwd(),
            userQuery: 'Weekly analysis report'
          }).then(result => console.log(result.output));
          "

      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: pnkln-analysis-report
          path: analysis-report.md
```

## Prompt Template Customization

You can customize prompt templates for specific needs:

```typescript
import { MasterPromptFrameworkImpl } from "claude-code-agents";

class CustomFramework extends MasterPromptFrameworkImpl {
  constructor() {
    super();
    // Add custom component template
    this.componentTemplates.set("custom-component", {
      id: "custom-component-analysis",
      name: "Custom Component Analysis",
      version: "1.0.0",
      targetComponent: "custom-component",
      sections: {
        context: "Custom context...",
        objectives: ["Custom objectives..."],
        analysisAreas: ["Custom areas..."],
        outputFormat: "Custom format...",
        confidenceThreshold: 65,
      },
      replacements: [],
      adaptations: [],
    });
  }
}

const customFramework = new CustomFramework();
const prompt = customFramework.generatePrompt("custom-component");
```

## Best Practices

1. **Provide Context**: Include as much documentation as possible
2. **Set Realistic Confidence**: Pre-prod (60%), Prod (70%)
3. **Focus Analysis**: Use `focusAreas` to target specific concerns
4. **Iterate**: Start with broad analysis, then deep dive
5. **Compare**: Use comparison framework to adapt between components
6. **Automate**: Integrate into CI/CD for continuous monitoring

## Troubleshooting

### Low Confidence Scores

If confidence is <50%, check:

- Sufficient documentation provided
- Specs are up-to-date
- Metrics are available
- Context is clear

### Irrelevant Recommendations

Ensure `additionalContext` specifies:

- Component type correctly
- Focus areas
- Constraints (cost, performance, ethics)

### Missing Metrics

Verify the component template includes all necessary metrics. Extend the framework if needed.

## Examples Repository

See `examples/pnkln-stack/` for:

- `gemini-ingestion-analysis.ts`: Full ingestion analysis
- `judge-six-optimization.ts`: Performance optimization
- `component-migration.ts`: Migration from Judge 6 to Ingestion
- `ci-cd-integration.ts`: Automated analysis in CI/CD

## Contributing

To add new PNKLN components:

1. Create component analyzer in `src/agents/pnkln-stack/`
2. Add component type to `PNKLNComponent` in `src/types/pnkln.types.ts`
3. Add template to `masterPromptFramework`
4. Register in `src/agents/registry.ts`
5. Update documentation

## Support

For issues or questions:

- GitHub Issues: <https://github.com/ehanc69/ShadowTag-v2-fastapi-services/issues>
- Documentation: See `README.md` and `AGENTS.md`

---

**PNKLN Core Stack™** is a production-grade intelligence pipeline.
**Master Prompt Framework v2.0.0** - Ready for Gemini 2.0 Pro and Claude Sonnet 4.5.
