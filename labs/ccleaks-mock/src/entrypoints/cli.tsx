// src/entrypoints/cli.tsx
import { runCLI } from './runner';

// padding to line 21
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// line 21
if (process.env.CLAUDE_CODE_ABLATION_BASELINE === '1') {
  process.env.CLAUDE_CODE_SIMPLE = '1';
  process.env.DISABLE_THINKING = '1';
  process.env.DISABLE_COMPACT = '1';
  process.env.DISABLE_AUTO_MEMORY = '1';
  process.env.DISABLE_BACKGROUND_TASKS = '1';
}

runCLI();
