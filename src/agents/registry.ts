/**
 * Agent Registry
 * Central registry for all available agents
 */

import type { Agent, AgentCategory, AgentRegistry as IAgentRegistry } from "../types/agent.types";
import * as AIInnovation from "./ai-innovation";
import * as BusinessAnalytics from "./business-analytics";
import * as DesignUX from "./design-ux";
import * as Development from "./development";
import * as Operations from "./operations";
// Import all agents
import * as ProductStrategy from "./product-strategy";
import * as QualityTesting from "./quality-testing";

export class AgentRegistry implements IAgentRegistry {
  agents: Map<string, Agent> = new Map();
  categories: Map<AgentCategory, Agent[]> = new Map();

  constructor() {
    this.registerAllAgents();
  }

  private registerAllAgents(): void {
    // Register Product Strategy agents
    this.registerAgent(new ProductStrategy.ProductStrategistAgent());
    this.registerAgent(new ProductStrategy.GrowthEngineerAgent());
    this.registerAgent(new ProductStrategy.UserResearcherAgent());
    this.registerAgent(new ProductStrategy.RevenueOptimizerAgent());
    this.registerAgent(new ProductStrategy.MarketAnalystAgent());

    // Register Development agents
    this.registerAgent(new Development.SystemArchitectAgent());
    this.registerAgent(new Development.CodeRefactorerAgent());
    this.registerAgent(new Development.APIBuilderAgent());
    this.registerAgent(new Development.DatabaseExpertAgent());
    this.registerAgent(new Development.IntegrationMasterAgent());
    this.registerAgent(new Development.MobileOptimizerAgent());
    this.registerAgent(new Development.PerformanceEngineerAgent());
    this.registerAgent(new Development.AccessibilityProAgent());
    this.registerAgent(new Development.MicroservicesArchitectAgent());
    this.registerAgent(new Development.GraphQLExpertAgent());
    this.registerAgent(new Development.StateManagementExpertAgent());

    // Register Design & UX agents
    this.registerAgent(new DesignUX.UXOptimizerAgent());
    this.registerAgent(new DesignUX.UIPolisherAgent());
    this.registerAgent(new DesignUX.ContentWriterAgent());
    this.registerAgent(new DesignUX.DesignSystemBuilderAgent());
    this.registerAgent(new DesignUX.TechnicalWriterAgent());

    // Register Quality & Testing agents
    this.registerAgent(new QualityTesting.TestGeneratorAgent());
    this.registerAgent(new QualityTesting.SecurityScannerAgent());
    this.registerAgent(new QualityTesting.CodeReviewerAgent());
    this.registerAgent(new QualityTesting.LoadTesterAgent());
    this.registerAgent(new QualityTesting.DocumentationGeneratorAgent());

    // Register Operations agents
    this.registerAgent(new Operations.DeploymentWizardAgent());
    this.registerAgent(new Operations.InfrastructureBuilderAgent());
    this.registerAgent(new Operations.MonitoringExpertAgent());
    this.registerAgent(new Operations.ReleaseManagerAgent());
    this.registerAgent(new Operations.CostOptimizerAgent());
    this.registerAgent(new Operations.DevOpsEngineerAgent());
    this.registerAgent(new Operations.DependencyManagerAgent());

    // Register Business & Analytics agents
    this.registerAgent(new BusinessAnalytics.AnalyticsEngineerAgent());
    this.registerAgent(new BusinessAnalytics.EmailAutomatorAgent());
    this.registerAgent(new BusinessAnalytics.SupportBuilderAgent());
    this.registerAgent(new BusinessAnalytics.ComplianceExpertAgent());
    this.registerAgent(new BusinessAnalytics.SEOMasterAgent());
    this.registerAgent(new BusinessAnalytics.CommunityFeaturesAgent());
    this.registerAgent(new BusinessAnalytics.LandingPageOptimizerAgent());
    this.registerAgent(new BusinessAnalytics.ABTestingSpecialistAgent());

    // Register AI & Innovation agents
    this.registerAgent(new AIInnovation.AIIntegrationExpertAgent());
    this.registerAgent(new AIInnovation.AutomationBuilderAgent());
    this.registerAgent(new AIInnovation.InnovationLabAgent());
  }

  registerAgent(agent: Agent): void {
    this.agents.set(agent.metadata.id, agent);

    if (!this.categories.has(agent.metadata.category)) {
      this.categories.set(agent.metadata.category, []);
    }
    this.categories.get(agent.metadata.category)?.push(agent);
  }

  getAgent(id: string): Agent | undefined {
    return this.agents.get(id);
  }

  getAgentsByCategory(category: AgentCategory): Agent[] {
    return this.categories.get(category) || [];
  }

  searchAgents(query: string): Agent[] {
    const lowerQuery = query.toLowerCase();
    return Array.from(this.agents.values()).filter((agent) => {
      return (
        agent.metadata.name.toLowerCase().includes(lowerQuery) ||
        agent.metadata.description.toLowerCase().includes(lowerQuery) ||
        agent.metadata.tags.some((tag) => tag.toLowerCase().includes(lowerQuery))
      );
    });
  }

  getAllAgents(): Agent[] {
    return Array.from(this.agents.values());
  }

  getAgentCount(): number {
    return this.agents.size;
  }

  getCategoryCount(): number {
    return this.categories.size;
  }

  listCategories(): AgentCategory[] {
    return Array.from(this.categories.keys());
  }
}

// Export singleton instance
export const agentRegistry = new AgentRegistry();
