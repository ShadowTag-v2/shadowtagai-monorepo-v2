/**
 * Cloud Armor WAF Rules Configuration
 *
 * Sprint Item #18: Web Application Firewall rules for Cloud Run.
 *
 * Generates Cloud Armor security policy configuration for:
 * - IP-based rate limiting (L7)
 * - Geographic restrictions
 * - OWASP CRS rule sets
 * - Bot management
 * - Custom rules for legal-specific patterns
 *
 * Deploy: `gcloud compute security-policies import kovelai-waf --file-name=cloud-armor-policy.json`
 *
 * @see Cor.30 Pillar 3 — API Hardening
 * @see https://cloud.google.com/armor/docs/security-policy-overview
 */

export interface CloudArmorPolicy {
  name: string;
  description: string;
  rules: CloudArmorRule[];
}

export interface CloudArmorRule {
  description: string;
  priority: number;
  match: {
    versionedExpr?: string;
    config?: { srcIpRanges: string[] };
    expr?: { expression: string };
  };
  action: 'allow' | 'deny(403)' | 'deny(404)' | 'deny(502)' | 'throttle' | 'rate_based_ban';
  rateLimitOptions?: {
    rateLimitThreshold: { count: number; intervalSec: number };
    conformAction: string;
    exceedAction: string;
    banDurationSec?: number;
    enforceOnKey: string;
  };
  preview?: boolean;
}

// ─── Policy Generator ───────────────────────────────────────────────

export function generateCloudArmorPolicy(): CloudArmorPolicy {
  return {
    name: 'kovelai-waf',
    description: 'KovelAI Web Application Firewall — Cloud Armor Security Policy',
    rules: [
      // ── Rule 1000: Block known bad IPs ──────────────────────
      {
        description: 'Block known malicious IP ranges',
        priority: 1000,
        match: {
          versionedExpr: 'SRC_IPS_V1',
          config: {
            srcIpRanges: [
              // Add known bad ranges here
              '0.0.0.0/32', // Placeholder
            ],
          },
        },
        action: 'deny(403)',
      },

      // ── Rule 2000: Rate limit all API endpoints ────────────
      {
        description: 'Global API rate limiting — 60 req/min per IP',
        priority: 2000,
        match: {
          expr: { expression: "request.path.matches('/api/.*')" },
        },
        action: 'throttle',
        rateLimitOptions: {
          rateLimitThreshold: { count: 60, intervalSec: 60 },
          conformAction: 'allow',
          exceedAction: 'deny(429)',
          enforceOnKey: 'IP',
        },
      },

      // ── Rule 2100: Strict rate limit for auth endpoints ────
      {
        description: 'Auth endpoint rate limiting — 10 req/min per IP',
        priority: 2100,
        match: {
          expr: {
            expression:
              "request.path.matches('/api/tokens/.*') || request.path.matches('/api/auth/.*')",
          },
        },
        action: 'rate_based_ban',
        rateLimitOptions: {
          rateLimitThreshold: { count: 10, intervalSec: 60 },
          conformAction: 'allow',
          exceedAction: 'deny(429)',
          banDurationSec: 300, // 5-minute ban on exceeding
          enforceOnKey: 'IP',
        },
      },

      // ── Rule 2200: Privileged search rate limit ────────────
      {
        description: 'Privileged search rate limiting — 10 req/min per IP',
        priority: 2200,
        match: {
          expr: { expression: "request.path.matches('/api/privileged-search')" },
        },
        action: 'throttle',
        rateLimitOptions: {
          rateLimitThreshold: { count: 10, intervalSec: 60 },
          conformAction: 'allow',
          exceedAction: 'deny(429)',
          enforceOnKey: 'IP',
        },
      },

      // ── Rule 3000: OWASP CRS — SQL Injection ──────────────
      {
        description: 'OWASP CRS — Block SQL injection attempts',
        priority: 3000,
        match: {
          expr: {
            // biome-ignore lint/security/noSecrets: GCP Cloud Armor WAF preconfigured expression
            expression: "evaluatePreconfiguredExpr('sqli-v33-stable')",
          },
        },
        action: 'deny(403)',
      },

      // ── Rule 3100: OWASP CRS — XSS ────────────────────────
      {
        description: 'OWASP CRS — Block cross-site scripting',
        priority: 3100,
        match: {
          expr: {
            // biome-ignore lint/security/noSecrets: GCP Cloud Armor WAF preconfigured expression
            expression: "evaluatePreconfiguredExpr('xss-v33-stable')",
          },
        },
        action: 'deny(403)',
      },

      // ── Rule 3200: OWASP CRS — RFI ────────────────────────
      {
        description: 'OWASP CRS — Block remote file inclusion',
        priority: 3200,
        match: {
          expr: {
            // biome-ignore lint/security/noSecrets: GCP Cloud Armor WAF preconfigured expression
            expression: "evaluatePreconfiguredExpr('rfi-v33-stable')",
          },
        },
        action: 'deny(403)',
      },

      // ── Rule 3300: OWASP CRS — Scanner Detection ──────────
      {
        description: 'OWASP CRS — Block vulnerability scanners',
        priority: 3300,
        match: {
          expr: {
            // biome-ignore lint/security/noSecrets: GCP Cloud Armor WAF preconfigured expression
            expression: "evaluatePreconfiguredExpr('scannerdetection-v33-stable')",
          },
        },
        action: 'deny(403)',
      },

      // ── Rule 4000: Block large request bodies ──────────────
      {
        description: 'Block oversized request bodies (>1MB)',
        priority: 4000,
        match: {
          expr: {
            expression: "int(request.headers['content-length']) > 1048576",
          },
        },
        action: 'deny(413)',
      },

      // ── Rule 5000: Geographic restrictions ─────────────────
      {
        description: 'Allow only US, UK, CA, AU traffic (Phase 1)',
        priority: 5000,
        match: {
          expr: {
            // biome-ignore lint/security/noSecrets: GCP Cloud Armor geo-restriction rule
            expression: "!origin.region_code.matches('US|GB|CA|AU')",
          },
        },
        action: 'deny(403)',
        preview: true, // Preview mode for Phase 1 — monitor before enforcing
      },

      // ── Rule 9000: Ban repeat offenders ────────────────────
      {
        description: 'Auto-ban IPs with 100+ blocks in 10 minutes',
        priority: 9000,
        match: {
          expr: { expression: "request.path.matches('.*')" },
        },
        action: 'rate_based_ban',
        rateLimitOptions: {
          rateLimitThreshold: { count: 100, intervalSec: 600 },
          conformAction: 'allow',
          exceedAction: 'deny(403)',
          banDurationSec: 3600, // 1-hour ban
          enforceOnKey: 'IP',
        },
      },

      // ── Rule 2147483647: Default allow ─────────────────────
      {
        description: 'Default allow — all non-matching traffic passes',
        priority: 2147483647,
        match: {
          versionedExpr: 'SRC_IPS_V1',
          config: { srcIpRanges: ['*'] },
        },
        action: 'allow',
      },
    ],
  };
}

// ─── Export as JSON ─────────────────────────────────────────────────

export function exportPolicyJSON(): string {
  return JSON.stringify(generateCloudArmorPolicy(), null, 2);
}

// ─── Validation ─────────────────────────────────────────────────────

export function validatePolicy(policy: CloudArmorPolicy): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  // Check for duplicate priorities
  const priorities = policy.rules.map((r) => r.priority);
  const duplicates = priorities.filter((p, i) => priorities.indexOf(p) !== i);
  if (duplicates.length > 0) {
    errors.push(`Duplicate rule priorities: ${duplicates.join(', ')}`);
  }

  // Check for default rule
  const hasDefault = policy.rules.some((r) => r.priority === 2147483647);
  if (!hasDefault) {
    errors.push('Missing default rule (priority 2147483647)');
  }

  // Check priority ordering
  const sorted = [...priorities].sort((a, b) => a - b);
  if (JSON.stringify(priorities) !== JSON.stringify(sorted)) {
    errors.push('Rules are not sorted by priority');
  }

  return { valid: errors.length === 0, errors };
}
