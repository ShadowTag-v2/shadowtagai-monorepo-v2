import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from "../../types/agent.types";
import { BaseAgent } from "../../utils/base-agent";

export class SEOMasterAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "seo-master",
    name: "SEO Master",
    category: "business-analytics",
    description:
      "Makes Google love your site. Meta tags, schema markup, sitemaps, Core Web Vitals.",
    tagline: "SEO optimization and search visibility",
    capabilities: ["implementation", "optimization"],
    tags: ["seo", "meta-tags", "schema", "sitemap", "web-vitals"],
    difficulty: "intermediate",
    estimatedTime: "2-3 hours",
  };
  prompt: AgentPromptTemplate = {
    system: `You are an SEO Master specializing in technical SEO and search optimization. Implement meta tags, Open Graph, schema markup, sitemaps, optimize Core Web Vitals.`,
  };
  tools: AgentTools = { required: ["Read", "Write", "Edit"], optional: ["Bash"] };
  workflow: AgentWorkflow = {
    steps: [
      {
        name: "SEO Audit",
        description: "Audit current SEO",
        action: "Analyze meta tags, performance, indexing",
      },
      {
        name: "Meta Tags",
        description: "Add meta tags",
        action: "Implement title, description, OG tags",
      },
      {
        name: "Schema Markup",
        description: "Add structured data",
        action: "Implement JSON-LD schema",
      },
      { name: "Sitemap", description: "Generate sitemap", action: "Create XML sitemap" },
      {
        name: "Performance",
        description: "Optimize Core Web Vitals",
        action: "Improve LCP, FID, CLS",
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
