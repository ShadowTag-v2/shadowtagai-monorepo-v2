/**
 * Wealth Acceleration Strategist Agent
 *
 * Main implementation file for the wealth acceleration agent that combines
 * the comprehensive prompt framework with custom monetization tools.
 *
 * This agent helps users:
 * - Identify revenue leaks and missed opportunities
 * - Design comprehensive monetization architectures
 * - Optimize conversion funnels and customer lifetime value
 * - Build scalable, automated income systems
 *
 * Version: 1.0.0
 * Last Updated: 2025-11-08
 */

import { query } from "@anthropic-ai/claude-agent-sdk";
import { WEALTH_ACCELERATION_AGENT_PROMPT } from "../prompts/wealth-acceleration-strategist";
import { monetizationTools } from "../tools/monetization-tools";

/**
 * Configuration options for the Wealth Acceleration Agent
 */
export interface WealthAccelerationAgentConfig {
  /**
   * API key for Anthropic Claude
   */
  apiKey?: string;

  /**
   * Model to use (default: claude-sonnet-4.5-20250514)
   */
  model?: string;

  /**
   * Maximum tokens for response
   */
  maxTokens?: number;

  /**
   * Temperature for response generation (0-1)
   */
  temperature?: number;

  /**
   * Enable extended thinking mode
   */
  enableExtendedThinking?: boolean;

  /**
   * Extended thinking budget (tokens)
   */
  thinkingBudget?: number;

  /**
   * Additional custom tools to include
   */
  customTools?: any[];

  /**
   * Enable verbose logging
   */
  verbose?: boolean;
}

/**
 * Business context for analysis
 */
export interface BusinessContext {
  /**
   * Primary niche or industry
   */
  niche?: string;

  /**
   * Current monthly revenue
   */
  currentMonthlyRevenue?: number;

  /**
   * Total audience size across all platforms
   */
  audienceSize?: number;

  /**
   * Engagement level (low, medium, high)
   */
  engagementLevel?: "low" | "medium" | "high";

  /**
   * Existing revenue streams
   */
  revenueStreams?: string[];

  /**
   * Current offers and pricing
   */
  offers?: Array<{
    name: string;
    price: number;
    monthlySales?: number;
  }>;

  /**
   * Content platforms
   */
  platforms?: string[];

  /**
   * Any additional context
   */
  additionalContext?: string;
}

/**
 * Main Wealth Acceleration Agent class
 */
export class WealthAccelerationAgent {
  private config: WealthAccelerationAgentConfig;
  private businessContext?: BusinessContext;

  constructor(config: WealthAccelerationAgentConfig = {}) {
    this.config = {
      model: "claude-sonnet-4.5-20250514",
      maxTokens: 8000,
      temperature: 1.0,
      enableExtendedThinking: true,
      thinkingBudget: 8000,
      verbose: false,
      ...config,
    };
  }

  /**
   * Set business context for the agent
   */
  setBusinessContext(context: BusinessContext): void {
    this.businessContext = context;
  }

  /**
   * Format business context as a prompt addition
   */
  private formatBusinessContext(): string {
    if (!this.businessContext) {
      return "";
    }

    const parts = ["<business_context>"];

    if (this.businessContext.niche) {
      parts.push(`Niche: ${this.businessContext.niche}`);
    }

    if (this.businessContext.currentMonthlyRevenue !== undefined) {
      parts.push(
        `Current Monthly Revenue: $${this.businessContext.currentMonthlyRevenue.toLocaleString()}`,
      );
    }

    if (this.businessContext.audienceSize) {
      parts.push(`Total Audience Size: ${this.businessContext.audienceSize.toLocaleString()}`);
    }

    if (this.businessContext.engagementLevel) {
      parts.push(`Engagement Level: ${this.businessContext.engagementLevel}`);
    }

    if (this.businessContext.revenueStreams?.length) {
      parts.push(`Current Revenue Streams: ${this.businessContext.revenueStreams.join(", ")}`);
    }

    if (this.businessContext.offers?.length) {
      parts.push("\nCurrent Offers:");
      this.businessContext.offers.forEach((offer) => {
        parts.push(
          `- ${offer.name}: $${offer.price}${offer.monthlySales ? ` (${offer.monthlySales} sales/month)` : ""}`,
        );
      });
    }

    if (this.businessContext.platforms?.length) {
      parts.push(`\nPlatforms: ${this.businessContext.platforms.join(", ")}`);
    }

    if (this.businessContext.additionalContext) {
      parts.push(`\nAdditional Context:\n${this.businessContext.additionalContext}`);
    }

    parts.push("</business_context>");

    return parts.join("\n");
  }

  /**
   * Run the agent with a specific query
   */
  async analyze(userPrompt: string): Promise<void> {
    const contextualPrompt = this.businessContext
      ? `${this.formatBusinessContext()}\n\n${userPrompt}`
      : userPrompt;

    const options: any = {
      systemPrompt: WEALTH_ACCELERATION_AGENT_PROMPT,
      tools: [...monetizationTools, ...(this.config.customTools || [])],
      model: this.config.model,
      maxTokens: this.config.maxTokens,
      temperature: this.config.temperature,
    };

    // Add extended thinking if enabled
    if (this.config.enableExtendedThinking) {
      options.extendedThinking = {
        enabled: true,
        budget: this.config.thinkingBudget,
      };
    }

    try {
      // Stream the agent's response
      for await (const message of query({
        prompt: contextualPrompt,
        options,
      })) {
        if (this.config.verbose) {
          console.log("[Wealth Acceleration Agent]:", message);
        } else {
          // Output the message content
          if (typeof message === "string") {
            process.stdout.write(message);
          } else if (message.type === "text") {
            process.stdout.write(message.text);
          }
        }
      }
    } catch (error) {
      console.error("Error running agent:", error);
      throw error;
    }
  }

  /**
   * Quick analysis methods for common tasks
   */

  /**
   * Analyze overall monetization strategy
   */
  async analyzeMonetizationStrategy(): Promise<void> {
    const prompt = `
Analyze my complete monetization strategy. I need you to:

1. Identify ALL revenue leaks in my current operation
2. Design a comprehensive monetization architecture across all price points
3. Map out the complete customer journey from discovery to high-ticket
4. Provide specific implementation steps for the next 30 days
5. Challenge me with immediate actions I can take TODAY

Give me the full strategic analysis with brutal honesty about what's missing.
`;
    return this.analyze(prompt);
  }

  /**
   * Optimize conversion funnel
   */
  async optimizeConversionFunnel(funnelStages: any[]): Promise<void> {
    const prompt = `
I need you to analyze my conversion funnel and identify exactly where I'm losing money.

Use the analyze_revenue_funnel tool with this data:
${JSON.stringify(funnelStages, null, 2)}

Then provide:
1. Specific diagnosis of the biggest leaks
2. Tactical fixes for each stage
3. Expected revenue impact of optimizations
4. A challenge for me to implement the highest-impact fix TODAY
`;
    return this.analyze(prompt);
  }

  /**
   * Evaluate pricing strategy
   */
  async evaluatePricing(
    productType: string,
    currentPrice: number,
    costToDeliver: number,
    monthlyCustomers: number,
    marketPosition: string,
  ): Promise<void> {
    const prompt = `
Evaluate my pricing strategy using the evaluate_pricing_strategy tool:

Product Type: ${productType}
Current Price: $${currentPrice}
Cost to Deliver: $${costToDeliver}
Monthly Customers: ${monthlyCustomers}
Market Position: ${marketPosition}

Tell me:
1. Am I leaving money on the table with my current pricing?
2. What should my optimal pricing strategy be?
3. How should I implement tiered pricing?
4. What's my first pricing experiment to run THIS WEEK?

Be brutally honest about whether I'm underpricing.
`;
    return this.analyze(prompt);
  }

  /**
   * Project revenue growth
   */
  async projectRevenue(
    currentMonthlyRevenue: number,
    currentAudienceSize: number,
    monthlyAudienceGrowth: number,
    currentConversionRate: number,
    months: number = 12,
  ): Promise<void> {
    const prompt = `
Calculate revenue projections using the calculate_revenue_projections tool:

Current Monthly Revenue: $${currentMonthlyRevenue}
Current Audience Size: ${currentAudienceSize}
Monthly Audience Growth: ${monthlyAudienceGrowth}%
Current Conversion Rate: ${currentConversionRate}%
Projection Period: ${months} months

Show me:
1. Baseline scenario (status quo)
2. Optimized scenario (what's possible with strategic improvements)
3. Aggressive scenario (what happens if I execute at the highest level)
4. The specific strategic moves that bridge the gap between scenarios
5. What I need to do THIS WEEK to start tracking toward the optimized scenario

Make it real. Show me the dollar difference between mediocre execution and excellence.
`;
    return this.analyze(prompt);
  }

  /**
   * Calculate customer lifetime value
   */
  async calculateCustomerLTV(
    averageOrderValue: number,
    purchaseFrequency: number,
    customerLifespan: number,
    grossMargin: number,
  ): Promise<void> {
    const prompt = `
Calculate customer lifetime value using the calculate_ltv tool:

Average Order Value: $${averageOrderValue}
Purchase Frequency: ${purchaseFrequency} purchases/year
Customer Lifespan: ${customerLifespan} years
Gross Margin: ${grossMargin}%

Then tell me:
1. What's my current LTV and is it good enough?
2. Which lever (AOV, frequency, lifespan) has the biggest impact?
3. Specific tactics to increase each lever
4. How backend monetization (upsells, continuity) transforms these numbers
5. The ONE thing I should implement THIS WEEK to increase LTV

Don't just give me numbers—tell me exactly how to engineer higher customer value.
`;
    return this.analyze(prompt);
  }

  /**
   * Assess market opportunities
   */
  async assessOpportunities(
    niche: string,
    audienceSize: number,
    engagement: "low" | "medium" | "high",
    currentRevenue: number,
    potentialStreams: string[],
  ): Promise<void> {
    const prompt = `
Assess market opportunities using the assess_market_opportunity tool:

Niche: ${niche}
Audience Size: ${audienceSize}
Engagement: ${engagement}
Current Revenue: $${currentRevenue}
Potential Revenue Streams: ${potentialStreams.join(", ")}

Analyze:
1. Which revenue streams are the highest-leverage opportunities for me RIGHT NOW?
2. What's the realistic revenue potential for each?
3. Which should I prioritize based on ease, speed, and scale?
4. What's the fastest path to my next $10K/month?
5. What should I validate or test THIS WEEK?

Give me a clear prioritization with specific reasoning—not generic advice.
`;
    return this.analyze(prompt);
  }
}

/**
 * Quick helper function to create and run agent
 */
export async function runWealthAccelerationAgent(
  prompt: string,
  context?: BusinessContext,
  config?: WealthAccelerationAgentConfig,
): Promise<void> {
  const agent = new WealthAccelerationAgent(config);
  if (context) {
    agent.setBusinessContext(context);
  }
  await agent.analyze(prompt);
}

// Export for library usage
export default WealthAccelerationAgent;
