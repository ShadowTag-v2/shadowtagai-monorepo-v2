/**
 * TypeScript Usage Examples for Wealth Acceleration Agent
 *
 * This file demonstrates various ways to use the Wealth Acceleration Agent
 * in TypeScript/Node.js applications.
 */

import WealthAccelerationAgent from '../../src/agents/wealth-acceleration-agent';

// =============================================================================
// Example 1: Basic Setup and Monetization Strategy Analysis
// =============================================================================

async function example1_basicMonetizationAnalysis() {
  console.log('=== Example 1: Basic Monetization Strategy Analysis ===\n');

  // Create agent instance
  const agent = new WealthAccelerationAgent({
    apiKey: process.env.ANTHROPIC_API_KEY,
    enableExtendedThinking: true,
    thinkingBudget: 8000,
  });

  // Set business context
  agent.setBusinessContext({
    niche: 'SaaS founders',
    currentMonthlyRevenue: 15000,
    audienceSize: 50000,
    engagementLevel: 'high',
    revenueStreams: ['consulting', 'courses'],
    platforms: ['Twitter', 'LinkedIn', 'Newsletter'],
    additionalContext:
      'Launching a new cohort-based course next month. Want to optimize entire revenue stack.',
  });

  // Run comprehensive monetization analysis
  await agent.analyzeMonetizationStrategy();
}

// =============================================================================
// Example 2: Funnel Optimization
// =============================================================================

async function example2_funnelOptimization() {
  console.log('\n=== Example 2: Funnel Optimization ===\n');

  const agent = new WealthAccelerationAgent({
    apiKey: process.env.ANTHROPIC_API_KEY,
  });

  agent.setBusinessContext({
    niche: 'Marketing consultants',
    currentMonthlyRevenue: 8000,
    audienceSize: 20000,
    engagementLevel: 'medium',
  });

  // Analyze conversion funnel
  await agent.optimizeConversionFunnel([
    {
      name: 'Blog/Content',
      visitors: 15000,
      conversions: 3000,
      revenue: 0,
    },
    {
      name: 'Lead Magnet Page',
      visitors: 3000,
      conversions: 1200,
      revenue: 0,
    },
    {
      name: 'Email Nurture Sequence',
      visitors: 1200,
      conversions: 300,
      revenue: 0,
    },
    {
      name: 'Sales Page',
      visitors: 300,
      conversions: 45,
      revenue: 22365,
    },
    {
      name: 'Customers',
      visitors: 45,
      conversions: 0,
      revenue: 0,
    },
  ]);
}

// =============================================================================
// Example 3: Pricing Strategy Evaluation
// =============================================================================

async function example3_pricingEvaluation() {
  console.log('\n=== Example 3: Pricing Strategy Evaluation ===\n');

  const agent = new WealthAccelerationAgent({
    apiKey: process.env.ANTHROPIC_API_KEY,
  });

  agent.setBusinessContext({
    niche: 'Fitness coaches',
    currentMonthlyRevenue: 12000,
    offers: [
      { name: 'Self-Paced Course', price: 197, monthlySales: 25 },
      { name: 'Group Coaching', price: 497, monthlySales: 10 },
    ],
  });

  // Evaluate pricing for main course
  await agent.evaluatePricing(
    'course', // product type
    197, // current price
    25, // cost to deliver
    25, // monthly customers
    'mid-market', // market position
  );
}

// =============================================================================
// Example 4: Revenue Projections
// =============================================================================

async function example4_revenueProjections() {
  console.log('\n=== Example 4: Revenue Projections ===\n');

  const agent = new WealthAccelerationAgent({
    apiKey: process.env.ANTHROPIC_API_KEY,
    enableExtendedThinking: true,
  });

  agent.setBusinessContext({
    niche: 'Content creators',
    currentMonthlyRevenue: 5000,
    audienceSize: 25000,
    engagementLevel: 'high',
  });

  // Project 12-month revenue growth
  await agent.projectRevenue(
    5000, // current monthly revenue
    25000, // current audience size
    15, // monthly audience growth (%)
    1.5, // current conversion rate (%)
    12, // months to project
  );
}

// =============================================================================
// Example 5: Customer LTV Optimization
// =============================================================================

async function example5_ltvOptimization() {
  console.log('\n=== Example 5: Customer LTV Optimization ===\n');

  const agent = new WealthAccelerationAgent({
    apiKey: process.env.ANTHROPIC_API_KEY,
  });

  agent.setBusinessContext({
    niche: 'E-commerce store owners',
    currentMonthlyRevenue: 20000,
    revenueStreams: ['courses', 'software', 'membership'],
  });

  // Calculate and optimize LTV
  await agent.calculateCustomerLTV(
    297, // average order value
    3.5, // purchase frequency (per year)
    2.5, // customer lifespan (years)
    85, // gross margin (%)
  );
}

// =============================================================================
// Example 6: Market Opportunity Assessment
// =============================================================================

async function example6_opportunityAssessment() {
  console.log('\n=== Example 6: Market Opportunity Assessment ===\n');

  const agent = new WealthAccelerationAgent({
    apiKey: process.env.ANTHROPIC_API_KEY,
    enableExtendedThinking: true,
    thinkingBudget: 16000,
  });

  agent.setBusinessContext({
    niche: 'Indie hackers',
    currentMonthlyRevenue: 3000,
    audienceSize: 15000,
    engagementLevel: 'high',
    platforms: ['Twitter', 'Newsletter', 'YouTube'],
  });

  // Assess multiple revenue stream opportunities
  await agent.assessOpportunities('Indie hackers', 15000, 'high', 3000, [
    'courses',
    'coaching',
    'software',
    'membership',
    'affiliate',
    'sponsorship',
  ]);
}

// =============================================================================
// Example 7: Custom Analysis with Extended Thinking
// =============================================================================

async function example7_customAnalysisWithThinking() {
  console.log('\n=== Example 7: Custom Analysis with Extended Thinking ===\n');

  const agent = new WealthAccelerationAgent({
    apiKey: process.env.ANTHROPIC_API_KEY,
    enableExtendedThinking: true,
    thinkingBudget: 32000, // Maximum thinking budget for complex analysis
  });

  agent.setBusinessContext({
    niche: 'B2B SaaS',
    currentMonthlyRevenue: 50000,
    audienceSize: 100000,
    engagementLevel: 'medium',
    revenueStreams: ['SaaS subscriptions', 'enterprise contracts', 'consulting'],
    additionalContext: `
      Current situation:
      - MRR: $50K (80% from small businesses, 20% from enterprise)
      - Churn: 8% monthly
      - CAC: $450
      - LTV: $1,200
      - Team: 8 people
      - Main challenge: Want to move upmarket to enterprise but unsure how to transition
    `,
  });

  // Custom strategic analysis with extended thinking
  await agent.analyze(`
    ultrathink this challenge:

    I want to transition from serving small businesses ($99-299/month) to enterprise ($2K-10K/month).

    I need you to:
    1. Analyze whether this transition makes sense given my current position
    2. Design a dual-track monetization strategy that doesn't kill existing revenue
    3. Map out the product/positioning changes needed for enterprise
    4. Calculate the economics: how many enterprise deals to replace SMB revenue?
    5. Identify the biggest risks and how to mitigate them
    6. Give me a 90-day transition roadmap
    7. Challenge me with the ONE thing I must do this week to de-risk this move

    Be brutally honest about whether this is the right move or if I should double down on SMB instead.
  `);
}

// =============================================================================
// Example 8: Multi-Stage Analysis Workflow
// =============================================================================

async function example8_multiStageWorkflow() {
  console.log('\n=== Example 8: Multi-Stage Analysis Workflow ===\n');

  const agent = new WealthAccelerationAgent({
    apiKey: process.env.ANTHROPIC_API_KEY,
  });

  const context = {
    niche: 'Online educators',
    currentMonthlyRevenue: 7500,
    audienceSize: 30000,
    engagementLevel: 'medium' as const,
    revenueStreams: ['courses'],
    platforms: ['YouTube', 'Newsletter'],
  };

  agent.setBusinessContext(context);

  // Stage 1: Overall monetization analysis
  console.log('\n--- Stage 1: Monetization Strategy ---\n');
  await agent.analyzeMonetizationStrategy();

  // Stage 2: Specific pricing evaluation
  console.log('\n--- Stage 2: Pricing Analysis ---\n');
  await agent.evaluatePricing('course', 497, 75, 15, 'mid-market');

  // Stage 3: Growth projections
  console.log('\n--- Stage 3: Revenue Projections ---\n');
  await agent.projectRevenue(7500, 30000, 12, 1.8, 12);

  // Stage 4: Opportunity assessment
  console.log('\n--- Stage 4: New Opportunities ---\n');
  await agent.assessOpportunities('Online educators', 30000, 'medium', 7500, [
    'coaching',
    'membership',
    'software',
    'affiliate',
  ]);
}

// =============================================================================
// Example 9: Error Handling and Validation
// =============================================================================

async function example9_errorHandling() {
  console.log('\n=== Example 9: Error Handling ===\n');

  const agent = new WealthAccelerationAgent({
    apiKey: process.env.ANTHROPIC_API_KEY,
    verbose: true, // Enable verbose logging
  });

  try {
    // Attempt analysis with minimal context
    await agent.analyze('Give me a complete monetization strategy for my business.');

    // The agent will ask for more context
    console.log(
      '\n\nNote: The agent will request more specific information when context is insufficient.',
    );
  } catch (_error) {
    // Implement your error handling logic here
  }
}

// =============================================================================
// Main execution
// =============================================================================

async function main() {
  console.log('Wealth Acceleration Agent - TypeScript Examples\n');
  console.log('================================================\n');

  // Run examples (uncomment the ones you want to try)

  // await example1_basicMonetizationAnalysis();
  // await example2_funnelOptimization();
  // await example3_pricingEvaluation();
  // await example4_revenueProjections();
  // await example5_ltvOptimization();
  // await example6_opportunityAssessment();
  // await example7_customAnalysisWithThinking();
  // await example8_multiStageWorkflow();
  // await example9_errorHandling();

  console.log('\n\nTo run these examples:');
  console.log('1. Ensure ANTHROPIC_API_KEY is set in your environment');
  console.log('2. Uncomment the example you want to run in the main() function');
  console.log('3. Run: npx ts-node docs/examples/typescript-example.ts');
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

export {
  example1_basicMonetizationAnalysis,
  example2_funnelOptimization,
  example3_pricingEvaluation,
  example4_revenueProjections,
  example5_ltvOptimization,
  example6_opportunityAssessment,
  example7_customAnalysisWithThinking,
  example8_multiStageWorkflow,
  example9_errorHandling,
};
