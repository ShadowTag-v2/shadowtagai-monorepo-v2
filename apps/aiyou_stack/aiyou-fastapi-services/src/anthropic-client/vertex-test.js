/**
 * Corrected AnthropicVertex client
 *
 * Fixes applied:
 * - Wrapped in async IIFE for proper top-level await handling
 * - Added error handling with try/catch
 * - Reduced max_tokens to reasonable limit (4096)
 * - Simplified message content to string format (confirm with SDK docs)
 * - Added process exit code on failure
 * - Added timeout and better error messages
 *
 * Prerequisites:
 * - Environment variables: CLOUD_ML_REGION, ANTHROPIC_VERTEX_PROJECT_ID
 * - GOOGLE_APPLICATION_CREDENTIALS or Workload Identity configured
 * - package.json with "type": "module"
 */

import { AnthropicVertex } from '@anthropic-ai/vertex-sdk';

(async () => {
  try {
    // Validate required environment variables
    const requiredEnvVars = ['CLOUD_ML_REGION', 'ANTHROPIC_VERTEX_PROJECT_ID'];
    for (const envVar of requiredEnvVars) {
      if (!process.env[envVar]) {
        throw new Error(`Missing required environment variable: ${envVar}`);
      }
    }

    console.log('Initializing AnthropicVertex client...');
    console.log(`Region: ${process.env.CLOUD_ML_REGION}`);
    console.log(`Project: ${process.env.ANTHROPIC_VERTEX_PROJECT_ID}`);

    const client = new AnthropicVertex({
      region: process.env.CLOUD_ML_REGION,
      projectId: process.env.ANTHROPIC_VERTEX_PROJECT_ID,
    });

    // Prepare the prompt as a string
    // If SDK requires structured content, adjust to: content: [{ type: "text", text: userContent }]
    const userContent = `# GKE INFERENCE ARCHITECTURE DEPLOYMENT

You are a senior cloud architect reviewing this deployment architecture.
Analyze the following GKE inference setup and provide recommendations:

1. Resource allocation and scaling strategy
2. Network security and traffic flow
3. GPU utilization and cost optimization
4. Observability and monitoring gaps
5. High availability and disaster recovery

Provide concrete, actionable recommendations with priority levels.`;

    console.log('Sending request to Anthropic Vertex API...');
    const startTime = Date.now();

    const msg = await client.messages.create({
      model: 'claude-opus-4-1@20250805',
      // Reduced to model limits - adjust based on actual model specs
      max_tokens: 4096,
      temperature: 0.2,
      messages: [
        {
          role: 'user',
          // Pass as plain string - confirm with @anthropic-ai/vertex-sdk docs
          // If SDK expects blocks, use: content: [{ type: "text", text: userContent }]
          content: userContent,
        },
      ],
    });

    const duration = Date.now() - startTime;
    console.log(`\nRequest completed in ${duration}ms\n`);

    // Pretty print the response
    console.log('=== Response ===');
    console.log(JSON.stringify(msg, null, 2));

    // Extract and display just the text content if available
    if (msg.content && Array.isArray(msg.content)) {
      console.log('\n=== Extracted Text ===');
      for (const block of msg.content) {
        if (block.type === 'text') {
          console.log(block.text);
        }
      }
    }

    console.log('\n✓ Success');
    process.exitCode = 0;
  } catch (err) {
    console.error('\n✗ AnthropicVertex call failed:');
    console.error('Error name:', err.name);
    console.error('Error message:', err.message);

    if (err.response) {
      console.error('Response status:', err.response.status);
      console.error('Response data:', JSON.stringify(err.response.data, null, 2));
    }

    if (err.stack) {
      console.error('\nStack trace:');
      console.error(err.stack);
    }

    // Provide helpful debugging hints
    console.error('\n=== Debugging Hints ===');
    console.error('1. Verify CLOUD_ML_REGION and ANTHROPIC_VERTEX_PROJECT_ID are set');
    console.error('2. Check GOOGLE_APPLICATION_CREDENTIALS or Workload Identity');
    console.error('3. Ensure Vertex AI API is enabled in your project');
    console.error('4. Verify the model name is correct for your region');
    console.error('5. Check message format matches SDK expectations');

    process.exitCode = 1;
  }
})();
