/**
 * Basic usage example for Vertex AI Agents
 * Demonstrates how to load and use agents with Vertex AI
 */

const { VertexAI } = require('@google-cloud/vertexai');
const { loadAgents, getAgent, searchAgents, getAgentsByCategory } = require('../index.js');

// Initialize Vertex AI
const projectId = process.env.VERTEX_AI_PROJECT_ID || 'your-project-id';
const location = process.env.VERTEX_AI_LOCATION || 'us-central1';

const vertexAI = new VertexAI({
  project: projectId,
  location: location,
});

/**
 * Example 1: Using a single agent
 */
async function exampleUseSingleAgent() {
  console.log('='.repeat(60));
  console.log('Example 1: Using a single agent');
  console.log('='.repeat(60));

  // Get the System Architect agent
  const agent = getAgent('system-architect');

  console.log(`\nAgent: ${agent.name}`);
  console.log(`Description: ${agent.description}`);
  console.log(`\nCapabilities:`);
  agent.capabilities.forEach((cap) => console.log(`  - ${cap}`));

  // Create a generative model with the agent's configuration
  const model = vertexAI.getGenerativeModel({
    model: agent.model,
    systemInstruction: agent.systemPrompt,
    generationConfig: {
      temperature: agent.temperature,
      maxOutputTokens: agent.maxTokens,
    },
  });

  // Generate a response
  const userPrompt = 'Analyze our codebase architecture and suggest improvements';

  const result = await model.generateContent(userPrompt);
  const response = result.response;

  console.log(`\nUser: ${userPrompt}`);
  console.log(`\nAgent Response:\n${response.text()}`);
}

/**
 * Example 2: Searching for agents
 */
async function exampleSearchAgents() {
  console.log('\n' + '='.repeat(60));
  console.log('Example 2: Searching for agents');
  console.log('='.repeat(60));

  // Search for agents related to "API"
  const results = searchAgents('API');

  console.log(`\nFound ${results.length} agents related to 'API':`);
  results.forEach((agent) => {
    console.log(`\n  ${agent.icon} ${agent.name}`);
    console.log(`     ${agent.description}`);
    console.log(`     Category: ${agent.category}`);
  });
}

/**
 * Example 3: Browse agents by category
 */
async function exampleBrowseByCategory() {
  console.log('\n' + '='.repeat(60));
  console.log('Example 3: Browse agents by category');
  console.log('='.repeat(60));

  // Get all development agents
  const devAgents = getAgentsByCategory('development');

  console.log(`\nDevelopment Category (${devAgents.length} agents):`);
  devAgents.forEach((agent) => {
    console.log(`\n  ${agent.icon} ${agent.name}`);
    console.log(`     ${agent.description}`);
    console.log(`     Example: ${agent.examplePrompts[0]}`);
  });
}

/**
 * Example 4: Multi-agent workflow
 */
async function exampleMultiAgentWorkflow() {
  console.log('\n' + '='.repeat(60));
  console.log('Example 4: Multi-agent workflow');
  console.log('='.repeat(60));

  // Step 1: Use System Architect to design
  const architect = getAgent('system-architect');
  console.log(`\n1. ${architect.name}: Designing system architecture...`);

  // Step 2: Use Code Refactorer to clean code
  const refactorer = getAgent('code-refactorer');
  console.log(`2. ${refactorer.name}: Refactoring code...`);

  // Step 3: Use Test Generator to add tests
  const tester = getAgent('test-generator');
  console.log(`3. ${tester.name}: Generating tests...`);

  // Step 4: Use Security Scanner to audit
  const security = getAgent('security-scanner');
  console.log(`4. ${security.name}: Scanning for vulnerabilities...`);

  console.log('\nMulti-agent workflow completed!');
}

/**
 * Example 5: Using an agent with conversation context
 */
async function exampleAgentWithContext() {
  console.log('\n' + '='.repeat(60));
  console.log('Example 5: Using an agent with conversation context');
  console.log('='.repeat(60));

  // Get the Code Mentor agent
  const mentor = getAgent('code-mentor');

  // Create model with system instruction
  const model = vertexAI.getGenerativeModel({
    model: mentor.model,
    systemInstruction: mentor.systemPrompt,
    generationConfig: {
      temperature: mentor.temperature,
      maxOutputTokens: mentor.maxTokens,
    },
  });

  // Start a chat session
  const chat = model.startChat();

  // Multi-turn conversation
  const conversations = [
    'What are SOLID principles?',
    'Can you give me an example of the Single Responsibility Principle?',
    'How would I refactor this code to follow SRP?',
  ];

  console.log(`\n${mentor.icon} ${mentor.name} - Teaching Session\n`);

  for (const userMessage of conversations) {
    const result = await chat.sendMessage(userMessage);
    const response = result.response;

    console.log(`Student: ${userMessage}`);
    console.log(`Mentor: ${response.text()}\n`);
  }
}

/**
 * Main function - Run all examples
 */
async function main() {
  try {
    // Load agents first
    await loadAgents();

    // Run examples
    await exampleUseSingleAgent();
    await exampleSearchAgents();
    await exampleBrowseByCategory();
    await exampleMultiAgentWorkflow();
    await exampleAgentWithContext();
  } catch (error) {
    console.error('\nError running examples:', error.message);
    console.log('Make sure you have:');
    console.log('  1. Set VERTEX_AI_PROJECT_ID environment variable');
    console.log('  2. Authenticated with Google Cloud');
    console.log('  3. Installed required dependencies');
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  exampleUseSingleAgent,
  exampleSearchAgents,
  exampleBrowseByCategory,
  exampleMultiAgentWorkflow,
  exampleAgentWithContext,
};
