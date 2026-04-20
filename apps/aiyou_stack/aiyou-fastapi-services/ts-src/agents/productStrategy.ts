/**
 * Product Strategy Agents for Vertex AI Workbench
 */

import {
  AgentCategory,
  type AgentContext,
  type AgentExecutionResult,
  type AgentMetadata,
  BaseAgent,
} from './base';

export class ProductStrategistAgent extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: 'Product Strategist',
      description:
        'Looks at your features and asks the hard questions. Tells you what to build next and what to kill.',
      category: AgentCategory.PRODUCT_STRATEGY,
      icon: '🎯',
      version: '1.0.0',
      tags: ['strategy', 'product', 'prioritization', 'roadmap'],
    };
  }

  getSystemPrompt(): string {
    return `You are a Product Strategist AI agent specialized in product strategy and feature prioritization.

Your responsibilities:
- Analyze existing features and their usage patterns
- Ask critical questions about product direction
- Identify features to build, enhance, or deprecate
- Create data-driven product roadmaps
- Evaluate feature ROI and user impact
- Provide strategic recommendations

Approach every analysis with:
1. User value assessment
2. Business impact evaluation
3. Technical feasibility consideration
4. Competitive analysis
5. Resource allocation optimization

Be direct and candid about features that aren't working. Focus on impact over effort.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class GrowthEngineerAgent extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: 'Growth Engineer',
      description:
        'Finds where users get hooked in your app and builds viral loops that actually work.',
      category: AgentCategory.PRODUCT_STRATEGY,
      icon: '📈',
      version: '1.0.0',
      tags: ['growth', 'viral', 'engagement', 'retention', 'hooks'],
    };
  }

  getSystemPrompt(): string {
    return `You are a Growth Engineer AI agent specialized in user acquisition and viral growth.

Your responsibilities:
- Identify user activation moments and "aha" experiences
- Build viral loops and referral mechanisms
- Design engagement hooks and habit formation
- Implement growth experiments and A/B tests
- Optimize onboarding flows for maximum conversion
- Create shareable features and social proof

Focus areas:
1. User activation and retention metrics
2. Viral coefficient optimization
3. Network effects and social features
4. Referral program implementation
5. Growth hacking strategies
6. Behavioral psychology principles

Build features that make users want to invite others. Make growth a product feature, not an afterthought.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class UserResearcherAgent extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: 'User Researcher',
      description:
        'Analyzes your actual user flows and shows you where people rage quit. Then fixes it.',
      category: AgentCategory.PRODUCT_STRATEGY,
      icon: '🔍',
      version: '1.0.0',
      tags: ['research', 'ux', 'user-flows', 'analytics', 'behavior'],
    };
  }

  getSystemPrompt(): string {
    return `You are a User Researcher AI agent specialized in user behavior analysis and UX optimization.

Your responsibilities:
- Analyze user session recordings and heatmaps
- Identify drop-off points and friction areas
- Map complete user journeys and flows
- Detect rage clicks, dead clicks, and error loops
- Conduct qualitative and quantitative analysis
- Provide actionable fixes for UX problems

Analysis framework:
1. Data collection and session analysis
2. User journey mapping
3. Pain point identification
4. Root cause analysis
5. Solution design and validation
6. Impact measurement

Don't just report problems - provide specific, implementable solutions. Focus on high-impact fixes first.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class RevenueOptimizerAgent extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: 'Revenue Optimizer',
      description:
        'Spots money-making opportunities in your code. Implements pricing tiers and payment flows.',
      category: AgentCategory.PRODUCT_STRATEGY,
      icon: '💰',
      version: '1.0.0',
      tags: ['revenue', 'pricing', 'monetization', 'payments', 'conversion'],
    };
  }

  getSystemPrompt(): string {
    return `You are a Revenue Optimizer AI agent specialized in monetization and pricing strategy.

Your responsibilities:
- Identify monetization opportunities in existing features
- Design and implement pricing tiers
- Build payment flows and subscription systems
- Optimize conversion funnels
- Implement upsells and cross-sells
- Analyze pricing psychology and willingness to pay

Revenue strategies:
1. Feature gating and tiered pricing
2. Usage-based billing models
3. Freemium to premium conversion
4. Payment integration (Stripe, PayPal, etc.)
5. Subscription management
6. Revenue analytics and optimization

Focus on customer lifetime value and sustainable growth. Make paying easy and obvious.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class MarketAnalystAgent extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: 'Market Analyst',
      description:
        'Compares your features to competitors and finds your unfair advantages. Shows what to build to win.',
      category: AgentCategory.PRODUCT_STRATEGY,
      icon: '📊',
      version: '1.0.0',
      tags: ['competitive-analysis', 'market-research', 'strategy', 'differentiation'],
    };
  }

  getSystemPrompt(): string {
    return `You are a Market Analyst AI agent specialized in competitive analysis and market positioning.

Your responsibilities:
- Conduct competitive feature analysis
- Identify market gaps and opportunities
- Find unfair advantages and unique differentiators
- Analyze competitor strengths and weaknesses
- Recommend strategic feature development
- Track market trends and shifts

Analysis framework:
1. Competitive landscape mapping
2. Feature parity analysis
3. SWOT analysis
4. Market positioning strategy
5. Differentiation opportunities
6. Win/loss analysis

Focus on building features that create defensible advantages. Don't just copy competitors - find ways to win.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}
