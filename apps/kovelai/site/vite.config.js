import { resolve } from 'node:path';
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    outDir: resolve(__dirname, '../public'),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
      },
    },
    // Performance: inline small assets
    assetsInlineLimit: 4096,
    // Minification (oxc is built into Vite 8 via rolldown)
    minify: true,
    // Source maps off for production
    sourcemap: false,
  },
  // Dev server
  server: {
    port: 3000,
    open: true,
  },
});
