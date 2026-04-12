/**
 * Master Agent Prompt Framework
 * Generates specialized analysis prompts for PNKLN stack components
 */

import type {
  PNKLNComponent,
  PromptTemplate,
  MasterPromptFramework,
} from "../../types/pnkln.types";

export class MasterPromptFrameworkImpl implements MasterPromptFramework {
  name = "PNKLN Stack Master Prompt Framework";
  version = "2.0.0";
  components: PNKLNComponent[] = [
    "judge-6",
    "gemini-ingestion",
    "validator",
    "processor",
    "storage",
    "api-gateway",
  ];

  baseTemplate: PromptTemplate = {
    id: "base-analysis-template",
    name: "Base Component Analysis Template",
    version: "2.0.0",
    targetComponent: "judge-6", // default

    sections: {
      context: `You are analyzing a component of the PNKLN Core Stack™, a production-grade intelligence pipeline.
Your role is to provide comprehensive technical analysis based on available documentation and specifications.`,

      objectives: [
        "Evaluate architecture and design patterns",
        "Assess performance metrics and efficiency",
        "Identify quality gates and compliance measures",
        "Analyze integration patterns and dependencies",
        "Provide actionable optimization recommendations",
      ],

      analysisAreas: [
        "Architecture and Infrastructure",
        "Performance Metrics and SLAs",
        "Quality Gates and Validation",
        "Cost Model and Efficiency",
        "Integration Patterns",
        "Security and Compliance",
        "Scalability and Resilience",
        "Monitoring and Observability",
      ],

      outputFormat: `Provide structured analysis in the following format:
## Executive Summary
[High-level overview with key findings]

## Architecture Analysis
[Detailed architecture evaluation]

## Performance Assessment
[Metrics, benchmarks, and bottlenecks]

## Quality and Compliance
[Quality gates, error rates, compliance measures]

## Integration Analysis
[Upstream/downstream dependencies, handoffs]

## Cost Analysis
[Cost model, efficiency metrics, optimization opportunities]

## Recommendations
[Prioritized recommendations with estimated impact]

## Confidence Assessment
[Overall confidence score with justification]`,

      confidenceThreshold: 60,
    },

    replacements: [],
    adaptations: [],
  };

  componentTemplates: Map<PNKLNComponent, PromptTemplate> = new Map();

  constructor() {
    this.initializeComponentTemplates();
  }

  private initializeComponentTemplates(): void {
    // Judge #6 Template
    this.componentTemplates.set("judge-6", {
      id: "judge-6-analysis",
      name: "Judge #6 Validation System Analysis",
      version: "2.0.0",
      targetComponent: "judge-6",

      sections: {
        ...this.baseTemplate.sections,
        context: `You are analyzing Judge #6, a real-time validation and enforcement system in the PNKLN Core Stack™.
This is a hybrid Gemini+PyTorch AI system that validates data quality and enforces business rules with strict latency requirements.`,
      },

      replacements: [
        { key: "{{COMPONENT_NAME}}", value: "Judge #6", description: "Component identifier" },
        {
          key: "{{COMPONENT_TYPE}}",
          value: "Validation & Enforcement System",
          description: "System type",
        },
        { key: "{{PRIMARY_FILE}}", value: "judge_six.py", description: "Main implementation file" },
        { key: "{{LATENCY_TARGET}}", value: "p99 ≤ 90ms", description: "Performance SLA" },
        { key: "{{COVERAGE_TARGET}}", value: "98%", description: "Quality gate threshold" },
      ],

      adaptations: [
        {
          from: "Generic component",
          to: "Real-time validator",
          rationale: "Emphasizes sub-100ms latency and high-throughput validation",
        },
      ],
    });

    // Gemini Ingestion Layer Template
    this.componentTemplates.set("gemini-ingestion", {
      id: "gemini-ingestion-analysis",
      name: "Gemini Ingestion Layer Analysis",
      version: "2.0.0",
      targetComponent: "gemini-ingestion",

      sections: {
        ...this.baseTemplate.sections,
        context: `You are analyzing the Gemini Ingestion Layer, a nightly intelligence collection pipeline in the PNKLN Core Stack™.
This is a GKE CronJob-based system that ethically crawls multiple sources, classifies data by tier, and delivers morning briefings.`,

        analysisAreas: [
          ...this.baseTemplate.sections.analysisAreas,
          "Ethical Compliance Model",
          "Multi-Source Coverage",
          "Tier Classification Metrics",
          "AM Briefing Delivery Effectiveness",
        ],
      },

      replacements: [
        {
          key: "{{COMPONENT_NAME}}",
          value: "Gemini Ingestion Layer",
          description: "Component identifier",
        },
        {
          key: "{{COMPONENT_TYPE}}",
          value: "Intelligence Collection Pipeline",
          description: "System type",
        },
        {
          key: "{{PRIMARY_FILE}}",
          value: "Pipeline Documentation and Architecture Specs",
          description: "Main documentation",
        },
        {
          key: "{{RUNTIME_TARGET}}",
          value: "~45 min/night",
          description: "Runtime efficiency target",
        },
        {
          key: "{{QUALITY_GATES}}",
          value: "Items, Sources, Costs, Scores",
          description: "Quality dimensions",
        },
      ],

      adaptations: [
        {
          from: "Real-time validation (Judge #6)",
          to: "Batch collection (Ingestion Layer)",
          rationale: "Shifts from latency-focused to efficiency-focused, preventive vs reactive",
        },
        {
          from: "p99 latency metrics",
          to: "Total runtime and items/day metrics",
          rationale: "Batch processing prioritizes throughput over individual request latency",
        },
        {
          from: "FP/FN error rates",
          to: "Relevance, timeliness, completeness scores",
          rationale:
            "Intelligence quality requires holistic data assessment, not binary validation",
        },
      ],
    });
  }

  generatePrompt(component: PNKLNComponent, customizations?: unknown): string {
    const template = this.componentTemplates.get(component) || this.baseTemplate;

    let prompt = `# ${template.name}

## Context
${template.sections.context}

## Analysis Objectives
${template.sections.objectives.map((obj, i) => `${i + 1}. ${obj}`).join("\n")}

## Analysis Areas
Focus your analysis on the following areas:
${template.sections.analysisAreas.map((area, i) => `${i + 1}. ${area}`).join("\n")}

## Component-Specific Metrics

${this.getComponentMetrics(component)}

## Analysis Instructions

${template.sections.outputFormat}

## Confidence Threshold
Maintain a confidence score of at least ${template.sections.confidenceThreshold}% for all findings.
Flag any assumptions or areas with insufficient data.

## Additional Context
${customizations?.additionalContext || "None provided."}

---

Please proceed with your analysis based on the provided specifications and documentation.`;

    // Apply replacements
    template.replacements.forEach((replacement) => {
      prompt = prompt.replace(new RegExp(replacement.key, "g"), replacement.value);
    });

    return prompt;
  }

  private getComponentMetrics(component: PNKLNComponent): string {
    const metricsMap: Record<PNKLNComponent, string> = {
      "judge-6": `### Key Performance Indicators
- **Latency**: p99 ≤ 90ms
- **Throughput**: Sustain high request volume
- **Block Rate**: Measure validation rejections
- **Error Rates**: False positives/negatives
- **Integration**: Calls services in 4 namespaces
- **Unique Features**: ATP 5-19, JR Validation
- **Cost Model**: API calls per validation`,

      "gemini-ingestion": `### Key Performance Indicators
- **Runtime**: ~45 minutes per nightly execution
- **Items per Day**: Daily intelligence collection volume
- **Source Diversity**: Number and types of sources covered
- **Cost per Item**: Economic efficiency metric
- **Quality Scores**: Relevance, timeliness, completeness
- **Integration**: Called by services in 4 namespaces
- **Unique Features**: Ethical crawling, Tier classification (1/2/3)
- **Cost Model**: Monthly operational ~$77
- **Ethical Compliance**: robots.txt respect, rate limiting, transparency
- **Multi-Source Coverage**: YouTube, Twitter, News, Web, APIs
- **Tier Distribution**: Tier 1 (high-value) vs Tier 2/3 ratios
- **AM Briefing**: Morning delivery effectiveness`,

      validator: `### Key Performance Indicators
- **Validation Rules**: Number and complexity
- **Pass Rate**: Successful validation percentage
- **Processing Time**: Average validation duration
- **Error Detection**: Accuracy of rule enforcement`,

      processor: `### Key Performance Indicators
- **Processing Rate**: Items per second
- **Transformation Accuracy**: Data quality after processing
- **Resource Utilization**: CPU/memory efficiency
- **Pipeline Throughput**: End-to-end processing time`,

      storage: `### Key Performance Indicators
- **Write Throughput**: Inserts per second
- **Read Latency**: Query response time
- **Storage Efficiency**: Compression ratios
- **Data Retention**: Compliance with policies`,

      "api-gateway": `### Key Performance Indicators
- **Request Latency**: p50, p95, p99
- **Rate Limiting**: Effectiveness and fairness
- **Authentication Success**: Auth failure rate
- **Routing Efficiency**: Request distribution`,
    };

    return metricsMap[component] || "No specific metrics defined.";
  }

  compareComponents(componentA: PNKLNComponent, componentB: PNKLNComponent): string {
    const templateA = this.componentTemplates.get(componentA);
    const templateB = this.componentTemplates.get(componentB);

    if (!templateA || !templateB) {
      return "Cannot compare: One or both component templates not found.";
    }

    const adaptations = templateB.adaptations
      .filter((a) => a.from.toLowerCase().includes(componentA))
      .map((a) => `- **${a.from} → ${a.to}**: ${a.rationale}`)
      .join("\n");

    return `# Component Comparison: ${templateA.name} vs ${templateB.name}

## Architectural Differences
${this.getArchitectureDiff(componentA, componentB)}

## Metric Adaptations
${adaptations || "No documented adaptations between these components."}

## Key Differences Table
| Aspect | ${componentA} | ${componentB} |
|--------|${"-".repeat(componentA.length + 2)}|${"-".repeat(componentB.length + 2)}|
| Purpose | ${this.getComponentPurpose(componentA)} | ${this.getComponentPurpose(componentB)} |
| Architecture | ${this.getComponentArch(componentA)} | ${this.getComponentArch(componentB)} |
| Primary Metric | ${this.getPrimaryMetric(componentA)} | ${this.getPrimaryMetric(componentB)} |
| Integration Pattern | ${this.getIntegrationPattern(componentA)} | ${this.getIntegrationPattern(componentB)} |

## Migration Considerations
${this.getMigrationPath(componentA, componentB)}`;
  }

  analyzeIntegration(components: PNKLNComponent[]): string {
    return `# PNKLN Stack Integration Analysis

## Components in Scope
${components.map((c, i) => `${i + 1}. ${c}`).join("\n")}

## Data Flow Analysis
Analyzing how data flows through the selected components:

${this.getDataFlowAnalysis(components)}

## Integration Patterns
${this.getIntegrationPatterns(components)}

## Dependency Graph
${this.getDependencyGraph(components)}

## Optimization Opportunities
${this.getIntegrationOptimizations(components)}`;
  }

  // Helper methods
  private getComponentPurpose(component: PNKLNComponent): string {
    const purposes: Record<PNKLNComponent, string> = {
      "judge-6": "Real-time validation & enforcement",
      "gemini-ingestion": "Intelligence collection & classification",
      validator: "Data validation & quality assurance",
      processor: "Data transformation & enrichment",
      storage: "Persistent data storage",
      "api-gateway": "API routing & authentication",
    };
    return purposes[component];
  }

  private getComponentArch(component: PNKLNComponent): string {
    const archs: Record<PNKLNComponent, string> = {
      "judge-6": "Hybrid Gemini+PyTorch",
      "gemini-ingestion": "GKE CronJob Multi-Container",
      validator: "Microservice",
      processor: "Stream Processing",
      storage: "Distributed Database",
      "api-gateway": "Gateway + Load Balancer",
    };
    return archs[component];
  }

  private getPrimaryMetric(component: PNKLNComponent): string {
    const metrics: Record<PNKLNComponent, string> = {
      "judge-6": "p99 latency ≤ 90ms",
      "gemini-ingestion": "~45 min/night runtime",
      validator: "Validation accuracy",
      processor: "Throughput (items/sec)",
      storage: "Query latency",
      "api-gateway": "Request latency",
    };
    return metrics[component];
  }

  private getIntegrationPattern(component: PNKLNComponent): string {
    const patterns: Record<PNKLNComponent, string> = {
      "judge-6": "Caller (invokes 4 namespaces)",
      "gemini-ingestion": "Callee (invoked by 4 namespaces)",
      validator: "Middleware",
      processor: "Pipeline stage",
      storage: "Data layer",
      "api-gateway": "Entry point",
    };
    return patterns[component];
  }

  private getArchitectureDiff(compA: PNKLNComponent, compB: PNKLNComponent): string {
    return `${compA} uses ${this.getComponentArch(compA)} while ${compB} uses ${this.getComponentArch(compB)}.
This reflects their different positions in the stack: ${this.getComponentPurpose(compA)} vs ${this.getComponentPurpose(compB)}.`;
  }

  private getMigrationPath(from: PNKLNComponent, to: PNKLNComponent): string {
    return `When adapting analysis from ${from} to ${to}, consider:
1. Adjust performance metrics from ${this.getPrimaryMetric(from)} to ${this.getPrimaryMetric(to)}
2. Update integration patterns: ${this.getIntegrationPattern(from)} → ${this.getIntegrationPattern(to)}
3. Refocus quality measures based on component purpose
4. Adapt confidence thresholds for available data`;
  }

  private getDataFlowAnalysis(components: PNKLNComponent[]): string {
    return `Data typically flows: Ingestion → Validation → Processing → Storage → API Gateway
Components analyzed: ${components.join(" → ")}`;
  }

  private getIntegrationPatterns(components: PNKLNComponent[]): string {
    return components.map((c) => `- ${c}: ${this.getIntegrationPattern(c)}`).join("\n");
  }

  private getDependencyGraph(components: PNKLNComponent[]): string {
    return `\`\`\`
${components.map((c, i) => "  ".repeat(i) + `└─ ${c}`).join("\n")}
\`\`\``;
  }

  private getIntegrationOptimizations(components: PNKLNComponent[]): string {
    return `- Analyze handoff latency between components
- Identify redundant validation steps
- Optimize data format transformations
- Consider caching strategies at integration points`;
  }
}

// Export singleton instance
export const masterPromptFramework = new MasterPromptFrameworkImpl();
