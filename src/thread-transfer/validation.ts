/**
 * Validation and Critique System
 * Self-assessment, assumption tracking, and quality checks
 */

import type {
  HandoffOutline,
  RestartPrompt,
  StateSummary,
  TransferPackage,
  ValidationResult,
} from "./types.js";

export interface Critique {
  assumptions: string[];
  weaknesses: string[];
  whatCouldBeWrong: string[];
}

export class CritiqueBuilder {
  private critique: Critique = {
    assumptions: [],
    weaknesses: [],
    whatCouldBeWrong: [],
  };

  addAssumption(assumption: string): this {
    this.critique.assumptions.push(assumption);
    return this;
  }

  addWeakness(weakness: string): this {
    this.critique.weaknesses.push(weakness);
    return this;
  }

  addRisk(risk: string): this {
    this.critique.whatCouldBeWrong.push(risk);
    return this;
  }

  build(): Critique {
    return this.critique;
  }

  toMarkdown(): string {
    const c = this.critique;
    const lines: string[] = [];

    lines.push("# CRITIQUE\n");

    if (c.assumptions.length > 0) {
      lines.push("## ASSUMPTIONS:");
      for (const a of c.assumptions) {
        lines.push(`* ${a}`);
      }
      lines.push("");
    }

    if (c.weaknesses.length > 0) {
      lines.push("## WEAKNESSES:");
      for (const w of c.weaknesses) {
        lines.push(`* ${w}`);
      }
      lines.push("");
    }

    if (c.whatCouldBeWrong.length > 0) {
      lines.push("## WHAT COULD BE WRONG:");
      for (const r of c.whatCouldBeWrong) {
        lines.push(`* ${r}`);
      }
    }

    return lines.join("\n");
  }
}

export class PackageValidator {
  validate(pkg: TransferPackage): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let score = 100;

    // Validate Part 1: State Summary
    const summaryResult = this.validateStateSummary(pkg.part1);
    errors.push(...summaryResult.errors);
    warnings.push(...summaryResult.warnings);
    score -= summaryResult.penalty;

    // Validate Part 2: Handoff Outline
    const handoffResult = this.validateHandoffOutline(pkg.part2);
    errors.push(...handoffResult.errors);
    warnings.push(...handoffResult.warnings);
    score -= handoffResult.penalty;

    // Validate Part 3: Restart Prompt
    const restartResult = this.validateRestartPrompt(pkg.part3);
    errors.push(...restartResult.errors);
    warnings.push(...restartResult.warnings);
    score -= restartResult.penalty;

    // Validate Critique
    const critiqueResult = this.validateCritique(pkg.critique);
    warnings.push(...critiqueResult.warnings);
    score -= critiqueResult.penalty;

    return {
      valid: errors.length === 0,
      errors,
      warnings,
      completeness: Math.max(0, Math.min(100, score)),
    };
  }

  private validateStateSummary(summary: StateSummary): {
    errors: string[];
    warnings: string[];
    penalty: number;
  } {
    const errors: string[] = [];
    const warnings: string[] = [];
    let penalty = 0;

    if (!summary.sessionScope.threadId) {
      errors.push("Part 1: Missing threadId");
      penalty += 20;
    }

    if (!summary.sessionScope.objective) {
      errors.push("Part 1: Missing session objective");
      penalty += 15;
    }

    if (!summary.whatWeBuilt || summary.whatWeBuilt.length === 0) {
      warnings.push("Part 1: No build artifacts documented");
      penalty += 10;
    }

    if (!summary.currentState.nextActions || summary.currentState.nextActions.length === 0) {
      warnings.push("Part 1: No next actions defined");
      penalty += 10;
    }

    if (summary.currentState.blockers.length > 0) {
      warnings.push(`Part 1: ${summary.currentState.blockers.length} active blockers`);
    }

    return { errors, warnings, penalty };
  }

  private validateHandoffOutline(outline: HandoffOutline): {
    errors: string[];
    warnings: string[];
    penalty: number;
  } {
    const errors: string[] = [];
    const warnings: string[] = [];
    let penalty = 0;

    if (!outline.frameworksActive) {
      errors.push("Part 2: Missing frameworks configuration");
      penalty += 20;
    }

    if (!outline.currentObjectives) {
      errors.push("Part 2: Missing current objectives");
      penalty += 15;
    }

    if (outline.openQuestions.length === 0) {
      warnings.push("Part 2: No open questions documented");
      penalty += 5;
    }

    if (outline.riskFlags.length === 0) {
      warnings.push("Part 2: No risk flags identified");
      penalty += 10;
    }

    if (Object.keys(outline.keyParameters).length === 0) {
      warnings.push("Part 2: No key parameters defined");
      penalty += 10;
    }

    return { errors, warnings, penalty };
  }

  private validateRestartPrompt(prompt: RestartPrompt): {
    errors: string[];
    warnings: string[];
    penalty: number;
  } {
    const errors: string[] = [];
    const warnings: string[] = [];
    let penalty = 0;

    if (!prompt.threadId) {
      errors.push("Part 3: Missing threadId");
      penalty += 20;
    }

    if (!prompt.mission || prompt.mission.length < 20) {
      errors.push("Part 3: Mission too brief or missing");
      penalty += 15;
    }

    if (!prompt.resumeFrom) {
      errors.push("Part 3: Missing resume point");
      penalty += 15;
    }

    if (prompt.currentState.length === 0) {
      warnings.push("Part 3: No current state items");
      penalty += 10;
    }

    if (prompt.frameworksActive.length === 0) {
      warnings.push("Part 3: No frameworks referenced");
      penalty += 10;
    }

    return { errors, warnings, penalty };
  }

  private validateCritique(critique: Critique): {
    warnings: string[];
    penalty: number;
  } {
    const warnings: string[] = [];
    let penalty = 0;

    if (critique.assumptions.length === 0) {
      warnings.push("Critique: No assumptions documented");
      penalty += 5;
    }

    if (critique.weaknesses.length === 0) {
      warnings.push("Critique: No weaknesses identified");
      penalty += 5;
    }

    if (critique.whatCouldBeWrong.length === 0) {
      warnings.push("Critique: No risks identified");
      penalty += 5;
    }

    return { warnings, penalty };
  }
}

/**
 * Auto-Critique Generator
 * Analyzes transfer package and generates self-assessment
 */
export const AutoCritique = {
  analyze(pkg: TransferPackage): CritiqueBuilder {
    const builder = new CritiqueBuilder();

    // Analyze scope assumptions
    if (!pkg.part2.repositoryTargets || pkg.part2.repositoryTargets.length === 0) {
      builder.addAssumption("No repository targets specified - assumes single-session scope");
    }

    if (pkg.part1.currentState.blockers.length === 0) {
      builder.addAssumption("No blockers identified - assumes smooth execution path");
    }

    if (pkg.part3.openQuestions.length === 0) {
      builder.addAssumption("No open questions - assumes complete context or simple task");
    }

    // Analyze weaknesses
    if (pkg.part1.whatWeBuilt.length < 2) {
      builder.addWeakness("Limited build artifacts - may not capture full session complexity");
    }

    if (Object.keys(pkg.part2.keyParameters).length < 3) {
      builder.addWeakness("Few key parameters - handoff may lack critical configuration details");
    }

    if (pkg.part3.currentState.length < 2) {
      builder.addWeakness("Minimal state capture - restart may require additional context");
    }

    if (!pkg.part2.currentObjectives.m1to3 || pkg.part2.currentObjectives.m1to3.length === 0) {
      builder.addWeakness("No M1-3 objectives - lacks medium-term planning context");
    }

    // Analyze risks
    if (!pkg.metadata.generated) {
      builder.addRisk("Missing timestamp - cannot track package freshness");
    }

    if (pkg.part1.technicalContext.architecture.length === 0) {
      builder.addRisk("No architecture context - restart may miss critical system details");
    }

    if (pkg.part2.riskFlags.length === 0) {
      builder.addRisk("No risk flags - may overlook operational hazards");
    }

    builder.addRisk("Conciseness may sacrifice critical nuance");
    builder.addRisk("Restart prompt may need expansion for different AI instances");
    builder.addRisk("No backup of generated code/scripts in transfer package");

    return builder;
  },

  forMCPIntegration(): CritiqueBuilder {
    return new CritiqueBuilder()
      .addAssumption(
        "Next thread continues MCP evaluation immediately (vs pivoting to different workstream)",
      )
      .addAssumption(
        "Reader has access to userMemories context (Pnkln stack, bootstrap constraints)",
      )
      .addAssumption(
        "Restart prompt sufficient to recreate working state without re-explaining fundamentals",
      )
      .addWeakness("Summary assumes single-session scope; multi-day context not captured")
      .addWeakness(
        "No project-level state (PNKLN Core Stack broader architecture not detailed here)",
      )
      .addWeakness(
        "Restart prompt lacks specific MCP integration test criteria (latency benchmarks, token counts)",
      )
      .addWeakness(
        "Handoff outline doesn't capture implicit decisions (why these 7 repos vs others?)",
      )
      .addWeakness("No timestamp/version metadata for script state")
      .addWeakness("Missing link to broader M1-3 milestones beyond MCP analysis")
      .addRisk("Conciseness may sacrifice critical nuance (e.g., why TypeScript SDK is PRIMARY)")
      .addRisk(
        "Restart prompt may need expansion if new thread involves different AI instance without prior memory",
      )
      .addRisk(
        "No backup of generated script code in transfer package (assumes script content known)",
      );
  },
};
