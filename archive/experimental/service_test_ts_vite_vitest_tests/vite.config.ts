/// <reference types="vitest" />

import react from '@vitejs/plugin-react-swc';
import type { PluginOption } from 'vite';
import { defineConfig } from 'vitest/config';

// https://vitejs.dev/config/

export default defineConfig({
  plugins: [react() as PluginOption],
  root: '.',
  build: {
    rollupOptions: {
      input: './src/index.html',
    },
    outDir: 'dist',
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/vitest-setup.ts',
  },
});
