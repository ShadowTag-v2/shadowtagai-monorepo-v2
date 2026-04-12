import { query } from "@anthropic-ai/claude-agent-sdk";
import { type AgentConfig, getAgentConfig } from "../config/agent-config";
import { SYSTEM_PROMPTS } from "../config/system-prompts";
import { architectureMcpServer } from "../tools/architecture-tools";

/**
 * System Architect Agent
 *
 * Transforms messy codebases into clean, scalable systems.
 *
 * Key Features:
 * - System design and architecture patterns
 * - Scalability analysis
 * - Clean architecture principles
 * - Refactoring plans
 * - Best practices recommendations
 * - Technical debt assessment
 *
 * Use Cases:
 * - Architecture design
 * - System refactoring
 * - Scalability planning
 * - Clean code improvements
 * - Pattern implementation
 * - Technical debt management
 */
export class SystemArchitect {
  private config: AgentConfig;

  constructor(config?: Partial<AgentConfig>) {
    this.config = getAgentConfig(config);
  }

  /**
   * Analyze codebase architecture and provide recommendations
   */
  async analyzeArchitecture(
    prompt: string,
    options?: {
      includeTools?: boolean;
      contextFiles?: string[];
    },
  ): Promise<string> {
    const { includeTools = true, contextFiles = [] } = options || {};

    // Build context from files if provided
    let fullPrompt = prompt;
    if (contextFiles.length > 0) {
      const contextInfo = contextFiles.map((file) => `Context file: ${file}`).join("\n");
      fullPrompt = `${contextInfo}\n\n${prompt}`;
    }

    const queryOptions: unknown = {
      systemPrompt: SYSTEM_PROMPTS.SYSTEM_ARCHITECT,
    };

    // Add MCP server with tools if requested
    if (includeTools) {
      queryOptions.mcpServers = {
        "architecture-tools": architectureMcpServer,
      };
    }

    const queryGenerator = query({
      prompt: fullPrompt,
      options: queryOptions,
    });

    // Collect all messages from the async generator
    let finalResult = "";
    for await (const message of queryGenerator) {
      if (message.type === "result" && message.subtype === "success") {
        finalResult = message.result;
      } else if (message.type === "assistant" && message.message.content) {
        // Collect assistant messages
        for (const block of message.message.content) {
          if (block.type === "text") {
            finalResult += block.text;
          }
        }
      }
    }

    return finalResult || "No response generated";
  }

  /**
   * Design a system architecture for a new project
   */
  async designSystem(requirements: {
    projectType: string;
    scalability: "low" | "medium" | "high";
    teamSize: number;
    specificRequirements?: string;
  }): Promise<string> {
    const prompt = `Design a system architecture for the following project:

Project Type: ${requirements.projectType}
Scalability Needs: ${requirements.scalability}
Team Size: ${requirements.teamSize}
${requirements.specificRequirements ? `Specific Requirements:\n${requirements.specificRequirements}` : ""}

Please provide:
1. Recommended architecture pattern with justification
2. System component diagram (ASCII/text format)
3. Technology stack recommendations
4. Scalability considerations
5. Potential challenges and mitigation strategies
6. Implementation roadmap`;

    return this.analyzeArchitecture(prompt);
  }

  /**
   * Create a refactoring plan for existing code
   */
  async createRefactoringPlan(codebaseInfo: {
    description: string;
    currentIssues: string[];
    goals: string[];
  }): Promise<string> {
    const prompt = `Create a comprehensive refactoring plan for the following codebase:

Description: ${codebaseInfo.description}

Current Issues:
${codebaseInfo.currentIssues.map((issue, i) => `${i + 1}. ${issue}`).join("\n")}

Goals:
${codebaseInfo.goals.map((goal, i) => `${i + 1}. ${goal}`).join("\n")}

Please provide:
1. Prioritized list of refactoring tasks
2. Step-by-step implementation plan
3. Risk assessment for each major change
4. Testing strategy
5. Estimated effort and timeline
6. Quick wins vs long-term improvements`;

    return this.analyzeArchitecture(prompt);
  }

  /**
   * Review architecture and identify issues
   */
  async reviewArchitecture(directory: string): Promise<string> {
    const prompt = `Review the architecture of the codebase at: ${directory}

Please:
1. Analyze the file structure and organization
2. Identify architectural patterns in use
3. Detect code smells and anti-patterns
4. Suggest improvements for scalability and maintainability
5. Provide specific, actionable recommendations

Use the available tools to analyze the codebase structure and files.`;

    return this.analyzeArchitecture(prompt, { includeTools: true });
  }

  /**
   * Assess technical debt and provide remediation plan
   */
  async assessTechnicalDebt(issues: string[]): Promise<string> {
    const prompt = `Assess the following technical debt issues and create a remediation plan:

Issues:
${issues.map((issue, i) => `${i + 1}. ${issue}`).join("\n")}

Please provide:
1. Categorization of debt (design, code quality, testing, documentation)
2. Impact assessment (high/medium/low)
3. Prioritized remediation plan
4. Quick wins that can be addressed immediately
5. Long-term strategies for preventing new debt
6. Estimated effort for each remediation item`;

    return this.analyzeArchitecture(prompt);
  }

  /**
   * Suggest design patterns for specific problems
   */
  async suggestPatterns(problem: string, context?: string): Promise<string> {
    const prompt = `Suggest appropriate design patterns for the following problem:

Problem: ${problem}
${context ? `Context: ${context}` : ""}

Please provide:
1. Recommended design patterns (with names)
2. How each pattern solves the problem
3. Code examples in TypeScript/Python
4. Trade-offs and considerations
5. When NOT to use each pattern
6. Alternative approaches`;

    return this.analyzeArchitecture(prompt);
  }
}

// Export a default instance
export const systemArchitect = new SystemArchitect();
