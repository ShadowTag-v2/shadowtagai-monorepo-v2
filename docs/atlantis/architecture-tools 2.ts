import { tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import * as fs from "fs/promises";
import * as path from "path";
import { z } from "zod";

/**
 * Tool for analyzing file structure and dependencies
 */
export const analyzeFileStructure = tool(
  "analyze_file_structure",
  "Analyzes the file and directory structure of a codebase to identify organizational patterns and potential issues",
  {
    directory: z.string().describe("The root directory to analyze"),
    maxDepth: z.number().default(5).describe("Maximum depth to traverse (default: 5)"),
  },
  async (input) => {
    const { directory, maxDepth = 5 } = input;

    const fileTree: any = {};
    const stats = {
      totalFiles: 0,
      totalDirs: 0,
      filesByExtension: {} as Record<string, number>,
    };

    async function traverse(dir: string, depth: number = 0): Promise<any> {
      if (depth > maxDepth) return null;

      try {
        const entries = await fs.readdir(dir, { withFileTypes: true });
        const result: any = {};

        for (const entry of entries) {
          const fullPath = path.join(dir, entry.name);

          // Skip node_modules and common build directories
          if (entry.name === "node_modules" || entry.name === "dist" || entry.name === ".git") {
            continue;
          }

          if (entry.isDirectory()) {
            stats.totalDirs++;
            result[entry.name] = await traverse(fullPath, depth + 1);
          } else {
            stats.totalFiles++;
            const ext = path.extname(entry.name);
            stats.filesByExtension[ext] = (stats.filesByExtension[ext] || 0) + 1;
            result[entry.name] = "file";
          }
        }

        return result;
      } catch (error) {
        return { error: `Unable to read directory: ${error}` };
      }
    }

    const tree = await traverse(directory);

    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(
            {
              structure: tree,
              statistics: stats,
              analysis: {
                organizationPattern: detectOrganizationPattern(tree, stats),
                suggestions: generateStructureSuggestions(stats),
              },
            },
            null,
            2,
          ),
        },
      ],
    };
  },
);

/**
 * Tool for identifying code smells and anti-patterns
 */
export const identifyCodeSmells = tool(
  "identify_code_smells",
  "Analyzes code files to identify common code smells, anti-patterns, and architectural issues",
  {
    filePath: z.string().describe("Path to the file to analyze"),
  },
  async (input) => {
    try {
      const content = await fs.readFile(input.filePath, "utf-8");
      const lines = content.split("\n");

      const issues: any[] = [];

      // Check for large files
      if (lines.length > 300) {
        issues.push({
          type: "large_file",
          severity: "warning",
          message: `File has ${lines.length} lines. Consider breaking it into smaller modules.`,
        });
      }

      // Check for long functions (simple heuristic)
      const functionMatches = content.match(/function\s+\w+|=>\s*{|class\s+\w+/g);
      if (functionMatches && functionMatches.length > 20) {
        issues.push({
          type: "too_many_functions",
          severity: "info",
          message: "File contains many functions. Consider organizing into separate modules.",
        });
      }

      // Check for deeply nested code
      const maxIndentation = Math.max(
        ...lines.map((line) => {
          const match = line.match(/^(\s*)/);
          return match ? match[1].length : 0;
        }),
      );

      if (maxIndentation > 32) {
        issues.push({
          type: "deep_nesting",
          severity: "warning",
          message: "Deep nesting detected. Consider refactoring to reduce complexity.",
        });
      }

      // Check for commented code
      const commentedCodeLines = lines.filter(
        (line) => line.trim().startsWith("//") && line.includes("(") && line.includes(")"),
      ).length;

      if (commentedCodeLines > 5) {
        issues.push({
          type: "commented_code",
          severity: "info",
          message:
            "Multiple lines of commented code found. Consider removing or documenting why it is kept.",
        });
      }

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(
              {
                filePath: input.filePath,
                issues,
                metrics: {
                  lines: lines.length,
                  estimatedComplexity: calculateComplexity(content),
                },
              },
              null,
              2,
            ),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({ error: `Unable to analyze file: ${error}` }),
          },
        ],
      };
    }
  },
);

/**
 * Tool for suggesting architecture patterns
 */
export const suggestArchitecturePattern = tool(
  "suggest_architecture_pattern",
  "Suggests appropriate architecture patterns based on project characteristics",
  {
    projectType: z
      .string()
      .describe("Type of project (e.g., web-api, microservice, monolith, spa, mobile)"),
    scalabilityNeeds: z
      .enum(["low", "medium", "high"])
      .optional()
      .describe("Scalability requirements"),
    teamSize: z.number().optional().describe("Team size working on the project"),
  },
  async (input) => {
    const patterns = getRecommendedPatterns(
      input.projectType,
      input.scalabilityNeeds || "medium",
      input.teamSize || 5,
    );

    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(
            {
              recommendations: patterns,
              reasoning: generatePatternReasoning(input),
            },
            null,
            2,
          ),
        },
      ],
    };
  },
);

// Helper functions
function detectOrganizationPattern(tree: any, stats: any): string {
  const extensions = Object.keys(stats.filesByExtension);

  if (extensions.includes(".ts") || extensions.includes(".js")) {
    if (tree.src) return "src-based (standard)";
    if (tree.lib) return "lib-based (library)";
  }

  if (extensions.includes(".py")) {
    if (tree.app) return "app-based (Flask/FastAPI)";
    if (tree.src) return "src-based (standard Python)";
  }

  return "flat or custom structure";
}

function generateStructureSuggestions(stats: any): string[] {
  const suggestions: string[] = [];

  if (stats.totalFiles > 50 && stats.totalDirs < 5) {
    suggestions.push("Consider organizing files into more directories to improve maintainability");
  }

  return suggestions;
}

function calculateComplexity(content: string): number {
  // Simple cyclomatic complexity estimate
  const controlFlowKeywords = ["if", "for", "while", "case", "catch", "&&", "||"];
  let complexity = 1;

  for (const keyword of controlFlowKeywords) {
    const matches = content.match(new RegExp(`\\b${keyword}\\b`, "g"));
    if (matches) complexity += matches.length;
  }

  return complexity;
}

function getRecommendedPatterns(projectType: string, scalability: string, teamSize: number): any[] {
  const patterns: any[] = [];

  if (projectType.includes("api") || projectType.includes("fastapi")) {
    patterns.push({
      name: "Clean Architecture",
      description: "Separates business logic from infrastructure concerns",
      pros: ["Testable", "Framework-independent", "Maintainable"],
      cons: ["Initial complexity", "More files/folders"],
      bestFor: "Medium to large APIs with complex business logic",
    });

    patterns.push({
      name: "Layered Architecture",
      description: "Organizes code into presentation, business, and data layers",
      pros: ["Simple to understand", "Clear separation of concerns"],
      cons: ["Can become tightly coupled", "May hinder testing"],
      bestFor: "Standard CRUD APIs",
    });
  }

  if (scalability === "high") {
    patterns.push({
      name: "Microservices",
      description: "Breaks application into small, independent services",
      pros: ["Scalable", "Technology flexibility", "Fault isolation"],
      cons: ["Operational complexity", "Distributed system challenges"],
      bestFor: "Large teams, high-scale applications",
    });

    patterns.push({
      name: "CQRS",
      description: "Separates read and write operations",
      pros: ["Optimized reads/writes", "Scalable"],
      cons: ["Increased complexity", "Eventual consistency"],
      bestFor: "High-throughput systems with different read/write patterns",
    });
  }

  if (teamSize < 5) {
    patterns.push({
      name: "Modular Monolith",
      description: "Single deployment with clear module boundaries",
      pros: ["Simpler deployment", "Good module boundaries", "Easy to test"],
      cons: ["Single scaling unit", "Shared database"],
      bestFor: "Small to medium teams, moderate scale",
    });
  }

  return patterns;
}

function generatePatternReasoning(input: any): string {
  return `Based on project type "${input.projectType}", scalability needs "${input.scalabilityNeeds || "medium"}", and team size ${input.teamSize || "unknown"}, the recommended patterns balance complexity with project requirements.`;
}

/**
 * Create an MCP server with architecture tools
 */
export const architectureMcpServer = createSdkMcpServer({
  name: "architecture-tools",
  version: "1.0.0",
  tools: [analyzeFileStructure, identifyCodeSmells, suggestArchitecturePattern],
});
