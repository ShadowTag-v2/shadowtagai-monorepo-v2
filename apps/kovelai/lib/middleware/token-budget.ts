/**
 * Per-User Token Budget Enforcement
 *
 * Sprint Item #8: OWASP LLM10 — Unbounded Consumption
 *
 * Tracks LLM token usage per firm and user, enforcing tier-based
 * daily/monthly limits. Prevents runaway costs and abuse.
 *
 * @see Cor.30 Pillar 6 — Ops & Audit
 * @see OWASP LLM Top 10 (2025) #10
 */

import { z } from "zod";

// ─── Budget Tiers ───────────────────────────────────────────────────

export const TIER_BUDGETS = {
  solo: {
    dailyTokenLimit: 500_000,
    monthlyTokenLimit: 10_000_000,
    maxConcurrentSessions: 3,
    maxQueryLength: 500,
  },
  practice: {
    dailyTokenLimit: 2_000_000,
    monthlyTokenLimit: 50_000_000,
    maxConcurrentSessions: 10,
    maxQueryLength: 1000,
  },
  enterprise: {
    dailyTokenLimit: 10_000_000,
    monthlyTokenLimit: 250_000_000,
    maxConcurrentSessions: 50,
    maxQueryLength: 2000,
  },
} as const;

export type BudgetTier = keyof typeof TIER_BUDGETS;

// ─── Usage Record ───────────────────────────────────────────────────

export const UsageRecordSchema = z.object({
  firmId: z.string().uuid(),
  userId: z.string().optional(),
  date: z.string(), // YYYY-MM-DD
  month: z.string(), // YYYY-MM
  inputTokens: z.number().int().default(0),
  outputTokens: z.number().int().default(0),
  totalTokens: z.number().int().default(0),
  requestCount: z.number().int().default(0),
  lastUpdated: z.string().datetime(),
});

export type UsageRecord = z.infer<typeof UsageRecordSchema>;

// ─── Budget Check Result ────────────────────────────────────────────

export interface BudgetCheckResult {
  allowed: boolean;
  reason?: "DAILY_LIMIT" | "MONTHLY_LIMIT" | "CONCURRENT_LIMIT" | "QUERY_TOO_LONG";
  currentUsage: {
    dailyTokens: number;
    monthlyTokens: number;
    dailyLimit: number;
    monthlyLimit: number;
    dailyPercentage: number;
    monthlyPercentage: number;
  };
  estimatedCostUsd?: number;
}

// ─── In-Memory Store (MVP) ──────────────────────────────────────────

const usageStore = new Map<string, UsageRecord>();

function getDateKey(): string {
  return new Date().toISOString().slice(0, 10);
}

function getMonthKey(): string {
  return new Date().toISOString().slice(0, 7);
}

function getUsageKey(firmId: string, period: string): string {
  return `${firmId}:${period}`;
}

// ─── Core Functions ─────────────────────────────────────────────────

/**
 * Checks if a request is within the firm's token budget.
 */
export function checkBudget(
  firmId: string,
  tier: BudgetTier,
  estimatedTokens: number,
): BudgetCheckResult {
  const limits = TIER_BUDGETS[tier];
  const dailyKey = getUsageKey(firmId, getDateKey());
  const monthlyKey = getUsageKey(firmId, getMonthKey());

  const dailyUsage = usageStore.get(dailyKey);
  const monthlyUsage = usageStore.get(monthlyKey);

  const currentDailyTokens = dailyUsage?.totalTokens ?? 0;
  const currentMonthlyTokens = monthlyUsage?.totalTokens ?? 0;

  const result: BudgetCheckResult = {
    allowed: true,
    currentUsage: {
      dailyTokens: currentDailyTokens,
      monthlyTokens: currentMonthlyTokens,
      dailyLimit: limits.dailyTokenLimit,
      monthlyLimit: limits.monthlyTokenLimit,
      dailyPercentage: Math.round((currentDailyTokens / limits.dailyTokenLimit) * 100),
      monthlyPercentage: Math.round((currentMonthlyTokens / limits.monthlyTokenLimit) * 100),
    },
    estimatedCostUsd: estimateCost(currentMonthlyTokens + estimatedTokens),
  };

  // Check daily limit
  if (currentDailyTokens + estimatedTokens > limits.dailyTokenLimit) {
    result.allowed = false;
    result.reason = "DAILY_LIMIT";
    return result;
  }

  // Check monthly limit
  if (currentMonthlyTokens + estimatedTokens > limits.monthlyTokenLimit) {
    result.allowed = false;
    result.reason = "MONTHLY_LIMIT";
    return result;
  }

  return result;
}

/**
 * Records token usage after a successful LLM call.
 */
export function recordUsage(firmId: string, inputTokens: number, outputTokens: number): void {
  const totalTokens = inputTokens + outputTokens;
  const now = new Date().toISOString();
  const dateKey = getDateKey();
  const monthKey = getMonthKey();

  // Update daily
  const dailyStoreKey = getUsageKey(firmId, dateKey);
  const dailyRecord = usageStore.get(dailyStoreKey) ?? {
    firmId,
    date: dateKey,
    month: monthKey,
    inputTokens: 0,
    outputTokens: 0,
    totalTokens: 0,
    requestCount: 0,
    lastUpdated: now,
  };
  dailyRecord.inputTokens += inputTokens;
  dailyRecord.outputTokens += outputTokens;
  dailyRecord.totalTokens += totalTokens;
  dailyRecord.requestCount += 1;
  dailyRecord.lastUpdated = now;
  usageStore.set(dailyStoreKey, dailyRecord);

  // Update monthly
  const monthlyStoreKey = getUsageKey(firmId, monthKey);
  const monthlyRecord = usageStore.get(monthlyStoreKey) ?? {
    firmId,
    date: dateKey,
    month: monthKey,
    inputTokens: 0,
    outputTokens: 0,
    totalTokens: 0,
    requestCount: 0,
    lastUpdated: now,
  };
  monthlyRecord.inputTokens += inputTokens;
  monthlyRecord.outputTokens += outputTokens;
  monthlyRecord.totalTokens += totalTokens;
  monthlyRecord.requestCount += 1;
  monthlyRecord.lastUpdated = now;
  usageStore.set(monthlyStoreKey, monthlyRecord);

  // Log budget warnings at 80% and 95%
  const limits = TIER_BUDGETS.practice; // Default to practice tier for logging
  const dailyPct = (dailyRecord.totalTokens / limits.dailyTokenLimit) * 100;
  if (dailyPct >= 95) {
  } else if (dailyPct >= 80) {
  }
}

/**
 * Gets current usage summary for a firm.
 */
export function getUsageSummary(firmId: string): {
  daily: UsageRecord | null;
  monthly: UsageRecord | null;
} {
  return {
    daily: usageStore.get(getUsageKey(firmId, getDateKey())) ?? null,
    monthly: usageStore.get(getUsageKey(firmId, getMonthKey())) ?? null,
  };
}

// ─── Cost Estimation ────────────────────────────────────────────────

function estimateCost(tokens: number): number {
  // Gemini Flash pricing: ~$0.075 per 1M tokens (blended input/output)
  return Math.round((tokens / 1_000_000) * 0.075 * 100) / 100;
}
