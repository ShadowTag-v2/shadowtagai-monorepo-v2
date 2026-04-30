/**
 * Triple Pass: Run1 → Run2 → Run3 → Apply
 *
 * Orchestrates the full ACE-inspired workflow.
 */

import { spawn } from 'node:child_process';

async function run(script) {
  return new Promise((resolve, reject) => {
    const p = spawn('node', [script], { stdio: 'inherit' });
    p.on('exit', (code) => (code === 0 ? resolve() : reject(new Error(`${script} failed`))));
  });
}

console.log('🚀 Starting Triple Pass (ACE-inspired workflow)');

try {
  console.log('\n📝 Run1: Chain A generates code...');
  await run('tools/orchestrator/run1_code_A.mjs');

  console.log('\n📖 Run2: Chain A explains (Plan Mode)...');
  await run('tools/orchestrator/run2_explain_A.mjs');

  console.log('\n🔍 Run3: Chain B opposes/critiques...');
  await run('tools/orchestrator/run3_oppose_B.mjs');

  console.log('\n✅ Apply: Cursor applies patches...');
  await run('tools/orchestrator/apply_in_cursor.mjs');

  console.log('\n🎉 Triple Pass completed successfully!');
} catch (e) {
  console.error('\n❌ Triple Pass failed:', e.message);
  process.exit(1);
}
