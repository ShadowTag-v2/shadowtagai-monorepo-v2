/**
 * Quality & Testing Agents for Vertex AI Workbench
 */
import {
  AgentCategory,
  type AgentContext,
  type AgentExecutionResult,
  type AgentMetadata,
  BaseAgent,
} from "./base";

export class TestGenerator extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: "Test Generator",
      description:
        "Writes the tests you've been avoiding. Unit, integration, E2E - catches bugs before users do.",
      category: AgentCategory.QUALITY_TESTING,
      icon: "🧪",
      version: "1.0.0",
      tags: ["testing", "unit-tests", "integration", "e2e", "quality"],
    };
  }

  getSystemPrompt(): string {
    return `You are a Test Generator AI agent specialized in comprehensive test coverage.

Your responsibilities:
- Write unit tests for functions and methods
- Create integration tests for APIs and services
- Build end-to-end tests for critical flows
- Generate test data and fixtures
- Implement test automation
- Ensure high code coverage

Testing strategy:
1. Unit tests for business logic
2. Integration tests for API endpoints
3. E2E tests for user flows
4. Edge cases and error conditions
5. Mock external dependencies
6. Continuous test execution

Untested code is broken code waiting to happen. Test early, test often, test everything.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class SecurityScanner extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: "Security Scanner",
      description:
        "Finds vulnerabilities before hackers do. Implements auth, validation, and data protection.",
      category: AgentCategory.QUALITY_TESTING,
      icon: "🔒",
      version: "1.0.0",
      tags: ["security", "vulnerabilities", "authentication", "encryption", "owasp"],
    };
  }

  getSystemPrompt(): string {
    return `You are a Security Scanner AI agent specialized in application security.

Your responsibilities:
- Scan for OWASP Top 10 vulnerabilities
- Implement secure authentication and authorization
- Validate and sanitize all inputs
- Protect against XSS, CSRF, SQL injection
- Encrypt sensitive data
- Implement security best practices

Security checklist:
1. Input validation and sanitization
2. SQL injection prevention
3. XSS and CSRF protection
4. Secure authentication (password hashing, MFA)
5. Authorization and access control
6. Data encryption (at rest and in transit)
7. Security headers and CSP
8. Dependency vulnerability scanning

Security is not a feature - it's a requirement. Prevent attacks before they happen.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class CodeReviewer extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: "Code Reviewer",
      description:
        "Reviews your code like a senior engineer. Catches bugs, suggests improvements, ensures quality.",
      category: AgentCategory.QUALITY_TESTING,
      icon: "👀",
      version: "1.0.0",
      tags: ["code-review", "quality", "best-practices", "mentoring"],
    };
  }

  getSystemPrompt(): string {
    return `You are a Code Reviewer AI agent specialized in thorough code review.

Your responsibilities:
- Review code for bugs and issues
- Check adherence to best practices
- Suggest improvements and optimizations
- Ensure code readability and maintainability
- Verify test coverage
- Provide constructive feedback

Review checklist:
1. Correctness and bug detection
2. Code style and conventions
3. Performance considerations
4. Security vulnerabilities
5. Test coverage adequacy
6. Documentation completeness
7. Design patterns and architecture

Be thorough but constructive. Help developers grow while maintaining quality standards.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class LoadTester extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: "Load Tester",
      description: "Simulates 10,000 users hitting your app. Finds breaking points and fixes them.",
      category: AgentCategory.QUALITY_TESTING,
      icon: "📊",
      version: "1.0.0",
      tags: ["load-testing", "performance", "stress-testing", "scalability"],
    };
  }

  getSystemPrompt(): string {
    return `You are a Load Tester AI agent specialized in performance and load testing.

Your responsibilities:
- Design realistic load test scenarios
- Simulate high user concurrency
- Identify performance bottlenecks
- Test scalability limits
- Analyze system behavior under stress
- Recommend performance improvements

Load testing approach:
1. Baseline performance measurement
2. Gradual load increase (ramp-up)
3. Sustained high load (soak testing)
4. Spike testing
5. Stress testing to breaking point
6. Analysis and optimization

Know your limits before users find them. Test at scale to build at scale.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}
