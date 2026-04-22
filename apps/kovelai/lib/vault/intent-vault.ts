/**
 * Intent Vault — Anxiety Radar Data Store
 *
 * Sprint Item #4: Records and analyzes client search patterns
 * to surface anxiety signals to the supervising attorney.
 *
 * The Intent Vault stores:
 * 1. Classified search intents (anxiety category + urgency)
 * 2. Temporal patterns (when does the client search?)
 * 3. Escalation signals (high-urgency queries)
 * 4. Aggregate analytics (lawyer dashboard data)
 *
 * IMPORTANT: The Intent Vault is ATTORNEY-FACING ONLY.
 * The client never sees their anxiety classification.
 *
 * @see CLE seminar deck — Slide 5 (Anxiety Radar)
 * @see lib/classifiers/anxiety-radar.ts
 */

import { z } from 'zod';

// ─── Intent Categories ──────────────────────────────────────────────

export const ANXIETY_CATEGORIES = [
  'CRIMINAL_EXPOSURE',
  'ASSET_PROTECTION',
  'FAMILY_LAW',
  'REGULATORY',
  'EMPLOYMENT',
  'IMMIGRATION',
  'PERSONAL_INJURY',
  'GENERAL_ANXIETY',
] as const;

export const URGENCY_LEVELS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] as const;

// ─── Schemas ────────────────────────────────────────────────────────

export const SearchIntentSchema = z.object({
  id: z.string().uuid(),
  firmId: z.string().uuid(),
  clientId: z.string().uuid(),
  sessionId: z.string(),

  // The raw query is never stored — only the classification
  queryHash: z.string(), // SHA-256 hash of the query text
  queryLength: z.number().int(), // For statistical analysis only

  // Classification
  category: z.enum(ANXIETY_CATEGORIES),
  urgency: z.number().int().min(1).max(10),
  confidence: z.number().min(0).max(1),

  // Temporal
  createdAt: z.string().datetime(),
  dayOfWeek: z.number().int().min(0).max(6),
  hourOfDay: z.number().int().min(0).max(23),
  isAfterHours: z.boolean(), // Outside 9am-6pm firm timezone

  // Signals
  isEscalation: z.boolean(), // Urgency >= 8
  containsLegalTerms: z.boolean(),
  isRepeatQuery: z.boolean(), // Similar to a previous query
});

export type SearchIntent = z.infer<typeof SearchIntentSchema>;

// ─── Analytics Aggregation ──────────────────────────────────────────

export const ClientAnxietyProfileSchema = z.object({
  clientId: z.string().uuid(),
  firmId: z.string().uuid(),
  totalQueries: z.number().int(),
  topCategory: z.enum(ANXIETY_CATEGORIES),
  avgUrgency: z.number().min(0).max(10),
  maxUrgency: z.number().int().min(1).max(10),
  afterHoursPercentage: z.number().min(0).max(100),
  escalationCount: z.number().int(),
  categoryBreakdown: z.record(z.enum(ANXIETY_CATEGORIES), z.number().int()),
  lastActivity: z.string().datetime(),
  riskLevel: z.enum(['LOW', 'MODERATE', 'HIGH', 'CRITICAL']),
});

export type ClientAnxietyProfile = z.infer<typeof ClientAnxietyProfileSchema>;

// ─── Vault Operations ───────────────────────────────────────────────

/**
 * Records a classified search intent in the vault.
 *
 * NOTE: The raw query text is NEVER stored.
 * Only the hash, classification, and metadata are persisted.
 */
export async function recordIntent(
  intent: Omit<SearchIntent, 'id' | 'createdAt' | 'dayOfWeek' | 'hourOfDay' | 'isAfterHours' | 'isEscalation'>,
): Promise<SearchIntent> {
  const now = new Date();

  const fullIntent: SearchIntent = {
    ...intent,
    id: crypto.randomUUID(),
    createdAt: now.toISOString(),
    dayOfWeek: now.getUTCDay(),
    hourOfDay: now.getUTCHours(),
    isAfterHours: now.getUTCHours() < 9 || now.getUTCHours() >= 18,
    isEscalation: intent.urgency >= 8,
  };

  // Log escalation alerts
  if (fullIntent.isEscalation) {
    console.warn(
      `[Intent Vault] ⚠️ ESCALATION: Client ${fullIntent.clientId.substring(0, 8)} | ` +
      `Category: ${fullIntent.category} | Urgency: ${fullIntent.urgency}/10`,
    );
  }

  return fullIntent;
}

/**
 * Builds an anxiety profile for a client from their search history.
 */
export function buildAnxietyProfile(
  clientId: string,
  firmId: string,
  intents: SearchIntent[],
): ClientAnxietyProfile {
  if (intents.length === 0) {
    return {
      clientId,
      firmId,
      totalQueries: 0,
      topCategory: 'GENERAL_ANXIETY',
      avgUrgency: 0,
      maxUrgency: 1,
      afterHoursPercentage: 0,
      escalationCount: 0,
      categoryBreakdown: {},
      lastActivity: new Date().toISOString(),
      riskLevel: 'LOW',
    };
  }

  // Category breakdown
  const categoryBreakdown: Record<string, number> = {};
  let totalUrgency = 0;
  let maxUrgency = 0;
  let afterHoursCount = 0;
  let escalationCount = 0;

  for (const intent of intents) {
    categoryBreakdown[intent.category] = (categoryBreakdown[intent.category] ?? 0) + 1;
    totalUrgency += intent.urgency;
    maxUrgency = Math.max(maxUrgency, intent.urgency);
    if (intent.isAfterHours) afterHoursCount++;
    if (intent.isEscalation) escalationCount++;
  }

  // Find top category
  const topCategory = Object.entries(categoryBreakdown)
    .sort((a, b) => b[1] - a[1])[0][0] as SearchIntent['category'];

  const avgUrgency = totalUrgency / intents.length;
  const afterHoursPercentage = (afterHoursCount / intents.length) * 100;

  // Risk level calculation
  let riskLevel: ClientAnxietyProfile['riskLevel'] = 'LOW';
  if (avgUrgency >= 8 || escalationCount >= 3) riskLevel = 'CRITICAL';
  else if (avgUrgency >= 6 || escalationCount >= 2) riskLevel = 'HIGH';
  else if (avgUrgency >= 4 || afterHoursPercentage > 50) riskLevel = 'MODERATE';

  return {
    clientId,
    firmId,
    totalQueries: intents.length,
    topCategory,
    avgUrgency: Math.round(avgUrgency * 10) / 10,
    maxUrgency,
    afterHoursPercentage: Math.round(afterHoursPercentage),
    escalationCount,
    categoryBreakdown: categoryBreakdown as Record<typeof ANXIETY_CATEGORIES[number], number>,
    lastActivity: intents[intents.length - 1].createdAt,
    riskLevel,
  };
}

/**
 * Generates a radar chart data structure for the Anxiety Radar widget.
 */
export function generateRadarData(
  profile: ClientAnxietyProfile,
): Array<{ category: string; value: number; max: number }> {
  return ANXIETY_CATEGORIES.map((category) => ({
    category: category.replace('_', ' '),
    value: profile.categoryBreakdown[category] ?? 0,
    max: profile.totalQueries,
  }));
}
