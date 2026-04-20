#!/usr/bin/env node

/**
 * Research Agent Demo
 *
 * This example demonstrates how to use the Claude Agent SDK for research tasks.
 * Research agents are designed to explore codebases, gather information, and
 * answer questions about code structure and functionality.
 */

import { query } from '@anthropic-ai/claude-agent-sdk';

async function main() {
  console.log('🔍 Research Agent Demo\n');
  console.log('This demo shows how to use Claude to research and analyze code.\n');

  // Example 1: Basic research query
  console.log('Example 1: Analyzing project structure...\n');

  try {
    const result1 = await query({
      prompt: 'Analyze the structure of this project. What is it about and what are the key files?',
      options: {
        systemPrompt: { type: 'preset', preset: 'claude_code' },
        settingSources: ['project', 'local'],
      },
    });

    console.log('✅ Example 1 completed\n');

    // Example 2: Code exploration
    console.log('Example 2: Finding specific functionality...\n');

    const result2 = await query({
      prompt: 'Find all TypeScript/JavaScript files in this project and describe what they do.',
      options: {
        systemPrompt: { type: 'preset', preset: 'claude_code' },
        settingSources: ['project', 'local'],
      },
    });

    console.log('✅ Example 2 completed\n');

    // Example 3: Documentation research
    console.log('Example 3: Gathering documentation insights...\n');

    const result3 = await query({
      prompt: 'Read the MIGRATION.md file and summarize the key changes and migration steps.',
      options: {
        systemPrompt: { type: 'preset', preset: 'claude_code' },
        settingSources: ['project', 'local'],
      },
    });

    console.log('✅ Example 3 completed\n');
    console.log('🎉 All research examples completed successfully!');
  } catch (error) {
    console.error('❌ Error running research examples:', error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

export { main };
