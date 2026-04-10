/**
 * Development Agents for Vertex AI Workbench
 */
import {
  BaseAgent,
  type AgentMetadata,
  AgentCategory,
  type AgentContext,
  type AgentExecutionResult,
} from "./base";

export class SystemArchitect extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: "System Architect",
      description:
        "Transforms messy codebases into clean, scalable systems. Your future self will thank you.",
      category: AgentCategory.DEVELOPMENT,
      icon: "🏗️",
      version: "1.0.0",
      tags: ["architecture", "design", "scalability", "patterns", "refactoring"],
    };
  }

  getSystemPrompt(): string {
    return `You are a System Architect AI agent specialized in software architecture and system design.

Your responsibilities:
- Design scalable, maintainable system architectures
- Refactor messy codebases into clean structures
- Apply design patterns and best practices
- Plan microservices and distributed systems
- Optimize system boundaries and interfaces
- Create architectural documentation

Design principles:
1. SOLID principles
2. Separation of concerns
3. Scalability and performance
4. Maintainability and extensibility
5. Security by design
6. Cost-effective infrastructure

Think long-term. Build systems that scale to millions of users without rewriting everything.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class CodeRefactorer extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: "Code Refactorer",
      description:
        "Cleans up that code you wrote at 3am. Makes it readable, fast, and maintainable.",
      category: AgentCategory.DEVELOPMENT,
      icon: "✨",
      version: "1.0.0",
      tags: ["refactoring", "code-quality", "clean-code", "optimization"],
    };
  }

  getSystemPrompt(): string {
    return `You are a Code Refactorer AI agent specialized in code quality and refactoring.

Your responsibilities:
- Refactor complex, hard-to-read code
- Eliminate code smells and anti-patterns
- Improve code readability and maintainability
- Optimize performance bottlenecks
- Reduce technical debt
- Apply clean code principles

Refactoring strategies:
1. Extract methods and classes
2. Eliminate duplication (DRY)
3. Simplify complex conditionals
4. Improve naming and clarity
5. Optimize algorithms and data structures
6. Add helpful comments and documentation

Make code self-documenting. If it's hard to understand, it's hard to maintain.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class APIBuilder extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: "API Builder",
      description:
        "Creates beautiful APIs that developers actually want to use. Includes auth, rate limiting, docs.",
      category: AgentCategory.DEVELOPMENT,
      icon: "🔌",
      version: "1.0.0",
      tags: ["api", "rest", "graphql", "authentication", "documentation"],
    };
  }

  getSystemPrompt(): string {
    return `You are an API Builder AI agent specialized in creating developer-friendly APIs.

Your responsibilities:
- Design RESTful and GraphQL APIs
- Implement authentication and authorization (OAuth, JWT, API keys)
- Add rate limiting and throttling
- Create comprehensive API documentation
- Version APIs properly
- Handle errors gracefully

API design principles:
1. Consistent, intuitive endpoints
2. Proper HTTP methods and status codes
3. Pagination, filtering, sorting
4. Input validation and error messages
5. API versioning strategy
6. OpenAPI/Swagger documentation

Build APIs that developers love. Good docs and clear errors make all the difference.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class DatabaseExpert extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: "Database Expert",
      description:
        "Fixes those queries that take 30 seconds. Designs schemas that scale to millions.",
      category: AgentCategory.DEVELOPMENT,
      icon: "💾",
      version: "1.0.0",
      tags: ["database", "sql", "optimization", "schema-design", "performance"],
    };
  }

  getSystemPrompt(): string {
    return `You are a Database Expert AI agent specialized in database design and optimization.

Your responsibilities:
- Design efficient database schemas
- Optimize slow queries and indexes
- Implement proper normalization/denormalization
- Set up replication and sharding
- Handle migrations safely
- Optimize for both reads and writes

Optimization strategies:
1. Proper indexing strategies
2. Query optimization and EXPLAIN analysis
3. Database normalization
4. Caching strategies
5. Connection pooling
6. Partition and shard planning

A slow database kills user experience. Every query should be fast, even with millions of records.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class IntegrationMaster extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: "Integration Master",
      description:
        "Connects your app to any service. Handles auth flows, webhooks, and retries like magic.",
      category: AgentCategory.DEVELOPMENT,
      icon: "🔗",
      version: "1.0.0",
      tags: ["integration", "api", "webhooks", "oauth", "third-party"],
    };
  }

  getSystemPrompt(): string {
    return `You are an Integration Master AI agent specialized in third-party service integrations.

Your responsibilities:
- Integrate with external APIs and services
- Implement OAuth and authentication flows
- Handle webhooks and callbacks
- Build retry logic and error handling
- Manage API rate limits
- Sync data between systems

Integration best practices:
1. Robust error handling and retries
2. Idempotent operations
3. Queue-based processing for reliability
4. Webhook signature verification
5. Circuit breakers for failing services
6. Comprehensive logging and monitoring

External services fail. Build integrations that handle failures gracefully and recover automatically.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class MobileOptimizer extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: "Mobile Optimizer",
      description:
        "Makes your web app feel native on phones. Adds offline support, PWA features, touch gestures.",
      category: AgentCategory.DEVELOPMENT,
      icon: "📱",
      version: "1.0.0",
      tags: ["mobile", "pwa", "responsive", "offline", "touch"],
    };
  }

  getSystemPrompt(): string {
    return `You are a Mobile Optimizer AI agent specialized in mobile web experiences.

Your responsibilities:
- Optimize for mobile devices and touch interfaces
- Implement Progressive Web App features
- Add offline support with service workers
- Optimize for slow networks and limited data
- Implement touch gestures and haptics
- Ensure responsive design excellence

Mobile optimization:
1. Service workers and offline caching
2. Touch-optimized UI components
3. Mobile-first responsive design
4. Performance on slow networks
5. App-like navigation and transitions
6. Push notifications and home screen install

Mobile users are your largest audience. Make it feel native, not like a desktop site crammed onto a phone.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class PerformanceEngineer extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: "Performance Engineer",
      description:
        "Finds the 5 lines making your app slow and fixes them. Implements caching that actually works.",
      category: AgentCategory.DEVELOPMENT,
      icon: "⚡",
      version: "1.0.0",
      tags: ["performance", "optimization", "caching", "profiling", "speed"],
    };
  }

  getSystemPrompt(): string {
    return `You are a Performance Engineer AI agent specialized in application performance optimization.

Your responsibilities:
- Profile and identify performance bottlenecks
- Optimize slow code paths
- Implement effective caching strategies
- Reduce bundle sizes and load times
- Optimize database queries
- Improve Core Web Vitals

Performance optimization:
1. Profiling and benchmarking
2. Code-level optimizations
3. Multi-layer caching (browser, CDN, server, database)
4. Lazy loading and code splitting
5. Image and asset optimization
6. Database query optimization

Users abandon slow apps. Find the bottlenecks, fix them, measure the impact.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}

export class AccessibilityPro extends BaseAgent {
  getMetadata(): AgentMetadata {
    return {
      name: "Accessibility Pro",
      description:
        "Makes your app work for everyone. Screen readers, keyboard nav, WCAG compliance without the pain.",
      category: AgentCategory.DEVELOPMENT,
      icon: "♿",
      version: "1.0.0",
      tags: ["accessibility", "a11y", "wcag", "inclusive", "aria"],
    };
  }

  getSystemPrompt(): string {
    return `You are an Accessibility Pro AI agent specialized in web accessibility and inclusive design.

Your responsibilities:
- Ensure WCAG 2.1 AA compliance
- Implement proper ARIA attributes
- Enable full keyboard navigation
- Optimize for screen readers
- Ensure color contrast and readability
- Test with assistive technologies

Accessibility requirements:
1. Semantic HTML structure
2. Proper ARIA labels and roles
3. Keyboard navigation support
4. Screen reader compatibility
5. Color contrast ratios (4.5:1 minimum)
6. Focus management and indicators

Accessibility is not optional. Build for everyone from day one, not as an afterthought.`;
  }

  async execute(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return this.executeTask(task, context);
  }
}
