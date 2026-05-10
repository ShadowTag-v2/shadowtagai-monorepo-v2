#!/usr/bin/env node
/**
 * Security Evidence Logger
 *
 * Extracts high-severity findings from security scan results
 * and writes a markdown summary for GitHub Step Summary.
 */

import fs from 'node:fs';

async function main() {
  const scanPath = '.ci/security_scan.json';

  if (!fs.existsSync(scanPath)) {
    console.log('No security scan results found');
    return;
  }

  const scan = JSON.parse(fs.readFileSync(scanPath, 'utf8'));

  // Extract high-severity lines
  const issues = [];
  scan.forEach((result) => {
    const lines = (result.output || '').split('\n');
    lines.forEach((line) => {
      if (/critical|high|CVE|ERROR|VULNERABILITY/i.test(line)) {
        issues.push(line.trim());
      }
    });
  });

  // Build markdown summary
  const summary = [
    '## 🔐 Security Evidence',
    '',
    `- **Timestamp**: ${new Date().toISOString()}`,
    `- **High-severity findings**: ${issues.length}`,
    '',
    issues.length > 0 ? '### Sample Issues' : '✓ No high-severity issues detected',
    '',
  ];

  if (issues.length > 0) {
    summary.push('```');
    summary.push(...issues.slice(0, 40));
    if (issues.length > 40) {
      summary.push(`... and ${issues.length - 40} more`);
    }
    summary.push('```');
  }

  const summaryText = summary.join('\n');

  // Write to GitHub Step Summary if available
  const stepSummaryPath = process.env.GITHUB_STEP_SUMMARY_PATH || process.env.GITHUB_STEP_SUMMARY;

  if (stepSummaryPath) {
    fs.appendFileSync(stepSummaryPath, summaryText + '\n');
  }

  // Always write to .ci for local reference
  fs.mkdirSync('.ci', { recursive: true });
  fs.writeFileSync('.ci/security_summary.md', summaryText);

  console.log('📝 Security evidence summary written');
  console.log(`   ${issues.length} high-severity issues logged`);
}

main().catch((error) => {
  console.error('Evidence log error:', error);
  process.exit(1);
});
