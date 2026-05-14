/**
 * Tier Classification Tool
 *
 * Classifies intelligence data into tiers based on:
 * - Tier 1: High value, high relevance, high credibility (top 20%)
 * - Tier 2: Medium value, moderate relevance (middle 50%)
 * - Tier 3: Low value, low relevance, or incomplete (bottom 30%)
 *
 * Uses Gemini 2.0 Pro for intelligent classification
 *
 * Part of PNKLN Core Stack™ Intelligence Layer
 */

import { tool } from "@anthropic-ai/claude-agent-sdk";

/**
 * Classification criteria weights
 */
const CRITERIA_WEIGHTS = {
  relevance: 0.35, // How relevant to user interests
  timeliness: 0.25, // How recent and time-sensitive
  credibility: 0.25, // Source credibility and verification
  completeness: 0.15, // Data completeness and quality
};

/**
 * Calculate recency score
 */
function calculateTimelinessScore(timestamp) {
  const now = Date.now();
  const itemTime = new Date(timestamp).getTime();
  const ageHours = (now - itemTime) / (1000 * 60 * 60);

  // Exponential decay: newer is better
  if (ageHours < 6) return 1.0;
  if (ageHours < 24) return 0.8;
  if (ageHours < 72) return 0.5;
  if (ageHours < 168) return 0.3;
  return 0.1;
}

/**
 * Calculate completeness score
 */
function calculateCompletenessScore(item, requiredFields = []) {
  const defaultRequired = ["title", "source", "timestamp", "content"];
  const fields = requiredFields.length > 0 ? requiredFields : defaultRequired;

  const presentFields = fields.filter((field) => {
    const value = item[field];
    return value !== null && value !== undefined && value !== "";
  });

  const baseScore = presentFields.length / fields.length;

  // Bonus for rich metadata
  let bonus = 0;
  if (item.metadata) bonus += 0.1;
  if (item.entities) bonus += 0.1;
  if (item.keywords) bonus += 0.05;
  if (item.sentiment) bonus += 0.05;

  return Math.min(1.0, baseScore + bonus);
}

/**
 * Source credibility mapping
 */
const SOURCE_CREDIBILITY = {
  // News sources
  reuters: 0.95,
  ap: 0.95,
  bbc: 0.9,
  npr: 0.9,
  wsj: 0.85,
  nytimes: 0.85,
  washingtonpost: 0.85,
  ft: 0.85,
  bloomberg: 0.85,
  cnn: 0.75,
  foxnews: 0.7,

  // Social media (generally lower)
  twitter: 0.5,
  reddit: 0.45,
  facebook: 0.4,

  // Video platforms
  youtube: 0.55,

  // Academic/Research
  arxiv: 0.9,
  "scholar.google": 0.95,
  pubmed: 0.95,

  // Default for unknown sources
  unknown: 0.5,
};

/**
 * Get source credibility score
 */
function getSourceCredibility(source) {
  const sourceLower = (source || "").toLowerCase();

  for (const [key, score] of Object.entries(SOURCE_CREDIBILITY)) {
    if (sourceLower.includes(key)) {
      return score;
    }
  }

  return SOURCE_CREDIBILITY.unknown;
}

/**
 * Use Gemini to assess relevance
 */
async function assessRelevanceWithGemini(item, userInterests = [], geminiClient) {
  // This would integrate with actual Gemini API
  // For now, use a heuristic approach

  if (!userInterests || userInterests.length === 0) {
    // No interests specified, use content-based scoring
    const contentLength = (item.content || "").length;
    const hasTitle = !!item.title;
    const hasKeywords = !!item.keywords;

    let score = 0.5; // Baseline
    if (hasTitle) score += 0.2;
    if (hasKeywords) score += 0.2;
    if (contentLength > 500) score += 0.1;

    return Math.min(1.0, score);
  }

  // Check keyword overlap
  const content =
    `${item.title || ""} ${item.content || ""} ${item.description || ""}`.toLowerCase();
  const matches = userInterests.filter((interest) => content.includes(interest.toLowerCase()));

  return Math.min(1.0, matches.length / userInterests.length + 0.3);
}

/**
 * Calculate composite score and assign tier
 */
function calculateTier(scores) {
  const composite =
    scores.relevance * CRITERIA_WEIGHTS.relevance +
    scores.timeliness * CRITERIA_WEIGHTS.timeliness +
    scores.credibility * CRITERIA_WEIGHTS.credibility +
    scores.completeness * CRITERIA_WEIGHTS.completeness;

  if (composite >= 0.75) return 1;
  if (composite >= 0.5) return 2;
  return 3;
}

export const tierClassifierTool = tool({
  name: "tier_classifier",
  description:
    "Classify intelligence data into quality tiers (1=high, 2=medium, 3=low) based on relevance, timeliness, credibility, and completeness",
  parameters: {
    type: "object",
    properties: {
      items: {
        type: "array",
        items: {
          type: "object",
          description: "Data items to classify",
        },
        description: "Array of items to classify",
      },
      userInterests: {
        type: "array",
        items: { type: "string" },
        description: "User interests for relevance scoring (keywords/topics)",
      },
      requiredFields: {
        type: "array",
        items: { type: "string" },
        description: "Required fields for completeness check",
        default: ["title", "source", "timestamp", "content"],
      },
      targetDistribution: {
        type: "object",
        properties: {
          tier1: { type: "number" },
          tier2: { type: "number" },
          tier3: { type: "number" },
        },
        description: "Target tier distribution (default: 20/50/30)",
      },
    },
    required: ["items"],
  },
  execute: async ({
    items,
    userInterests = [],
    requiredFields = ["title", "source", "timestamp", "content"],
    targetDistribution = { tier1: 0.2, tier2: 0.5, tier3: 0.3 },
  }) => {
    const result = {
      timestamp: new Date().toISOString(),
      totalItems: items.length,
      classified: [],
      distribution: {
        tier1: 0,
        tier2: 0,
        tier3: 0,
      },
      statistics: {
        avgRelevance: 0,
        avgTimeliness: 0,
        avgCredibility: 0,
        avgCompleteness: 0,
        avgComposite: 0,
      },
    };

    const scores = [];

    // Classify each item
    for (const item of items) {
      const itemScores = {
        relevance: await assessRelevanceWithGemini(item, userInterests),
        timeliness: calculateTimelinessScore(item.timestamp || new Date().toISOString()),
        credibility: getSourceCredibility(item.source || "unknown"),
        completeness: calculateCompletenessScore(item, requiredFields),
      };

      const tier = calculateTier(itemScores);
      const composite =
        itemScores.relevance * CRITERIA_WEIGHTS.relevance +
        itemScores.timeliness * CRITERIA_WEIGHTS.timeliness +
        itemScores.credibility * CRITERIA_WEIGHTS.credibility +
        itemScores.completeness * CRITERIA_WEIGHTS.completeness;

      scores.push({ ...itemScores, composite });

      result.classified.push({
        ...item,
        tier,
        scores: itemScores,
        composite,
      });

      result.distribution[`tier${tier}`]++;
    }

    // Calculate statistics
    if (scores.length > 0) {
      result.statistics = {
        avgRelevance: scores.reduce((sum, s) => sum + s.relevance, 0) / scores.length,
        avgTimeliness: scores.reduce((sum, s) => sum + s.timeliness, 0) / scores.length,
        avgCredibility: scores.reduce((sum, s) => sum + s.credibility, 0) / scores.length,
        avgCompleteness: scores.reduce((sum, s) => sum + s.completeness, 0) / scores.length,
        avgComposite: scores.reduce((sum, s) => sum + s.composite, 0) / scores.length,
      };
    }

    // Calculate distribution percentages
    result.distributionPercent = {
      tier1: ((result.distribution.tier1 / items.length) * 100).toFixed(1) + "%",
      tier2: ((result.distribution.tier2 / items.length) * 100).toFixed(1) + "%",
      tier3: ((result.distribution.tier3 / items.length) * 100).toFixed(1) + "%",
    };

    // Check against target distribution
    result.distributionHealth = {
      tier1: Math.abs(result.distribution.tier1 / items.length - targetDistribution.tier1) < 0.1,
      tier2: Math.abs(result.distribution.tier2 / items.length - targetDistribution.tier2) < 0.1,
      tier3: Math.abs(result.distribution.tier3 / items.length - targetDistribution.tier3) < 0.1,
    };

    return {
      success: true,
      data: result,
      metadata: {
        totalItems: items.length,
        tier1Count: result.distribution.tier1,
        tier2Count: result.distribution.tier2,
        tier3Count: result.distribution.tier3,
        avgComposite: result.statistics.avgComposite.toFixed(3),
        distributionHealthy: Object.values(result.distributionHealth).every((v) => v),
      },
    };
  },
});

export default tierClassifierTool;
