#!/usr/bin/env node

/**
 * Multi-Agent Workflow Demo
 *
 * This example demonstrates how to orchestrate multiple Claude agents to work
 * together on complex tasks. Each agent can specialize in different aspects
 * (research, coding, testing, documentation) and collaborate on a larger goal.
 */

import { query } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  console.log("🤝 Multi-Agent Workflow Demo\n");
  console.log("This demo shows how to orchestrate multiple agents for complex tasks.\n");

  try {
    // Workflow: Build a complete feature with multiple agents
    console.log("=".repeat(60));
    console.log("Workflow: Create a Calculator Module");
    console.log("=".repeat(60) + "\n");

    // Step 1: Research Agent - Analyze requirements
    console.log("Step 1: 🔍 Research Agent - Analyzing requirements...\n");

    const researchResult = await query({
      prompt: `Analyze the requirements for creating a calculator module:
1. What functions should a basic calculator have?
2. What edge cases should we consider?
3. What TypeScript types would be appropriate?

Provide a structured analysis.`,
      options: {
        systemPrompt:
          "You are a research specialist. Analyze requirements thoroughly and provide detailed insights.",
      },
    });

    console.log("✅ Research phase completed\n");

    // Step 2: Coding Agent - Implement the feature
    console.log("Step 2: 💻 Coding Agent - Implementing calculator module...\n");

    const codingResult = await query({
      prompt: `Create a new file 'examples/calculator/calculator.ts' with:
- A Calculator class with methods: add, subtract, multiply, divide
- Proper error handling (e.g., division by zero)
- TypeScript types and interfaces
- JSDoc comments

Make it production-ready with proper error handling.`,
      options: {
        systemPrompt: { type: "preset", preset: "claude_code" },
        settingSources: ["project", "local"],
      },
    });

    console.log("✅ Coding phase completed\n");

    // Step 3: Testing Agent - Create comprehensive tests
    console.log("Step 3: 🧪 Testing Agent - Creating test suite...\n");

    const testingResult = await query({
      prompt: `Create comprehensive tests for the calculator module at 'examples/calculator/calculator.test.ts':
- Test all basic operations
- Test edge cases (division by zero, negative numbers, decimals)
- Test method chaining if applicable
- Use clear test descriptions

Use a simple assertion-based approach.`,
      options: {
        systemPrompt:
          "You are a testing specialist. Write comprehensive tests that cover all edge cases and ensure code quality.",
      },
    });

    console.log("✅ Testing phase completed\n");

    // Step 4: Documentation Agent - Create documentation
    console.log("Step 4: 📚 Documentation Agent - Writing documentation...\n");

    const docsResult = await query({
      prompt: `Create a README.md file at 'examples/calculator/README.md' that documents:
- Overview of the calculator module
- Usage examples for each method
- API documentation
- Edge cases and error handling
- How to run the tests

Make it clear and beginner-friendly.`,
      options: {
        systemPrompt:
          "You are a technical writer. Create clear, comprehensive documentation with examples.",
      },
    });

    console.log("✅ Documentation phase completed\n");

    // Step 5: Review Agent - Final quality check
    console.log("Step 5: ✨ Review Agent - Conducting final review...\n");

    const reviewResult = await query({
      prompt: `Review the calculator module we just created:
1. Check the code in examples/calculator/calculator.ts for quality
2. Verify tests in examples/calculator/calculator.test.ts are comprehensive
3. Ensure documentation in examples/calculator/README.md is complete
4. Suggest any improvements

Provide a summary of the review.`,
      options: {
        systemPrompt:
          "You are a senior code reviewer. Evaluate code quality, test coverage, and documentation completeness.",
      },
    });

    console.log("✅ Review phase completed\n");

    console.log("=".repeat(60));
    console.log("🎉 Multi-Agent Workflow Completed Successfully!");
    console.log("=".repeat(60) + "\n");
    console.log("Summary:");
    console.log("✅ Requirements analyzed by Research Agent");
    console.log("✅ Code implemented by Coding Agent");
    console.log("✅ Tests created by Testing Agent");
    console.log("✅ Documentation written by Documentation Agent");
    console.log("✅ Quality verified by Review Agent");
  } catch (error) {
    console.error("❌ Error running workflow:", error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

export { main };
