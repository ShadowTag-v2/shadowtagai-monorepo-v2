/**
 * Thread Transfer Package System
 * Main orchestrator for creating complete transfer packages
 */

import { HandoffOutlineBuilder } from "./handoff-outline.js";
import { RestartPromptBuilder } from "./restart-prompt.js";
import { StateSummaryBuilder } from "./state-summary.js";
import type { HandoffOutline, RestartPrompt, StateSummary, TransferPackage } from "./types.js";
import { AutoCritique, CritiqueBuilder, PackageValidator } from "./validation.js";

export class TransferPackageBuilder {
  private package: Partial<TransferPackage> = {
    metadata: {
      version: "1.0.0",
      generated: new Date().toISOString(),
      threadId: "",
    },
  };

  withThreadId(id: string): this {
    this.package.metadata!.threadId = id;
    return this;
  }

  withPart1(summary: StateSummary): this {
    this.package.part1 = summary;
    return this;
  }

  withPart2(outline: HandoffOutline): this {
    this.package.part2 = outline;
    return this;
  }

  withPart3(prompt: RestartPrompt): this {
    this.package.part3 = prompt;
    return this;
  }

  withCritique(critique: CritiqueBuilder): this {
    this.package.critique = critique.build();
    return this;
  }

  autoCritique(): this {
    if (!this.package.part1 || !this.package.part2 || !this.package.part3) {
      throw new Error("Parts 1-3 must be set before auto-critique");
    }

    const pkg = this.package as TransferPackage;
    this.package.critique = AutoCritique.analyze(pkg).build();
    return this;
  }

  build(): TransferPackage {
    if (!this.package.part1) {
      throw new Error("Part 1 (State Summary) is required");
    }
    if (!this.package.part2) {
      throw new Error("Part 2 (Handoff Outline) is required");
    }
    if (!this.package.part3) {
      throw new Error("Part 3 (Restart Prompt) is required");
    }
    if (!this.package.critique) {
      throw new Error("Critique is required (use autoCritique() or withCritique())");
    }

    return this.package as TransferPackage;
  }

  validate(): { package: TransferPackage; validation: any } {
    const pkg = this.build();
    const validator = new PackageValidator();
    const validation = validator.validate(pkg);

    return { package: pkg, validation };
  }

  toMarkdown(): string {
    const pkg = this.build();
    const validator = new PackageValidator();
    const validation = validator.validate(pkg);

    const lines: string[] = [];

    lines.push("# 3-PART THREAD TRANSFER PACKAGE\n");
    lines.push(`**Version**: ${pkg.metadata.version}`);
    lines.push(`**Generated**: ${pkg.metadata.generated}`);
    lines.push(`**Thread ID**: ${pkg.metadata.threadId}`);
    lines.push(`**Completeness**: ${validation.completeness}%\n`);

    lines.push("---\n");

    // Part 1
    const part1Builder = new StateSummaryBuilder();
    Object.assign(part1Builder, { summary: pkg.part1 });
    lines.push(part1Builder.toMarkdown());
    lines.push("\n---\n");

    // Part 2
    const part2Builder = new HandoffOutlineBuilder();
    Object.assign(part2Builder, { outline: pkg.part2 });
    lines.push(part2Builder.toMarkdown());
    lines.push("\n---\n");

    // Part 3
    const part3Builder = new RestartPromptBuilder();
    Object.assign(part3Builder, { prompt: pkg.part3 });
    lines.push(part3Builder.toMarkdown());
    lines.push("\n---\n");

    // Critique
    const critiqueBuilder = new CritiqueBuilder();
    Object.assign(critiqueBuilder, { critique: pkg.critique });
    lines.push(critiqueBuilder.toMarkdown());

    lines.push("\n---\n");

    lines.push("# TRANSFER COMPLETE\n");
    lines.push(
      "Copy **PART 3** into new thread to restore full context. " +
        "Parts 1-2 provide audit trail if deeper history needed.\n",
    );

    if (validation.errors.length > 0) {
      lines.push("## VALIDATION ERRORS:\n");
      validation.errors.forEach((e: string) => lines.push(`* ❌ ${e}`));
      lines.push("");
    }

    if (validation.warnings.length > 0) {
      lines.push("## VALIDATION WARNINGS:\n");
      validation.warnings.forEach((w: string) => lines.push(`* ⚠️  ${w}`));
    }

    return lines.join("\n");
  }

  toJSON(): string {
    return JSON.stringify(this.build(), null, 2);
  }

  toCompact(): string {
    const pkg = this.build();
    const part3Builder = new RestartPromptBuilder();
    Object.assign(part3Builder, { prompt: pkg.part3 });

    const lines: string[] = [];
    lines.push(`TRANSFER PACKAGE: ${pkg.metadata.threadId}`);
    lines.push(`Generated: ${pkg.metadata.generated}`);
    lines.push("");
    lines.push("QUICK RESTORE:");
    lines.push(part3Builder.toCompactFormat());

    return lines.join("\n");
  }
}

import { FrameworkPresets, RiskAssessment } from "./handoff-outline.js";
import { RestartPromptFactory } from "./restart-prompt.js";
/**
 * Quick-start templates for common scenarios
 */
import { StateSummaryFactory } from "./state-summary.js";
import { Probability, Severity } from "./types.js";

export class TransferPackageTemplates {
  static mcpIntegrationAnalysis(
    threadId: string,
    repos: string[],
    strategy: string,
  ): TransferPackageBuilder {
    const part1 = StateSummaryFactory.forMCPIntegration(threadId, repos, strategy).build();

    const part2Builder = new HandoffOutlineBuilder()
      .addParameters({
        GH_USER: "erikcleveland",
        ORG_TARGET: "pnkln",
        FORK_STRATEGY: strategy,
        REPO_COUNT: repos.length,
      })
      .withFrameworks(FrameworkPresets.pnklnBootstrap())
      .setObjectives(
        [`Execute ${strategy} fork strategy`, "Validate MCP token reduction claims (40-60%)"],
        [
          "Map MCP architecture to PNKLN namespace strategy",
          "Integrate into judge-six, core-stack, shadow-tag, ns-mesh, audit-compress",
        ],
        ["GKE-native production deployment", "MCP-optimized Judge #6 enforcement"],
      )
      .addVariable("REPOS", "Array of org/repo strings")
      .addVariable("fork_repo()", "Function: Fork with existence check")
      .addVariable("GH_USER", "Target fork namespace")
      .addQuestion("Fork to personal (erikcleveland) vs org (pnkln)?")
      .addQuestion("Full clone vs on-demand API reads?")
      .addQuestion("Upstream sync cadence? (ad-hoc vs scheduled)")
      .addRiskFlag(
        RiskAssessment.createRisk(
          "Rate Limits",
          "GitHub API 5000/hr authenticated",
          Probability.C,
          Severity.III,
          "Implement backoff + batch operations",
        ),
      )
      .addRiskFlag(
        RiskAssessment.createRisk(
          "Fork Sprawl",
          "No hygiene policy defined yet",
          Probability.B,
          Severity.IV,
          "Define fork lifecycle + cleanup process",
        ),
      )
      .addRiskFlag(
        RiskAssessment.createRisk(
          "Sync Debt",
          "Manual upstream merge required",
          Probability.B,
          Severity.III,
          "Establish automated sync checks",
        ),
      );

    repos.forEach((repo) => {
      const [org, name] = repo.split("/");
      const priority =
        name === "typescript-sdk"
          ? ("PRIMARY" as const)
          : name.includes("quickstart") || name.includes("servers")
            ? ("SECONDARY" as const)
            : ("REFERENCE" as const);

      part2Builder.addRepository({
        org,
        repo: name,
        priority,
        purpose: TransferPackageTemplates.getRepoPurpose(name),
      });
    });

    const part3 = RestartPromptFactory.forMCPIntegration(threadId, strategy, repos).build();

    return new TransferPackageBuilder()
      .withThreadId(threadId)
      .withPart1(part1)
      .withPart2(part2Builder.build())
      .withPart3(part3)
      .autoCritique();
  }

  static geminiIngestionLayer(threadId: string, sources: string[]): TransferPackageBuilder {
    const part1 = StateSummaryFactory.forGeminiIngestion(threadId, sources).build();

    const part2Builder = new HandoffOutlineBuilder()
      .addParameters({
        RUNTIME_TARGET: "~45 min/night",
        MONTHLY_COST: 77,
        SOURCE_COUNT: sources.length,
      })
      .withFrameworks(FrameworkPresets.pnklnBootstrap())
      .setObjectives(
        ["Analyze current ingestion performance", "Identify optimization opportunities"],
        ["Implement tier classification system", "Enhance ethical compliance model"],
        ["Scale to additional sources", "Reduce per-item cost"],
      );

    const part3 = RestartPromptFactory.forGeminiIngestion(threadId, sources).build();

    return new TransferPackageBuilder()
      .withThreadId(threadId)
      .withPart1(part1)
      .withPart2(part2Builder.build())
      .withPart3(part3)
      .autoCritique();
  }

  private static getRepoPurpose(repoName: string): string {
    const purposes: Record<string, string> = {
      "anthropic-quickstarts": "Reference implementations",
      servers: "MCP server patterns",
      "typescript-sdk": "Core SDK for integration",
      courses: "Training materials",
      "DeepSeek-V3": "Model architecture reference",
      "Qwen2.5-Coder": "Code generation benchmarks",
      "llama-models": "Alternative model comparison",
    };

    return purposes[repoName] || "General reference";
  }
}
