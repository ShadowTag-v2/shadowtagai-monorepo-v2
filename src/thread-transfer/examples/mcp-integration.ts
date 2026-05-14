/**
 * Example: MCP Integration Analysis Transfer Package
 */

import {
  FrameworkPresets,
  HandoffOutlineBuilder,
  Probability,
  RestartPromptBuilder,
  RiskAssessment,
  Severity,
  StateSummaryBuilder,
  TransferPackageBuilder,
  TransferPackageTemplates,
} from "../index.js";

/**
 * Example 1: Using the template (quickest)
 */
export function exampleUsingTemplate() {
  const repos = [
    "anthropics/anthropic-quickstarts",
    "modelcontextprotocol/servers",
    "modelcontextprotocol/typescript-sdk",
    "anthropics/courses",
    "deepseek-ai/DeepSeek-V3",
    "QwenLM/Qwen2.5-Coder",
    "meta-llama/llama-models",
  ];

  const package1 = TransferPackageTemplates.mcpIntegrationAnalysis(
    "MCP-FORK-20241117",
    repos,
    "BEST",
  );

  console.log(package1.toMarkdown());
}

/**
 * Example 2: Building from scratch (most flexible)
 */
export function exampleFromScratch() {
  const threadId = "MCP-CUSTOM-20241117";

  // Part 1: State Summary
  const part1 = new StateSummaryBuilder()
    .withSessionScope({
      domain: "MCP Integration",
      objective: "Custom MCP analysis with specific focus areas",
      startDate: "2024-11-17",
      threadId,
    })
    .addBuildArtifact({
      type: "script",
      path: "custom-fork.sh",
      description: "Custom fork script with enhanced error handling",
      ready: true,
      dependencies: ["GitHub CLI", "jq"],
    })
    .addBuildArtifact({
      type: "config",
      path: ".mcp-config.json",
      description: "MCP integration configuration",
      ready: false,
      dependencies: ["custom-fork.sh"],
    })
    .setCurrentState(
      "Custom script development in progress",
      ["Need to finalize error handling", "Waiting for GitHub token"],
      ["Complete error handling", "Obtain GitHub token", "Test fork script"],
    )
    .withTechnicalContext({
      architecture: [
        "Custom MCP integration with enhanced logging",
        "Multi-stage validation pipeline",
        "Rollback support for failed forks",
      ],
      namespaces: ["mcp-integration", "validation", "rollback"],
      metrics: {
        "Expected Token Reduction": "50-65%",
        "Validation Stages": 3,
        "Rollback Window": "24h",
      },
      integrations: ["GitHub API", "Slack notifications", "Datadog monitoring"],
    })
    .build();

  // Part 2: Handoff Outline
  const part2 = new HandoffOutlineBuilder()
    .addParameters({
      GH_USER: "erikcleveland",
      FORK_STRATEGY: "CUSTOM",
      VALIDATION_ENABLED: true,
      ROLLBACK_ENABLED: true,
    })
    .withFrameworks(FrameworkPresets.pnklnBootstrap())
    .setObjectives(
      ["Complete custom fork script", "Test with single repo", "Validate rollback"],
      [
        "Fork all 7 repos with validation",
        "Implement monitoring dashboards",
        "Document integration patterns",
      ],
      ["Scale to 20+ repos", "Automate sync schedules", "Build self-healing system"],
    )
    .addVariable("VALIDATION_STAGES", "Array of validation functions")
    .addVariable("ROLLBACK_WINDOW_HOURS", "Number of hours to keep rollback data")
    .addQuestion("Should we notify on every fork or batch notifications?")
    .addQuestion("What threshold for automatic rollback?")
    .addQuestion("Enable dry-run mode by default?")
    .addRiskFlag(
      RiskAssessment.createRisk(
        "GitHub API Limits",
        "Rate limits could block batch operations",
        Probability.B,
        Severity.III,
        "Implement exponential backoff + request queuing",
      ),
    )
    .addRiskFlag(
      RiskAssessment.createRisk(
        "Validation Overhead",
        "Multi-stage validation may slow operations significantly",
        Probability.C,
        Severity.IV,
        "Make validation stages optional/configurable",
      ),
    )
    .build();

  // Part 3: Restart Prompt
  const part3 = new RestartPromptBuilder()
    .withThreadId(threadId)
    .withMission(
      "Build custom MCP fork system with enhanced validation, rollback, and monitoring capabilities",
    )
    .addStateItem("Custom fork script 80% complete")
    .addStateItem("Validation pipeline designed but not implemented")
    .addStateItem("Rollback mechanism pending design")
    .addConstraint("Must support dry-run mode")
    .addConstraint("Rollback within 24h window")
    .addConstraint("Slack notifications required")
    .addFramework("JR Engine: Purpose → Reasons → Brakes")
    .addFramework("ATP 5-19 Risk Matrix")
    .addFramework("Custom validation pipeline (3 stages)")
    .addRepo("modelcontextprotocol/typescript-sdk")
    .addRepo("anthropics/courses")
    .addQuestion("Batch vs individual notifications?")
    .addQuestion("Auto-rollback threshold?")
    .withResumePoint("Complete fork script → implement validation → test rollback")
    .build();

  // Complete package
  const package2 = new TransferPackageBuilder()
    .withThreadId(threadId)
    .withPart1(part1)
    .withPart2(part2)
    .withPart3(part3)
    .autoCritique();

  console.log(package2.toMarkdown());
  console.log("\n\n=== VALIDATION ===\n");

  const { validation } = package2.validate();
  console.log(`Completeness: ${validation.completeness}%`);
  console.log(`Errors: ${validation.errors.length}`);
  console.log(`Warnings: ${validation.warnings.length}`);
}

/**
 * Example 3: JSON export for programmatic use
 */
export function exampleJSONExport() {
  const repos = ["modelcontextprotocol/typescript-sdk"];

  const pkg = TransferPackageTemplates.mcpIntegrationAnalysis("MCP-JSON-EXPORT", repos, "FAST");

  const json = pkg.toJSON();
  console.log(json);

  // Can be parsed and used programmatically
  const parsed = JSON.parse(json);
  console.log(`\nThread ID: ${parsed.metadata.threadId}`);
  console.log(`Mission: ${parsed.part3.mission}`);
}

/**
 * Example 4: Compact format for quick restore
 */
export function exampleCompactFormat() {
  const repos = ["anthropics/anthropic-quickstarts"];

  const pkg = TransferPackageTemplates.mcpIntegrationAnalysis("MCP-COMPACT", repos, "CHEAP");

  const compact = pkg.toCompact();
  console.log(compact);
}

// Run examples
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log("=== EXAMPLE 1: Using Template ===\n");
  exampleUsingTemplate();

  console.log("\n\n=== EXAMPLE 2: Building from Scratch ===\n");
  exampleFromScratch();

  console.log("\n\n=== EXAMPLE 3: JSON Export ===\n");
  exampleJSONExport();

  console.log("\n\n=== EXAMPLE 4: Compact Format ===\n");
  exampleCompactFormat();
}
