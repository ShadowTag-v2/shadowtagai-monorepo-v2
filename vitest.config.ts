import path from 'node:path';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: [
      'tests/**/*.test.ts',
      'tests/**/*.spec.ts',
    ],
    exclude: [
      'tests/e2e/**',
      'tests/playwright/**',
      'tests/gemini_bridge.spec.ts',
      'tests/semantic_routing.test.ts',
      'node_modules/**',
    ],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@agents': path.resolve(__dirname, './src/agents'),
      '@tools': path.resolve(__dirname, './src/tools'),
      '@skills': path.resolve(__dirname, './src/skills'),
    },
  },
});
