#!/usr/bin/env node

/**
 * PNKLN Analyzer - Gemini 2.0 Pro Integration
 *
 * Utility for analyzing PNKLN Core Stack™ components using Gemini 2.0 Pro.
 * Supports both Judge 6 (validation) and Gemini Ingestion Layer (collection) analyses.
 *
 * Usage:
 *   node pnkln-analyzer.js <component> <command> [options]
 *
 * Components:
 *   ingestion    - Gemini Ingestion Layer
 *   Cor.Claude_Code_6       - Judge 6 Validation System
 *
 * Commands:
 *   analyze      - Run Gemini analysis on component
 *   prepare      - Prepare documentation for analysis
 *   report       - Generate analysis report from results
 *   compare      - Compare two analysis results
 */

const fs = require('fs').promises;
const path = require('path');

// Configuration
const CONFIG = {
  promptsDir: 'docs/pnkln-analysis',
  outputDir: 'analysis-results',
  metricsConfig: 'docs/pnkln-analysis/metrics-config.yaml',

  components: {
    ingestion: {
      name: 'Gemini Ingestion Layer',
      promptFile: 'gemini-ingestion-layer-prompt.md',
      confidenceTarget: 60,
      type: 'collection',
      docsRequired: [
        'architecture-diagram.png',
        'pipeline-config.yaml',
        'source-definitions.json',
        'ethical-compliance-policy.md',
        'cost-breakdown.xlsx',
      ],
    },
    Cor.Claude_Code_6: {
      name: 'Judge 6',
      promptFile: 'judge-six-prompt.md',
      confidenceTarget: 70,
      type: 'validation',
      docsRequired: [
        'judge_six.py',
        'architecture-specs.md',
        'atp-5-19-compliance.pdf',
        'jr-validation-rules.yaml',
        'production-metrics-30d.csv',
      ],
    },
  },
};

/**
 * Load prompt template for a component
 */
async function loadPrompt(component) {
  const config = CONFIG.components[component];
  if (!config) {
    throw new Error(`Unknown component: ${component}`);
  }

  const promptPath = path.join(CONFIG.promptsDir, config.promptFile);
  const content = await fs.readFile(promptPath, 'utf-8');

  // Extract the actual prompt from markdown (skip frontmatter/headers)
  const promptMatch = content.match(/```markdown\n([\s\S]*?)\n```/);
  if (!promptMatch) {
    throw new Error(`Could not extract prompt from ${promptPath}`);
  }

  return {
    prompt: promptMatch[1],
    config,
    component,
  };
}

/**
 * Check if required documentation is available
 */
async function checkDocumentation(component, docsDir = '.') {
  const config = CONFIG.components[component];
  const missing = [];
  const found = [];

  for (const doc of config.docsRequired) {
    const docPath = path.join(docsDir, doc);
    try {
      await fs.access(docPath);
      found.push({ name: doc, path: docPath, status: 'found' });
    } catch (err) {
      missing.push({ name: doc, status: 'missing' });
    }
  }

  return { found, missing, complete: missing.length === 0 };
}

/**
 * Prepare analysis by validating documentation
 */
async function prepareAnalysis(component, docsDir) {
  console.log(`\n📋 Preparing ${CONFIG.components[component].name} Analysis\n`);

  const check = await checkDocumentation(component, docsDir);

  console.log('Required Documentation:\n');

  if (check.found.length > 0) {
    console.log('✅ Found:');
    check.found.forEach((doc) => {
      console.log(`   - ${doc.name}`);
      console.log(`     ${doc.path}`);
    });
    console.log();
  }

  if (check.missing.length > 0) {
    console.log('❌ Missing:');
    check.missing.forEach((doc) => {
      console.log(`   - ${doc.name}`);
    });
    console.log();
  }

  const config = CONFIG.components[component];
  console.log('Analysis Configuration:');
  console.log(`  Component: ${config.name}`);
  console.log(`  Type: ${config.type}`);
  console.log(`  Confidence Target: ≥${config.confidenceTarget}%`);
  console.log(`  Prompt Template: ${config.promptFile}\n`);

  if (!check.complete) {
    console.log(
      '⚠️  Warning: Missing required documentation. Analysis may have lower confidence.\n',
    );
    return { ready: false, check };
  }

  console.log('✅ Ready for analysis!\n');
  return { ready: true, check };
}

/**
 * Generate analysis instructions for Gemini 2.0 Pro
 */
async function generateAnalysisInstructions(component, docsDir) {
  const { prompt, config } = await loadPrompt(component);
  const { found } = await checkDocumentation(component, docsDir);

  console.log(`\n🤖 Gemini 2.0 Pro Analysis Instructions\n`);
  console.log('='.repeat(60));
  console.log(`Component: ${config.name}`);
  console.log(`Confidence Target: ≥${config.confidenceTarget}%`);
  console.log('='.repeat(60));
  console.log();

  console.log('📄 Documents to Upload:\n');
  found.forEach((doc, i) => {
    console.log(`   ${i + 1}. ${doc.name}`);
    console.log(`      Path: ${doc.path}`);
  });
  console.log();

  console.log('📝 Prompt Template:\n');
  console.log('-'.repeat(60));
  console.log(prompt);
  console.log('-'.repeat(60));
  console.log();

  console.log('🔧 Python/Node.js Integration:\n');
  console.log('```python');
  console.log('import google.generativeai as genai');
  console.log();
  console.log("genai.configure(api_key='YOUR_API_KEY')");
  console.log("model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')");
  console.log();
  console.log('# Upload documents');
  console.log('files = [');
  found.forEach((doc) => {
    console.log(`    genai.upload_file('${doc.path}'),`);
  });
  console.log(']');
  console.log();
  console.log('# Run analysis');
  console.log('response = model.generate_content([prompt, *files])');
  console.log('print(response.text)');
  console.log('```\n');

  // Save to file
  const outputPath = path.join(CONFIG.outputDir, `${component}-analysis-instructions.md`);
  await fs.mkdir(CONFIG.outputDir, { recursive: true });

  const instructionsContent = `# ${config.name} - Gemini Analysis Instructions

Generated: ${new Date().toISOString()}

## Configuration

- **Component**: ${config.name}
- **Type**: ${config.type}
- **Confidence Target**: ≥${config.confidenceTarget}%
- **Prompt Template**: ${config.promptFile}

## Documents to Upload

${found.map((doc, i) => `${i + 1}. \`${doc.name}\` - ${doc.path}`).join('\n')}

## Prompt

\`\`\`markdown
${prompt}
\`\`\`

## Python Integration Example

\`\`\`python
import google.generativeai as genai

genai.configure(api_key='YOUR_API_KEY')
model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

# Upload documents
files = [
${found.map((doc) => `    genai.upload_file('${doc.path}'),`).join('\n')}
]

# Run analysis
response = model.generate_content([
    prompt,  # The prompt from above
    *files
])

print(response.text)

# Save results
with open('${component}-analysis-result.md', 'w') as f:
    f.write(response.text)
\`\`\`

## Node.js Integration Example

\`\`\`javascript
const { GoogleGenerativeAI } = require('@google/generative-ai');
const fs = require('fs').promises;

const genai = new GoogleGenerativeAI('YOUR_API_KEY');
const model = genai.getGenerativeModel({ model: 'gemini-3.1-flash-lite-preview' });

async function runAnalysis() {
  // Upload files
  const files = await Promise.all([
${found.map((doc) => `    genai.uploadFile('${doc.path}'),`).join('\n')}
  ]);

  // Run analysis
  const result = await model.generateContent([prompt, ...files]);
  const response = await result.response;
  const text = response.text();

  // Save results
  await fs.writeFile('${component}-analysis-result.md', text);
  console.log('Analysis complete!');
}

runAnalysis();
\`\`\`

## Expected Output

The Gemini analysis should produce:

1. **Executive Summary** (1 page)
   - Overall health assessment (1-5 scale)
   - Top 3 strengths
   - Top 3 risks/concerns
   - Go/no-go recommendation

2. **Detailed Findings** (10-20 pages)
   - Analysis by dimension (architecture, performance, cost, etc.)
   - Confidence scores per finding
   - Evidence references
   - Prioritized recommendations

3. **Metrics Summary Tables**
   - Quantitative data
   - Performance targets vs. actuals
   - Cost breakdowns
   - Quality metrics

4. **Visualization Suggestions**
   - Charts and graphs to create
   - Dashboard recommendations

5. **Open Questions**
   - Documentation gaps
   - Low-confidence areas
   - Validation needed

## Next Steps

1. Review and validate Gemini's analysis
2. Create visualizations as suggested
3. Prioritize recommendations by ROI
4. Create engineering tickets for actions
5. Update documentation based on insights
6. Schedule follow-up analysis if needed
`;

  await fs.writeFile(outputPath, instructionsContent);
  console.log(`✅ Instructions saved to: ${outputPath}\n`);

  return { prompt, config, found, instructionsPath: outputPath };
}

/**
 * Compare two analysis results
 */
async function compareAnalyses(file1, file2) {
  console.log('\n📊 Comparing Analysis Results\n');

  const [content1, content2] = await Promise.all([
    fs.readFile(file1, 'utf-8'),
    fs.readFile(file2, 'utf-8'),
  ]);

  console.log('Comparison Report:\n');
  console.log(`File 1: ${file1}`);
  console.log(`  Length: ${content1.length} characters`);
  console.log(`  Lines: ${content1.split('\n').length}`);
  console.log();
  console.log(`File 2: ${file2}`);
  console.log(`  Length: ${content2.length} characters`);
  console.log(`  Lines: ${content2.split('\n').length}`);
  console.log();

  // Extract sections for comparison
  const extractSections = (content) => {
    const sections = {};
    const regex = /^##\s+(.+)$/gm;
    let match;
    while ((match = regex.exec(content)) !== null) {
      sections[match[1]] = true;
    }
    return Object.keys(sections);
  };

  const sections1 = extractSections(content1);
  const sections2 = extractSections(content2);

  console.log('Sections Comparison:\n');
  console.log('Common Sections:');
  const common = sections1.filter((s) => sections2.includes(s));
  common.forEach((s) => console.log(`  ✓ ${s}`));
  console.log();

  const only1 = sections1.filter((s) => !sections2.includes(s));
  if (only1.length > 0) {
    console.log(`Only in ${path.basename(file1)}:`);
    only1.forEach((s) => console.log(`  - ${s}`));
    console.log();
  }

  const only2 = sections2.filter((s) => !sections1.includes(s));
  if (only2.length > 0) {
    console.log(`Only in ${path.basename(file2)}:`);
    only2.forEach((s) => console.log(`  - ${s}`));
    console.log();
  }

  console.log('\n✅ Comparison complete!\n');
}

/**
 * Main CLI handler
 */
async function main() {
  const [, , component, command, ...args] = process.argv;

  if (!component) {
    console.log(`
PNKLN Analyzer - Gemini 2.0 Pro Integration

Usage:
  node pnkln-analyzer.js <component> <command> [options]
  node pnkln-analyzer.js list                          (list all components)

Components:
  ingestion    Gemini Ingestion Layer (collection pipeline)
  Cor.Claude_Code_6       Judge 6 (validation system)

Commands:
  prepare [docs-dir]              Validate documentation for analysis
  analyze [docs-dir]              Generate Gemini analysis instructions
  compare <file1> <file2>         Compare two analysis results
  list                            List available components

Examples:
  node pnkln-analyzer.js list
  node pnkln-analyzer.js ingestion prepare ./docs
  node pnkln-analyzer.js Cor.Claude_Code_6 analyze ./production-data
  node pnkln-analyzer.js compare result1.md result2.md

For more information, see: docs/pnkln-analysis/README.md
    `);
    process.exit(0);
  }

  try {
    // Handle component-less commands
    if (component === 'list') {
      console.log('\nAvailable Components:\n');
      Object.entries(CONFIG.components).forEach(([key, config]) => {
        console.log(`  ${key.padEnd(12)} - ${config.name}`);
        console.log(`  ${''.padEnd(12)}   Type: ${config.type}`);
        console.log(`  ${''.padEnd(12)}   Confidence: ≥${config.confidenceTarget}%`);
        console.log();
      });
      return;
    }

    if (!command) {
      console.error(`Error: No command specified for component '${component}'`);
      console.log('Run without arguments for usage information.');
      process.exit(1);
    }

    switch (command) {
      case 'prepare': {
        const docsDir = args[0] || '.';
        await prepareAnalysis(component, docsDir);
        break;
      }

      case 'analyze': {
        const analysisDir = args[0] || '.';
        await generateAnalysisInstructions(component, analysisDir);
        break;
      }

      case 'compare':
        if (args.length < 2) {
          console.error('Error: compare requires two file paths');
          process.exit(1);
        }
        await compareAnalyses(args[0], args[1]);
        break;

      default:
        console.error(`Unknown command: ${command}`);
        console.log('Run without arguments for usage information.');
        process.exit(1);
    }
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = {
  loadPrompt,
  checkDocumentation,
  prepareAnalysis,
  generateAnalysisInstructions,
  compareAnalyses,
};
