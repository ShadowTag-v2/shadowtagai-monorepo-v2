import { SystemArchitect } from '../src/agents/system-architect';

/**
 * Example usage of the System Architect agent
 *
 * Before running:
 * 1. Set your ANTHROPIC_API_KEY environment variable
 * 2. Compile TypeScript: npm run build
 * 3. Run: node dist/examples/system-architect-example.js
 */

async function main() {
  // Create a System Architect agent instance
  const architect = new SystemArchitect({
    apiKey: process.env.ANTHROPIC_API_KEY,
  });

  console.log('=== System Architect Agent Examples ===\n');

  // Example 1: Design a new system
  console.log('1. Designing a new system architecture...');
  const systemDesign = await architect.designSystem({
    projectType: 'FastAPI microservices',
    scalability: 'high',
    teamSize: 8,
    specificRequirements: `
      - Handle 10,000 requests per second
      - Support multiple data sources (PostgreSQL, Redis, MongoDB)
      - Require async task processing
      - Need real-time notifications
      - Must be cloud-native (AWS)
    `,
  });
  console.log(systemDesign);
  console.log('\n---\n');

  // Example 2: Create a refactoring plan
  console.log('2. Creating a refactoring plan...');
  const refactoringPlan = await architect.createRefactoringPlan({
    description: 'Legacy FastAPI monolith with 50k lines of code',
    currentIssues: [
      'All routes in a single main.py file',
      'No separation between business logic and API handlers',
      'Direct database queries in route handlers',
      'No dependency injection',
      'Minimal test coverage (15%)',
      'Circular dependencies between modules',
    ],
    goals: [
      'Implement clean architecture',
      'Achieve 80% test coverage',
      'Separate into distinct modules',
      'Add proper dependency injection',
      'Improve performance by 50%',
    ],
  });
  console.log(refactoringPlan);
  console.log('\n---\n');

  // Example 3: Assess technical debt
  console.log('3. Assessing technical debt...');
  const debtAssessment = await architect.assessTechnicalDebt([
    'No API versioning strategy',
    'Hardcoded configuration values',
    'Missing error handling in 60% of endpoints',
    'No rate limiting',
    'Direct SQL queries without ORM',
    'No logging or monitoring',
    'Synchronous I/O blocking the event loop',
  ]);
  console.log(debtAssessment);
  console.log('\n---\n');

  // Example 4: Suggest design patterns
  console.log('4. Suggesting design patterns for a specific problem...');
  const patternSuggestions = await architect.suggestPatterns(
    'Managing database connections and transactions across multiple services',
    'Using FastAPI with SQLAlchemy and Alembic migrations',
  );
  console.log(patternSuggestions);
  console.log('\n---\n');

  // Example 5: Review architecture
  console.log('5. Reviewing current codebase architecture...');
  const architectureReview = await architect.reviewArchitecture(process.cwd());
  console.log(architectureReview);
  console.log('\n---\n');

  // Example 6: Custom architecture analysis
  console.log('6. Custom analysis query...');
  const customAnalysis = await architect.analyzeArchitecture(`
    I have a FastAPI application that needs to:
    - Process large file uploads (up to 5GB)
    - Run ML inference on uploaded files
    - Return results in real-time to users
    - Scale to handle 1000 concurrent uploads

    What architecture would you recommend, and how should I structure the code?
  `);
  console.log(customAnalysis);
}

// Run examples
main().catch(console.error);
