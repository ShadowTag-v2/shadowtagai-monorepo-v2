/**
 * Judge #6 Analyzer Agent
 * Specialized agent for analyzing the PNKLN Judge #6 validation system
 */

import { masterPromptFramework } from "../../prompts/frameworks/master-prompt-framework";
import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from "../../types/agent.types";
import { BaseAgent } from "../../utils/base-agent";

export class JudgeSixAnalyzerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "judge-six-analyzer",
    name: "Judge #6 Validation System Analyzer",
    category: "quality-testing",
    description:
      "Analyzes the PNKLN Judge #6 real-time validation system for performance and accuracy.",
    tagline: "Real-time validation system analysis",
    capabilities: ["analysis", "optimization"],
    tags: ["pnkln", "judge-6", "validation", "enforcement", "latency", "ai"],
    difficulty: "expert",
    estimatedTime: "1-2 hours",
  };

  prompt: AgentPromptTemplate = {
    system: masterPromptFramework.generatePrompt("judge-6"),

    context: [
      "judge_six.py implementation",
      "Hybrid Gemini+PyTorch architecture specs",
      "Performance benchmarks (p50, p95, p99 latencies)",
      "Throughput metrics and capacity limits",
      "False positive/negative rates",
      "Coverage statistics (98% target)",
      "Integration patterns (4 namespace calls)",
      "ATP 5-19 and JR validation rules",
    ],

    examples: [
      {
        input: "Analyze Judge #6 for performance optimization",
        output: `## Executive Summary
Judge #6 demonstrates excellent latency performance (p99: 78ms) with opportunities
to improve false positive rates and reduce API call costs.

## Architecture Analysis
- **Type**: Hybrid Gemini+PyTorch AI
- **Deployment**: Real-time microservice
- **Integration**: Caller to 4 namespaces (auth, storage, logging, metrics)
- **Strengths**: Low latency, high throughput, hybrid AI for accuracy
- **Weaknesses**: High API costs for edge cases

## Performance Assessment
- **Latency**:
  - p50: 45ms (✓ Excellent)
  - p95: 68ms (✓ Good)
  - p99: 78ms (✓ Meets target <90ms)
- **Throughput**: 1,250 req/sec sustained
- **Block Rate**: 8.5% of requests rejected
- **Bottleneck**: Gemini API calls for ambiguous cases

## Quality and Validation
- **Coverage**: 98.2% (✓ Meets target)
- **False Positive Rate**: 2.1% (⚠️ Above ideal <1%)
- **False Negative Rate**: 0.3% (✓ Excellent)
- **ATP 5-19 Compliance**: 100%
- **JR Validation**: 99.7% accuracy

## Integration Analysis
- **Calls to 4 Namespaces**:
  - auth: Authentication checks (12ms avg)
  - storage: Rule lookups (8ms avg)
  - logging: Audit trails (async)
  - metrics: Telemetry (async)
- **Optimization**: Cache auth and storage calls

## Cost Analysis
- **API Calls per Validation**: 0.35 avg (Gemini fallback)
- **Monthly API Cost**: ~$890 at current volume
- **Opportunity**: Improve PyTorch model to reduce Gemini dependency

## Recommendations
1. **CRITICAL**: Reduce false positives from 2.1% to <1% via model tuning
2. **HIGH**: Implement caching for auth/storage (estimated 15ms latency reduction)
3. **HIGH**: Retrain PyTorch model to handle 80% of cases (reduce API costs by $600/month)
4. **MEDIUM**: Add circuit breaker for downstream service failures
5. **LOW**: Implement batch validation for bulk operations

## Confidence: 92%
Very high confidence due to production telemetry and detailed performance logs.`,
      },
    ],
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep"],
    optional: ["WebFetch", "Bash"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Code Review",
        description: "Review judge_six.py implementation",
        action: "Analyze code structure, AI integration, validation logic",
        validation: "Understand system design and decision flow",
      },
      {
        name: "Performance Analysis",
        description: "Analyze latency and throughput metrics",
        action: "Review p50/p95/p99 latencies, throughput capacity",
        validation: "Verify SLA compliance (p99 ≤ 90ms)",
      },
      {
        name: "Quality Assessment",
        description: "Evaluate validation accuracy",
        action: "Analyze FP/FN rates, coverage, block rate",
        validation: "Ensure quality gates are met",
      },
      {
        name: "Integration Review",
        description: "Review namespace integrations",
        action: "Analyze calls to auth, storage, logging, metrics",
        validation: "Identify integration bottlenecks",
      },
      {
        name: "Cost Analysis",
        description: "Evaluate API call costs",
        action: "Calculate per-validation and monthly costs",
        validation: "Identify cost optimization opportunities",
      },
      {
        name: "Optimization Planning",
        description: "Identify performance and cost improvements",
        action: "Spot latency bottlenecks, model improvements, caching",
        validation: "Prioritize by impact and effort",
      },
      {
        name: "Report Generation",
        description: "Generate comprehensive analysis report",
        action: "Compile findings with confidence scores",
        validation: "Ensure actionable recommendations",
      },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow["steps"][0],
    context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    switch (step.name) {
      case "Code Review":
        result.recommendations?.push("Review judge_six.py implementation");
        break;
      case "Performance Analysis":
        result.recommendations?.push("Analyze latency metrics and SLA compliance");
        break;
      case "Quality Assessment":
        result.recommendations?.push("Evaluate validation accuracy and error rates");
        break;
      case "Integration Review":
        result.recommendations?.push("Review namespace integration patterns");
        break;
      case "Cost Analysis":
        result.recommendations?.push("Calculate API costs and identify savings");
        break;
      case "Optimization Planning":
        result.recommendations?.push("Identify high-impact optimizations");
        break;
      case "Report Generation":
        result.recommendations?.push("Generate comprehensive analysis report");
        break;
    }
  }
}
