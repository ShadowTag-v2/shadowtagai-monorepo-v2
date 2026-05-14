/**
 * Handoff Outline System
 * Key parameters, frameworks, risk assessment, and open questions
 */

import {
  type FrameworkConfig,
  type HandoffOutline,
  Probability,
  type Repository,
  type RiskFlag,
  RiskLevel,
  Severity,
} from "./types.js";

export class HandoffOutlineBuilder {
  private outline: Partial<HandoffOutline> = {
    keyParameters: {},
    variableConventions: {},
    openQuestions: [],
    riskFlags: [],
  };

  addParameter(key: string, value: string | number | boolean): this {
    this.outline.keyParameters![key] = value;
    return this;
  }

  addParameters(params: Record<string, string | number | boolean>): this {
    Object.assign(this.outline.keyParameters!, params);
    return this;
  }

  withFrameworks(config: FrameworkConfig): this {
    this.outline.frameworksActive = config;
    return this;
  }

  addRepository(repo: Repository): this {
    if (!this.outline.repositoryTargets) {
      this.outline.repositoryTargets = [];
    }
    this.outline.repositoryTargets.push(repo);
    return this;
  }

  setObjectives(immediate: string[], m1to3: string[], m3plus: string[]): this {
    this.outline.currentObjectives = { immediate, m1to3, m3plus };
    return this;
  }

  addVariable(name: string, description: string): this {
    this.outline.variableConventions![name] = description;
    return this;
  }

  addQuestion(question: string): this {
    this.outline.openQuestions?.push(question);
    return this;
  }

  addRiskFlag(risk: RiskFlag): this {
    this.outline.riskFlags?.push(risk);
    return this;
  }

  build(): HandoffOutline {
    if (!this.outline.frameworksActive) {
      throw new Error("FrameworkConfig is required");
    }
    if (!this.outline.currentObjectives) {
      throw new Error("CurrentObjectives is required");
    }

    return this.outline as HandoffOutline;
  }

  toMarkdown(): string {
    const outline = this.build();
    const lines: string[] = [];

    lines.push("# PART 2: HANDOFF OUTLINE\n");

    // Key Parameters
    lines.push("## Key Parameters\n");
    Object.entries(outline.keyParameters).forEach(([k, v]) => {
      lines.push(`**${k}** = \`${v}\``);
    });
    lines.push("");

    // Frameworks Active
    lines.push("## Frameworks Active\n");

    lines.push("### JR Engine");
    lines.push(`* **Purpose**: ${outline.frameworksActive.jrEngine.purpose}`);
    lines.push("* **Reasons**:");
    outline.frameworksActive.jrEngine.reasons.forEach((r) => lines.push(`  - ${r}`));
    lines.push("* **Brakes**:");
    outline.frameworksActive.jrEngine.brakes.forEach((b) => lines.push(`  - ${b}`));
    lines.push("");

    lines.push("### ATP 5-19 Risk Matrix");
    lines.push(`* **Enabled**: ${outline.frameworksActive.atp519.enabled}`);
    lines.push("* **Thresholds**:");
    Object.entries(outline.frameworksActive.atp519.thresholds).forEach(([level, desc]) => {
      lines.push(`  - **${level}**: ${desc}`);
    });
    lines.push("");

    lines.push("### Bootstrap Constraints");
    const bs = outline.frameworksActive.bootstrap;
    lines.push(`* Capital: $${bs.capital.toLocaleString()}`);
    lines.push(`* SLA p99: ≤${bs.slaP99Ms}ms`);
    lines.push(`* ROI: ≥${bs.roiMultiple}× (${bs.roiMonths}mo)`);
    lines.push(`* LTV:CAC: ≥${bs.ltvCacRatio}:1 (${bs.ltvCacMonths}mo)`);
    lines.push(`* Compression Target: ${bs.targetCompression.from} → ${bs.targetCompression.to}`);
    lines.push("");

    // Repository Targets
    if (outline.repositoryTargets && outline.repositoryTargets.length > 0) {
      lines.push("## Repository Targets\n");
      outline.repositoryTargets.forEach((repo, idx) => {
        const badge =
          repo.priority === "PRIMARY"
            ? "🎯 PRIMARY"
            : repo.priority === "SECONDARY"
              ? "📌 SECONDARY"
              : "📚 REFERENCE";
        lines.push(`${idx + 1}. **${repo.org}/${repo.repo}** - ${badge}`);
        lines.push(`   - ${repo.purpose}`);
      });
      lines.push("");
    }

    // Current Objectives
    lines.push("## Current Objectives\n");

    lines.push("### Immediate (M0)");
    outline.currentObjectives.immediate.forEach((obj) => lines.push(`* ${obj}`));
    lines.push("");

    lines.push("### M1-3");
    outline.currentObjectives.m1to3.forEach((obj) => lines.push(`* ${obj}`));
    lines.push("");

    lines.push("### M3+");
    outline.currentObjectives.m3plus.forEach((obj) => lines.push(`* ${obj}`));
    lines.push("");

    // Variable Conventions
    if (Object.keys(outline.variableConventions).length > 0) {
      lines.push("## Variable Names & Conventions\n");
      Object.entries(outline.variableConventions).forEach(([name, desc]) => {
        lines.push(`* \`${name}\` - ${desc}`);
      });
      lines.push("");
    }

    // Open Questions
    if (outline.openQuestions.length > 0) {
      lines.push("## Open Questions\n");
      outline.openQuestions.forEach((q) => lines.push(`* ${q}`));
      lines.push("");
    }

    // Risk Flags
    if (outline.riskFlags.length > 0) {
      lines.push("## Risk Flags\n");
      outline.riskFlags.forEach((risk) => {
        const icon = this.getRiskIcon(risk.level);
        lines.push(
          `* ${icon} **${risk.category}** [${risk.probability}×${risk.severity} → ${risk.level}]`,
        );
        lines.push(`  - ${risk.description}`);
        if (risk.mitigation) {
          lines.push(`  - *Mitigation*: ${risk.mitigation}`);
        }
      });
    }

    return lines.join("\n");
  }

  private getRiskIcon(level: RiskLevel): string {
    switch (level) {
      case RiskLevel.EH:
        return "🔴";
      case RiskLevel.H:
        return "🟠";
      case RiskLevel.M:
        return "🟡";
      case RiskLevel.L:
        return "🟢";
      default:
        return "⚪";
    }
  }
}

/**
 * Risk Assessment Utilities
 */
export class RiskAssessment {
  private static readonly RISK_MATRIX: Record<Probability, Record<Severity, RiskLevel>> = {
    [Probability.A]: {
      [Severity.I]: RiskLevel.EH,
      [Severity.II]: RiskLevel.EH,
      [Severity.III]: RiskLevel.H,
      [Severity.IV]: RiskLevel.M,
    },
    [Probability.B]: {
      [Severity.I]: RiskLevel.EH,
      [Severity.II]: RiskLevel.H,
      [Severity.III]: RiskLevel.M,
      [Severity.IV]: RiskLevel.L,
    },
    [Probability.C]: {
      [Severity.I]: RiskLevel.H,
      [Severity.II]: RiskLevel.M,
      [Severity.III]: RiskLevel.M,
      [Severity.IV]: RiskLevel.L,
    },
    [Probability.D]: {
      [Severity.I]: RiskLevel.M,
      [Severity.II]: RiskLevel.M,
      [Severity.III]: RiskLevel.L,
      [Severity.IV]: RiskLevel.L,
    },
    [Probability.E]: {
      [Severity.I]: RiskLevel.M,
      [Severity.II]: RiskLevel.L,
      [Severity.III]: RiskLevel.L,
      [Severity.IV]: RiskLevel.L,
    },
  };

  static calculateLevel(probability: Probability, severity: Severity): RiskLevel {
    return RiskAssessment.RISK_MATRIX[probability][severity];
  }

  static createRisk(
    category: string,
    description: string,
    probability: Probability,
    severity: Severity,
    mitigation?: string,
  ): RiskFlag {
    return {
      category,
      description,
      probability,
      severity,
      level: RiskAssessment.calculateLevel(probability, severity),
      mitigation,
    };
  }
}

/**
 * Predefined Framework Configurations
 */
export class FrameworkPresets {
  static pnklnBootstrap(): FrameworkConfig {
    return {
      jrEngine: {
        purpose: "Advances Pnkln/revenue?",
        reasons: ["Defensible?", "Evidence-based?", "Scalable?"],
        brakes: ["p99 survivable?", "Security maintained?", "ROI viable?"],
      },
      atp519: {
        enabled: true,
        thresholds: {
          [RiskLevel.EH]: "Probability (A-E) × Severity (I-IV) → Immediate escalation",
          [RiskLevel.H]: "Senior review required before proceed",
          [RiskLevel.M]: "Document and monitor",
          [RiskLevel.L]: "Accept and track",
        },
      },
      bootstrap: {
        capital: 0,
        slaP99Ms: 90,
        roiMultiple: 3,
        roiMonths: 18,
        ltvCacRatio: 4,
        ltvCacMonths: 12,
        targetCompression: {
          from: "50KB",
          to: "487 bytes",
        },
      },
    };
  }

  static productionReady(): FrameworkConfig {
    const base = FrameworkPresets.pnklnBootstrap();
    return {
      ...base,
      bootstrap: {
        ...base.bootstrap,
        roiMultiple: 5,
        roiMonths: 12,
        ltvCacRatio: 6,
        ltvCacMonths: 6,
      },
    };
  }
}
