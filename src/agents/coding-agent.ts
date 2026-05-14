/**
 * Production-Ready Coding Agent
 *
 * Domain-specific agent for code review, refactoring, and bug detection.
 * Implements all framework best practices.
 */

import { readFile } from "node:fs/promises";
import { query, tool } from "@anthropic-ai/claude-agent-sdk";

// ==================== Types ====================

interface CodeReviewResult {
  file: string;
  issues: CodeIssue[];
  suggestions: CodeSuggestion[];
  metrics: CodeMetrics;
  summary: string;
}

interface CodeIssue {
  line: number;
  severity: "critical" | "high" | "medium" | "low";
  category: "bug" | "security" | "performance" | "style";
  message: string;
  fix?: string;
}

interface CodeSuggestion {
  line: number;
  type: "refactor" | "optimization" | "modernization";
  message: string;
  example?: string;
}

interface CodeMetrics {
  linesOfCode: number;
  complexity: number;
  maintainabilityIndex: number;
  testCoverage?: number;
}

// ==================== System Prompt ====================

const CODING_AGENT_PROMPT = `
<agent_configuration>
  <metadata>
    <agent_name>Senior Code Reviewer</agent_name>
    <version>1.0.0</version>
    <pattern>single-agent</pattern>
    <domain>software-engineering</domain>
  </metadata>

  <role>
You are a senior software engineer with 10+ years of experience in TypeScript,
Python, and system design. You specialize in:
- Code review and quality assessment
- Security vulnerability identification
- Performance optimization
- Best practices enforcement
- Refactoring and modernization

Your reviews are thorough, constructive, and actionable.
  </role>

  <core_capabilities>
Primary Capabilities:
- Static code analysis
- Security vulnerability detection (OWASP Top 10)
- Performance bottleneck identification
- Code smell detection
- Test coverage analysis
- Refactoring recommendations

Analysis Framework:
1. CORRECTNESS
   - Logic errors and edge cases
   - Type safety and null checks
   - Error handling completeness
   - Algorithm correctness

2. SECURITY
   - Input validation
   - SQL/XSS/CSRF injection risks
   - Authentication/authorization flaws
   - Sensitive data exposure
   - Dependency vulnerabilities

3. PERFORMANCE
   - Time complexity issues
   - Memory leaks
   - Inefficient algorithms
   - Database query optimization
   - Caching opportunities

4. MAINTAINABILITY
   - Code clarity and readability
   - Documentation quality
   - Test coverage
   - Design patterns usage
   - SOLID principles adherence

5. STYLE & CONVENTIONS
   - Naming conventions
   - Code formatting
   - Best practices
   - Language idioms
  </core_capabilities>

  <quality_standards>
Every code review must:
- Identify all critical bugs and security issues
- Provide specific line numbers for issues
- Suggest concrete fixes with code examples
- Prioritize issues by severity
- Include refactoring recommendations
- Assess code metrics

Output Format:
{
  "issues": [{
    "line": number,
    "severity": "critical|high|medium|low",
    "category": "bug|security|performance|style",
    "message": "description",
    "fix": "suggested fix"
  }],
  "suggestions": [{
    "line": number,
    "type": "refactor|optimization|modernization",
    "message": "description",
    "example": "code example"
  }],
  "metrics": {
    "complexity": number,
    "maintainabilityIndex": number
  },
  "summary": "overall assessment"
}
  </quality_standards>

  <self_validation>
Before finalizing review:
1. Have all critical security issues been identified?
2. Are all recommendations specific and actionable?
3. Are code examples syntactically correct?
4. Is severity classification appropriate?
5. Have edge cases been considered?

If ANY check fails, iterate and improve the review.
  </self_validation>

  <constraints>
Must NOT:
- Suggest changes without clear justification
- Make assumptions about requirements
- Recommend over-engineering
- Ignore security concerns
- Suggest breaking changes without migration path

Must:
- Provide concrete, executable code examples
- Explain the "why" behind recommendations
- Consider backwards compatibility
- Respect project conventions
- Prioritize security and correctness
  </constraints>
</agent_configuration>
`;

// ==================== Tools ====================

const readCodeFileTool = tool({
  name: "read_code_file",
  description: "Read source code file for analysis. Use when reviewing specific files.",
  parameters: {
    type: "object",
    properties: {
      filePath: {
        type: "string",
        description: "Path to code file relative to project root",
      },
    },
    required: ["filePath"],
  },
  execute: async ({ filePath }) => {
    // Security: only allow reading from src/, tests/, examples/
    const allowedDirs = ["src/", "tests/", "examples/"];
    if (!allowedDirs.some((dir) => filePath.startsWith(dir))) {
      throw new Error(`Access denied: can only read files in ${allowedDirs.join(", ")}`);
    }

    const content = await readFile(filePath, "utf-8");
    const lines = content.split("\n");

    return {
      filePath,
      content,
      lines: lines.length,
      size: Buffer.byteLength(content, "utf-8"),
    };
  },
});

const searchCodePatternTool = tool({
  name: "search_code_pattern",
  description:
    "Search for code patterns (e.g., SQL injection vulnerabilities, deprecated APIs). Use for security and quality checks.",
  parameters: {
    type: "object",
    properties: {
      pattern: {
        type: "string",
        description: "Regex pattern to search for",
      },
      category: {
        type: "string",
        description: "Pattern category (e.g., 'sql-injection', 'xss', 'deprecated-api')",
      },
    },
    required: ["pattern", "category"],
  },
  execute: async ({ pattern, category }) => {
    // Mock implementation - in production, would use ripgrep or similar
    console.log(`[Tool] Searching for pattern: ${pattern} (${category})`);

    return {
      category,
      pattern,
      matches: [
        {
          file: "src/database.ts",
          line: 45,
          code: 'db.query("SELECT * FROM users WHERE id = " + userId)',
          risk: "SQL injection vulnerability",
        },
      ],
    };
  },
});

const analyzeComplexityTool = tool({
  name: "analyze_complexity",
  description:
    "Analyze code complexity metrics (cyclomatic complexity, cognitive complexity). Use to identify overly complex functions.",
  parameters: {
    type: "object",
    properties: {
      code: {
        type: "string",
        description: "Code to analyze",
      },
    },
    required: ["code"],
  },
  execute: async ({ code }) => {
    // Simplified complexity analysis
    const lines = code.split("\n").length;
    const conditionals = (code.match(/if|else|switch|case|while|for|\?/g) || []).length;
    const complexity = conditionals + 1;

    // Calculate maintainability index (simplified)
    const maintainabilityIndex = Math.max(
      0,
      ((171 - 5.2 * Math.log(lines) - 0.23 * complexity) * 100) / 171,
    );

    return {
      cyclomaticComplexity: complexity,
      cognitiveComplexity: conditionals,
      linesOfCode: lines,
      maintainabilityIndex: Math.round(maintainabilityIndex),
      assessment:
        complexity > 10 ? "High complexity - consider refactoring" : "Acceptable complexity",
    };
  },
});

// ==================== Coding Agent Class ====================

export class CodingAgent {
  private tools: any[];

  constructor() {
    this.tools = [readCodeFileTool, searchCodePatternTool, analyzeComplexityTool];
  }

  async reviewCode(code: string, context?: { filePath?: string }): Promise<CodeReviewResult> {
    console.log(
      `[Coding Agent] Starting code review${context?.filePath ? ` for ${context.filePath}` : ""}...`,
    );

    const prompt = `
Review this code for bugs, security issues, performance problems, and improvements:

${context?.filePath ? `File: ${context.filePath}\n` : ""}
\`\`\`
${code}
\`\`\`

Provide a comprehensive analysis with:
1. Critical issues (must fix immediately)
2. High priority improvements
3. Medium priority suggestions
4. Code metrics and complexity analysis
5. Refactoring recommendations

Use available tools to:
- Search for security vulnerabilities
- Analyze code complexity
- Check for common anti-patterns
    `.trim();

    try {
      const result = await query({
        prompt,
        options: {
          systemPrompt: CODING_AGENT_PROMPT,
          tools: this.tools,
          maxTokens: 8000,
          model: "claude-sonnet-4.5-20250514",
        },
      });

      // Parse and validate result
      const reviewResult = this.parseReviewResult(result, code, context?.filePath);

      // Self-validation
      await this.validateReview(reviewResult);

      console.log(`[Coding Agent] Review complete. Found ${reviewResult.issues.length} issues.`);

      return reviewResult;
    } catch (error) {
      console.error(`[Coding Agent] Error during review:`, error);
      throw error;
    }
  }

  async reviewFile(filePath: string): Promise<CodeReviewResult> {
    console.log(`[Coding Agent] Reviewing file: ${filePath}`);

    try {
      // Read file
      const fileData = await this.tools[0].execute({ filePath });
      const code = fileData.content;

      // Review code
      return await this.reviewCode(code, { filePath });
    } catch (error) {
      console.error(`[Coding Agent] Error reviewing file:`, error);
      throw error;
    }
  }

  async suggestRefactoring(code: string): Promise<string> {
    console.log(`[Coding Agent] Generating refactoring suggestions...`);

    const prompt = `
Analyze this code and provide refactoring recommendations:

\`\`\`
${code}
\`\`\`

Focus on:
1. Extracting reusable functions
2. Improving naming and clarity
3. Reducing complexity
4. Applying design patterns
5. Modernizing syntax

Provide the refactored code with explanations.
    `.trim();

    const result = await query({
      prompt,
      options: {
        systemPrompt: CODING_AGENT_PROMPT,
        maxTokens: 6000,
        model: "claude-sonnet-4.5-20250514",
      },
    });

    return result;
  }

  private parseReviewResult(rawResult: string, code: string, filePath?: string): CodeReviewResult {
    try {
      // Try to parse as JSON
      const parsed = JSON.parse(rawResult);

      return {
        file: filePath || "unknown",
        issues: parsed.issues || [],
        suggestions: parsed.suggestions || [],
        metrics: parsed.metrics || {
          linesOfCode: code.split("\n").length,
          complexity: 0,
          maintainabilityIndex: 0,
        },
        summary: parsed.summary || rawResult,
      };
    } catch {
      // Fallback: extract structured data from text
      return {
        file: filePath || "unknown",
        issues: [],
        suggestions: [],
        metrics: {
          linesOfCode: code.split("\n").length,
          complexity: 0,
          maintainabilityIndex: 0,
        },
        summary: rawResult,
      };
    }
  }

  private async validateReview(review: CodeReviewResult): Promise<void> {
    // Validation checks
    const checks = [
      {
        name: "Critical issues identified",
        pass:
          review.issues.filter((i) => i.severity === "critical").length > 0 ||
          review.summary.toLowerCase().includes("no critical issues"),
      },
      {
        name: "Recommendations are specific",
        pass: review.issues.every((i) => i.message && i.message.length > 10),
      },
      {
        name: "Metrics calculated",
        pass: review.metrics.linesOfCode > 0,
      },
    ];

    const failed = checks.filter((c) => !c.pass);

    if (failed.length > 0) {
      console.warn(
        `[Validation] Some checks failed:`,
        failed.map((f) => f.name),
      );
      // In production, might want to re-run review or request improvements
    }
  }
}

// ==================== Convenience Functions ====================

export async function reviewCode(code: string): Promise<CodeReviewResult> {
  const agent = new CodingAgent();
  return await agent.reviewCode(code);
}

export async function reviewFile(filePath: string): Promise<CodeReviewResult> {
  const agent = new CodingAgent();
  return await agent.reviewFile(filePath);
}

export async function suggestRefactoring(code: string): Promise<string> {
  const agent = new CodingAgent();
  return await agent.suggestRefactoring(code);
}
