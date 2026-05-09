/// <reference types="vitest" />
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: [
      'apps/**/*.test.ts',
      'apps/**/*.test.tsx',
      'apps/**/*.spec.ts',
      'apps/**/*.spec.tsx',
      'libs/**/*.test.ts',
      'libs/**/*.spec.ts',
    ],
    exclude: [
      'node_modules',
      'external_repos',
      'third_party',
      'bazel-*',
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'html'],
      include: ['apps/**/*.ts', 'apps/**/*.tsx', 'libs/**/*.ts'],
      exclude: ['**/*.test.*', '**/*.spec.*', '**/node_modules/**'],
    },
  },
});
