/**
 * State Summary Generator
 * Captures session scope, build artifacts, and technical context
 */

import type { BuildArtifact, SessionScope, StateSummary, TechnicalContext } from "./types.js";

export class StateSummaryBuilder {
  private summary: Partial<StateSummary> = {};

  withSessionScope(scope: SessionScope): this {
    this.summary.sessionScope = scope;
    return this;
  }

  addBuildArtifact(artifact: BuildArtifact): this {
    if (!this.summary.whatWeBuilt) {
      this.summary.whatWeBuilt = [];
    }
    this.summary.whatWeBuilt.push(artifact);
    return this;
  }

  setCurrentState(status: string, blockers: string[], nextActions: string[]): this {
    this.summary.currentState = { status, blockers, nextActions };
    return this;
  }

  withTechnicalContext(context: TechnicalContext): this {
    this.summary.technicalContext = context;
    return this;
  }

  build(): StateSummary {
    if (!this.summary.sessionScope) {
      throw new Error("SessionScope is required");
    }
    if (!this.summary.whatWeBuilt || this.summary.whatWeBuilt.length === 0) {
      throw new Error("At least one BuildArtifact is required");
    }
    if (!this.summary.currentState) {
      throw new Error("CurrentState is required");
    }
    if (!this.summary.technicalContext) {
      throw new Error("TechnicalContext is required");
    }

    return this.summary as StateSummary;
  }

  toMarkdown(): string {
    const summary = this.build();
    const lines: string[] = [];

    lines.push("# PART 1: STATE SUMMARY\n");

    // Session Scope
    lines.push(`**Session Scope**: ${summary.sessionScope.objective}`);
    lines.push(`**Thread ID**: ${summary.sessionScope.threadId}`);
    lines.push(`**Domain**: ${summary.sessionScope.domain}`);
    lines.push(`**Started**: ${summary.sessionScope.startDate}\n`);

    // What We Built
    lines.push("## What We Built:\n");
    for (const artifact of summary.whatWeBuilt) {
      const status = artifact.ready ? "✅" : "⏳";
      lines.push(`* ${status} **${artifact.type.toUpperCase()}** (${artifact.path})`);
      lines.push(`  - ${artifact.description}`);
      if (artifact.dependencies && artifact.dependencies.length > 0) {
        lines.push(`  - Dependencies: ${artifact.dependencies.join(", ")}`);
      }
    }
    lines.push("");

    // Current State
    lines.push("## Current State:\n");
    lines.push(`**Status**: ${summary.currentState.status}\n`);

    if (summary.currentState.blockers.length > 0) {
      lines.push("**Blockers**:");
      for (const b of summary.currentState.blockers) {
        lines.push(`* ${b}`);
      }
      lines.push("");
    }

    lines.push("**Next Actions**:");
    for (const a of summary.currentState.nextActions) {
      lines.push(`* ${a}`);
    }
    lines.push("");

    // Technical Context
    lines.push("## Technical Context:\n");

    if (summary.technicalContext.architecture.length > 0) {
      lines.push("**Architecture**:");
      for (const a of summary.technicalContext.architecture) {
        lines.push(`* ${a}`);
      }
      lines.push("");
    }

    if (summary.technicalContext.namespaces) {
      lines.push(`**Namespaces**: ${summary.technicalContext.namespaces.join(", ")}`);
      lines.push("");
    }

    if (summary.technicalContext.metrics) {
      lines.push("**Metrics**:");
      for (const [k, v] of Object.entries(summary.technicalContext.metrics)) {
        lines.push(`* ${k}: ${v}`);
      }
      lines.push("");
    }

    if (summary.technicalContext.integrations) {
      lines.push(`**Integrations**: ${summary.technicalContext.integrations.join(", ")}`);
    }

    return lines.join("\n");
  }
}

/**
 * Factory functions for common session patterns
 */
export const StateSummaryFactory = {
  forMCPIntegration(threadId: string, repos: string[], strategy: string): StateSummaryBuilder {
    return new StateSummaryBuilder()
      .withSessionScope({
        domain: "MCP Integration Analysis",
        objective: "Validate MCP 40-60% token reduction claims through direct code analysis",
        startDate: new Date().toISOString().split("T")[0],
        threadId,
      })
      .addBuildArtifact({
        type: "script",
        path: "fork-repos.sh",
        description: `Fork ${repos.length} critical AI/MCP repos to erikcleveland GitHub namespace`,
        ready: true,
        dependencies: ["GitHub CLI"],
      })
      .setCurrentState(
        "Script ready for execution, pending user decision on fork strategy",
        [],
        [
          `Execute ${strategy} strategy`,
          "Clone MCP TypeScript SDK",
          "Map to PNKLN 4-5 namespace architecture",
        ],
      )
      .withTechnicalContext({
        architecture: [
          "MCP integration evaluation for Judge #6 (p99≤90ms SLA)",
          "Semantic compression targets: 487 bytes vs 50KB for governance decisions",
          "GKE-native deployment architecture",
        ],
        namespaces: ["judge-six", "core-stack", "shadow-tag", "ns-mesh", "audit-compress"],
        metrics: {
          "Target Token Reduction": "40-60%",
          "Current Compression": "487 bytes vs 50KB",
          "SLA p99": "≤90ms",
        },
      });
  },

  forGeminiIngestion(threadId: string, sources: string[]): StateSummaryBuilder {
    return new StateSummaryBuilder()
      .withSessionScope({
        domain: "Gemini Ingestion Layer",
        objective: "Intelligence collection pipeline analysis and optimization",
        startDate: new Date().toISOString().split("T")[0],
        threadId,
      })
      .withTechnicalContext({
        architecture: [
          "GKE CronJob Multi-Container",
          "Nightly batch processing (~45 min runtime)",
          "Multi-source coverage analysis",
        ],
        metrics: {
          "Runtime Target": "~45 min/night",
          "Monthly Cost": "$77",
          Sources: sources.length,
        },
        integrations: sources,
      });
  },
};
