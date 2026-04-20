#!/usr/bin/env node

/**
 * Gemini Ingestion Layer Analysis Runner
 *
 * This script prepares and executes the comprehensive analysis of the
 * Gemini Ingestion Layer using Gemini 2.0 Pro or other LLMs.
 *
 * Usage:
 *   node scripts/analyze-ingestion-layer.js [options]
 *
 * Options:
 *   --provider <gemini|claude|openai>  LLM provider (default: gemini)
 *   --output <file>                    Output file path
 *   --dry-run                          Show combined prompt without running analysis
 */

const fs = require('fs');
const path = require('path');

// ============================================================================
// Configuration
// ============================================================================

const CONFIG = {
  promptPath: path.join(
    __dirname,
    '..',
    'prompts',
    'analysis',
    'gemini-ingestion-layer-analysis.md',
  ),
  inputsDir: path.join(__dirname, '..', 'analysis-inputs', 'ingestion-layer'),
  outputDir: path.join(__dirname, '..', 'analysis-outputs'),
  defaultProvider: 'gemini',
};

// ============================================================================
// Command Line Parsing
// ============================================================================

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    provider: CONFIG.defaultProvider,
    output: null,
    dryRun: false,
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--provider' && args[i + 1]) {
      options.provider = args[++i];
    } else if (arg === '--output' && args[i + 1]) {
      options.output = args[++i];
    } else if (arg === '--dry-run') {
      options.dryRun = true;
    } else if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    }
  }

  return options;
}

function printHelp() {
  console.log(`
Gemini Ingestion Layer Analysis Runner

Usage:
  node scripts/analyze-ingestion-layer.js [options]

Options:
  --provider <gemini|claude|openai>  LLM provider (default: gemini)
  --output <file>                    Output file path (default: auto-generated)
  --dry-run                          Show combined prompt without running analysis
  --help, -h                         Show this help message

Examples:
  # Dry run (show combined prompt)
  node scripts/analyze-ingestion-layer.js --dry-run

  # Run with Gemini (requires GEMINI_API_KEY environment variable)
  GEMINI_API_KEY=xxx node scripts/analyze-ingestion-layer.js --provider gemini

  # Run with Claude Code
  node scripts/analyze-ingestion-layer.js --provider claude

Environment Variables:
  GEMINI_API_KEY     Gemini API key (for --provider gemini)
  ANTHROPIC_API_KEY  Claude API key (for --provider claude)
  OPENAI_API_KEY     OpenAI API key (for --provider openai)
`);
}

// ============================================================================
// File Loading
// ============================================================================

function loadPrompt() {
  console.log(`📄 Loading prompt from: ${CONFIG.promptPath}`);

  if (!fs.existsSync(CONFIG.promptPath)) {
    console.error(`❌ Error: Prompt file not found at ${CONFIG.promptPath}`);
    process.exit(1);
  }

  return fs.readFileSync(CONFIG.promptPath, 'utf-8');
}

function loadSupportingDocuments() {
  console.log(`📂 Loading supporting documents from: ${CONFIG.inputsDir}`);

  if (!fs.existsSync(CONFIG.inputsDir)) {
    console.warn(`⚠️  Warning: Inputs directory not found. Creating empty directory.`);
    fs.mkdirSync(CONFIG.inputsDir, { recursive: true });
    return '';
  }

  const files = fs.readdirSync(CONFIG.inputsDir);

  if (files.length === 0) {
    console.warn(`⚠️  Warning: No supporting documents found in ${CONFIG.inputsDir}`);
    console.warn(`   Add specification files (YAML, Markdown, etc.) to improve analysis quality.`);
    return '';
  }

  let combined = '\n\n## Supporting Documents\n\n';
  combined += '_The following documents were provided to support the analysis:_\n\n';

  for (const file of files) {
    const filePath = path.join(CONFIG.inputsDir, file);
    const stats = fs.statSync(filePath);

    if (!stats.isFile()) continue;

    console.log(`   ├─ ${file} (${(stats.size / 1024).toFixed(2)} KB)`);

    const content = fs.readFileSync(filePath, 'utf-8');
    const extension = path.extname(file).slice(1);

    combined += `### Document: ${file}\n\n`;
    combined += '```' + extension + '\n';
    combined += content;
    combined += '\n```\n\n';
  }

  console.log(`✅ Loaded ${files.length} supporting document(s)`);

  return combined;
}

function combineMaterials(prompt, supportingDocs) {
  const divider = '\n\n' + '='.repeat(80) + '\n\n';
  return prompt + divider + supportingDocs;
}

// ============================================================================
// Analysis Execution
// ============================================================================

async function runAnalysisWithGemini(combinedPrompt) {
  console.log('\n🔮 Running analysis with Gemini 2.0 Pro...\n');

  const apiKey = process.env.GEMINI_API_KEY;

  if (!apiKey) {
    console.error('❌ Error: GEMINI_API_KEY environment variable not set.');
    console.error('   Set it with: export GEMINI_API_KEY=your_key_here');
    process.exit(1);
  }

  // Note: In a real implementation, you would use the @google/generative-ai package
  console.log('ℹ️  To run with Gemini API, install: npm install @google/generative-ai');
  console.log('ℹ️  For now, showing how to use the combined prompt...\n');

  return `
# Analysis Output (Mock)

This is where the Gemini 2.0 Pro analysis results would appear.

To run the actual analysis:

1. Install the Gemini SDK:
   npm install @google/generative-ai

2. Use the following code:

\`\`\`javascript
const { GoogleGenerativeAI } = require('@google/generative-ai');

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-2.0-pro-exp' });

async function runAnalysis(prompt) {
  const result = await model.generateContent(prompt);
  const response = await result.response;
  return response.text();
}

runAnalysis(combinedPrompt).then(console.log);
\`\`\`

3. Or use the Gemini API directly via REST
`;
}

async function runAnalysisWithClaude(combinedPrompt) {
  console.log('\n🤖 Running analysis with Claude Agent SDK...\n');

  try {
    const { query, ClaudeAgentOptions } = require('@anthropic-ai/claude-agent-sdk');

    console.log('ℹ️  Using Claude Code preset for analysis...');

    const messages = [];

    // Stream the analysis
    for await (const message of query(combinedPrompt, {
      systemPrompt: { type: 'preset', preset: 'claude_code' },
      model: 'claude-sonnet-4',
    })) {
      if (message.type === 'text') {
        messages.push(message.text);
        // Stream output to console
        process.stdout.write('.');
      }
    }

    console.log('\n✅ Analysis complete\n');

    return messages.join('');
  } catch (error) {
    console.error('❌ Error running Claude analysis:', error.message);
    console.error('\nMake sure @anthropic-ai/claude-agent-sdk is installed.');
    process.exit(1);
  }
}

async function runAnalysisWithOpenAI(combinedPrompt) {
  console.log('\n🧠 Running analysis with OpenAI GPT-4...\n');

  const apiKey = process.env.OPENAI_API_KEY;

  if (!apiKey) {
    console.error('❌ Error: OPENAI_API_KEY environment variable not set.');
    process.exit(1);
  }

  console.log('ℹ️  To run with OpenAI API, install: npm install openai');
  console.log('ℹ️  For now, showing mock output...\n');

  return `# Analysis Output (Mock - OpenAI)\n\nOpenAI GPT-4 analysis would appear here.`;
}

async function runAnalysis(provider, combinedPrompt) {
  switch (provider) {
    case 'gemini':
      return await runAnalysisWithGemini(combinedPrompt);
    case 'claude':
      return await runAnalysisWithClaude(combinedPrompt);
    case 'openai':
      return await runAnalysisWithOpenAI(combinedPrompt);
    default:
      console.error(`❌ Error: Unknown provider "${provider}"`);
      console.error('   Supported providers: gemini, claude, openai');
      process.exit(1);
  }
}

// ============================================================================
// Output Handling
// ============================================================================

function saveOutput(content, outputPath) {
  // Ensure output directory exists
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }

  // Generate output filename if not provided
  if (!outputPath) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    outputPath = path.join(CONFIG.outputDir, `ingestion-layer-analysis-${timestamp}.md`);
  }

  fs.writeFileSync(outputPath, content, 'utf-8');
  console.log(`\n💾 Analysis saved to: ${outputPath}`);
  console.log(`   File size: ${(Buffer.byteLength(content, 'utf-8') / 1024).toFixed(2)} KB`);
}

// ============================================================================
// Statistics
// ============================================================================

function printStatistics(combinedPrompt) {
  const lines = combinedPrompt.split('\n').length;
  const words = combinedPrompt.split(/\s+/).length;
  const chars = combinedPrompt.length;

  // Rough token estimate (1 token ≈ 4 characters for English text)
  const estimatedTokens = Math.ceil(chars / 4);

  console.log('\n📊 Prompt Statistics:');
  console.log(`   Lines:     ${lines.toLocaleString()}`);
  console.log(`   Words:     ${words.toLocaleString()}`);
  console.log(`   Characters: ${chars.toLocaleString()}`);
  console.log(
    `   Est. Tokens: ${estimatedTokens.toLocaleString()} (~${(chars / 1024).toFixed(2)} KB)`,
  );

  // Cost estimates
  console.log('\n💰 Estimated Analysis Cost:');
  console.log('   Gemini 2.0 Pro:');
  console.log(`     Input:  ${((estimatedTokens / 1000) * 0.001).toFixed(4)} USD`);
  console.log(`     Output: ~0.0030-0.0090 USD (estimated 1K-3K tokens)`);
  console.log(`     Total:  ~0.0040-0.0100 USD per analysis`);
  console.log('\n   Claude Sonnet 4:');
  console.log(`     Input:  ${((estimatedTokens / 1000000) * 3).toFixed(4)} USD`);
  console.log(`     Output: ~0.0450-0.1350 USD (estimated 1K-3K tokens)`);
  console.log(`     Total:  ~0.0500-0.1400 USD per analysis`);
}

// ============================================================================
// Main Execution
// ============================================================================

async function main() {
  console.log('╔══════════════════════════════════════════════════════════╗');
  console.log('║   Gemini Ingestion Layer Analysis Runner                ║');
  console.log('║   PNKLN Core Stack - Pre-Production Analysis            ║');
  console.log('╚══════════════════════════════════════════════════════════╝\n');

  const options = parseArgs();

  console.log(`🔧 Configuration:`);
  console.log(`   Provider:  ${options.provider}`);
  console.log(`   Dry Run:   ${options.dryRun}`);
  console.log(`   Output:    ${options.output || 'auto-generated'}\n`);

  // Load materials
  const prompt = loadPrompt();
  const supportingDocs = loadSupportingDocuments();
  const combinedPrompt = combineMaterials(prompt, supportingDocs);

  // Print statistics
  printStatistics(combinedPrompt);

  // Dry run mode: just save the combined prompt
  if (options.dryRun) {
    console.log('\n🔍 Dry Run Mode: Saving combined prompt for manual review...');
    const dryRunPath = path.join(CONFIG.outputDir, 'combined-prompt-dryrun.md');
    saveOutput(combinedPrompt, dryRunPath);
    console.log(
      '\n✅ Dry run complete. Review the combined prompt and run without --dry-run when ready.',
    );
    return;
  }

  // Run analysis
  console.log(`\n🚀 Starting analysis with ${options.provider}...`);
  const startTime = Date.now();

  const analysisResult = await runAnalysis(options.provider, combinedPrompt);

  const duration = ((Date.now() - startTime) / 1000).toFixed(2);
  console.log(`\n⏱️  Analysis completed in ${duration} seconds`);

  // Save output
  saveOutput(analysisResult, options.output);

  console.log('\n✅ Analysis pipeline complete!');
  console.log('\n📋 Next Steps:');
  console.log('   1. Review the analysis output');
  console.log('   2. Address any "Critical" recommendations before production');
  console.log('   3. Create issues for "Important" and "Strategic" items');
  console.log('   4. Re-run analysis after addressing findings\n');
}

// ============================================================================
// Entry Point
// ============================================================================

main().catch((error) => {
  console.error('\n❌ Fatal error:', error);
  process.exit(1);
});
