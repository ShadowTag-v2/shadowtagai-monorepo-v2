/**
 * Master Agent Framework - Research Agent Example
 *
 * This example demonstrates how to use the research agent archetype
 * with different personas and tools for various research tasks.
 */

import { ClaudeAgentOptions, query } from "@anthropic-ai/claude-agent-sdk";
import searchTool from "../agents/research/tools/search.js";
import synthesisTool from "../agents/research/tools/synthesis.js";

/**
 * Example 1: Academic Research
 * Using the academic persona for rigorous scholarly research
 */
async function academicResearchExample() {
  console.log("=== Academic Research Example ===\n");

  const result = await query({
    prompt: `Conduct a comprehensive literature review on the following topic:

    "The impact of transformer architectures on natural language processing"

    Please:
    1. Search for relevant academic papers from the last 3 years
    2. Synthesize the key findings
    3. Provide proper citations in APA format
    4. Identify research gaps`,

    options: {
      systemPrompt: {
        type: "file",
        path: "./agents/research/personas/academic.md",
      },
      tools: [searchTool, synthesisTool],
      settingSources: ["project", "local"],
      temperature: 0.3, // Academic persona uses low temperature
    },
  });

  console.log("Academic Research Result:");
  console.log(result);
}

/**
 * Example 2: Business Research
 * Using the business persona for market intelligence
 */
async function businessResearchExample() {
  console.log("\n=== Business Research Example ===\n");

  const result = await query({
    prompt: `Research the following market opportunity:

    "AI-powered customer service automation market in 2024"

    Please provide:
    1. Market size and growth trends
    2. Key players and competitive landscape
    3. Customer pain points and opportunities
    4. ROI analysis for potential solutions
    5. Strategic recommendations`,

    options: {
      systemPrompt: {
        type: "file",
        path: "./agents/research/personas/business.md",
      },
      tools: [searchTool, synthesisTool],
      settingSources: ["project", "local"],
      temperature: 0.5, // Business persona uses moderate temperature
    },
  });

  console.log("Business Research Result:");
  console.log(result);
}

/**
 * Example 3: Technical Research
 * Using the technical persona for technology evaluation
 */
async function technicalResearchExample() {
  console.log("\n=== Technical Research Example ===\n");

  const result = await query({
    prompt: `Evaluate the following technology for our infrastructure:

    "Kubernetes vs. Amazon ECS for container orchestration"

    Please analyze:
    1. Architecture and design patterns
    2. Performance characteristics (latency, throughput)
    3. Scalability and reliability
    4. Security model
    5. Operational complexity
    6. Cost considerations
    7. Provide a recommendation with trade-off analysis`,

    options: {
      systemPrompt: {
        type: "file",
        path: "./agents/research/personas/technical.md",
      },
      tools: [searchTool, synthesisTool],
      settingSources: ["project", "local"],
      temperature: 0.4, // Technical persona uses moderate-low temperature
    },
  });

  console.log("Technical Research Result:");
  console.log(result);
}

/**
 * Example 4: Custom Research with Manual Tool Invocation
 * Demonstrating direct tool usage for fine-grained control
 */
async function customResearchWithToolsExample() {
  console.log("\n=== Custom Research with Direct Tool Usage ===\n");

  // Step 1: Search for information
  const searchResult = await searchTool.execute({
    query: "Claude AI agent SDK best practices",
    sources: ["web", "technical"],
    maxResults: 15,
    depth: "comprehensive",
  });

  console.log("Search Results:", searchResult);

  // Step 2: Synthesize findings
  if (searchResult.success) {
    const sources = searchResult.data.results.map((result: any) => ({
      content: result.snippet,
      citation: result.title,
      credibility: result.credibility || 0.8,
    }));

    const synthesisResult = await synthesisTool.execute({
      sources,
      mode: "comprehensive",
      citationStyle: "APA",
      theme: "Claude AI Agent SDK Best Practices",
    });

    console.log("\nSynthesis Result:", synthesisResult);
  }
}

/**
 * Example 5: Streaming Research Results
 * Using streaming for real-time research updates
 */
async function streamingResearchExample() {
  console.log("\n=== Streaming Research Example ===\n");

  console.log("Research in progress...\n");

  for await (const chunk of query({
    prompt: "Research the latest developments in quantum computing and provide a summary",
    options: {
      systemPrompt: {
        type: "file",
        path: "./agents/research/personas/technical.md",
      },
      tools: [searchTool, synthesisTool],
      settingSources: ["project", "local"],
      stream: true,
    },
  })) {
    // Process each chunk as it arrives
    if (chunk.type === "text") {
      process.stdout.write(chunk.content);
    } else if (chunk.type === "tool_use") {
      console.log(`\n[Using tool: ${chunk.name}]`);
    }
  }

  console.log("\n\nResearch complete!");
}

/**
 * Main execution
 */
async function main() {
  console.log("Master Agent Framework - Research Agent Examples\n");
  console.log("=".repeat(60));

  try {
    // Run examples
    await academicResearchExample();
    await businessResearchExample();
    await technicalResearchExample();
    await customResearchWithToolsExample();
    await streamingResearchExample();

    console.log("\n" + "=".repeat(60));
    console.log("\nAll examples completed successfully!");
  } catch (error) {
    console.error("Error running examples:", error);
    process.exit(1);
  }
}

// Run examples if this file is executed directly
if (require.main === module) {
  main();
}

export {
  academicResearchExample,
  businessResearchExample,
  customResearchWithToolsExample,
  streamingResearchExample,
  technicalResearchExample,
};
