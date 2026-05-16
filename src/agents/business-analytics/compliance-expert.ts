import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from "../../types/agent.types";
import { BaseAgent } from "../../utils/base-agent";

export class ComplianceExpertAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "compliance-expert",
    name: "Compliance Expert",
    category: "business-analytics",
    description: "Handles GDPR, CCPA, cookies. Keeps you legal without the lawyer bills.",
    tagline: "Legal compliance and data privacy",
    capabilities: ["implementation", "analysis"],
    tags: ["gdpr", "ccpa", "compliance", "privacy", "cookies"],
    difficulty: "intermediate",
    estimatedTime: "2-4 hours",
  };
  prompt: AgentPromptTemplate = {
    system: `You are a Compliance Expert specializing in GDPR, CCPA, and data privacy. Implement cookie banners, privacy policies, data deletion, consent management.`,
  };
  tools: AgentTools = { required: ["Read", "Write", "Edit"], optional: ["Grep"] };
  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Compliance Audit",
        description: "Audit current compliance",
        action: "Identify compliance gaps",
      },
      {
        name: "Cookie Consent",
        description: "Add cookie banner",
        action: "Implement GDPR-compliant consent",
      },
      {
        name: "Privacy Policy",
        description: "Create privacy policy",
        action: "Write privacy documentation",
      },
      {
        name: "Data Rights",
        description: "Implement data rights",
        action: "Add data deletion, export features",
      },
    ],
  };
  protected async executeStep(
    step: AgentWorkflow["steps"][0],
    _context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    result.recommendations?.push(`Execute: ${step.description}`);
  }
}
