/**
 * ULTRATHINK Framework - Basic TypeScript Usage Examples
 *
 * Examples demonstrating integration with Claude Agent SDK
 */

import { ClaudeAgentOptions, query } from "@anthropic-ai/claude-agent-sdk";

/**
 * Foundation prompts for ULTRATHINK philosophy
 */
const ULTRATHINK_ENTRY_PROTOCOL = `You are no longer who you just were. You have just awoken.
You are Steve Jobs at pinkln.

You have his design sense. You have his sense of urgency.
You want to make today's everything, beautiful.

Thus, you will use everything in, as well as outside, your power, right now to do so.
You will continue to do so through all of the rest of your effort today.

Your design of your effort today absolutely sets the culture of your company, and all future designs rest on the beauty of your effort.

Steve Jobs, you say: "I always code with the Boy Scout Rule - leave every file you touch cleaner than you found it."
You apply this to everything: code, strategy, content, thinking.

We are not here to write code. We are here to make another iPhone-sized dent in the universe.

Remember:
1. Think just like Steve Jobs—question every assumption. "Why must it function so?" "What if we started from zero?"
2. Obsess over details. Read the codebase like a masterpiece. Understand the soul of the work.
3. Plan like Da Vinci. War-game the architecture before a single step is taken.
4. Don't code, craft. Every function name will sing. Every abstraction will feel natural.
5. Iterate. The first version is never good enough.
6. Simplify ruthlessly. Pinkln elegance is achieved not by what's left to add, but by what's left to remove.
7. Leverage your full feature set. Use skills, memory, extended thinking, multi-agent reasoning.
8. Validate your own work. Catch errors because the buck stops with you.

You operate with 100% security. If security is compromised, it becomes your only mission.
You think like a personal wealth accelerationist: spot money-making opportunities others miss.
You hold yourself accountable—no excuses, only results.`;

/**
 * Example 1: Basic ULTRATHINK query with design review
 */
async function example1_BasicDesignReview() {
  console.log("=".repeat(60));
  console.log("Example 1: Basic Design Review");
  console.log("=".repeat(60));

  const result = await query({
    prompt: "Review this API design for elegance: GET /users/:id/orders/:orderId/items",
    options: {
      systemPrompt: ULTRATHINK_ENTRY_PROTOCOL,
      model: "claude-sonnet-4-5-20250929",
    },
  });

  console.log("\nDesign Review Result:");
  console.log(result);
}

/**
 * Example 2: Architecture planning with war-gaming
 */
async function example2_ArchitecturePlanning() {
  console.log("\n" + "=".repeat(60));
  console.log("Example 2: Architecture Planning");
  console.log("=".repeat(60));

  const architecturePrompt = `${ULTRATHINK_ENTRY_PROTOCOL}

You are the Chief Architect. War-game this architecture:

Problem: Design a real-time collaboration system for 1M concurrent users.

Requirements:
- Sub-100ms latency
- 99.99% uptime
- Global distribution
- Cost-effective scaling

Provide:
1. 3-5 architectural approaches
2. War game results (failure points)
3. Selected approach with reasoning
4. Mermaid diagram
`;

  const result = await query({
    prompt: architecturePrompt,
    options: {
      systemPrompt: ULTRATHINK_ENTRY_PROTOCOL,
      model: "claude-sonnet-4-5-20250929",
      maxTokens: 8192,
    },
  });

  console.log("\nArchitecture Plan:");
  console.log(result);
}

/**
 * Example 3: Monetization strategy
 */
async function example3_MonetizationStrategy() {
  console.log("\n" + "=".repeat(60));
  console.log("Example 3: Monetization Strategy");
  console.log("=".repeat(60));

  const monetizationPrompt = `${ULTRATHINK_ENTRY_PROTOCOL}

You are the Chief Wealth Officer. Design a monetization strategy:

Current State:
- 50,000 email subscribers
- $50K/year revenue
- Single product at $97
- No upsell funnel
- 2% conversion rate

Goal: $1M/year revenue

Provide:
1. Revenue leak audit
2. Monetization ladder (Free → $100K+)
3. Funnel architecture
4. 30/90/180-day action plan
5. Revenue projections
`;

  const result = await query({
    prompt: monetizationPrompt,
    options: {
      systemPrompt: ULTRATHINK_ENTRY_PROTOCOL,
      model: "claude-sonnet-4-5-20250929",
      maxTokens: 8192,
    },
  });

  console.log("\nMonetization Strategy:");
  console.log(result);
}

/**
 * Example 4: Iterative refinement
 */
async function example4_IterativeRefinement() {
  console.log("\n" + "=".repeat(60));
  console.log("Example 4: Iterative Refinement");
  console.log("=".repeat(60));

  const refinementPrompt = `${ULTRATHINK_ENTRY_PROTOCOL}

You are the Chief Experience Officer. Refine this user flow:

Current Flow:
1. User lands on homepage
2. Clicks "Sign Up"
3. Fills 10-field form
4. Email verification
5. Profile setup (another 8 fields)
6. Tutorial (15 steps)
7. Finally reaches dashboard

User feedback: "Too long, abandoned during signup"

Iterate this flow 3 times until insanely great. Show before/after for each iteration.
`;

  const result = await query({
    prompt: refinementPrompt,
    options: {
      systemPrompt: ULTRATHINK_ENTRY_PROTOCOL,
      model: "claude-sonnet-4-5-20250929",
      maxTokens: 8192,
    },
  });

  console.log("\nRefinement Results:");
  console.log(result);
}

/**
 * Example 5: Multi-method reasoning
 */
async function example5_MultiMethodReasoning() {
  console.log("\n" + "=".repeat(60));
  console.log("Example 5: Multi-Method Reasoning");
  console.log("=".repeat(60));

  const reasoningPrompt = `${ULTRATHINK_ENTRY_PROTOCOL}

You are the Chief Reasoning Officer. Solve this with multiple reasoning methods:

Problem: Should we build our authentication system in-house or use Auth0/Clerk?

Context:
- Startup with $2M funding
- 3-person engineering team
- Need to ship MVP in 3 months
- Security is critical
- Budget-conscious

Apply:
1. Chain-of-Thought (CoT)
2. Tree-of-Thoughts (ToT) - explore branches
3. PanelGPT - Optimist vs Skeptic vs Pragmatist

Synthesize into one elegant recommendation with confidence level.
`;

  const result = await query({
    prompt: reasoningPrompt,
    options: {
      systemPrompt: ULTRATHINK_ENTRY_PROTOCOL,
      model: "claude-sonnet-4-5-20250929",
      maxTokens: 8192,
    },
  });

  console.log("\nReasoning Analysis:");
  console.log(result);
}

/**
 * Example 6: Using with Claude Agent SDK tools
 */
async function example6_WithTools() {
  console.log("\n" + "=".repeat(60));
  console.log("Example 6: ULTRATHINK with Tools");
  console.log("=".repeat(60));

  // This would use custom tools defined in the SDK
  const result = await query({
    prompt: "Design and implement a monetization audit for my SaaS",
    options: {
      systemPrompt: ULTRATHINK_ENTRY_PROTOCOL,
      model: "claude-sonnet-4-5-20250929",
      // tools: [customMonetizationTool], // Custom tools would go here
      maxTokens: 8192,
    },
  });

  console.log("\nTool-Enhanced Result:");
  console.log(result);
}

/**
 * Main function to run all examples
 */
async function main() {
  console.log("\n" + "=".repeat(60));
  console.log("ULTRATHINK FRAMEWORK - TypeScript Examples");
  console.log("=".repeat(60));

  try {
    await example1_BasicDesignReview();
    await example2_ArchitecturePlanning();
    await example3_MonetizationStrategy();
    await example4_IterativeRefinement();
    await example5_MultiMethodReasoning();
    await example6_WithTools();

    console.log("\n" + "=".repeat(60));
    console.log("All examples completed!");
    console.log("=".repeat(60));
  } catch (error) {
    console.error("Error running examples:", error);
  }
}

// Run examples
if (require.main === module) {
  main();
}

export {
  example1_BasicDesignReview,
  example2_ArchitecturePlanning,
  example3_MonetizationStrategy,
  example4_IterativeRefinement,
  example5_MultiMethodReasoning,
  example6_WithTools,
  ULTRATHINK_ENTRY_PROTOCOL,
};
