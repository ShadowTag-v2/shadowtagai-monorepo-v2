import path from 'node:path';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: [
      'tests/**/*.test.ts',
      'tests/**/*.spec.ts',
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
