/**
 * VCR Test Setup — V25 Pinnacle
 * Mocks external AI SDK calls for deterministic property-based testing.
 * Preloaded via: bun test --preload ./tests/vcr_setup.ts
 */
import { mock } from 'bun:test';

mock.module('@google/genai', () => ({
  GoogleGenAI: class {
    models = {
      generateContent: async (_opts: unknown) => ({
        text: 'AST_REWRITE_RULE: MOCK_MUTATION\npattern: const $X = $Y\nrewrite: const $X = /* optimized */ $Y',
      }),
    };
  },
}));

mock.module('googleapis', () => ({
  google: {
    auth: {
      GoogleAuth: class {
        getClient() { return {}; }
      },
    },
    drive: () => ({
      files: {
        export: async () => ({ data: 'Mock PRD content for testing' }),
        list: async () => ({ data: { files: [] } }),
      },
    }),
  },
}));

console.log('🎬 VCR fixtures loaded — external APIs mocked for property testing.');
