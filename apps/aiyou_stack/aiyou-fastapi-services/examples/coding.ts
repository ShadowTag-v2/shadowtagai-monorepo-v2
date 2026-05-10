#!/usr/bin/env node

/**
 * Coding Agent Demo
 *
 * This example demonstrates how to use the Claude Agent SDK for coding tasks.
 * Coding agents can write, modify, and refactor code, fix bugs, and implement
 * new features.
 */

import { query } from '@anthropic-ai/claude-agent-sdk';

async function main() {
  console.log('💻 Coding Agent Demo\n');
  console.log('This demo shows how to use Claude for code generation and modification.\n');

  // Example 1: Creating a simple utility function
  console.log('Example 1: Creating a utility function...\n');

  try {
    const result1 = await query({
      prompt: `Create a new file called 'examples/utils/stringHelpers.ts' with the following utility functions:
- capitalize(str: string): Capitalizes the first letter of a string
- truncate(str: string, maxLength: number): Truncates a string to a max length
- slugify(str: string): Converts a string to a URL-friendly slug

Include JSDoc comments and export all functions.`,
      options: {
        systemPrompt: { type: 'preset', preset: 'claude_code' },
        settingSources: ['project', 'local'],
      },
    });

    console.log('✅ Example 1 completed\n');

    // Example 2: Code review and refactoring
    console.log('Example 2: Code review and suggestions...\n');

    const result2 = await query({
      prompt:
        'Review the research.ts example file and suggest any improvements for code quality, error handling, or TypeScript best practices.',
      options: {
        systemPrompt: { type: 'preset', preset: 'claude_code' },
        settingSources: ['project', 'local'],
      },
    });

    console.log('✅ Example 2 completed\n');

    // Example 3: Adding tests
    console.log('Example 3: Generating test file...\n');

    const result3 = await query({
      prompt: `Create a test file 'examples/utils/stringHelpers.test.ts' that tests all the functions in stringHelpers.ts. Use a simple assertion-based approach without external testing frameworks.`,
      options: {
        systemPrompt: { type: 'preset', preset: 'claude_code' },
        settingSources: ['project', 'local'],
      },
    });

    console.log('✅ Example 3 completed\n');
    console.log('🎉 All coding examples completed successfully!');
  } catch (error) {
    console.error('❌ Error running coding examples:', error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

export { main };
