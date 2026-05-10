#!/usr/bin/env node
/**
 * Documentation validator for ShadowTag-v2 FastAPI Services
 * Validates markdown files for proper structure and formatting
 */

const fs = require('fs');
const path = require('path');

const DOCS = ['README.md', 'HOOKS_GUIDE.md', 'GEMINI_INGESTION_ANALYSIS.md', 'MIGRATION.md'];

let errors = 0;
let warnings = 0;

console.log('🔍 Validating documentation...\n');

DOCS.forEach((doc) => {
  const filePath = path.join(process.cwd(), doc);

  if (!fs.existsSync(filePath)) {
    console.error(`❌ Missing: ${doc}`);
    errors++;
    return;
  }

  const content = fs.readFileSync(filePath, 'utf-8');

  // Check for proper heading
  if (!content.startsWith('# ')) {
    console.error(`❌ ${doc}: Missing top-level heading`);
    errors++;
  }

  // Check for empty file
  if (content.trim().length === 0) {
    console.error(`❌ ${doc}: File is empty`);
    errors++;
  }

  // Check for broken markdown links (basic check)
  const brokenLinks = content.match(/\[.*?\]\(\)/g);
  if (brokenLinks) {
    console.warn(`⚠️  ${doc}: Found ${brokenLinks.length} empty link(s)`);
    warnings++;
  }

  console.log(`✅ ${doc}: Valid`);
});

console.log(`\n📊 Validation complete:`);
console.log(`   ✅ Passed: ${DOCS.length - errors}`);
console.log(`   ❌ Errors: ${errors}`);
console.log(`   ⚠️  Warnings: ${warnings}`);

if (errors > 0) {
  console.error('\n❌ Documentation validation failed!');
  process.exit(1);
}

console.log('\n✅ All documentation is valid!');
process.exit(0);
