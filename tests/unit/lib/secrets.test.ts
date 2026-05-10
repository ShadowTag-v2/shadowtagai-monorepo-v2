/**
 * Secrets Doctrine Tests
 *
 * Validates: GCP Secret Manager doctrine compliance.
 * Rule: No hardcoded API keys in source files or committed config.
 */

import { describe, it, expect } from 'vitest';
import { readFileSync, readdirSync, existsSync } from 'fs';
import { join } from 'path';

/** Patterns that indicate hardcoded secrets in source */
const SECRET_PATTERNS = [
  /['"]sk-[a-zA-Z0-9]{20,}['"]/,       // OpenAI keys
  /['"]AIza[a-zA-Z0-9_-]{35}['"]/,       // Google API keys
  /['"]ghp_[a-zA-Z0-9]{36}['"]/,          // GitHub PATs
  /['"]AKIA[A-Z0-9]{16}['"]/,             // AWS access keys
  /['"]rk_live_[a-zA-Z0-9]{24,}['"]/,     // Stripe live keys
  /password\s*[:=]\s*['"][^'"]{8,}['"]/i,  // Hardcoded passwords
];

function scanFileForSecrets(content: string): string[] {
  const violations: string[] = [];
  for (const pattern of SECRET_PATTERNS) {
    const match = content.match(pattern);
    if (match) {
      violations.push(`Pattern ${pattern.source} matched: ${match[0].substring(0, 20)}...`);
    }
  }
  return violations;
}

describe('Secrets Doctrine', () => {
  it('should not find a bare .env file in the repo root', () => {
    // The doctrine bans bare .env files committed to source.
    // .env.local, .env.example, .env.template are development-only artifacts
    // that MUST be in .gitignore and never committed.
    const repoRoot = join(__dirname, '..', '..', '..');
    expect(existsSync(join(repoRoot, '.env'))).toBe(false);
  });

  it('should not have hardcoded secrets in config files', () => {
    const repoRoot = join(__dirname, '..', '..', '..');
    const configFiles = ['firebase.json', 'antigravity-mcp-config.json'];
    const violations: string[] = [];

    for (const file of configFiles) {
      const path = join(repoRoot, file);
      if (!existsSync(path)) continue;
      const content = readFileSync(path, 'utf-8');
      const fileViolations = scanFileForSecrets(content);
      violations.push(...fileViolations.map((v) => `${file}: ${v}`));
    }

    expect(violations).toEqual([]);
  });

  it('should validate secret pattern detection works', () => {
    // Positive cases (should detect)
    expect(scanFileForSecrets('"sk-abc12345678901234567890"')).toHaveLength(1);
    expect(scanFileForSecrets('"ghp_abcdefghijklmnopqrstuvwxyz0123456789"')).toHaveLength(1);

    // Negative cases (should not detect)
    expect(scanFileForSecrets('"normal-api-response"')).toHaveLength(0);
    expect(scanFileForSecrets('"${STRIPE_SECRET_KEY}"')).toHaveLength(0);
  });
});
