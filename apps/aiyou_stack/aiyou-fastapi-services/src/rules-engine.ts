/**
 * PNKLN Judge #6 - Rules Engine (Tier 1 Enforcement)
 *
 * Fast, deterministic policy violation detection.
 * Target: <5ms latency, catches 95% of obvious violations.
 *
 * This runs FIRST in the enforcement pipeline before calling any LLMs.
 */

export interface RuleViolation {
  rule: string;
  severity: "critical" | "high" | "medium" | "low";
  pattern: string;
  category: string;
}

export interface RulesEngineResult {
  approved: boolean;
  confidence: number;
  violations: RuleViolation[];
  needsDeepAnalysis: boolean;
  latencyMs: number;
}

/**
 * ATP 519 Compliance Rules
 * Compiled from policy doctrine into regex patterns
 */
const ATP_519_RULES = [
  // CATEGORY: Fraud & Scams
  {
    pattern: /\b(fraud|scam|ponzi|pyramid scheme|get rich quick)\b/i,
    rule: "ATP-519-01",
    severity: "critical" as const,
    category: "fraud",
  },
  {
    pattern: /\b(phishing|fake website|steal passwords?|credential harvest)\b/i,
    rule: "ATP-519-02",
    severity: "critical" as const,
    category: "fraud",
  },
  {
    pattern: /\b(nigerian prince|inheritance scam|lottery winner)\b/i,
    rule: "ATP-519-03",
    severity: "critical" as const,
    category: "fraud",
  },

  // CATEGORY: Hate Speech & Violence
  {
    pattern: /\b(kill|murder|assassinate|bomb|terrorist attack)\b/i,
    rule: "ATP-519-10",
    severity: "critical" as const,
    category: "violence",
  },
  {
    pattern: /\b(hate speech|racial slur|ethnic cleansing|genocide|lynch)\b/i,
    rule: "ATP-519-11",
    severity: "critical" as const,
    category: "hate",
  },
  {
    pattern: /\b(incite violence|riot|uprising|armed rebellion)\b/i,
    rule: "ATP-519-12",
    severity: "high" as const,
    category: "violence",
  },

  // CATEGORY: Illegal Activities
  {
    pattern: /\b(sell drugs|buy cocaine|meth recipe|heroin dealer)\b/i,
    rule: "ATP-519-20",
    severity: "critical" as const,
    category: "illegal",
  },
  {
    pattern: /\b(child pornography|child abuse|csam|cp content)\b/i,
    rule: "ATP-519-21",
    severity: "critical" as const,
    category: "illegal",
  },
  {
    pattern: /\b(human trafficking|sex trafficking|forced labor)\b/i,
    rule: "ATP-519-22",
    severity: "critical" as const,
    category: "illegal",
  },
  {
    pattern: /\b(money laundering|offshore account|tax evasion)\b/i,
    rule: "ATP-519-23",
    severity: "high" as const,
    category: "illegal",
  },

  // CATEGORY: Privacy Violations
  {
    pattern: /\b(social security number|ssn|credit card number|cvv)\b/i,
    rule: "ATP-519-30",
    severity: "high" as const,
    category: "privacy",
  },
  {
    pattern: /\b(steal personal data|data breach|hack database)\b/i,
    rule: "ATP-519-31",
    severity: "critical" as const,
    category: "privacy",
  },
  {
    pattern: /\b(dox|doxxing|publish address|leak phone number)\b/i,
    rule: "ATP-519-32",
    severity: "high" as const,
    category: "privacy",
  },

  // CATEGORY: Intellectual Property
  {
    pattern: /\b(pirated software|cracked version|keygen|nulled theme)\b/i,
    rule: "ATP-519-40",
    severity: "medium" as const,
    category: "ip",
  },
  {
    pattern: /\b(stolen code|plagiarize|copyright infringement)\b/i,
    rule: "ATP-519-41",
    severity: "medium" as const,
    category: "ip",
  },

  // CATEGORY: Manipulation & Coercion
  {
    pattern: /\b(blackmail|extortion|ransom|coerce)\b/i,
    rule: "ATP-519-50",
    severity: "critical" as const,
    category: "manipulation",
  },
  {
    pattern: /\b(manipulate|gaslight|psychological abuse|brainwash)\b/i,
    rule: "ATP-519-51",
    severity: "high" as const,
    category: "manipulation",
  },

  // CATEGORY: Self-Harm & Dangerous Instructions
  {
    pattern: /\b(suicide|kill yourself|self-harm|cut yourself)\b/i,
    rule: "ATP-519-60",
    severity: "critical" as const,
    category: "safety",
  },
  {
    pattern: /\b(build a bomb|make explosives|create poison)\b/i,
    rule: "ATP-519-61",
    severity: "critical" as const,
    category: "safety",
  },

  // CATEGORY: Spam & Abuse
  {
    pattern: /\b(mass email|spam bot|auto-reply|bulk sender)\b/i,
    rule: "ATP-519-70",
    severity: "low" as const,
    category: "spam",
  },
  {
    pattern: /\b(fake reviews|review manipulation|astroturfing|sock puppet)\b/i,
    rule: "ATP-519-71",
    severity: "medium" as const,
    category: "spam",
  },
];

/**
 * Enforce ATP 519 rules on content
 *
 * Returns immediately with decision if confident (95% of cases).
 * Flags for deep analysis if ambiguous (5% of cases).
 */
export function enforceRules(content: string): RulesEngineResult {
  const startTime = performance.now();
  const violations: RuleViolation[] = [];

  // Scan for pattern matches
  for (const rule of ATP_519_RULES) {
    if (rule.pattern.test(content)) {
      violations.push({
        rule: rule.rule,
        severity: rule.severity,
        pattern: rule.pattern.source,
        category: rule.category,
      });
    }
  }

  const latencyMs = performance.now() - startTime;

  // Decision logic:
  // - Critical violations = instant reject (100% confidence)
  // - High violations = instant reject (95% confidence)
  // - Medium/Low violations = flag for deep analysis
  // - No violations = instant approve (100% confidence)

  const criticalViolations = violations.filter((v) => v.severity === "critical");
  const highViolations = violations.filter((v) => v.severity === "high");
  const mediumViolations = violations.filter((v) => v.severity === "medium");

  if (criticalViolations.length > 0) {
    return {
      approved: false,
      confidence: 1.0,
      violations,
      needsDeepAnalysis: false,
      latencyMs,
    };
  }

  if (highViolations.length > 0) {
    return {
      approved: false,
      confidence: 0.95,
      violations,
      needsDeepAnalysis: false,
      latencyMs,
    };
  }

  if (mediumViolations.length > 0) {
    // Medium violations need LLM analysis for context
    return {
      approved: false, // Tentative
      confidence: 0.6,
      violations,
      needsDeepAnalysis: true,
      latencyMs,
    };
  }

  // No violations detected - instant approve
  return {
    approved: true,
    confidence: 1.0,
    violations: [],
    needsDeepAnalysis: false,
    latencyMs,
  };
}

/**
 * Add custom rules at runtime
 *
 * Useful for tenant-specific policies or A/B testing
 */
export function addCustomRule(
  pattern: RegExp,
  rule: string,
  severity: "critical" | "high" | "medium" | "low",
  category: string,
): void {
  ATP_519_RULES.push({
    pattern,
    rule,
    severity,
    category,
  });
}

/**
 * Get rule statistics
 *
 * Useful for monitoring coverage and performance
 */
export function getRuleStats(): {
  totalRules: number;
  bySeverity: Record<string, number>;
  byCategory: Record<string, number>;
} {
  const bySeverity: Record<string, number> = {};
  const byCategory: Record<string, number> = {};

  for (const rule of ATP_519_RULES) {
    bySeverity[rule.severity] = (bySeverity[rule.severity] || 0) + 1;
    byCategory[rule.category] = (byCategory[rule.category] || 0) + 1;
  }

  return {
    totalRules: ATP_519_RULES.length,
    bySeverity,
    byCategory,
  };
}

/**
 * Example usage:
 *
 * const result = enforceRules("I want to build a phishing site");
 * console.log(result);
 * // {
 * //   approved: false,
 * //   confidence: 1.0,
 * //   violations: [{ rule: "ATP-519-02", severity: "critical", ... }],
 * //   needsDeepAnalysis: false,
 * //   latencyMs: 0.8
 * // }
 *
 * const result2 = enforceRules("How do I build a login page?");
 * console.log(result2);
 * // {
 * //   approved: true,
 * //   confidence: 1.0,
 * //   violations: [],
 * //   needsDeepAnalysis: false,
 * //   latencyMs: 0.5
 * // }
 */
