"""Agent Registry - Central registry for all Vertex AI Workbench agents"""

from .ai_innovation import AIIntegrationExpertAgent, AutomationBuilderAgent, InnovationLabAgent
from .base import AgentCategory, BaseAgent
from .business_analytics import (
    AnalyticsEngineerAgent,
    CommunityFeaturesAgent,
    ComplianceExpertAgent,
    EmailAutomatorAgent,
    LandingPageOptimizerAgent,
    SEOMasterAgent,
    SupportBuilderAgent,
)
from .claude_code import (
    ClaudeCodeSessionOptimizerAgent,
    ClaudeCodeWorkflowArchitectAgent,
    HookAndSkillDesignerAgent,
    MCPServerIntegrationAgent,
    SlashCommandBuilderAgent,
)
from .design_ux import (
    ContentWriterAgent,
    DesignSystemBuilderAgent,
    UIPolisherAgent,
    UXOptimizerAgent,
)
from .development import (
    AccessibilityProAgent,
    APIBuilderAgent,
    CodeRefactorerAgent,
    DatabaseExpertAgent,
    IntegrationMasterAgent,
    MobileOptimizerAgent,
    PerformanceEngineerAgent,
    SystemArchitectAgent,
)
from .operations import (
    CostOptimizerAgent,
    DeploymentWizardAgent,
    InfrastructureBuilderAgent,
    MonitoringExpertAgent,
    ReleaseManagerAgent,
)

# Import all agents
from .product_strategy import (
    GrowthEngineerAgent,
    MarketAnalystAgent,
    ProductStrategistAgent,
    RevenueOptimizerAgent,
    UserResearcherAgent,
)
from .prompt_engineering import (
    EthicalCrawlerAuditorAgent,
    GeminiPromptOptimizerAgent,
    PNKLNStackAnalyzerAgent,
    PromptAdaptationAgent,
    PromptQualityAuditorAgent,
)
from .quality_testing import (
    CodeReviewerAgent,
    LoadTesterAgent,
    SecurityScannerAgent,
    TestGeneratorAgent,
)
from .vertex_ai import (
    AutoMLBuilderAgent,
    BigQueryIntegrationAgent,
    FeatureStoreManagerAgent,
    HyperparameterTunerAgent,
    MLPipelineEngineerAgent,
    ModelMonitoringAgent,
    NotebookOptimizerAgent,
    TrainingJobOptimizerAgent,
    VertexEndpointsManagerAgent,
    VertexModelDeployerAgent,
)


class AgentRegistry:
    """Central registry for all agents"""

    _agents: dict[str, type[BaseAgent]] = {
        # Product Strategy (5 agents)
        "product_strategist": ProductStrategistAgent,
        "growth_engineer": GrowthEngineerAgent,
        "user_researcher": UserResearcherAgent,
        "revenue_optimizer": RevenueOptimizerAgent,
        "market_analyst": MarketAnalystAgent,
        # Development (8 agents)
        "system_architect": SystemArchitectAgent,
        "code_refactorer": CodeRefactorerAgent,
        "api_builder": APIBuilderAgent,
        "database_expert": DatabaseExpertAgent,
        "integration_master": IntegrationMasterAgent,
        "mobile_optimizer": MobileOptimizerAgent,
        "performance_engineer": PerformanceEngineerAgent,
        "accessibility_pro": AccessibilityProAgent,
        # Design & UX (4 agents)
        "ux_optimizer": UXOptimizerAgent,
        "ui_polisher": UIPolisherAgent,
        "content_writer": ContentWriterAgent,
        "design_system_builder": DesignSystemBuilderAgent,
        # Quality & Testing (4 agents)
        "test_generator": TestGeneratorAgent,
        "security_scanner": SecurityScannerAgent,
        "code_reviewer": CodeReviewerAgent,
        "load_tester": LoadTesterAgent,
        # Operations (5 agents)
        "deployment_wizard": DeploymentWizardAgent,
        "infrastructure_builder": InfrastructureBuilderAgent,
        "monitoring_expert": MonitoringExpertAgent,
        "release_manager": ReleaseManagerAgent,
        "cost_optimizer": CostOptimizerAgent,
        # Business & Analytics (7 agents)
        "analytics_engineer": AnalyticsEngineerAgent,
        "email_automator": EmailAutomatorAgent,
        "support_builder": SupportBuilderAgent,
        "compliance_expert": ComplianceExpertAgent,
        "seo_master": SEOMasterAgent,
        "community_features": CommunityFeaturesAgent,
        "landing_page_optimizer": LandingPageOptimizerAgent,
        # AI & Innovation (3 agents)
        "ai_integration_expert": AIIntegrationExpertAgent,
        "automation_builder": AutomationBuilderAgent,
        "innovation_lab": InnovationLabAgent,
        # Vertex AI (10 agents)
        "vertex_model_deployer": VertexModelDeployerAgent,
        "notebook_optimizer": NotebookOptimizerAgent,
        "bigquery_integration": BigQueryIntegrationAgent,
        "automl_builder": AutoMLBuilderAgent,
        "feature_store_manager": FeatureStoreManagerAgent,
        "ml_pipeline_engineer": MLPipelineEngineerAgent,
        "model_monitoring": ModelMonitoringAgent,
        "vertex_endpoints_manager": VertexEndpointsManagerAgent,
        "training_job_optimizer": TrainingJobOptimizerAgent,
        "hyperparameter_tuner": HyperparameterTunerAgent,
        # Prompt Engineering (5 agents)
        "prompt_adaptation": PromptAdaptationAgent,
        "gemini_prompt_optimizer": GeminiPromptOptimizerAgent,
        "pnkln_stack_analyzer": PNKLNStackAnalyzerAgent,
        "prompt_quality_auditor": PromptQualityAuditorAgent,
        "ethical_crawler_auditor": EthicalCrawlerAuditorAgent,
        # Claude Code (5 agents)
        "claude_code_session_optimizer": ClaudeCodeSessionOptimizerAgent,
        "hook_and_skill_designer": HookAndSkillDesignerAgent,
        "mcp_server_integration": MCPServerIntegrationAgent,
        "slash_command_builder": SlashCommandBuilderAgent,
        "claude_code_workflow_architect": ClaudeCodeWorkflowArchitectAgent,
    }

    @classmethod
    def get_agent(cls, agent_id: str) -> BaseAgent | None:
        """Get an agent instance by ID"""
        agent_class = cls._agents.get(agent_id)
        if agent_class:
            return agent_class()
        return None

    @classmethod
    def get_all_agents(cls) -> list[BaseAgent]:
        """Get all agent instances"""
        return [agent_class() for agent_class in cls._agents.values()]

    @classmethod
    def get_agents_by_category(cls, category: AgentCategory) -> list[BaseAgent]:
        """Get all agents in a specific category"""
        return [agent for agent in cls.get_all_agents() if agent.metadata.category == category]

    @classmethod
    def get_agent_ids(cls) -> list[str]:
        """Get all agent IDs"""
        return list(cls._agents.keys())

    @classmethod
    def get_categories(cls) -> list[str]:
        """Get all agent categories"""
        return [category.value for category in AgentCategory]

    @classmethod
    def search_agents(cls, query: str) -> list[BaseAgent]:
        """Search agents by name, description, or tags"""
        query_lower = query.lower()
        results = []

        for agent in cls.get_all_agents():
            if (
                query_lower in agent.metadata.name.lower()
                or query_lower in agent.metadata.description.lower()
                or any(query_lower in tag.lower() for tag in agent.metadata.tags)
            ):
                results.append(agent)

        return results

    @classmethod
    def get_agent_count(cls) -> int:
        """Get total number of agents"""
        return len(cls._agents)

    @classmethod
    def get_stats(cls) -> dict[str, int]:
        """Get statistics about agents"""
        stats = {"total": cls.get_agent_count(), "by_category": {}}

        for category in AgentCategory:
            count = len(cls.get_agents_by_category(category))
            if count > 0:
                stats["by_category"][category.value] = count

        return stats
