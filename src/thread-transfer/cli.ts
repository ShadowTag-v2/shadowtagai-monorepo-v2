#!/usr/bin/env node
/**
 * Thread Transfer Package CLI
 * Command-line interface for generating transfer packages
 */

import { writeFileSync } from "node:fs";
import { TransferPackageTemplates } from "./package.js";

interface CLIArgs {
  command: "mcp" | "gemini" | "help";
  threadId?: string;
  output?: string;
  format?: "markdown" | "json" | "compact";
  repos?: string[];
  sources?: string[];
  strategy?: string;
}

function parseArgs(args: string[]): CLIArgs {
  const parsed: CLIArgs = {
    command: "help",
    format: "markdown",
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    switch (arg) {
      case "mcp":
      case "gemini":
        parsed.command = arg;
        break;
      case "--thread-id":
      case "-t":
        parsed.threadId = args[++i];
        break;
      case "--output":
      case "-o":
        parsed.output = args[++i];
        break;
      case "--format":
      case "-f":
        parsed.format = args[++i] as "markdown" | "json" | "compact";
        break;
      case "--repos":
      case "-r":
        parsed.repos = args[++i].split(",");
        break;
      case "--sources":
      case "-s":
        parsed.sources = args[++i].split(",");
        break;
      case "--strategy":
        parsed.strategy = args[++i];
        break;
      case "--help":
      case "-h":
        parsed.command = "help";
        break;
    }
  }

  return parsed;
}

function generateThreadId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  return `${timestamp}-${random}`.toUpperCase();
}

function showHelp(): void {
  console.log(`
Thread Transfer Package Generator

USAGE:
  thread-transfer <command> [options]

COMMANDS:
  mcp       Generate MCP integration analysis package
  gemini    Generate Gemini ingestion layer package
  help      Show this help message

OPTIONS:
  -t, --thread-id <id>      Thread ID (auto-generated if not provided)
  -o, --output <file>       Output file path (stdout if not provided)
  -f, --format <format>     Output format: markdown, json, compact (default: markdown)
  -r, --repos <repos>       Comma-separated list of repos (for mcp)
  -s, --sources <sources>   Comma-separated list of sources (for gemini)
  --strategy <strategy>     Fork strategy: BEST, FAST, CHEAP (for mcp, default: BEST)

EXAMPLES:
  # MCP integration analysis
  thread-transfer mcp -r "anthropics/anthropic-quickstarts,modelcontextprotocol/typescript-sdk" -o transfer.md

  # Gemini ingestion layer
  thread-transfer gemini -s "YouTube,Twitter,News" -f json -o transfer.json

  # Auto-generate thread ID and output to stdout
  thread-transfer mcp -r "anthropics/courses" --strategy FAST

  # Compact format for quick restore
  thread-transfer mcp -r "modelcontextprotocol/servers" -f compact
`);
}

function main(): void {
  const args = parseArgs(process.argv.slice(2));

  if (args.command === "help") {
    showHelp();
    return;
  }

  const threadId = args.threadId || generateThreadId();

  try {
    let builder: ReturnType<typeof TransferPackageTemplates.mcpIntegrationAnalysis> | undefined;
    let output = "";

    switch (args.command) {
      case "mcp": {
        if (!args.repos || args.repos.length === 0) {
          console.error("Error: --repos is required for mcp command");
          process.exit(1);
        }

        const strategy = args.strategy || "BEST";
        const repoStrings = args.repos.map((r) => (r.includes("/") ? r : `unknown/${r}`));

        builder = TransferPackageTemplates.mcpIntegrationAnalysis(threadId, repoStrings, strategy);
        break;
      }

      case "gemini": {
        if (!args.sources || args.sources.length === 0) {
          console.error("Error: --sources is required for gemini command");
          process.exit(1);
        }

        builder = TransferPackageTemplates.geminiIngestionLayer(threadId, args.sources);
        break;
      }

      default:
        console.error(`Unknown command: ${args.command}`);
        showHelp();
        process.exit(1);
    }

    // Generate output based on format
    switch (args.format) {
      case "json":
        output = builder.toJSON();
        break;
      case "compact":
        output = builder.toCompact();
        break;
      default:
        output = builder.toMarkdown();
        break;
    }

    // Write to file or stdout
    if (args.output) {
      writeFileSync(args.output, output, "utf-8");
      console.log(`✅ Transfer package written to: ${args.output}`);

      const { validation } = builder.validate();
      console.log(`📊 Completeness: ${validation.completeness}%`);

      if (validation.errors.length > 0) {
        console.log(`❌ Errors: ${validation.errors.length}`);
      }
      if (validation.warnings.length > 0) {
        console.log(`⚠️  Warnings: ${validation.warnings.length}`);
      }
    } else {
      console.log(output);
    }
  } catch (error) {
    console.error("Error generating transfer package:");
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

// Run CLI if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { generateThreadId, main, parseArgs, showHelp };
