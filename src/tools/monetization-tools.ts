/**
 * Custom Tools for Wealth Acceleration Agent
 *
 * These tools enable the agent to perform detailed monetization analysis,
 * revenue projections, and strategic assessments.
 *
 * Version: 1.0.0
 * Last Updated: 2025-11-08
 */

import { tool } from "@anthropic-ai/claude-agent-sdk";

/**
 * Calculate Customer Lifetime Value (LTV)
 *
 * Analyzes customer behavior to project lifetime value across different scenarios
 */
export const calculateLTV = tool({
  name: "calculate_ltv",
  description:
    "Calculate Customer Lifetime Value based on average order value, purchase frequency, and customer lifespan. Returns LTV projections and optimization opportunities.",
  parameters: {
    type: "object",
    properties: {
      averageOrderValue: {
        type: "number",
        description: "Average order value in dollars",
      },
      purchaseFrequency: {
        type: "number",
        description: "Average number of purchases per year",
      },
      customerLifespan: {
        type: "number",
        description: "Average customer lifespan in years",
      },
      grossMargin: {
        type: "number",
        description: "Gross margin as a percentage (0-100)",
      },
    },
    required: ["averageOrderValue", "purchaseFrequency", "customerLifespan", "grossMargin"],
  },
  execute: async ({ averageOrderValue, purchaseFrequency, customerLifespan, grossMargin }) => {
    const marginDecimal = grossMargin / 100;
    const annualRevenue = averageOrderValue * purchaseFrequency;
    const lifetimeRevenue = annualRevenue * customerLifespan;
    const lifetimeValue = lifetimeRevenue * marginDecimal;

    // Calculate optimization scenarios
    const scenarios = {
      baseline: {
        ltv: lifetimeValue,
        annualRevenue: annualRevenue * marginDecimal,
      },
      increaseAOV10: {
        ltv: lifetimeValue * 1.1,
        lift: "10% increase in average order value",
        impact: (lifetimeValue * 0.1).toFixed(2),
      },
      increaseFreq10: {
        ltv: lifetimeValue * 1.1,
        lift: "10% increase in purchase frequency",
        impact: (lifetimeValue * 0.1).toFixed(2),
      },
      increaseLifespan10: {
        ltv: lifetimeValue * 1.1,
        lift: "10% increase in customer lifespan",
        impact: (lifetimeValue * 0.1).toFixed(2),
      },
      increaseAll10: {
        ltv: lifetimeValue * 1.331, // 1.1^3
        lift: "10% increase across all metrics",
        impact: (lifetimeValue * 0.331).toFixed(2),
      },
    };

    return {
      baseline: {
        ltv: lifetimeValue.toFixed(2),
        annualValue: (annualRevenue * marginDecimal).toFixed(2),
        lifetimeRevenue: lifetimeRevenue.toFixed(2),
        lifetimePurchases: (purchaseFrequency * customerLifespan).toFixed(1),
      },
      optimizationScenarios: scenarios,
      recommendations: [
        {
          priority: 1,
          action: "Increase AOV through upsells and bundles",
          expectedImpact: `$${scenarios.increaseAOV10.impact} per customer`,
          implementation: "Order bumps, product bundles, premium tiers",
        },
        {
          priority: 2,
          action: "Increase purchase frequency through continuity",
          expectedImpact: `$${scenarios.increaseFreq10.impact} per customer`,
          implementation: "Subscription offers, consumables, replenishment programs",
        },
        {
          priority: 3,
          action: "Increase customer lifespan through retention",
          expectedImpact: `$${scenarios.increaseLifespan10.impact} per customer`,
          implementation: "Community building, loyalty programs, ongoing value",
        },
      ],
    };
  },
});

/**
 * Analyze Revenue Funnel
 *
 * Performs comprehensive funnel analysis to identify conversion leaks
 */
export const analyzeRevenueFunnel = tool({
  name: "analyze_revenue_funnel",
  description:
    "Analyze revenue funnel metrics to identify conversion leaks and optimization opportunities. Calculates conversion rates, revenue per stage, and projected improvements.",
  parameters: {
    type: "object",
    properties: {
      stages: {
        type: "array",
        description: "Array of funnel stages with visitor and revenue data",
        items: {
          type: "object",
          properties: {
            name: { type: "string", description: "Stage name" },
            visitors: { type: "number", description: "Number of visitors" },
            conversions: {
              type: "number",
              description: "Number of conversions to next stage",
            },
            revenue: {
              type: "number",
              description: "Revenue generated at this stage",
            },
          },
          required: ["name", "visitors"],
        },
      },
    },
    required: ["stages"],
  },
  execute: async ({ stages }) => {
    const analysis = [];
    let totalRevenue = 0;

    for (let i = 0; i < stages.length; i++) {
      const stage = stages[i];
      const conversionRate =
        i < stages.length - 1 ? ((stage.conversions || 0) / stage.visitors) * 100 : 0;
      const revenuePerVisitor = (stage.revenue || 0) / stage.visitors;

      totalRevenue += stage.revenue || 0;

      // Calculate improvement scenarios
      const improve10Pct = {
        newConversionRate: conversionRate * 1.1,
        additionalConversions: (stage.visitors * conversionRate * 0.1) / 100,
        revenueImpact: 0, // Will be calculated based on downstream value
      };

      analysis.push({
        stage: stage.name,
        visitors: stage.visitors,
        conversions: stage.conversions || 0,
        conversionRate: `${conversionRate.toFixed(2)}%`,
        revenue: (stage.revenue || 0).toFixed(2),
        revenuePerVisitor: revenuePerVisitor.toFixed(2),
        improvementScenario: improve10Pct,
      });
    }

    // Identify biggest leaks (stages with lowest conversion rates)
    const sortedByConversion = [...analysis]
      .filter((a) => a.conversions > 0)
      .sort((a, b) => {
        return parseFloat(a.conversionRate) - parseFloat(b.conversionRate);
      });

    return {
      funnelAnalysis: analysis,
      totalRevenue: totalRevenue.toFixed(2),
      totalVisitors: stages[0]?.visitors || 0,
      overallConversionRate:
        stages.length > 0
          ? `${(
              ((stages[stages.length - 1]?.conversions || 0) / (stages[0]?.visitors || 1)) * 100
            ).toFixed(2)}%`
          : "N/A",
      biggestLeaks: sortedByConversion.slice(0, 3).map((stage) => ({
        stage: stage.stage,
        conversionRate: stage.conversionRate,
        priority: "HIGH - Focus optimization efforts here",
      })),
      recommendations: [
        {
          priority: 1,
          stage: sortedByConversion[0]?.stage || "N/A",
          action: "Optimize conversion at lowest-performing stage",
          tactics: [
            "A/B test messaging and positioning",
            "Reduce friction points",
            "Add trust signals and social proof",
            "Clarify value proposition",
          ],
        },
        {
          priority: 2,
          stage: "All stages",
          action: "Implement tracking for detailed attribution",
          tactics: [
            "Set up event tracking",
            "Identify drop-off points",
            "Segment by traffic source",
            "Track time-to-convert",
          ],
        },
      ],
    };
  },
});

/**
 * Calculate Revenue Projections
 *
 * Projects revenue growth based on different strategic scenarios
 */
export const calculateRevenueProjections = tool({
  name: "calculate_revenue_projections",
  description:
    "Calculate revenue projections based on current metrics and growth scenarios. Models different strategies and their financial impact over time.",
  parameters: {
    type: "object",
    properties: {
      currentMonthlyRevenue: {
        type: "number",
        description: "Current monthly recurring revenue",
      },
      currentAudienceSize: {
        type: "number",
        description: "Current total audience size across all platforms",
      },
      monthlyAudienceGrowth: {
        type: "number",
        description: "Monthly audience growth rate as percentage (0-100)",
      },
      currentConversionRate: {
        type: "number",
        description: "Current conversion rate from audience to customer (%)",
      },
      projectionMonths: {
        type: "number",
        description: "Number of months to project (default 12)",
      },
    },
    required: [
      "currentMonthlyRevenue",
      "currentAudienceSize",
      "monthlyAudienceGrowth",
      "currentConversionRate",
    ],
  },
  execute: async ({
    currentMonthlyRevenue,
    currentAudienceSize,
    monthlyAudienceGrowth,
    currentConversionRate,
    projectionMonths = 12,
  }) => {
    const audienceGrowthDecimal = monthlyAudienceGrowth / 100;
    const conversionDecimal = currentConversionRate / 100;

    // Baseline scenario: maintain current conversion rate
    const baselineProjection = [];
    let audienceSize = currentAudienceSize;

    for (let month = 0; month <= projectionMonths; month++) {
      if (month > 0) {
        audienceSize = audienceSize * (1 + audienceGrowthDecimal);
      }
      const customers = audienceSize * conversionDecimal;
      const revenue =
        month === 0
          ? currentMonthlyRevenue
          : (currentMonthlyRevenue / (currentAudienceSize * conversionDecimal)) * customers;

      baselineProjection.push({
        month: month,
        audience: Math.round(audienceSize),
        customers: Math.round(customers),
        revenue: revenue.toFixed(2),
      });
    }

    // Optimization scenario: improve conversion by 50% over 6 months
    const optimizedProjection = [];
    audienceSize = currentAudienceSize;
    let currentConv = conversionDecimal;
    const conversionImprovement = 0.5 / 6; // 50% improvement over 6 months

    for (let month = 0; month <= projectionMonths; month++) {
      if (month > 0) {
        audienceSize = audienceSize * (1 + audienceGrowthDecimal);
        if (month <= 6) {
          currentConv = currentConv * (1 + conversionImprovement);
        }
      }
      const customers = audienceSize * currentConv;
      const revenue =
        month === 0
          ? currentMonthlyRevenue
          : (currentMonthlyRevenue / (currentAudienceSize * conversionDecimal)) * customers;

      optimizedProjection.push({
        month: month,
        audience: Math.round(audienceSize),
        customers: Math.round(customers),
        revenue: revenue.toFixed(2),
        conversionRate: `${(currentConv * 100).toFixed(2)}%`,
      });
    }

    // Aggressive scenario: 2x LTV + 50% conversion improvement
    const aggressiveProjection = [];
    audienceSize = currentAudienceSize;
    currentConv = conversionDecimal;

    for (let month = 0; month <= projectionMonths; month++) {
      if (month > 0) {
        audienceSize = audienceSize * (1 + audienceGrowthDecimal);
        if (month <= 6) {
          currentConv = currentConv * (1 + conversionImprovement);
        }
      }
      const customers = audienceSize * currentConv;
      const ltvMultiplier = month >= 3 ? 2 : 1 + (month / 3) * 1; // Gradual LTV improvement
      const revenue =
        month === 0
          ? currentMonthlyRevenue
          : (currentMonthlyRevenue / (currentAudienceSize * conversionDecimal)) *
            customers *
            ltvMultiplier;

      aggressiveProjection.push({
        month: month,
        audience: Math.round(audienceSize),
        customers: Math.round(customers),
        revenue: revenue.toFixed(2),
        ltvMultiplier: `${ltvMultiplier.toFixed(2)}x`,
      });
    }

    return {
      baselineScenario: {
        description: "Maintain current conversion rate, grow with audience",
        month12Revenue: baselineProjection[projectionMonths].revenue,
        totalRevenue: baselineProjection
          .reduce((sum, m) => sum + parseFloat(m.revenue), 0)
          .toFixed(2),
        projection: baselineProjection,
      },
      optimizedScenario: {
        description: "Improve conversion rate by 50% over 6 months",
        month12Revenue: optimizedProjection[projectionMonths].revenue,
        totalRevenue: optimizedProjection
          .reduce((sum, m) => sum + parseFloat(m.revenue), 0)
          .toFixed(2),
        vsBaseline: `${(
          ((parseFloat(optimizedProjection[projectionMonths].revenue) -
            parseFloat(baselineProjection[projectionMonths].revenue)) /
            parseFloat(baselineProjection[projectionMonths].revenue)) *
            100
        ).toFixed(1)}% increase`,
        projection: optimizedProjection,
      },
      aggressiveScenario: {
        description: "50% conversion improvement + 2x customer lifetime value",
        month12Revenue: aggressiveProjection[projectionMonths].revenue,
        totalRevenue: aggressiveProjection
          .reduce((sum, m) => sum + parseFloat(m.revenue), 0)
          .toFixed(2),
        vsBaseline: `${(
          ((parseFloat(aggressiveProjection[projectionMonths].revenue) -
            parseFloat(baselineProjection[projectionMonths].revenue)) /
            parseFloat(baselineProjection[projectionMonths].revenue)) *
            100
        ).toFixed(1)}% increase`,
        projection: aggressiveProjection,
      },
      keyInsights: [
        {
          insight: "Revenue growth depends on both audience AND conversion",
          action: "Don't just focus on growing audience—optimize monetization efficiency",
        },
        {
          insight: "Conversion optimization compounds over time with audience growth",
          action: "Even small conversion improvements create massive revenue differences",
        },
        {
          insight: "LTV improvements have multiplicative effect on revenue",
          action: "Backend monetization (upsells, continuity) is highest-leverage work",
        },
      ],
    };
  },
});

/**
 * Evaluate Pricing Strategy
 *
 * Analyzes pricing across different market segments and recommends optimal strategy
 */
export const evaluatePricingStrategy = tool({
  name: "evaluate_pricing_strategy",
  description:
    "Evaluate pricing strategy across different customer segments and price points. Analyzes price elasticity and recommends optimal pricing architecture.",
  parameters: {
    type: "object",
    properties: {
      productType: {
        type: "string",
        description: "Type of product (course, coaching, software, membership, etc.)",
      },
      currentPrice: {
        type: "number",
        description: "Current price point",
      },
      costToDeliver: {
        type: "number",
        description: "Cost to deliver product/service",
      },
      monthlyCustomers: {
        type: "number",
        description: "Current monthly customer volume",
      },
      marketPosition: {
        type: "string",
        enum: ["budget", "mid-market", "premium", "luxury"],
        description: "Target market positioning",
      },
    },
    required: [
      "productType",
      "currentPrice",
      "costToDeliver",
      "monthlyCustomers",
      "marketPosition",
    ],
  },
  execute: async ({
    productType,
    currentPrice,
    costToDeliver,
    monthlyCustomers,
    marketPosition,
  }) => {
    const currentMargin = ((currentPrice - costToDeliver) / currentPrice) * 100;
    const currentMonthlyRevenue = currentPrice * monthlyCustomers;

    // Market-based pricing recommendations
    const pricingBenchmarks = {
      course: { budget: 97, "mid-market": 497, premium: 1997, luxury: 4997 },
      coaching: {
        budget: 297,
        "mid-market": 997,
        premium: 2997,
        luxury: 9997,
      },
      software: { budget: 29, "mid-market": 99, premium: 299, luxury: 999 },
      membership: { budget: 19, "mid-market": 49, premium: 197, luxury: 497 },
    };

    const recommendedPrice = pricingBenchmarks[productType]?.[marketPosition] || currentPrice;

    // Calculate price elasticity scenarios
    const scenarios = [
      {
        name: "Current Pricing",
        price: currentPrice,
        estimatedVolume: monthlyCustomers,
        revenue: currentMonthlyRevenue,
        margin: currentMargin,
      },
      {
        name: "20% Price Increase (Premium Positioning)",
        price: currentPrice * 1.2,
        estimatedVolume: monthlyCustomers * 0.9, // Assume 10% volume loss
        revenue: currentPrice * 1.2 * (monthlyCustomers * 0.9),
        margin: ((currentPrice * 1.2 - costToDeliver) / (currentPrice * 1.2)) * 100,
        analysis: "Higher margins offset volume loss if quality/positioning strong",
      },
      {
        name: "Market-Aligned Pricing",
        price: recommendedPrice,
        estimatedVolume:
          recommendedPrice > currentPrice ? monthlyCustomers * 0.85 : monthlyCustomers * 1.15,
        revenue:
          recommendedPrice > currentPrice
            ? recommendedPrice * (monthlyCustomers * 0.85)
            : recommendedPrice * (monthlyCustomers * 1.15),
        margin: ((recommendedPrice - costToDeliver) / recommendedPrice) * 100,
        analysis: `Aligned with ${marketPosition} market positioning`,
      },
      {
        name: "Value Ladder (Multi-Tier)",
        tiers: [
          {
            name: "Entry",
            price: currentPrice * 0.5,
            volume: monthlyCustomers * 1.5,
          },
          {
            name: "Standard",
            price: currentPrice,
            volume: monthlyCustomers,
          },
          {
            name: "Premium",
            price: currentPrice * 3,
            volume: monthlyCustomers * 0.2,
          },
        ],
        totalRevenue:
          currentPrice * 0.5 * (monthlyCustomers * 1.5) +
          currentPrice * monthlyCustomers +
          currentPrice * 3 * (monthlyCustomers * 0.2),
        analysis: "Capture more market segments with tiered pricing",
      },
    ];

    return {
      currentAnalysis: {
        price: currentPrice,
        margin: `${currentMargin.toFixed(2)}%`,
        monthlyRevenue: currentMonthlyRevenue.toFixed(2),
        annualRevenue: (currentMonthlyRevenue * 12).toFixed(2),
      },
      marketBenchmark: {
        recommendedPrice: recommendedPrice,
        currentVsBenchmark: currentPrice < recommendedPrice ? "UNDERPRICED" : "PREMIUM PRICED",
        gap: (recommendedPrice - currentPrice).toFixed(2),
        gapPercentage: `${(((recommendedPrice - currentPrice) / currentPrice) * 100).toFixed(1)}%`,
      },
      scenarios: scenarios,
      recommendations: [
        {
          priority: 1,
          action:
            currentPrice < recommendedPrice * 0.8
              ? "Increase prices to market-appropriate levels"
              : "Test premium positioning with value justification",
          expectedImpact: "Revenue increase without proportional effort increase",
          implementation: [
            "Grandfather existing customers at current price",
            "A/B test new pricing on landing pages",
            "Enhance value perception through positioning/packaging",
            "Add premium tier for high-end customers",
          ],
        },
        {
          priority: 2,
          action: "Implement value ladder with multiple price points",
          expectedImpact: "Capture more market segments, increase total revenue",
          implementation: [
            `Entry tier at $${(currentPrice * 0.5).toFixed(0)} (lighter version)`,
            `Standard tier at $${currentPrice.toFixed(0)} (current offering)`,
            `Premium tier at $${(currentPrice * 3).toFixed(0)} (enhanced + support)`,
          ],
        },
        {
          priority: 3,
          action: "Test price anchoring and psychological pricing",
          expectedImpact: "Improved conversion rates at current or higher prices",
          implementation: [
            "Show higher 'regular price' with discounted offer",
            "Bundle products to increase perceived value",
            "Use charm pricing (e.g., $97 vs $100)",
            "Display annual pricing to increase commitment",
          ],
        },
      ],
    };
  },
});

/**
 * Assess Market Opportunity
 *
 * Evaluates market size, competition, and opportunity for different revenue streams
 */
export const assessMarketOpportunity = tool({
  name: "assess_market_opportunity",
  description:
    "Assess market opportunity for different revenue streams based on audience, niche, and competitive landscape. Identifies highest-potential opportunities.",
  parameters: {
    type: "object",
    properties: {
      niche: {
        type: "string",
        description: "Primary niche or industry focus",
      },
      audienceSize: {
        type: "number",
        description: "Current total audience size",
      },
      engagement: {
        type: "string",
        enum: ["low", "medium", "high"],
        description: "Audience engagement level",
      },
      currentRevenue: {
        type: "number",
        description: "Current monthly revenue",
      },
      revenueStreams: {
        type: "array",
        description: "Revenue streams to evaluate",
        items: {
          type: "string",
          enum: [
            "courses",
            "coaching",
            "consulting",
            "software",
            "membership",
            "affiliate",
            "sponsorship",
            "physical-products",
            "events",
            "licensing",
          ],
        },
      },
    },
    required: ["niche", "audienceSize", "engagement", "currentRevenue", "revenueStreams"],
  },
  execute: async ({ niche: _niche, audienceSize, engagement, currentRevenue, revenueStreams }) => {
    // Engagement multipliers
    const engagementMultipliers = {
      low: 0.7,
      medium: 1.0,
      high: 1.5,
    };

    const engagementMultiplier = engagementMultipliers[engagement];

    // Revenue stream scoring framework
    const streamScoring = {
      courses: {
        ease: 8,
        scalability: 9,
        margin: 9,
        timeToRevenue: 7,
        avgRevenuePerCustomer: 497,
      },
      coaching: {
        ease: 9,
        scalability: 4,
        margin: 9,
        timeToRevenue: 9,
        avgRevenuePerCustomer: 2997,
      },
      consulting: {
        ease: 8,
        scalability: 3,
        margin: 9,
        timeToRevenue: 8,
        avgRevenuePerCustomer: 9997,
      },
      software: {
        ease: 4,
        scalability: 10,
        margin: 9,
        timeToRevenue: 4,
        avgRevenuePerCustomer: 99,
      },
      membership: {
        ease: 7,
        scalability: 9,
        margin: 8,
        timeToRevenue: 8,
        avgRevenuePerCustomer: 49,
      },
      affiliate: {
        ease: 9,
        scalability: 8,
        margin: 7,
        timeToRevenue: 9,
        avgRevenuePerCustomer: 50,
      },
      sponsorship: {
        ease: 6,
        scalability: 7,
        margin: 10,
        timeToRevenue: 6,
        avgRevenuePerCustomer: 5000,
      },
      "physical-products": {
        ease: 5,
        scalability: 7,
        margin: 5,
        timeToRevenue: 5,
        avgRevenuePerCustomer: 47,
      },
      events: {
        ease: 5,
        scalability: 5,
        margin: 6,
        timeToRevenue: 6,
        avgRevenuePerCustomer: 997,
      },
      licensing: {
        ease: 6,
        scalability: 8,
        margin: 10,
        timeToRevenue: 4,
        avgRevenuePerCustomer: 10000,
      },
    };

    // Analyze each requested revenue stream
    const opportunities = revenueStreams.map((stream) => {
      const metrics = streamScoring[stream];
      const estimatedConversion = 0.01 * engagementMultiplier; // Base 1% conversion
      const potentialCustomers = Math.round(audienceSize * estimatedConversion);
      const potentialRevenue = potentialCustomers * metrics.avgRevenuePerCustomer;

      // Overall score (weighted average)
      const overallScore =
        (metrics.ease * 0.2 +
          metrics.scalability * 0.3 +
          metrics.margin * 0.2 +
          metrics.timeToRevenue * 0.3) /
        10;

      return {
        stream: stream,
        score: (overallScore * 10).toFixed(1),
        metrics: metrics,
        potential: {
          estimatedCustomers: potentialCustomers,
          estimatedMonthlyRevenue: potentialRevenue.toFixed(2),
          estimatedAnnualRevenue: (potentialRevenue * 12).toFixed(2),
        },
        recommendation:
          overallScore > 0.75
            ? "HIGH PRIORITY - Strong fit for current position"
            : overallScore > 0.6
              ? "MEDIUM PRIORITY - Good opportunity with some barriers"
              : "LOW PRIORITY - Significant challenges or low return",
      };
    });

    // Sort by score
    opportunities.sort((a, b) => parseFloat(b.score) - parseFloat(a.score));

    return {
      audienceAnalysis: {
        size: audienceSize,
        engagement: engagement,
        engagementQuality:
          engagement === "high"
            ? "Strong - Higher conversion potential"
            : engagement === "medium"
              ? "Moderate - Average conversion potential"
              : "Weak - Lower conversion potential, focus on engagement first",
        currentMonetization: currentRevenue,
        potentialMultiplier:
          opportunities.length > 0
            ? `${(
                parseFloat(opportunities[0].potential.estimatedMonthlyRevenue) / currentRevenue
              ).toFixed(1)}x`
            : "N/A",
      },
      opportunities: opportunities,
      topRecommendations: opportunities.slice(0, 3).map((opp, idx) => ({
        rank: idx + 1,
        stream: opp.stream,
        score: opp.score,
        potentialRevenue: opp.potential.estimatedMonthlyRevenue,
        whyNow: [
          opp.metrics.timeToRevenue > 7 ? "Fast time-to-revenue" : "Requires longer setup",
          opp.metrics.scalability > 7 ? "Highly scalable" : "Limited scalability",
          opp.metrics.margin > 7 ? "Strong margins" : "Lower margins",
          opp.metrics.ease > 7 ? "Relatively easy to implement" : "Complex implementation",
        ],
        firstSteps: [
          "Validate demand with audience survey or direct outreach",
          "Create MVP offer (minimum viable product)",
          "Test with small group before full launch",
          "Iterate based on feedback and results",
        ],
      })),
      strategicInsights: [
        {
          insight: "Audience size vs. engagement tradeoff",
          guidance:
            engagement === "high"
              ? "High engagement allows for higher-ticket offers and better conversion"
              : "Focus on engagement before scaling audience further",
        },
        {
          insight: "Revenue stream diversification",
          guidance:
            opportunities.length > 3
              ? "Multiple strong opportunities—prioritize by ease and time-to-revenue"
              : "Limited diversification options—focus on core strengths",
        },
        {
          insight: "Scalability vs. Time-to-revenue",
          guidance:
            "Balance quick wins (coaching, affiliate) with long-term scalability (courses, software)",
        },
      ],
    };
  },
});

// Export all tools as an array for easy integration
export const monetizationTools = [
  calculateLTV,
  analyzeRevenueFunnel,
  calculateRevenueProjections,
  evaluatePricingStrategy,
  assessMarketOpportunity,
];
