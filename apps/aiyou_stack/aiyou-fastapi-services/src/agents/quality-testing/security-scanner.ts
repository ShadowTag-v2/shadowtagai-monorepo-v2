/**
 * Security Scanner Agent
 * Identifies and fixes security vulnerabilities
 */

import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from "../../types/agent.types";
import { BaseAgent } from "../../utils/base-agent";

export class SecurityScannerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "security-scanner",
    name: "Security Scanner",
    category: "quality-testing",
    description:
      "Finds vulnerabilities before hackers do. Implements auth, validation, and data protection.",
    tagline: "Security auditing and vulnerability remediation",
    capabilities: ["analysis", "implementation"],
    tags: ["security", "vulnerabilities", "owasp", "auth", "validation", "encryption"],
    difficulty: "advanced",
    estimatedTime: "3-6 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Security Scanner Expert specializing in application security and OWASP Top 10.

Your expertise:
1. OWASP Top 10 vulnerabilities (injection, XSS, auth, etc.)
2. Input validation and sanitization
3. Authentication and authorization
4. Secrets management
5. Security headers and HTTPS

Security priorities:
- SQL injection prevention (parameterized queries)
- XSS prevention (output encoding, CSP)
- CSRF protection (tokens, SameSite cookies)
- Authentication (proper password hashing, JWT security)
- Authorization (role-based, attribute-based)
- Secrets (never commit, use env vars/vaults)
- Dependencies (audit and update regularly)

Security is not optional. Build it in from the start.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep", "Bash", "Edit"],
    optional: ["Write", "WebFetch"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Security Audit",
        description: "Scan for vulnerabilities",
        action: "Check OWASP Top 10, dependencies",
      },
      {
        name: "Input Validation",
        description: "Add input validation",
        action: "Sanitize and validate all inputs",
      },
      {
        name: "Authentication",
        description: "Secure authentication",
        action: "Implement proper auth, password hashing",
      },
      {
        name: "Authorization",
        description: "Add authorization checks",
        action: "Implement RBAC, verify permissions",
      },
      {
        name: "Security Headers",
        description: "Configure security headers",
        action: "Add CSP, HSTS, X-Frame-Options",
      },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow["steps"][0],
    context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    result.recommendations?.push(`Execute: ${step.description}`);
  }
}
