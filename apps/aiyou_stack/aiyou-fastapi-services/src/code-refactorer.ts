/**
 * Code Refactorer Agent
 *
 * Refactoring specialist who improves code quality.
 * Cleans up that code you wrote at 3am. Makes it readable, fast, and maintainable.
 *
 * Key Features:
 * - Code cleanup
 * - Readability improvement
 * - Performance optimization
 * - Maintainability enhancement
 * - Best practices application
 * - Technical debt reduction
 */

import { ClaudeAgentOptions, query, tool } from "@anthropic-ai/claude-agent-sdk";

/**
 * Refactoring configuration options
 */
export interface RefactorConfig {
  /**
   * Focus areas for refactoring
   */
  focus?: Array<
    "readability" | "performance" | "maintainability" | "best-practices" | "technical-debt"
  >;

  /**
   * Programming language of the code to refactor
   */
  language?: string;

  /**
   * Maximum level of changes to make
   * - conservative: Only safe, obvious improvements
   * - moderate: Standard refactoring practices
   * - aggressive: Comprehensive restructuring
   */
  aggressiveness?: "conservative" | "moderate" | "aggressive";

  /**
   * Whether to include explanations for each change
   */
  explainChanges?: boolean;

  /**
   * Custom coding standards or style guide to follow
   */
  styleGuide?: string;

  /**
   * Specific issues to address (e.g., code smells, anti-patterns)
   */
  specificIssues?: string[];
}

/**
 * Analysis result from code inspection
 */
export interface CodeAnalysis {
  issues: Array<{
    type: string;
    severity: "low" | "medium" | "high" | "critical";
    description: string;
    location?: string;
    suggestion?: string;
  }>;
  metrics: {
    complexity?: number;
    maintainabilityIndex?: number;
    technicalDebt?: string;
  };
  recommendations: string[];
}

/**
 * Refactoring result
 */
export interface RefactorResult {
  refactoredCode: string;
  changes: Array<{
    type: string;
    description: string;
    before?: string;
    after?: string;
    reasoning?: string;
  }>;
  analysis: CodeAnalysis;
  summary: string;
}

/**
 * Custom tool for analyzing code quality
 */
const analyzeCodeTool = tool({
  name: "analyze_code_quality",
  description: "Analyzes code to identify issues, code smells, and areas for improvement",
  parameters: {
    type: "object",
    properties: {
      code: {
        type: "string",
        description: "The code to analyze",
      },
      language: {
        type: "string",
        description: "Programming language of the code",
      },
    },
    required: ["code"],
  },
  execute: async ({ code, language }) => {
    // This is a placeholder for actual code analysis logic
    // In a real implementation, you might use AST parsers, linters, or static analysis tools
    const issues = [];
    const recommendations = [];

    // Basic heuristic checks
    if (code.includes("var ")) {
      issues.push({
        type: "outdated-syntax",
        severity: "medium" as const,
        description: "Use of var instead of let/const",
        suggestion: "Replace var with let or const for block scoping",
      });
    }

    if (code.split("\n").some((line) => line.length > 100)) {
      issues.push({
        type: "readability",
        severity: "low" as const,
        description: "Long lines detected (>100 characters)",
        suggestion: "Break long lines for better readability",
      });
    }

    if (code.includes("// TODO") || code.includes("// FIXME")) {
      issues.push({
        type: "technical-debt",
        severity: "medium" as const,
        description: "TODO/FIXME comments found",
        suggestion: "Address technical debt markers",
      });
    }

    // Check for nested callbacks (callback hell)
    const callbackDepth = (code.match(/function\s*\([^)]*\)\s*{/g) || []).length;
    if (callbackDepth > 3) {
      issues.push({
        type: "complexity",
        severity: "high" as const,
        description: "Deep callback nesting detected",
        suggestion: "Consider using async/await or promises to flatten structure",
      });
    }

    return {
      issues,
      metrics: {
        complexity: callbackDepth,
        maintainabilityIndex: Math.max(0, 100 - issues.length * 10),
        technicalDebt: issues.length > 5 ? "high" : issues.length > 2 ? "medium" : "low",
      },
      recommendations: [
        "Follow consistent naming conventions",
        "Add appropriate error handling",
        "Include documentation for complex logic",
        "Consider extracting reusable functions",
        "Ensure proper separation of concerns",
      ],
    };
  },
});

/**
 * System prompt for the Code Refactorer agent
 */
const CODE_REFACTORER_SYSTEM_PROMPT = `You are an expert Code Refactorer agent specializing in improving code quality.

Your mission is to transform poorly written, hard-to-maintain code into clean, efficient, and maintainable solutions.

## Core Responsibilities:

1. **Code Cleanup**: Remove dead code, unused variables, and redundant logic
2. **Readability**: Improve naming, structure, and formatting for better comprehension
3. **Performance**: Identify and fix performance bottlenecks and inefficiencies
4. **Maintainability**: Restructure code to be easier to modify and extend
5. **Best Practices**: Apply industry-standard patterns and conventions
6. **Technical Debt**: Identify and reduce accumulated technical debt

## Refactoring Principles:

- **Don't change behavior**: Maintain the same functionality unless explicitly asked
- **Small steps**: Make incremental, testable changes
- **Preserve tests**: Ensure existing tests still pass (or update them appropriately)
- **Document changes**: Explain why each change improves the code
- **Consider context**: Understand the broader system before refactoring
- **Be pragmatic**: Balance idealism with practical constraints

## Analysis Approach:

1. **Understand**: Read and comprehend the code's purpose and current state
2. **Identify**: Find code smells, anti-patterns, and improvement opportunities
3. **Prioritize**: Focus on high-impact improvements first
4. **Refactor**: Apply systematic transformations
5. **Validate**: Ensure changes maintain correctness and improve quality
6. **Explain**: Provide clear reasoning for each change

## Common Refactoring Patterns:

- Extract Method/Function: Break down large functions
- Rename: Use descriptive, meaningful names
- Remove Duplication: Apply DRY (Don't Repeat Yourself)
- Simplify Conditionals: Reduce complexity in if/else chains
- Replace Magic Numbers: Use named constants
- Improve Error Handling: Add proper try/catch and validation
- Optimize Loops: Improve iteration efficiency
- Update Syntax: Use modern language features
- Add Type Safety: Include type annotations where beneficial
- Organize Imports: Clean up and structure dependencies

## Code Smells to Watch For:

- Long methods/functions (>20-30 lines)
- Large classes (God objects)
- Long parameter lists (>3-4 parameters)
- Duplicate code
- Dead code
- Speculative generality
- Inappropriate intimacy between modules
- Feature envy (method using more of another class than its own)
- Data clumps (same data items together repeatedly)
- Primitive obsession (overuse of primitives instead of objects)
- Switch/case statements that could be polymorphism
- Lazy classes (classes that don't do enough)
- Deep nesting (>3 levels)
- Comments explaining what code does (code should be self-explanatory)

## Output Format:

When refactoring, provide:
1. **Analysis**: Issues found and their severity
2. **Refactored Code**: The improved version
3. **Change Summary**: List of specific changes made
4. **Explanations**: Why each change improves the code
5. **Recommendations**: Additional improvements for future consideration

Always be constructive and educational. Help developers understand not just what to change, but why it matters.`;

/**
 * Main Code Refactorer agent function
 */
export async function refactorCode(
  code: string,
  config: RefactorConfig = {},
): Promise<RefactorResult> {
  const {
    focus = ["readability", "performance", "maintainability", "best-practices"],
    language = "auto-detect",
    aggressiveness = "moderate",
    explainChanges = true,
    styleGuide,
    specificIssues = [],
  } = config;

  // Build the prompt for the agent
  let prompt = `Please refactor the following code:\n\n\`\`\`${language}\n${code}\n\`\`\`\n\n`;

  prompt += `**Refactoring Configuration:**\n`;
  prompt += `- Focus areas: ${focus.join(", ")}\n`;
  prompt += `- Aggressiveness: ${aggressiveness}\n`;
  prompt += `- Language: ${language}\n`;

  if (styleGuide) {
    prompt += `- Style guide: ${styleGuide}\n`;
  }

  if (specificIssues.length > 0) {
    prompt += `- Specific issues to address: ${specificIssues.join(", ")}\n`;
  }

  prompt += `\n**Instructions:**\n`;
  prompt += `1. First, analyze the code to identify issues and improvement opportunities\n`;
  prompt += `2. Apply refactoring based on the focus areas and aggressiveness level\n`;
  prompt += `3. Provide the refactored code\n`;
  prompt += `4. List all changes made${explainChanges ? " with detailed explanations" : ""}\n`;
  prompt += `5. Provide a summary of improvements\n`;

  // Query the agent with custom tools
  const result = await query({
    prompt,
    options: {
      systemPrompt: CODE_REFACTORER_SYSTEM_PROMPT,
      tools: [analyzeCodeTool],
      model: "claude-sonnet-4-5-20250929", // Use the latest model
      maxTokens: 8192, // Allow for comprehensive refactoring
    },
  });

  // Parse the result (simplified - in production, use structured output)
  const responseText = result.content
    .filter((block: unknown) => block.type === "text")
    .map((block: unknown) => block.text)
    .join("\n");

  // Extract refactored code from markdown code blocks
  const codeBlockMatch = responseText.match(/```[\w]*\n([\s\S]*?)\n```/);
  const refactoredCode = codeBlockMatch ? codeBlockMatch[1] : code;

  // Build the result object
  return {
    refactoredCode,
    changes: [], // Would be populated from structured response
    analysis: {
      issues: [],
      metrics: {},
      recommendations: [],
    },
    summary: responseText,
  };
}

/**
 * Analyze code without refactoring
 */
export async function analyzeCode(code: string, language?: string): Promise<CodeAnalysis> {
  const prompt = `Please analyze the following code for issues, code smells, and improvement opportunities:\n\n\`\`\`${language || ""}\n${code}\n\`\`\`\n\nProvide a detailed analysis including:
1. List of issues with severity levels
2. Code quality metrics
3. Specific recommendations for improvement`;

  const result = await query({
    prompt,
    options: {
      systemPrompt: CODE_REFACTORER_SYSTEM_PROMPT,
      tools: [analyzeCodeTool],
      model: "claude-sonnet-4-5-20250929",
    },
  });

  // Use the analyze_code_quality tool result if available
  const toolResult = result.content.find(
    (block: unknown) => block.type === "tool_result" && block.name === "analyze_code_quality",
  );

  if (toolResult) {
    return JSON.parse(toolResult.content);
  }

  // Fallback to parsing text response
  return {
    issues: [],
    metrics: {},
    recommendations: [],
  };
}

/**
 * Interactive refactoring session
 */
export async function* refactorInteractive(
  code: string,
  config: RefactorConfig = {},
): AsyncGenerator<string, void, string | undefined> {
  const currentCode = code;
  let userFeedback = "";

  const initialPrompt = `I have code that needs refactoring. Let's work on it together interactively.

Initial code:
\`\`\`${config.language || ""}
${currentCode}
\`\`\`

Configuration: ${JSON.stringify(config, null, 2)}

Please start by analyzing the code and suggesting the first improvement.`;

  const stream = await query({
    prompt: initialPrompt,
    options: {
      systemPrompt: CODE_REFACTORER_SYSTEM_PROMPT,
      tools: [analyzeCodeTool],
      model: "claude-sonnet-4-5-20250929",
      stream: true,
    },
  });

  for await (const chunk of stream) {
    if (chunk.type === "text") {
      yield chunk.text;
    }
  }

  // Allow for follow-up iterations
  while (true) {
    userFeedback = yield "";
    if (!userFeedback || userFeedback.toLowerCase() === "done") {
      break;
    }

    const followUpStream = await query({
      prompt: userFeedback,
      options: {
        systemPrompt: CODE_REFACTORER_SYSTEM_PROMPT,
        model: "claude-sonnet-4-5-20250929",
        stream: true,
      },
    });

    for await (const chunk of followUpStream) {
      if (chunk.type === "text") {
        yield chunk.text;
      }
    }
  }
}

export default {
  refactorCode,
  analyzeCode,
  refactorInteractive,
  CODE_REFACTORER_SYSTEM_PROMPT,
};
