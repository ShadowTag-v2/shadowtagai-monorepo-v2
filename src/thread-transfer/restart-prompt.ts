/**
 * Restart Prompt Builder
 * Context restoration for new thread initialization
 */

import type { RestartPrompt } from "./types.js";

export class RestartPromptBuilder {
  private prompt: Partial<RestartPrompt> = {
    currentState: [],
    bootstrapConstraints: [],
    frameworksActive: [],
    openQuestions: [],
  };

  withThreadId(id: string): this {
    this.prompt.threadId = id;
    return this;
  }

  withMission(mission: string): this {
    this.prompt.mission = mission;
    return this;
  }

  addStateItem(item: string): this {
    this.prompt.currentState?.push(item);
    return this;
  }

  addConstraint(constraint: string): this {
    this.prompt.bootstrapConstraints?.push(constraint);
    return this;
  }

  addFramework(framework: string): this {
    this.prompt.frameworksActive?.push(framework);
    return this;
  }

  addRepo(repo: string): this {
    if (!this.prompt.repos) {
      this.prompt.repos = [];
    }
    this.prompt.repos.push(repo);
    return this;
  }

  addQuestion(question: string): this {
    this.prompt.openQuestions?.push(question);
    return this;
  }

  withResumePoint(point: string): this {
    this.prompt.resumeFrom = point;
    return this;
  }

  build(): RestartPrompt {
    if (!this.prompt.threadId) {
      throw new Error("ThreadId is required");
    }
    if (!this.prompt.mission) {
      throw new Error("Mission is required");
    }
    if (!this.prompt.resumeFrom) {
      throw new Error("ResumeFrom is required");
    }

    return this.prompt as RestartPrompt;
  }

  toMarkdown(): string {
    const prompt = this.build();
    const lines: string[] = [];

    lines.push("# PART 3: RESTART PROMPT\n");
    lines.push(`**CONTEXT RESTORATION - THREAD ID**: ${prompt.threadId}\n`);

    // Mission
    lines.push(`**Mission**: ${prompt.mission}\n`);

    // Current State
    if (prompt.currentState.length > 0) {
      lines.push("**Current State**:");
      prompt.currentState.forEach((item) => lines.push(`- ${item}`));
      lines.push("");
    }

    // Bootstrap Constraints
    if (prompt.bootstrapConstraints.length > 0) {
      lines.push("**Bootstrap Constraints**:");
      prompt.bootstrapConstraints.forEach((c) => lines.push(`- ${c}`));
      lines.push("");
    }

    // Frameworks Active
    if (prompt.frameworksActive.length > 0) {
      lines.push("**Frameworks Active**:");
      prompt.frameworksActive.forEach((f) => lines.push(`- ${f}`));
      lines.push("");
    }

    // Repos
    if (prompt.repos && prompt.repos.length > 0) {
      lines.push(`**Repos**: ${prompt.repos.join(", ")}`);
      lines.push("");
    }

    // Open Questions
    if (prompt.openQuestions.length > 0) {
      lines.push("**Open Questions**:");
      prompt.openQuestions.forEach((q, idx) => lines.push(`${idx + 1}. ${q}`));
      lines.push("");
    }

    // Resume Point
    lines.push(`**Resume from**: ${prompt.resumeFrom}`);

    return lines.join("\n");
  }

  toCompactFormat(): string {
    const prompt = this.build();
    const sections: string[] = [];

    sections.push(`THREAD: ${prompt.threadId}`);
    sections.push(`MISSION: ${prompt.mission}`);

    if (prompt.currentState.length > 0) {
      sections.push(`STATE: ${prompt.currentState.join(" | ")}`);
    }

    if (prompt.bootstrapConstraints.length > 0) {
      sections.push(`CONSTRAINTS: ${prompt.bootstrapConstraints.join(" | ")}`);
    }

    if (prompt.frameworksActive.length > 0) {
      sections.push(`FRAMEWORKS: ${prompt.frameworksActive.join(" | ")}`);
    }

    if (prompt.repos && prompt.repos.length > 0) {
      sections.push(`REPOS: ${prompt.repos.length} targets`);
    }

    if (prompt.openQuestions.length > 0) {
      sections.push(`QUESTIONS: ${prompt.openQuestions.length} open`);
    }

    sections.push(`RESUME: ${prompt.resumeFrom}`);

    return sections.join("\n");
  }

  toJSON(): string {
    return JSON.stringify(this.build(), null, 2);
  }
}

/**
 * Restart Prompt Factory
 */
export class RestartPromptFactory {
  static forMCPIntegration(
    threadId: string,
    strategy: string,
    repos: string[],
  ): RestartPromptBuilder {
    return new RestartPromptBuilder()
      .withThreadId(threadId)
      .withMission(
        "Validate MCP (Model Context Protocol) 40-60% token reduction claims through direct code analysis. " +
          `Fork ${repos.length} critical repos (Anthropic/MCP/DeepSeek/Qwen/Llama) to erikcleveland namespace ` +
          "for implementation mapping to PNKLN Judge #6 architecture.",
      )
      .addStateItem(
        `Script ready: fork-repos.sh (GitHub CLI, ${repos.length} repos, personal namespace default)`,
      )
      .addStateItem(`Pending: Execution strategy selection (${strategy})`)
      .addStateItem("Next: Fork → clone MCP TypeScript SDK → map to GKE 4-5 namespace architecture")
      .addConstraint("$0K capital, Judge #6 p99≤90ms SLA non-negotiable")
      .addConstraint("Target: 487 bytes vs 50KB governance decisions via semantic compression")
      .addConstraint("GCP-exclusive, Vertex Workbench → GKE-native production")
      .addFramework("JR Engine: Purpose → Reasons → Brakes")
      .addFramework("ATP 5-19 Risk Matrix: Probability × Severity → EH/H/M/L")
      .addFramework("ROI ≥3× (18mo), LTV:CAC ≥4:1 (12mo)")
      .addQuestion(`Fork strategy? (Best=full clone, Fast=API-only, Cheap=selective)`)
      .addQuestion("Namespace? (erikcleveland personal vs pnkln org)")
      .addQuestion("Sync policy? (ad-hoc vs scheduled upstream merge)")
      .withResumePoint("Execute fork decision → begin MCP SDK analysis");
  }

  static forGeminiIngestion(threadId: string, sources: string[]): RestartPromptBuilder {
    return new RestartPromptBuilder()
      .withThreadId(threadId)
      .withMission(
        "Analyze Gemini Ingestion Layer for intelligence collection pipeline optimization. " +
          "Focus on ethical compliance, multi-source coverage, and tier classification.",
      )
      .addStateItem("GKE CronJob Multi-Container architecture defined")
      .addStateItem(`${sources.length} sources configured`)
      .addStateItem("Nightly batch processing (~45 min runtime)")
      .addConstraint("Monthly operational cost: ~$77")
      .addConstraint("Quality gates: Items, Sources, Costs, Scores")
      .addFramework("Ethical Compliance Model (robots.txt, rate limiting)")
      .addFramework("Multi-Source Coverage Analysis")
      .addFramework("Tier Classification Metrics (Tier 1/2/3)")
      .addQuestion("Optimize for speed vs cost vs coverage?")
      .addQuestion("Tier distribution targets?")
      .withResumePoint("Execute coverage analysis → optimize tier ratios");
  }

  static minimal(threadId: string, mission: string, resumeFrom: string): RestartPromptBuilder {
    return new RestartPromptBuilder()
      .withThreadId(threadId)
      .withMission(mission)
      .withResumePoint(resumeFrom);
  }
}
