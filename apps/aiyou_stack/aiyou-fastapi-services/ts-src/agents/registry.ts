/**
 * Agent Registry - Central registry for all Vertex AI Workbench agents
 */

import { type BaseAgent, AgentCategory } from "./base";

// Product Strategy
import {
  ProductStrategistAgent,
  GrowthEngineerAgent,
  UserResearcherAgent,
  RevenueOptimizerAgent,
  MarketAnalystAgent,
} from "./productStrategy";

// Development
import {
  SystemArchitectAgent,
  CodeRefactorerAgent,
  APIBuilderAgent,
  DatabaseExpertAgent,
  IntegrationMasterAgent,
  MobileOptimizerAgent,
  PerformanceEngineerAgent,
  AccessibilityProAgent,
} from "./development";

// Design & UX
import {
  UXOptimizerAgent,
  UIPolisherAgent,
  ContentWriterAgent,
  DesignSystemBuilderAgent,
} from "./designUX";

// Quality & Testing
import {
  TestGeneratorAgent,
  SecurityScannerAgent,
  CodeReviewerAgent,
  LoadTesterAgent,
} from "./qualityTesting";

// Operations
import {
  DeploymentWizardAgent,
  InfrastructureBuilderAgent,
  MonitoringExpertAgent,
  ReleaseManagerAgent,
  CostOptimizerAgent,
} from "./operations";

// Business & Analytics
import {
  AnalyticsEngineerAgent,
  EmailAutomatorAgent,
  SupportBuilderAgent,
  ComplianceExpertAgent,
  SEOMasterAgent,
  CommunityFeaturesAgent,
  LandingPageOptimizerAgent,
} from "./businessAnalytics";

// AI & Innovation
import {
  AIIntegrationExpertAgent,
  AutomationBuilderAgent,
  InnovationLabAgent,
} from "./aiInnovation";

// Vertex AI
import {
  VertexModelDeployerAgent,
  NotebookOptimizerAgent,
  BigQueryIntegrationAgent,
  AutoMLBuilderAgent,
  FeatureStoreManagerAgent,
  MLPipelineEngineerAgent,
  ModelMonitoringAgent,
  VertexEndpointsManagerAgent,
  TrainingJobOptimizerAgent,
  HyperparameterTunerAgent,
} from "./vertexAI";

// Prompt Engineering
import {
  PromptAdaptation,
  GeminiPromptOptimizer,
  PNKLNStackAnalyzer,
  PromptQualityAuditor,
  EthicalCrawlerAuditor,
} from "./promptEngineering";

// Claude Code
import {
  ClaudeCodeSessionOptimizer,
  HookAndSkillDesigner,
  MCPServerIntegration,
  SlashCommandBuilder,
  ClaudeCodeWorkflowArchitect,
} from "./claudeCode";

/**
 * Type definition for agent constructor
 */
type AgentConstructor = new () => BaseAgent;

/**
 * Central registry for all agents
 */
export class AgentRegistry {
  private static agents: Map<string, AgentConstructor> = new Map([
    // Product Strategy (5 agents)
    ["product_strategist", ProductStrategistAgent],
    ["growth_engineer", GrowthEngineerAgent],
    ["user_researcher", UserResearcherAgent],
    ["revenue_optimizer", RevenueOptimizerAgent],
    ["market_analyst", MarketAnalystAgent],

    // Development (8 agents)
    ["system_architect", SystemArchitectAgent],
    ["code_refactorer", CodeRefactorerAgent],
    ["api_builder", APIBuilderAgent],
    ["database_expert", DatabaseExpertAgent],
    ["integration_master", IntegrationMasterAgent],
    ["mobile_optimizer", MobileOptimizerAgent],
    ["performance_engineer", PerformanceEngineerAgent],
    ["accessibility_pro", AccessibilityProAgent],

    // Design & UX (4 agents)
    ["ux_optimizer", UXOptimizerAgent],
    ["ui_polisher", UIPolisherAgent],
    ["content_writer", ContentWriterAgent],
    ["design_system_builder", DesignSystemBuilderAgent],

    // Quality & Testing (4 agents)
    ["test_generator", TestGeneratorAgent],
    ["security_scanner", SecurityScannerAgent],
    ["code_reviewer", CodeReviewerAgent],
    ["load_tester", LoadTesterAgent],

    // Operations (5 agents)
    ["deployment_wizard", DeploymentWizardAgent],
    ["infrastructure_builder", InfrastructureBuilderAgent],
    ["monitoring_expert", MonitoringExpertAgent],
    ["release_manager", ReleaseManagerAgent],
    ["cost_optimizer", CostOptimizerAgent],

    // Business & Analytics (7 agents)
    ["analytics_engineer", AnalyticsEngineerAgent],
    ["email_automator", EmailAutomatorAgent],
    ["support_builder", SupportBuilderAgent],
    ["compliance_expert", ComplianceExpertAgent],
    ["seo_master", SEOMasterAgent],
    ["community_features", CommunityFeaturesAgent],
    ["landing_page_optimizer", LandingPageOptimizerAgent],

    // AI & Innovation (3 agents)
    ["ai_integration_expert", AIIntegrationExpertAgent],
    ["automation_builder", AutomationBuilderAgent],
    ["innovation_lab", InnovationLabAgent],

    // Vertex AI (10 agents)
    ["vertex_model_deployer", VertexModelDeployerAgent],
    ["notebook_optimizer", NotebookOptimizerAgent],
    ["bigquery_integration", BigQueryIntegrationAgent],
    ["automl_builder", AutoMLBuilderAgent],
    ["feature_store_manager", FeatureStoreManagerAgent],
    ["ml_pipeline_engineer", MLPipelineEngineerAgent],
    ["model_monitoring", ModelMonitoringAgent],
    ["vertex_endpoints_manager", VertexEndpointsManagerAgent],
    ["training_job_optimizer", TrainingJobOptimizerAgent],
    ["hyperparameter_tuner", HyperparameterTunerAgent],

    // Prompt Engineering (5 agents)
    ["prompt_adaptation", PromptAdaptation],
    ["gemini_prompt_optimizer", GeminiPromptOptimizer],
    ["pnkln_stack_analyzer", PNKLNStackAnalyzer],
    ["prompt_quality_auditor", PromptQualityAuditor],
    ["ethical_crawler_auditor", EthicalCrawlerAuditor],

    // Claude Code (5 agents)
    ["claude_code_session_optimizer", ClaudeCodeSessionOptimizer],
    ["hook_and_skill_designer", HookAndSkillDesigner],
    ["mcp_server_integration", MCPServerIntegration],
    ["slash_command_builder", SlashCommandBuilder],
    ["claude_code_workflow_architect", ClaudeCodeWorkflowArchitect],
  ]);

  /**
   * Get an agent instance by ID
   */
  static getAgent(agentId: string): BaseAgent | null {
    const AgentClass = AgentRegistry.agents.get(agentId);
    return AgentClass ? new AgentClass() : null;
  }

  /**
   * Get all agent instances
   */
  static getAllAgents(): BaseAgent[] {
    return Array.from(AgentRegistry.agents.values()).map((AgentClass) => new AgentClass());
  }

  /**
   * Get all agents in a specific category
   */
  static getAgentsByCategory(category: AgentCategory): BaseAgent[] {
    return AgentRegistry.getAllAgents().filter((agent) => agent.metadata.category === category);
  }

  /**
   * Get all agent IDs
   */
  static getAgentIds(): string[] {
    return Array.from(AgentRegistry.agents.keys());
  }

  /**
   * Get all categories
   */
  static getCategories(): string[] {
    return Object.values(AgentCategory);
  }

  /**
   * Search agents by name, description, or tags
   */
  static searchAgents(query: string): BaseAgent[] {
    const lowerQuery = query.toLowerCase();
    return AgentRegistry.getAllAgents().filter((agent) => {
      return (
        agent.metadata.name.toLowerCase().includes(lowerQuery) ||
        agent.metadata.description.toLowerCase().includes(lowerQuery) ||
        agent.metadata.tags.some((tag) => tag.toLowerCase().includes(lowerQuery))
      );
    });
  }

  /**
   * Get total number of agents
   */
  static getAgentCount(): number {
    return AgentRegistry.agents.size;
  }

  /**
   * Get statistics about agents
   */
  static getStats(): Record<string, any> {
    const stats: Record<string, any> = {
      total: AgentRegistry.getAgentCount(),
      by_category: {},
    };

    for (const category of Object.values(AgentCategory)) {
      const count = AgentRegistry.getAgentsByCategory(category).length;
      if (count > 0) {
        stats.by_category[category] = count;
      }
    }

    return stats;
  }

  /**
   * Get agent with ID for response
   */
  static getAgentWithId(agentId: string): { id: string; agent: BaseAgent } | null {
    const agent = AgentRegistry.getAgent(agentId);
    return agent ? { id: agentId, agent } : null;
  }

  /**
   * Get all agents with their IDs
   */
  static getAllAgentsWithIds(): Array<{ id: string; agent: BaseAgent }> {
    return Array.from(AgentRegistry.agents.keys()).map((id) => ({
      id,
      agent: AgentRegistry.getAgent(id)!,
    }));
  }
}
