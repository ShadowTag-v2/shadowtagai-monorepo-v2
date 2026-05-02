import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    include: ['tests/unit/**/*.test.ts', 'tests/integration/**/*.test.ts', 'tests/utils/**/*.test.ts'],
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
