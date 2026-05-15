/**
 * Apply patches and summarize using Cursor's 4-model stack
 */

import { load } from './lib/io.mjs';
import { cursorApplyAndSummarize } from './lib/models.mjs';

const payload = {
  patches: {
    A: await load('patches/A.run1.patch').catch(() => ''),
    B: await load('patches/B.run3.patch').catch(() => ''),
  },
  explainMd: await load('explain/A.run2.explain.md').catch(() => ''),
  reviewMd: await load('review/B.run3.review.md').catch(() => ''),
};

const res = await cursorApplyAndSummarize(payload);
console.log('✅ Applied patches');
console.log(res.summary || 'Summary not available');
