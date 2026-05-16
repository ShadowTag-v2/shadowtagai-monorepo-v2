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
    const params = this.outline.keyParameters ?? {};
    params[key] = value;
    this.outline.keyParameters = params;
    return this;
  }

  addParameters(params: Record<string, string | number | boolean>): this {
    this.outline.keyParameters = { ...this.outline.keyParameters, ...params };
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
    const conventions = this.outline.variableConventions ?? {};
    conventions[name] = description;
    this.outline.variableConventions = conventions;
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
    for (const [k, v] of Object.entries(outline.keyParameters)) {
      lines.push(`**${k}** = \`${v}\``);
    }
    lines.push("");

    // Frameworks Active
    lines.push("## Frameworks Active\n");

    lines.push("### JR Engine");
    lines.push(`* **Purpose**: ${outline.frameworksActive.jrEngine.purpose}`);
    lines.push("* **Reasons**:");
    for (const r of outline.frameworksActive.jrEngine.reasons) {
      lines.push(`  - ${r}`);
    }
    lines.push("* **Brakes**:");
    for (const b of outline.frameworksActive.jrEngine.brakes) {
      lines.push(`  - ${b}`);
    }
    lines.push("");

    lines.push("### ATP 5-19 Risk Matrix");
    lines.push(`* **Enabled**: ${outline.frameworksActive.atp519.enabled}`);
    lines.push("* **Thresholds**:");
    for (const [level, desc] of Object.entries(outline.frameworksActive.atp519.thresholds)) {
      lines.push(`  - **${level}**: ${desc}`);
    }
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
      for (const [idx, repo] of outline.repositoryTargets.entries()) {
        const badge =
          repo.priority === "PRIMARY"
            ? "🎯 PRIMARY"
            : repo.priority === "SECONDARY"
              ? "📌 SECONDARY"
              : "📚 REFERENCE";
        lines.push(`${idx + 1}. **${repo.org}/${repo.repo}** - ${badge}`);
        lines.push(`   - ${repo.purpose}`);
      }
      lines.push("");
    }

    // Current Objectives
    lines.push("## Current Objectives\n");

    lines.push("### Immediate (M0)");
    for (const obj of outline.currentObjectives.immediate) {
      lines.push(`* ${obj}`);
    }
    lines.push("");

    lines.push("### M1-3");
    for (const obj of outline.currentObjectives.m1to3) {
      lines.push(`* ${obj}`);
    }
    lines.push("");

    lines.push("### M3+");
    for (const obj of outline.currentObjectives.m3plus) {
      lines.push(`* ${obj}`);
    }
    lines.push("");

    // Variable Conventions
    if (Object.keys(outline.variableConventions).length > 0) {
      lines.push("## Variable Names & Conventions\n");
      for (const [name, desc] of Object.entries(outline.variableConventions)) {
        lines.push(`* \`${name}\` - ${desc}`);
      }
      lines.push("");
    }

    // Open Questions
    if (outline.openQuestions.length > 0) {
      lines.push("## Open Questions\n");
      for (const q of outline.openQuestions) {
        lines.push(`* ${q}`);
      }
      lines.push("");
    }

    // Risk Flags
    if (outline.riskFlags.length > 0) {
      lines.push("## Risk Flags\n");
      for (const risk of outline.riskFlags) {
        const icon = this.getRiskIcon(risk.level);
        lines.push(
          `* ${icon} **${risk.category}** [${risk.probability}×${risk.severity} → ${risk.level}]`,
        );
        lines.push(`  - ${risk.description}`);
        if (risk.mitigation) {
          lines.push(`  - *Mitigation*: ${risk.mitigation}`);
        }
      }
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
const RISK_MATRIX: Record<Probability, Record<Severity, RiskLevel>> = {
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

export const RiskAssessment = {
  calculateLevel(probability: Probability, severity: Severity): RiskLevel {
    return RISK_MATRIX[probability][severity];
  },

  createRisk(
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
  },
};

/**
 * Predefined Framework Configurations
 */
export const FrameworkPresets = {
  pnklnBootstrap(): FrameworkConfig {
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
  },

  productionReady(): FrameworkConfig {
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
  },
};
