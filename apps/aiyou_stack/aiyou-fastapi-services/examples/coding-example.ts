/**
 * Master Agent Framework - Coding Agent Example
 *
 * This example demonstrates how to use the coding agent archetype
 * with different personas and tools for software development tasks.
 */

import { query } from "@anthropic-ai/claude-agent-sdk";
import testRunnerTool from "../agents/coding/tools/test-runner.js";

/**
 * Example 1: Backend Development
 * Using the backend developer persona for API development
 */
async function backendDevelopmentExample() {
  console.log("=== Backend Development Example ===\n");

  const result = await query({
    prompt: `Create a RESTful API endpoint for user management with the following requirements:

    - POST /api/users - Create a new user
    - GET /api/users/:id - Get user by ID
    - PUT /api/users/:id - Update user
    - DELETE /api/users/:id - Delete user

    Requirements:
    - Use FastAPI (Python)
    - Include input validation with Pydantic models
    - Add authentication middleware
    - Include comprehensive error handling
    - Write unit tests using pytest
    - Add API documentation
    - Follow REST best practices`,

    options: {
      systemPrompt: {
        type: "file",
        path: "./agents/coding/personas/backend-dev.md",
      },
      tools: [testRunnerTool],
      settingSources: ["project", "local"],
      temperature: 0.3, // Backend dev uses low temperature for consistency
    },
  });

  console.log("Backend Development Result:");
  console.log(result);
}

/**
 * Example 2: Frontend Development
 * Using the frontend developer persona for UI component creation
 */
async function frontendDevelopmentExample() {
  console.log("\n=== Frontend Development Example ===\n");

  const result = await query({
    prompt: `Create a reusable data table component with the following features:

    - Built with React and TypeScript
    - Sortable columns
    - Filterable rows
    - Pagination
    - Row selection
    - Responsive design (mobile-first)
    - Accessible (WCAG 2.1 compliant)
    - Styled with Tailwind CSS

    Include:
    - Component implementation
    - TypeScript interfaces
    - Unit tests with React Testing Library
    - Storybook stories
    - Usage examples`,

    options: {
      systemPrompt: {
        type: "file",
        path: "./agents/coding/personas/frontend-dev.md",
      },
      tools: [testRunnerTool],
      settingSources: ["project", "local"],
      temperature: 0.4,
    },
  });

  console.log("Frontend Development Result:");
  console.log(result);
}

/**
 * Example 3: DevOps - CI/CD Pipeline
 * Using the DevOps persona for deployment automation
 */
async function devopsPipelineExample() {
  console.log("\n=== DevOps CI/CD Pipeline Example ===\n");

  const result = await query({
    prompt: `Create a complete CI/CD pipeline for a Node.js application:

    Requirements:
    - GitHub Actions workflow
    - Multi-stage build process:
      1. Install dependencies
      2. Run linting (ESLint)
      3. Run tests (Jest) with coverage
      4. Build application
      5. Build Docker image
      6. Deploy to staging (on main branch)
      7. Deploy to production (on release tags)
    - Include environment-specific configurations
    - Add security scanning
    - Implement rollback capability
    - Set up monitoring and alerts

    Also provide:
    - Dockerfile (multi-stage build)
    - docker-compose.yml for local development
    - Kubernetes deployment manifests
    - Terraform for infrastructure`,

    options: {
      systemPrompt: {
        type: "file",
        path: "./agents/coding/personas/devops.md",
      },
      settingSources: ["project", "local"],
      temperature: 0.3,
    },
  });

  console.log("DevOps Pipeline Result:");
  console.log(result);
}

/**
 * Example 4: Code Review
 * Using coding agent for comprehensive code review
 */
async function codeReviewExample() {
  console.log("\n=== Code Review Example ===\n");

  const codeToReview = `
  function getUserData(userId) {
    const user = database.query("SELECT * FROM users WHERE id = " + userId);
    return user;
  }

  async function processPayment(amount, cardNumber) {
    console.log("Processing payment:", cardNumber);
    const result = await paymentGateway.charge(amount, cardNumber);
    return result;
  }
  `;

  const result = await query({
    prompt: `Review the following code and provide feedback:

    ${codeToReview}

    Please analyze:
    1. Security vulnerabilities
    2. Best practices violations
    3. Performance issues
    4. Error handling
    5. Code style and maintainability
    6. Provide specific recommendations with code examples`,

    options: {
      systemPrompt: {
        type: "file",
        path: "./agents/coding/personas/backend-dev.md",
      },
      temperature: 0.3,
    },
  });

  console.log("Code Review Result:");
  console.log(result);
}

/**
 * Example 5: Test Suite Creation
 * Demonstrating automated test generation
 */
async function testSuiteCreationExample() {
  console.log("\n=== Test Suite Creation Example ===\n");

  const result = await query({
    prompt: `Create a comprehensive test suite for an e-commerce shopping cart:

    Cart functionality:
    - Add item to cart
    - Remove item from cart
    - Update item quantity
    - Calculate subtotal
    - Apply discount codes
    - Calculate tax
    - Calculate total

    Create tests for:
    - Unit tests for each function
    - Edge cases (empty cart, invalid quantities, etc.)
    - Integration tests
    - Performance tests
    - Aim for >90% code coverage

    Use pytest for Python or Jest for JavaScript.
    Include fixtures, mocks, and test data.`,

    options: {
      systemPrompt: {
        type: "file",
        path: "./agents/coding/personas/backend-dev.md",
      },
      tools: [testRunnerTool],
      temperature: 0.3,
    },
  });

  console.log("Test Suite Creation Result:");
  console.log(result);

  // Run the generated tests
  console.log("\nRunning tests...");
  const testResult = await testRunnerTool.execute({
    framework: "jest",
    path: "./tests",
    coverage: true,
    verbose: true,
  });

  console.log("Test Results:", testResult);
}

/**
 * Example 6: Refactoring Legacy Code
 * Using coding agent to modernize legacy code
 */
async function refactoringExample() {
  console.log("\n=== Code Refactoring Example ===\n");

  const legacyCode = `
  var app = {
    users: [],
    addUser: function(name, email) {
      var user = {id: this.users.length + 1, name: name, email: email};
      this.users.push(user);
      return user;
    },
    findUser: function(id) {
      for (var i = 0; i < this.users.length; i++) {
        if (this.users[i].id === id) {
          return this.users[i];
        }
      }
      return null;
    }
  };
  `;

  const result = await query({
    prompt: `Refactor this legacy JavaScript code to modern TypeScript:

    ${legacyCode}

    Requirements:
    - Convert to TypeScript with proper types
    - Use modern ES6+ syntax
    - Follow SOLID principles
    - Add error handling
    - Include JSDoc comments
    - Make it testable
    - Maintain backward compatibility`,

    options: {
      systemPrompt: {
        type: "file",
        path: "./agents/coding/personas/backend-dev.md",
      },
      temperature: 0.3,
    },
  });

  console.log("Refactoring Result:");
  console.log(result);
}

/**
 * Example 7: Performance Optimization
 * Using coding agent to optimize code performance
 */
async function performanceOptimizationExample() {
  console.log("\n=== Performance Optimization Example ===\n");

  const result = await query({
    prompt: `Optimize the performance of a slow database query application:

    Current issues:
    - N+1 query problem in user posts endpoint
    - No caching layer
    - Large payload sizes
    - Slow pagination
    - No connection pooling

    Provide:
    1. Optimized database queries
    2. Caching strategy (Redis)
    3. Pagination improvements
    4. Connection pool configuration
    5. Response payload optimization
    6. Before/after performance benchmarks
    7. Monitoring setup`,

    options: {
      systemPrompt: {
        type: "file",
        path: "./agents/coding/personas/backend-dev.md",
      },
      temperature: 0.3,
    },
  });

  console.log("Performance Optimization Result:");
  console.log(result);
}

/**
 * Main execution
 */
async function main() {
  console.log("Master Agent Framework - Coding Agent Examples\n");
  console.log("=".repeat(60));

  try {
    // Run examples
    await backendDevelopmentExample();
    await frontendDevelopmentExample();
    await devopsPipelineExample();
    await codeReviewExample();
    await testSuiteCreationExample();
    await refactoringExample();
    await performanceOptimizationExample();

    console.log(`\n${"=".repeat(60)}`);
    console.log("\nAll examples completed successfully!");
  } catch (_error) {
    process.exit(1);
  }
}

// Run examples if this file is executed directly
if (require.main === module) {
  main();
}

export {
  backendDevelopmentExample,
  codeReviewExample,
  devopsPipelineExample,
  frontendDevelopmentExample,
  performanceOptimizationExample,
  refactoringExample,
  testSuiteCreationExample,
};
