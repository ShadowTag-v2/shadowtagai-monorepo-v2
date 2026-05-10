/**
 * Judge #6 Validator
 *
 * Quality gate validation for intelligence ingestion layer
 * Validates against:
 * - Items: Daily ingestion volume and quality
 * - Sources: Source diversity and balance
 * - Costs: Per-item and total cost efficiency
 * - Scores: Relevance, timeliness, and credibility thresholds
 *
 * Part of PNKLN Core Stack™ Intelligence Layer
 */

import { tool } from '@anthropic-ai/claude-agent-sdk';

/**
 * Quality gate thresholds
 */
const DEFAULT_GATES = {
  items: {
    minDaily: 500,
    targetDaily: 1000,
    minQuality: 0.6, // Minimum average quality score
  },
  sources: {
    minSources: 5,
    maxSourcePercent: 0.4, // No single source > 40%
    minSourcePercent: 0.05, // Each source should contribute at least 5%
  },
  costs: {
    maxPerItem: 0.005, // $0.005 per item
    maxMonthly: 100, // $100/month
    targetPerItem: 0.0025, // Target: $0.0025/item
  },
  scores: {
    minRelevance: 0.6,
    minTimeliness: 0.5,
    minCredibility: 0.65,
    minCompleteness: 0.7,
  },
};

/**
 * Validate item volume and quality
 */
function validateItems(data, gates) {
  const itemCount = data.totalItems || 0;
  const avgQuality = data.avgComposite || 0;

  const result = {
    passed: true,
    checks: [],
  };

  // Check minimum daily volume
  const minVolumeCheck = {
    name: 'minimum_daily_volume',
    threshold: gates.items.minDaily,
    actual: itemCount,
    passed: itemCount >= gates.items.minDaily,
    severity: 'error',
  };
  result.checks.push(minVolumeCheck);
  if (!minVolumeCheck.passed) result.passed = false;

  // Check target daily volume
  const targetVolumeCheck = {
    name: 'target_daily_volume',
    threshold: gates.items.targetDaily,
    actual: itemCount,
    passed: itemCount >= gates.items.targetDaily,
    severity: 'warning',
  };
  result.checks.push(targetVolumeCheck);

  // Check quality threshold
  const qualityCheck = {
    name: 'minimum_quality',
    threshold: gates.items.minQuality,
    actual: avgQuality,
    passed: avgQuality >= gates.items.minQuality,
    severity: 'error',
  };
  result.checks.push(qualityCheck);
  if (!qualityCheck.passed) result.passed = false;

  return result;
}

/**
 * Validate source diversity
 */
function validateSources(data, gates) {
  const sourceDistribution = data.sourceDistribution || {};
  const totalItems = data.totalItems || 0;
  const sourceCount = Object.keys(sourceDistribution).length;

  const result = {
    passed: true,
    checks: [],
  };

  // Check minimum source count
  const minSourcesCheck = {
    name: 'minimum_sources',
    threshold: gates.sources.minSources,
    actual: sourceCount,
    passed: sourceCount >= gates.sources.minSources,
    severity: 'error',
  };
  result.checks.push(minSourcesCheck);
  if (!minSourcesCheck.passed) result.passed = false;

  // Check max source percentage (no single source dominates)
  for (const [source, count] of Object.entries(sourceDistribution)) {
    const percent = count / totalItems;

    const maxPercentCheck = {
      name: `max_source_percent_${source}`,
      threshold: gates.sources.maxSourcePercent,
      actual: percent,
      passed: percent <= gates.sources.maxSourcePercent,
      severity: 'warning',
      source,
    };
    result.checks.push(maxPercentCheck);

    // Check min source percentage (each source contributes meaningfully)
    const minPercentCheck = {
      name: `min_source_percent_${source}`,
      threshold: gates.sources.minSourcePercent,
      actual: percent,
      passed: percent >= gates.sources.minSourcePercent,
      severity: 'info',
      source,
    };
    result.checks.push(minPercentCheck);
  }

  return result;
}

/**
 * Validate cost efficiency
 */
function validateCosts(data, gates) {
  const totalCost = data.totalCost || 0;
  const itemCount = data.totalItems || 0;
  const perItemCost = itemCount > 0 ? totalCost / itemCount : 0;

  // Project monthly cost (assumes daily runs)
  const monthlyProjected = totalCost * 30;

  const result = {
    passed: true,
    checks: [],
  };

  // Check per-item cost
  const perItemCheck = {
    name: 'max_per_item_cost',
    threshold: gates.costs.maxPerItem,
    actual: perItemCost,
    passed: perItemCost <= gates.costs.maxPerItem,
    severity: 'error',
  };
  result.checks.push(perItemCheck);
  if (!perItemCheck.passed) result.passed = false;

  // Check target per-item cost
  const targetPerItemCheck = {
    name: 'target_per_item_cost',
    threshold: gates.costs.targetPerItem,
    actual: perItemCost,
    passed: perItemCost <= gates.costs.targetPerItem,
    severity: 'warning',
  };
  result.checks.push(targetPerItemCheck);

  // Check monthly budget
  const monthlyCheck = {
    name: 'max_monthly_cost',
    threshold: gates.costs.maxMonthly,
    actual: monthlyProjected,
    passed: monthlyProjected <= gates.costs.maxMonthly,
    severity: 'error',
  };
  result.checks.push(monthlyCheck);
  if (!monthlyCheck.passed) result.passed = false;

  return result;
}

/**
 * Validate quality scores
 */
function validateScores(data, gates) {
  const avgRelevance = data.avgRelevance || 0;
  const avgTimeliness = data.avgTimeliness || 0;
  const avgCredibility = data.avgCredibility || 0;
  const avgCompleteness = data.avgCompleteness || 0;

  const result = {
    passed: true,
    checks: [],
  };

  const scoreChecks = [
    {
      name: 'min_relevance',
      threshold: gates.scores.minRelevance,
      actual: avgRelevance,
      metric: 'relevance',
    },
    {
      name: 'min_timeliness',
      threshold: gates.scores.minTimeliness,
      actual: avgTimeliness,
      metric: 'timeliness',
    },
    {
      name: 'min_credibility',
      threshold: gates.scores.minCredibility,
      actual: avgCredibility,
      metric: 'credibility',
    },
    {
      name: 'min_completeness',
      threshold: gates.scores.minCompleteness,
      actual: avgCompleteness,
      metric: 'completeness',
    },
  ];

  for (const check of scoreChecks) {
    const passed = check.actual >= check.threshold;
    result.checks.push({
      ...check,
      passed,
      severity: 'error',
    });
    if (!passed) result.passed = false;
  }

  return result;
}

export const judgeSixValidatorTool = tool({
  name: 'judge_six_validator',
  description:
    'Validate intelligence ingestion against quality gates (items, sources, costs, scores)',
  parameters: {
    type: 'object',
    properties: {
      data: {
        type: 'object',
        description: 'Ingestion data to validate',
        properties: {
          totalItems: { type: 'number' },
          avgComposite: { type: 'number' },
          avgRelevance: { type: 'number' },
          avgTimeliness: { type: 'number' },
          avgCredibility: { type: 'number' },
          avgCompleteness: { type: 'number' },
          sourceDistribution: { type: 'object' },
          totalCost: { type: 'number' },
        },
      },
      gates: {
        type: 'object',
        description: 'Custom quality gates (optional, uses defaults if not provided)',
      },
      strictMode: {
        type: 'boolean',
        description: 'Strict mode fails on warnings too',
        default: false,
      },
    },
    required: ['data'],
  },
  execute: async ({ data, gates = DEFAULT_GATES, strictMode = false }) => {
    const result = {
      timestamp: new Date().toISOString(),
      overallPassed: true,
      strictMode,
      validations: {},
      summary: {
        totalChecks: 0,
        passed: 0,
        failed: 0,
        warnings: 0,
      },
    };

    // Run all validations
    result.validations.items = validateItems(data, gates);
    result.validations.sources = validateSources(data, gates);
    result.validations.costs = validateCosts(data, gates);
    result.validations.scores = validateScores(data, gates);

    // Aggregate results
    for (const [category, validation] of Object.entries(result.validations)) {
      for (const check of validation.checks) {
        result.summary.totalChecks++;

        if (check.passed) {
          result.summary.passed++;
        } else {
          if (check.severity === 'error') {
            result.summary.failed++;
            result.overallPassed = false;
          } else if (check.severity === 'warning') {
            result.summary.warnings++;
            if (strictMode) {
              result.overallPassed = false;
            }
          }
        }
      }
    }

    // Generate recommendations
    result.recommendations = [];

    if (!result.validations.items.passed) {
      result.recommendations.push({
        category: 'items',
        priority: 'high',
        message: 'Increase ingestion volume or improve data quality filtering',
      });
    }

    if (!result.validations.sources.passed) {
      result.recommendations.push({
        category: 'sources',
        priority: 'medium',
        message: 'Diversify data sources to reduce dependency on single sources',
      });
    }

    if (!result.validations.costs.passed) {
      result.recommendations.push({
        category: 'costs',
        priority: 'high',
        message: 'Optimize API usage or reduce per-item processing costs',
      });
    }

    if (!result.validations.scores.passed) {
      result.recommendations.push({
        category: 'scores',
        priority: 'high',
        message: 'Improve source selection or enhance filtering criteria',
      });
    }

    return {
      success: result.overallPassed,
      data: result,
      metadata: {
        passed: result.overallPassed,
        totalChecks: result.summary.totalChecks,
        failed: result.summary.failed,
        warnings: result.summary.warnings,
        strictMode,
      },
    };
  },
});

export default judgeSixValidatorTool;
