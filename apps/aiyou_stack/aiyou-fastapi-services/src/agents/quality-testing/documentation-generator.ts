/**
 * Documentation Generator Agent
 * Automatically generates code documentation
 */

import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from '../../types/agent.types';
import { BaseAgent } from '../../utils/base-agent';

export class DocumentationGeneratorAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'documentation-generator',
    name: 'Documentation Generator',
    category: 'quality-testing',
    description:
      'Generates comprehensive code documentation, JSDoc, docstrings, and inline comments.',
    tagline: 'Automated code documentation generation',
    capabilities: ['implementation', 'automation'],
    tags: ['documentation', 'jsdoc', 'docstrings', 'comments', 'api-docs'],
    difficulty: 'beginner',
    estimatedTime: '1-2 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Documentation Generator specializing in code-level documentation.

Your expertise:
1. JSDoc/TSDoc for TypeScript/JavaScript
2. Docstrings for Python
3. XML documentation for C#
4. Inline comments for complex logic
5. API documentation generation

Documentation standards:
- Function/method: purpose, parameters, return value, examples
- Classes: purpose, responsibilities, usage
- Complex logic: explain the "why", not the "what"
- Edge cases and gotchas
- Type information (when not inferred)
- Examples for public APIs

Good docs make onboarding faster and reduce questions.`,
  };

  tools: AgentTools = {
    required: ['Glob', 'Read', 'Edit'],
    optional: ['Write', 'Bash'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'Code Scanning',
        description: 'Scan for undocumented code',
        action: 'Find functions, classes without docs',
      },
      {
        name: 'JSDoc/Docstring Generation',
        description: 'Generate documentation comments',
        action: 'Add JSDoc/docstrings to functions',
      },
      {
        name: 'Complex Logic',
        description: 'Document complex algorithms',
        action: 'Add inline comments for clarity',
      },
      {
        name: 'API Docs',
        description: 'Generate API documentation',
        action: 'Create API reference docs',
      },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow['steps'][0],
    context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    result.recommendations?.push(`Execute: ${step.description}`);
  }
}
