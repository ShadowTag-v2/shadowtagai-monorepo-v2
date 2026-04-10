#!/usr/bin/env node

import { Agent } from '@anthropic-ai/claude-agent-sdk';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Test Generator CLI Tool
 *
 * An AI-powered test generation tool that creates comprehensive test suites
 * using Claude's Agent SDK. Supports unit, integration, and E2E tests.
 */

interface TestGeneratorOptions {
  type: 'unit' | 'integration' | 'e2e';
  filePath: string;
  outputPath?: string;
  coverage?: boolean;
  framework?: 'jest' | 'vitest' | 'mocha';
}

const TEST_GENERATOR_PROMPT = `You are a testing expert specializing in creating comprehensive test suites.

Your responsibilities:
1. Analyze the provided source code thoroughly
2. Identify all functions, classes, and methods that need testing
3. Write comprehensive tests including:
   - Happy path scenarios
   - Edge cases
   - Error handling
   - Boundary conditions
   - Input validation
4. Follow testing best practices:
   - Use descriptive test names
   - Follow AAA pattern (Arrange, Act, Assert)
   - Mock external dependencies appropriately
   - Ensure tests are isolated and independent
   - Include setup and teardown when needed
5. Generate tests that catch bugs before users do
6. Aim for high code coverage while maintaining test quality

Output Format:
- Generate complete, runnable test files
- Include necessary imports and setup
- Add helpful comments explaining complex test scenarios
- Follow the project's coding style and conventions`;

export class TestGenerator {
  private agent: Agent;
  private options: TestGeneratorOptions;

  constructor(options: TestGeneratorOptions) {
    this.options = {
      framework: 'jest',
      ...options,
    };

    this.agent = new Agent({
      systemPrompt: TEST_GENERATOR_PROMPT,
      modelName: 'claude-sonnet-4-5',
    });
  }

  /**
   * Reads the source file to be tested
   */
  private readSourceFile(): string {
    const fullPath = path.resolve(this.options.filePath);
    if (!fs.existsSync(fullPath)) {
      throw new Error(`Source file not found: ${fullPath}`);
    }
    return fs.readFileSync(fullPath, 'utf-8');
  }

  /**
   * Determines the output path for the generated test file
   */
  private getOutputPath(): string {
    if (this.options.outputPath) {
      return path.resolve(this.options.outputPath);
    }

    const sourceFile = path.basename(this.options.filePath);
    const testFileName = sourceFile.replace(/\.(ts|js)$/, '.test.$1');
    const testDir = path.join(process.cwd(), 'tests', this.options.type);

    return path.join(testDir, testFileName);
  }

  /**
   * Generates the test file using Claude
   */
  async generate(): Promise<string> {
    const sourceCode = this.readSourceFile();
    const testType = this.options.type;
    const framework = this.options.framework;

    const prompt = `Generate ${testType} tests for the following code using ${framework}:

\`\`\`typescript
${sourceCode}
\`\`\`

Requirements:
- Test type: ${testType}
- Framework: ${framework}
- Generate comprehensive tests covering all scenarios
- Include proper mocking for external dependencies
- Add comments explaining test scenarios
- Follow best practices for ${testType} testing

Please provide the complete test file with all necessary imports and setup.`;

    const response = await this.agent.run(prompt);

    return this.extractCodeFromResponse(response);
  }

  /**
   * Extracts code blocks from Claude's response
   */
  private extractCodeFromResponse(response: string): string {
    // Extract code from markdown code blocks
    const codeBlockRegex = /```(?:typescript|javascript|ts|js)?\n([\s\S]*?)\n```/;
    const match = response.match(codeBlockRegex);

    if (match && match[1]) {
      return match[1];
    }

    // If no code block found, return the full response
    return response;
  }

  /**
   * Writes the generated test to a file
   */
  async writeTest(testCode: string): Promise<string> {
    const outputPath = this.getOutputPath();
    const outputDir = path.dirname(outputPath);

    // Ensure output directory exists
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    fs.writeFileSync(outputPath, testCode, 'utf-8');
    return outputPath;
  }

  /**
   * Main execution method
   */
  async run(): Promise<void> {
    try {
      console.log(`🧪 Generating ${this.options.type} tests for: ${this.options.filePath}`);
      console.log('⚡ Analyzing code with Claude...\n');

      const testCode = await this.generate();
      const outputPath = await this.writeTest(testCode);

      console.log('✅ Test generation complete!');
      console.log(`📝 Test file created: ${outputPath}`);

      if (this.options.coverage) {
        console.log('\n📊 Run "npm run test:coverage" to check coverage');
      }
    } catch (error) {
      console.error('❌ Test generation failed:', error);
      throw error;
    }
  }
}

/**
 * CLI Entry Point
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`
🧪 Test Generator - AI-Powered Test Suite Creation

Usage: test-generator [options] <file-path>

Options:
  -t, --type <type>        Test type: unit, integration, e2e (default: unit)
  -o, --output <path>      Output path for test file
  -c, --coverage           Show coverage information after generation
  -f, --framework <name>   Testing framework: jest, vitest, mocha (default: jest)
  -h, --help              Show this help message

Examples:
  # Generate unit tests
  test-generator src/utils/math.ts

  # Generate integration tests
  test-generator -t integration src/api/users.ts

  # Generate E2E tests with custom output
  test-generator -t e2e -o tests/e2e/auth.test.ts src/auth/login.ts

  # Generate tests and check coverage
  test-generator -c src/services/payment.ts
    `);
    process.exit(0);
  }

  // Parse command line arguments
  const options: Partial<TestGeneratorOptions> = {
    type: 'unit',
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    switch (arg) {
      case '-t':
      case '--type':
        options.type = args[++i] as 'unit' | 'integration' | 'e2e';
        break;
      case '-o':
      case '--output':
        options.outputPath = args[++i];
        break;
      case '-c':
      case '--coverage':
        options.coverage = true;
        break;
      case '-f':
      case '--framework':
        options.framework = args[++i] as 'jest' | 'vitest' | 'mocha';
        break;
      default:
        if (!arg.startsWith('-')) {
          options.filePath = arg;
        }
    }
  }

  if (!options.filePath) {
    console.error('❌ Error: File path is required');
    process.exit(1);
  }

  const generator = new TestGenerator(options as TestGeneratorOptions);
  await generator.run();
}

// Run if executed directly
if (require.main === module) {
  main().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { TestGeneratorOptions, TEST_GENERATOR_PROMPT };
