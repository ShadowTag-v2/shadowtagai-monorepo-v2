/**
 * Master Agent Framework - Multi-Agent Workflow Example
 *
 * This example demonstrates how to orchestrate multiple agents
 * in a coordinated workflow for complex tasks.
 */

import { query } from '@anthropic-ai/claude-agent-sdk';
import testRunnerTool from '../agents/coding/tools/test-runner.js';
import searchTool from '../agents/research/tools/search.js';
import synthesisTool from '../agents/research/tools/synthesis.js';

/**
 * Workflow 1: Research → Design → Implementation
 *
 * Complete product development workflow using multiple agents:
 * 1. Research Agent: Market research and competitive analysis
 * 2. Analysis Agent: Requirements analysis
 * 3. Coding Agent: Implementation
 * 4. Deployment Agent: Production deployment
 */
async function productDevelopmentWorkflow() {
  console.log('=== Product Development Workflow ===\n');

  // Step 1: Market Research (Research Agent - Business Persona)
  console.log('Step 1: Market Research...');
  const marketResearch = await query({
    prompt: `Research the market for a new AI-powered code review tool:

    Analyze:
    1. Market size and growth
    2. Competitor analysis (GitHub Copilot, Tabnine, etc.)
    3. Customer pain points
    4. Pricing strategies
    5. Differentiation opportunities`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/research/personas/business.md',
      },
      tools: [searchTool, synthesisTool],
      temperature: 0.5,
    },
  });

  console.log('Market research completed.\n');

  // Step 2: Technical Feasibility (Research Agent - Technical Persona)
  console.log('Step 2: Technical Feasibility Analysis...');
  const techFeasibility = await query({
    prompt: `Based on the market research, evaluate technical approaches for building an AI code review tool:

    Market findings: ${JSON.stringify(marketResearch).slice(0, 500)}...

    Analyze:
    1. Technology stack options
    2. AI model selection (fine-tuned vs. pre-trained)
    3. Architecture patterns
    4. Integration requirements (GitHub, GitLab, etc.)
    5. Performance and scalability considerations`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/research/personas/technical.md',
      },
      tools: [searchTool, synthesisTool],
      temperature: 0.4,
    },
  });

  console.log('Technical feasibility analysis completed.\n');

  // Step 3: Backend Implementation (Coding Agent - Backend Persona)
  console.log('Step 3: Backend Implementation...');
  const backendCode = await query({
    prompt: `Implement the core backend service for the AI code review tool:

    Technical requirements: ${JSON.stringify(techFeasibility).slice(0, 500)}...

    Create:
    1. FastAPI application structure
    2. GitHub webhook integration
    3. Code analysis service
    4. AI model integration (Claude API)
    5. Database models (PostgreSQL)
    6. Authentication and API keys
    7. Unit tests with pytest
    8. API documentation`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/coding/personas/backend-dev.md',
      },
      tools: [testRunnerTool],
      temperature: 0.3,
    },
  });

  console.log('Backend implementation completed.\n');

  // Step 4: Frontend Implementation (Coding Agent - Frontend Persona)
  console.log('Step 4: Frontend Implementation...');
  const frontendCode = await query({
    prompt: `Create a dashboard for the AI code review tool:

    Requirements:
    1. React + TypeScript + Tailwind CSS
    2. Repository connection page
    3. Review results dashboard
    4. Settings and configuration
    5. Real-time updates (WebSocket)
    6. Responsive design
    7. Component tests`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/coding/personas/frontend-dev.md',
      },
      tools: [testRunnerTool],
      temperature: 0.4,
    },
  });

  console.log('Frontend implementation completed.\n');

  // Step 5: Infrastructure Setup (Coding Agent - DevOps Persona)
  console.log('Step 5: Infrastructure and Deployment...');
  const infrastructure = await query({
    prompt: `Set up production infrastructure for the code review tool:

    Create:
    1. Docker containers for backend and frontend
    2. Kubernetes deployment manifests
    3. CI/CD pipeline (GitHub Actions)
    4. Infrastructure as Code (Terraform for AWS)
    5. Monitoring (Prometheus + Grafana)
    6. Logging (ELK stack)
    7. Auto-scaling configuration`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/coding/personas/devops.md',
      },
      temperature: 0.3,
    },
  });

  console.log('Infrastructure setup completed.\n');

  return {
    marketResearch,
    techFeasibility,
    backendCode,
    frontendCode,
    infrastructure,
  };
}

/**
 * Workflow 2: Bug Investigation and Fix
 *
 * Coordinated workflow for investigating and fixing production bugs:
 * 1. Research Agent: Search for similar issues and solutions
 * 2. Coding Agent: Implement fix
 * 3. Coding Agent: Create tests
 * 4. Deployment Agent: Deploy fix
 */
async function bugFixWorkflow(bugDescription: string) {
  console.log('=== Bug Fix Workflow ===\n');
  console.log(`Bug: ${bugDescription}\n`);

  // Step 1: Research similar issues
  console.log('Step 1: Researching similar issues...');
  const research = await query({
    prompt: `Research this production bug and find similar issues:

    Bug: ${bugDescription}

    Search for:
    1. Similar issues in Stack Overflow
    2. GitHub issues in similar projects
    3. Known vulnerabilities or CVEs
    4. Best practices for fixing this type of bug`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/research/personas/technical.md',
      },
      tools: [searchTool, synthesisTool],
      temperature: 0.4,
    },
  });

  console.log('Research completed.\n');

  // Step 2: Implement fix
  console.log('Step 2: Implementing fix...');
  const fix = await query({
    prompt: `Based on the research, implement a fix for this bug:

    Bug: ${bugDescription}

    Research findings: ${JSON.stringify(research).slice(0, 500)}...

    Provide:
    1. Root cause analysis
    2. Fix implementation
    3. Unit tests for the fix
    4. Integration tests
    5. Documentation update`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/coding/personas/backend-dev.md',
      },
      tools: [testRunnerTool],
      temperature: 0.3,
    },
  });

  console.log('Fix implemented.\n');

  // Step 3: Run tests
  console.log('Step 3: Running tests...');
  const testResults = await testRunnerTool.execute({
    framework: 'jest',
    path: './tests',
    coverage: true,
    verbose: true,
  });

  console.log('Tests completed:', testResults.metadata);

  return {
    research,
    fix,
    testResults,
  };
}

/**
 * Workflow 3: Documentation Generation
 *
 * Generate comprehensive documentation using multiple agents:
 * 1. Research Agent: Gather context and best practices
 * 2. Coding Agent: Analyze code and generate API docs
 * 3. Research Agent: Create user-facing documentation
 */
async function documentationWorkflow(projectPath: string) {
  console.log('=== Documentation Generation Workflow ===\n');

  // Step 1: Research documentation best practices
  console.log('Step 1: Researching documentation best practices...');
  const bestPractices = await query({
    prompt: `Research best practices for technical documentation:

    Focus on:
    1. API documentation standards
    2. User guide structure
    3. Code documentation (JSDoc/TSDoc)
    4. README best practices
    5. Architecture documentation`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/research/personas/technical.md',
      },
      tools: [searchTool, synthesisTool],
      temperature: 0.4,
    },
  });

  console.log('Best practices research completed.\n');

  // Step 2: Generate API documentation
  console.log('Step 2: Generating API documentation...');
  const apiDocs = await query({
    prompt: `Generate comprehensive API documentation for the project at: ${projectPath}

    Include:
    1. OpenAPI/Swagger specification
    2. Endpoint descriptions
    3. Request/response examples
    4. Authentication documentation
    5. Error codes and handling
    6. Rate limiting information`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/coding/personas/backend-dev.md',
      },
      temperature: 0.3,
    },
  });

  console.log('API documentation generated.\n');

  // Step 3: Create user guide
  console.log('Step 3: Creating user guide...');
  const userGuide = await query({
    prompt: `Create a comprehensive user guide:

    Best practices: ${JSON.stringify(bestPractices).slice(0, 300)}...
    API docs: ${JSON.stringify(apiDocs).slice(0, 300)}...

    Include:
    1. Getting started guide
    2. Tutorials and examples
    3. Configuration guide
    4. Troubleshooting
    5. FAQ`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/research/personas/technical.md',
      },
      temperature: 0.5,
    },
  });

  console.log('User guide created.\n');

  return {
    bestPractices,
    apiDocs,
    userGuide,
  };
}

/**
 * Workflow 4: Performance Optimization Pipeline
 *
 * End-to-end performance optimization:
 * 1. Research Agent: Research optimization techniques
 * 2. Coding Agent: Profile and identify bottlenecks
 * 3. Coding Agent: Implement optimizations
 * 4. Coding Agent: Benchmark and validate
 */
async function performanceOptimizationWorkflow(serviceName: string) {
  console.log('=== Performance Optimization Workflow ===\n');

  // Step 1: Research optimization techniques
  console.log('Step 1: Researching optimization techniques...');
  const research = await query({
    prompt: `Research performance optimization techniques for: ${serviceName}

    Focus on:
    1. Database query optimization
    2. Caching strategies
    3. Code-level optimizations
    4. Infrastructure scaling
    5. Monitoring and profiling tools`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/research/personas/technical.md',
      },
      tools: [searchTool, synthesisTool],
      temperature: 0.4,
    },
  });

  console.log('Research completed.\n');

  // Step 2: Profile and identify bottlenecks
  console.log('Step 2: Profiling application...');
  const profiling = await query({
    prompt: `Set up profiling for ${serviceName}:

    Create:
    1. Performance profiling setup
    2. Load testing scripts
    3. Database query analysis
    4. Memory profiling
    5. Identify top 10 bottlenecks`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/coding/personas/backend-dev.md',
      },
      temperature: 0.3,
    },
  });

  console.log('Profiling completed.\n');

  // Step 3: Implement optimizations
  console.log('Step 3: Implementing optimizations...');
  const optimizations = await query({
    prompt: `Implement optimizations based on profiling:

    Research: ${JSON.stringify(research).slice(0, 300)}...
    Bottlenecks: ${JSON.stringify(profiling).slice(0, 300)}...

    Provide:
    1. Optimized code
    2. Caching implementation
    3. Database index creation
    4. Connection pooling
    5. Before/after benchmarks`,

    options: {
      systemPrompt: {
        type: 'file',
        path: './agents/coding/personas/backend-dev.md',
      },
      temperature: 0.3,
    },
  });

  console.log('Optimizations implemented.\n');

  return {
    research,
    profiling,
    optimizations,
  };
}

/**
 * Main execution
 */
async function main() {
  console.log('Master Agent Framework - Multi-Agent Workflow Examples\n');
  console.log('='.repeat(70));

  try {
    // Example 1: Full product development
    console.log('\n\nWorkflow 1: Product Development\n');
    const _productResult = await productDevelopmentWorkflow();
    console.log('Product development workflow completed!');

    // Example 2: Bug fix workflow
    console.log('\n\nWorkflow 2: Bug Fix\n');
    const _bugResult = await bugFixWorkflow(
      'Memory leak in WebSocket connections causing server crashes after 24 hours',
    );
    console.log('Bug fix workflow completed!');

    // Example 3: Documentation generation
    console.log('\n\nWorkflow 3: Documentation Generation\n');
    const _docsResult = await documentationWorkflow('./src');
    console.log('Documentation workflow completed!');

    // Example 4: Performance optimization
    console.log('\n\nWorkflow 4: Performance Optimization\n');
    const _perfResult = await performanceOptimizationWorkflow('User Authentication Service');
    console.log('Performance optimization workflow completed!');

    console.log(`\n${'='.repeat(70)}`);
    console.log('\nAll workflows completed successfully!');
    console.log('\nResults summary:');
    console.log('- Product development: Complete');
    console.log('- Bug fix: Implemented and tested');
    console.log('- Documentation: Generated');
    console.log('- Performance: Optimized');
  } catch (_error) {
    process.exit(1);
  }
}

// Run workflows if this file is executed directly
if (require.main === module) {
  main();
}

export {
  bugFixWorkflow,
  documentationWorkflow,
  performanceOptimizationWorkflow,
  productDevelopmentWorkflow,
};
