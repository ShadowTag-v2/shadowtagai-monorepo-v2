#!/usr/bin/env node
/**
 * SDK Plugin Loader - Loads erik-interaction plugin
 * Usage: node load-erik-plugin.mjs
 */

import { runAgent } from "@anthropic-ai/claude-agent-sdk";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const pluginPath = path.join(__dirname, ".claude/plugins/erik-interaction");

console.log("Loading Erik Interaction Plugin...");
console.log(`Plugin path: ${pluginPath}`);

// SDK configuration with plugin
const options = {
  // Load the erik-interaction plugin
  plugins: [
    {
      type: "local",
      path: pluginPath,
    },
  ],

  // Permission mode from plugin.json
  permissionMode: "acceptEdits",

  // Enable verbose logging to see plugin loading
  verbose: true,

  // API key from environment
  apiKey: process.env.ANTHROPIC_API_KEY,

  // Model selection
  model: "sonnet",

  // Initial prompt
  prompt: "Plugin loaded. Testing Erik response format: What is Judge #6?",
};

async function main() {
  try {
    console.log("\nInitializing Claude Agent SDK with erik-interaction plugin...\n");

    // Run agent with plugin loaded
    const result = await runAgent(options);

    console.log("\n=== AGENT RESULT ===");
    console.log(result);

    if (result.type === "result" && result.subtype === "success") {
      console.log("\n✅ Plugin loaded successfully!");
      console.log(`\nResponse:\n${result.result}`);
      console.log(`\nCost: $${result.total_cost_usd.toFixed(4)}`);
      console.log(`Duration: ${result.duration_ms}ms`);
      console.log(`Turns: ${result.num_turns}`);
    } else {
      console.log("\n❌ Plugin loading failed");
      if (result.errors) {
        console.log("Errors:", result.errors);
      }
    }
  } catch (error) {
    console.error("❌ Error loading plugin:", error);
    process.exit(1);
  }
}

main();
