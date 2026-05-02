import path from 'path';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.{test,spec}.ts', 'tests/**/*.ts'],
    exclude: ['node_modules', 'dist', '**/*.py'],
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
