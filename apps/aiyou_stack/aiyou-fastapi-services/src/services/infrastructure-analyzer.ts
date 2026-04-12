/**
 * Infrastructure Analysis Service
 * Routes infrastructure analysis requests to specialized prompts
 */

import { AnthropicVertex } from "@anthropic-ai/vertex-sdk";
import { GEMINI_INGESTION_ANALYSIS_PROMPT } from "../prompts/gemini-ingestion-analysis";
import { logger } from "../utils/logger";

export enum InfrastructureComponent {
  GEMINI_INGESTION = "gemini-ingestion",
  JUDGE_SIX = "judge-six",
  PNKLN_CORE = "pnkln-core",
  UNKNOWN = "unknown",
}

export interface InfrastructureAnalysisRequest {
  component: InfrastructureComponent;
  documentation?: string;
  architectureSpecs?: string;
  context?: Record<string, any>;
}

export interface InfrastructureAnalysisResult {
  component: InfrastructureComponent;
  analysis: unknown; // Parsed JSON from Claude
  rawResponse: string;
  confidence: number;
  timestamp: string;
}

export class InfrastructureAnalyzer {
  private client: AnthropicVertex;

  constructor() {
    this.client = new AnthropicVertex({
      region: process.env.CLOUD_ML_REGION || "us-central1",
      projectId: process.env.ANTHROPIC_VERTEX_PROJECT_ID,
    });
  }

  /**
   * Detect which infrastructure component is being referenced
   */
  detectComponent(userInput: string): InfrastructureComponent {
    const input = userInput.toLowerCase();

    // Gemini Ingestion Layer
    if (
      input.includes("gemini ingestion") ||
      input.includes("ingestion layer") ||
      input.includes("intelligence collection") ||
      input.includes("crawler") ||
      input.includes("data ingestion")
    ) {
      return InfrastructureComponent.GEMINI_INGESTION;
    }

    // Judge #6
    if (input.includes("judge") || input.includes("validation") || input.includes("enforcement")) {
      return InfrastructureComponent.JUDGE_SIX;
    }

    // PNKLN Core
    if (
      input.includes("pnkln core") ||
      input.includes("core stack") ||
      input.includes("orchestrator")
    ) {
      return InfrastructureComponent.PNKLN_CORE;
    }

    return InfrastructureComponent.UNKNOWN;
  }

  /**
   * Get the appropriate analysis prompt for a component
   */
  private getAnalysisPrompt(component: InfrastructureComponent): string {
    switch (component) {
      case InfrastructureComponent.GEMINI_INGESTION:
        return GEMINI_INGESTION_ANALYSIS_PROMPT;

      case InfrastructureComponent.JUDGE_SIX:
        // TODO: Add Judge #6 analysis prompt
        return "Judge #6 analysis not yet implemented";

      case InfrastructureComponent.PNKLN_CORE:
        // TODO: Add PNKLN Core analysis prompt
        return "PNKLN Core analysis not yet implemented";

      default:
        return "Unknown component - cannot analyze";
    }
  }

  /**
   * Analyze an infrastructure component
   */
  async analyzeComponent(
    request: InfrastructureAnalysisRequest,
  ): Promise<InfrastructureAnalysisResult> {
    const startTime = Date.now();

    logger.info("Starting infrastructure analysis", {
      component: request.component,
    });

    // Get the appropriate prompt
    const systemPrompt = this.getAnalysisPrompt(request.component);

    // Build user message with documentation context
    let userMessage = `Analyze the ${request.component} component.\n\n`;

    if (request.documentation) {
      userMessage += `DOCUMENTATION:\n${request.documentation}\n\n`;
    }

    if (request.architectureSpecs) {
      userMessage += `ARCHITECTURE SPECS:\n${request.architectureSpecs}\n\n`;
    }

    if (request.context) {
      userMessage += `ADDITIONAL CONTEXT:\n${JSON.stringify(request.context, null, 2)}\n\n`;
    }

    userMessage += "Provide a comprehensive analysis in the specified JSON format.";

    try {
      // Call Claude via Vertex AI
      const response = await this.client.messages.create({
        model: "claude-opus-4-1@20250805",
        max_tokens: 20000,
        temperature: 0.7,
        system: systemPrompt,
        messages: [
          {
            role: "user",
            content: [{ type: "text", text: userMessage }],
          },
        ],
      });

      const rawResponse = response.content[0].text;
      const duration = Date.now() - startTime;

      logger.info("Infrastructure analysis completed", {
        component: request.component,
        duration,
        tokensUsed: response.usage?.total_tokens,
      });

      // Parse JSON response
      let analysis: unknown;
      let confidence = 0;

      try {
        // Extract JSON from response (handle markdown code blocks)
        const jsonMatch = rawResponse.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          analysis = JSON.parse(jsonMatch[0]);
          confidence = analysis.summary?.confidence || 0;
        } else {
          throw new Error("No JSON found in response");
        }
      } catch (error) {
        logger.warn("Failed to parse analysis JSON", {
          error: error instanceof Error ? error.message : String(error),
        });

        // Return raw response if parsing fails
        analysis = {
          summary: {
            overallAssessment: "Failed to parse structured analysis",
            confidence: 0,
            readinessLevel: "unknown",
          },
          rawAnalysis: rawResponse,
        };
      }

      return {
        component: request.component,
        analysis,
        rawResponse,
        confidence,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      logger.error("Infrastructure analysis failed", {
        component: request.component,
        error: error instanceof Error ? error.message : String(error),
      });

      throw error;
    }
  }

  /**
   * Format analysis result for user display
   */
  formatAnalysisForDisplay(result: InfrastructureAnalysisResult): string {
    const { component, analysis, confidence } = result;

    let output = `
# Infrastructure Analysis: ${component}

**Confidence**: ${(confidence * 100).toFixed(0)}%
**Timestamp**: ${result.timestamp}

---

## Executive Summary

${analysis.summary?.overallAssessment || "No summary available"}

**Readiness Level**: ${analysis.summary?.readinessLevel?.toUpperCase() || "UNKNOWN"}

---
`;

    // Architecture section
    if (analysis.architecture) {
      output += `
## Architecture

**Strengths**:
${analysis.architecture.strengths?.map((s: string) => `- ${s}`).join("\n") || "- None identified"}

**Weaknesses**:
${analysis.architecture.weaknesses?.map((w: string) => `- ${w}`).join("\n") || "- None identified"}

**Recommendations**:
${analysis.architecture.recommendations?.map((r: string) => `- ${r}`).join("\n") || "- None"}

---
`;
    }

    // Performance section
    if (analysis.performance) {
      output += `
## Performance Metrics

${JSON.stringify(analysis.performance, null, 2)}

---
`;
    }

    // Ethical Compliance (for Gemini Ingestion)
    if (analysis.ethicalCompliance) {
      output += `
## Ethical Compliance

- **robots.txt Adherence**: ${analysis.ethicalCompliance.robotsTxtAdherence || "Unknown"}
- **Rate Limiting**: ${analysis.ethicalCompliance.rateLimiting || "Unknown"}
- **Transparency**: ${analysis.ethicalCompliance.transparency || "Unknown"}

**Risks**:
${analysis.ethicalCompliance.risks?.map((r: string) => `- ${r}`).join("\n") || "- None identified"}

---
`;
    }

    // Recommendations
    if (analysis.recommendations) {
      output += `
## Recommendations

**Immediate** (Urgent):
${analysis.recommendations.immediate?.map((r: string) => `- ${r}`).join("\n") || "- None"}

**Short-Term** (1 month):
${analysis.recommendations.shortTerm?.map((r: string) => `- ${r}`).join("\n") || "- None"}

**Long-Term** (Strategic):
${analysis.recommendations.longTerm?.map((r: string) => `- ${r}`).join("\n") || "- None"}

---
`;
    }

    // Next Steps
    if (analysis.nextSteps) {
      output += `
## Next Steps

${JSON.stringify(analysis.nextSteps, null, 2)}
`;
    }

    return output;
  }
}
