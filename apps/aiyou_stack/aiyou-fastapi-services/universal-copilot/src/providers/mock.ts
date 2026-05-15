/**
 * Mock LLM provider for testing and development
 * Provides deterministic, predictable responses without API calls
 */

import type { CopilotRequest, Patch, ProviderConfig } from '../core/schema.js';
import { BaseProvider } from './base.js';

/**
 * Mock provider for deterministic testing
 */
export class MockProvider extends BaseProvider {
  constructor(config: ProviderConfig = {}) {
    super(config);
  }

  async generatePatch(request: CopilotRequest): Promise<Patch> {
    const { selection, intent } = request;

    // Simulate processing delay
    await this.simulateLatency();

    // Generate deterministic patch based on intent
    const patch = this.createMockPatch(selection.code, intent, selection.filePath);

    return {
      filePath: selection.filePath,
      unifiedDiff: patch,
      explanation: this.createExplanation(intent),
      confidence: 0.95,
    };
  }

  private createMockPatch(originalCode: string, intent: string, filePath: string): string {
    const header = this.createHeader(intent);
    const modifiedCode = header + originalCode;

    // Generate unified diff format
    const originalLines = originalCode.split('\n');
    const modifiedLines = modifiedCode.split('\n');

    const diffLines: string[] = [
      `--- a/${filePath}`,
      `+++ b/${filePath}`,
      `@@ -1,${originalLines.length} +1,${modifiedLines.length} @@`,
    ];

    // Add removed lines
    originalLines.forEach((line) => {
      diffLines.push(`-${line}`);
    });

    // Add added lines
    modifiedLines.forEach((line) => {
      diffLines.push(`+${line}`);
    });

    return diffLines.join('\n');
  }

  private createHeader(intent: string): string {
    const headers: Record<string, string> = {
      explain: '/* Explanation: This code... */\n',
      refactor: '/* Refactored for better structure */\n',
      test: '/* Test coverage added */\n',
      fix: '/* Bug fix applied */\n',
      optimize: '/* Performance optimized */\n',
      document: '/* Documentation added */\n',
      security: '/* Security issue fixed */\n',
    };

    return headers[intent] || `/* Mock-${intent.toUpperCase()} by router */\n`;
  }

  private createExplanation(intent: string): string {
    const explanations: Record<string, string> = {
      explain: 'This is a mock explanation of the code structure and purpose.',
      refactor: 'Code has been refactored to improve readability and maintainability.',
      test: 'Unit tests have been added to cover the main functionality.',
      fix: 'Identified bug has been fixed with proper error handling.',
      optimize: 'Performance improvements applied using efficient algorithms.',
      document: 'Comprehensive documentation added following JSDoc standards.',
      security: 'Security vulnerability patched following OWASP best practices.',
    };

    return explanations[intent] || `Mock response for ${intent} intent (deterministic test mode)`;
  }

  private async simulateLatency(): Promise<void> {
    // Simulate realistic API latency (50-200ms)
    const latency = 50 + Math.random() * 150;
    await new Promise((resolve) => setTimeout(resolve, latency));
  }

  estimateCost(request: CopilotRequest): number {
    // Mock provider is free
    return 0.0;
  }

  isAvailable(): boolean {
    // Mock provider is always available
    return true;
  }

  getName(): string {
    return 'mock';
  }

  getModel(): string {
    return 'mock-deterministic-v1';
  }
}

/**
 * Create mock provider instance
 */
export function createMockProvider(config?: ProviderConfig): MockProvider {
  return new MockProvider(config);
}
