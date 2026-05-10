#!/usr/bin/env node

/**
 * Example: Using Output Styles with Claude Agent SDK
 *
 * This example demonstrates how to programmatically use output styles
 * with the Claude Agent SDK.
 */

const {
  loadActiveOutputStyle,
  listOutputStyles,
  setActiveOutputStyle,
} = require('./output-style-loader');

// Example 1: List all available output styles
async function example1_listStyles() {
  console.log('=== Example 1: List Available Output Styles ===\n');

  const styles = await listOutputStyles();

  console.log('Available styles:');
  styles.forEach((style) => {
    console.log(`\n  ${style.name} (${style.level}-level)`);
    console.log(`  Description: ${style.description}`);
    console.log(`  File: ${style.filename}`);
  });
  console.log('\n');
}

// Example 2: Load a specific output style
async function example2_loadSpecificStyle() {
  console.log('=== Example 2: Load Specific Output Style ===\n');

  const { loadOutputStyle } = require('./output-style-loader');

  // Load the explanatory style
  const explanatoryPrompt = await loadOutputStyle('explanatory');

  console.log('Loaded "Explanatory" style system prompt:');
  console.log('---');
  console.log(explanatoryPrompt.substring(0, 500) + '...');
  console.log('---\n');
}

// Example 3: Set and load active output style
async function example3_setAndLoadActive() {
  console.log('=== Example 3: Set and Load Active Style ===\n');

  // Set the active style
  await setActiveOutputStyle('learning');
  console.log('✓ Set active style to: learning\n');

  // Load the active style
  const activePrompt = await loadActiveOutputStyle();
  console.log('Active style system prompt (first 500 chars):');
  console.log('---');
  console.log(activePrompt.substring(0, 500) + '...');
  console.log('---\n');
}

// Example 4: Using with Claude Agent SDK (pseudo-code)
async function example4_withClaudeAgentSDK() {
  console.log('=== Example 4: Using with Claude Agent SDK ===\n');

  console.log('Example code for using output styles with Claude Agent SDK:\n');

  const exampleCode = `
const { ClaudeAgent } = require('@anthropic-ai/claude-agent-sdk');
const { loadActiveOutputStyle } = require('./output-style-loader');

async function createAgentWithOutputStyle() {
  // Load the active output style
  const systemPrompt = await loadActiveOutputStyle();

  // Create agent with custom system prompt
  const agent = new ClaudeAgent({
    systemPrompt: systemPrompt,
    apiKey: process.env.ANTHROPIC_API_KEY,
    // other options...
  });

  // Use the agent
  const response = await agent.query({
    prompt: 'Help me understand async/await in JavaScript'
  });

  console.log(response);
}

createAgentWithOutputStyle();
  `.trim();

  console.log(exampleCode);
  console.log('\n');
}

// Example 5: Dynamic style selection
async function example5_dynamicSelection() {
  console.log('=== Example 5: Dynamic Style Selection ===\n');

  const styles = await listOutputStyles();

  console.log('Let user choose from available styles:\n');

  styles.forEach((style, index) => {
    console.log(`  [${index + 1}] ${style.name}`);
    console.log(`      ${style.description}`);
  });

  console.log('\n// In a real app, you would prompt the user to select a number');
  console.log('// Then load and apply that style\n');

  // Simulate user selecting option 2 (Explanatory)
  const selectedStyle = styles[1]; // Assuming Explanatory is second
  if (selectedStyle) {
    console.log(`User selected: ${selectedStyle.name}`);
    await setActiveOutputStyle(selectedStyle.name.toLowerCase());
    console.log(`✓ Activated: ${selectedStyle.name}\n`);
  }
}

// Example 6: Error handling
async function example6_errorHandling() {
  console.log('=== Example 6: Error Handling ===\n');

  const { loadOutputStyle } = require('./output-style-loader');

  try {
    // Try to load a non-existent style
    await loadOutputStyle('nonexistent-style');
  } catch (error) {
    console.log('✓ Caught expected error:', error.message);
  }

  console.log('\nAlways wrap output style operations in try-catch blocks\n');
}

// Run all examples
async function runAllExamples() {
  try {
    await example1_listStyles();
    await example2_loadSpecificStyle();
    await example3_setAndLoadActive();
    await example4_withClaudeAgentSDK();
    await example5_dynamicSelection();
    await example6_errorHandling();

    console.log('=== All Examples Complete ===\n');
  } catch (error) {
    console.error('Error running examples:', error);
  }
}

// Run examples if this file is executed directly
if (require.main === module) {
  const arg = process.argv[2];

  if (arg === '--all' || !arg) {
    runAllExamples();
  } else {
    const examples = {
      1: example1_listStyles,
      2: example2_loadSpecificStyle,
      3: example3_setAndLoadActive,
      4: example4_withClaudeAgentSDK,
      5: example5_dynamicSelection,
      6: example6_errorHandling,
    };

    const example = examples[arg];
    if (example) {
      example().catch(console.error);
    } else {
      console.log(`
Usage:
  node example-output-style-usage.js          # Run all examples
  node example-output-style-usage.js --all    # Run all examples
  node example-output-style-usage.js 1        # Run example 1
  node example-output-style-usage.js 2        # Run example 2
  ... etc
      `);
    }
  }
}

module.exports = {
  example1_listStyles,
  example2_loadSpecificStyle,
  example3_setAndLoadActive,
  example4_withClaudeAgentSDK,
  example5_dynamicSelection,
  example6_errorHandling,
};
