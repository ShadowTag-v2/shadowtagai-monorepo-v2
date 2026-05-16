# Thread Transfer Package System

**Modular context preservation and restoration for AI session continuity**

## Overview

The Thread Transfer Package System enables seamless handoff of complex AI sessions across threads, instances, or time periods. It captures session state, technical context, risk assessment, and provides structured restart prompts—ensuring no loss of context or momentum.

### Key Features

- **3-Part Structure**: State Summary → Handoff Outline → Restart Prompt
- **Built-in Validation**: Completeness scoring, error detection, quality gates
- **Auto-Critique**: Self-assessment of assumptions, weaknesses, and risks
- **ATP 5-19 Risk Matrix**: Military-grade risk assessment (Probability × Severity)
- **Multiple Formats**: Markdown, JSON, compact (for quick restore)
- **Template System**: Pre-configured packages for common scenarios
- **CLI Tool**: Command-line generation and export

## Quick Start

### Installation

```bash
npm install  # Installs @anthropic-ai/claude-agent-sdk
```

### Basic Usage

```typescript
import { TransferPackageTemplates } from './src/thread-transfer/index.js';

// Generate MCP integration analysis package
const repos = [
  'anthropics/anthropic-quickstarts',
  'modelcontextprotocol/typescript-sdk'
];

const package = TransferPackageTemplates.mcpIntegrationAnalysis(
  'MCP-FORK-20241117',
  repos,
  'BEST'
);

console.log(package.toMarkdown());
```

### CLI Usage

```bash
# MCP integration analysis
node src/thread-transfer/cli.ts mcp \
  -r "anthropics/anthropic-quickstarts,modelcontextprotocol/typescript-sdk" \
  -o transfer.md

# Gemini ingestion layer
node src/thread-transfer/cli.ts gemini \
  -s "YouTube,Twitter,News" \
  -f json \
  -o transfer.json

# Auto-generate thread ID
node src/thread-transfer/cli.ts mcp \
  -r "modelcontextprotocol/servers" \
  --strategy FAST

# Compact format for quick restore
node src/thread-transfer/cli.ts mcp \
  -r "anthropics/courses" \
  -f compact
```

## Architecture

### Part 1: State Summary

Captures:
- **Session Scope**: Domain, objective, thread ID, start date
- **Build Artifacts**: Scripts, configs, code, docs (with ready status)
- **Current State**: Status, blockers, next actions
- **Technical Context**: Architecture, namespaces, metrics, integrations

```typescript
import { StateSummaryBuilder } from './src/thread-transfer/index.js';

const summary = new StateSummaryBuilder()
  .withSessionScope({
    domain: 'MCP Integration',
    objective: 'Validate 40-60% token reduction',
    startDate: '2024-11-17',
    threadId: 'MCP-001'
  })
  .addBuildArtifact({
    type: 'script',
    path: 'fork-repos.sh',
    description: 'Fork 7 AI/MCP repos',
    ready: true,
    dependencies: ['GitHub CLI']
  })
  .setCurrentState(
    'Script ready for execution',
    [],
    ['Execute fork', 'Clone SDK', 'Map to namespaces']
  )
  .withTechnicalContext({
    architecture: ['GKE-native deployment', 'p99≤90ms SLA'],
    namespaces: ['judge-six', 'core-stack'],
    metrics: { 'Token Reduction': '40-60%' }
  })
  .build();
```

### Part 2: Handoff Outline

Captures:
- **Key Parameters**: Configuration values, flags, settings
- **Frameworks Active**: JR Engine, ATP 5-19, Bootstrap constraints
- **Repository Targets**: Org/repo with priority and purpose
- **Objectives**: Immediate (M0), M1-3, M3+
- **Variable Conventions**: Naming and descriptions
- **Open Questions**: Unresolved decisions
- **Risk Flags**: ATP 5-19 matrix (Probability × Severity → Risk Level)

```typescript
import {
  HandoffOutlineBuilder,
  FrameworkPresets,
  RiskAssessment,
  Probability,
  Severity
} from './src/thread-transfer/index.js';

const outline = new HandoffOutlineBuilder()
  .addParameters({
    GH_USER: 'erikcleveland',
    FORK_STRATEGY: 'BEST'
  })
  .withFrameworks(FrameworkPresets.pnklnBootstrap())
  .addRepository({
    org: 'modelcontextprotocol',
    repo: 'typescript-sdk',
    priority: 'PRIMARY',
    purpose: 'Core SDK for integration'
  })
  .setObjectives(
    ['Execute fork', 'Validate claims'],
    ['Map to namespaces'],
    ['Deploy to GKE']
  )
  .addQuestion('Fork to personal vs org?')
  .addRiskFlag(
    RiskAssessment.createRisk(
      'Rate Limits',
      'GitHub API 5000/hr',
      Probability.C,
      Severity.III,
      'Implement backoff'
    )
  )
  .build();
```

### Part 3: Restart Prompt

Captures:
- **Thread ID**: Unique identifier
- **Mission**: High-level goal
- **Current State**: Snapshot of progress
- **Bootstrap Constraints**: Non-negotiable requirements
- **Frameworks Active**: Active decision frameworks
- **Repos**: Target repositories
- **Open Questions**: Unresolved items
- **Resume Point**: Exact continuation instruction

```typescript
import { RestartPromptBuilder } from './src/thread-transfer/index.js';

const prompt = new RestartPromptBuilder()
  .withThreadId('MCP-001')
  .withMission('Validate MCP 40-60% token reduction claims')
  .addStateItem('Script ready, pending strategy selection')
  .addConstraint('p99≤90ms SLA non-negotiable')
  .addFramework('JR Engine: Purpose → Reasons → Brakes')
  .addRepo('modelcontextprotocol/typescript-sdk')
  .addQuestion('Fork to personal vs org?')
  .withResumePoint('Execute fork → analyze SDK')
  .build();
```

### Critique Layer

Auto-generates self-assessment:
- **Assumptions**: What's taken for granted
- **Weaknesses**: Gaps or limitations
- **What Could Be Wrong**: Potential failure modes

```typescript
import { AutoCritique } from './src/thread-transfer/index.js';

const critique = AutoCritique.forMCPIntegration();
// Automatically analyzes and documents:
// - Implicit assumptions
// - Missing context
// - Potential risks
```

## Risk Assessment (ATP 5-19)

Military-grade risk matrix:

| Probability | Severity I | Severity II | Severity III | Severity IV |
|-------------|-----------|------------|--------------|-------------|
| A (Almost Certain) | EH | EH | H | M |
| B (Likely) | EH | H | M | L |
| C (Possible) | H | M | M | L |
| D (Unlikely) | M | M | L | L |
| E (Rare) | M | L | L | L |

**Severity Levels**:
- **I**: Catastrophic (mission failure)
- **II**: Critical (major degradation)
- **III**: Moderate (degraded capability)
- **IV**: Negligible (minimal impact)

**Risk Levels**:
- **EH**: Extremely High (immediate escalation)
- **H**: High (senior review required)
- **M**: Medium (document and monitor)
- **L**: Low (accept and track)

## Bootstrap Constraints (PNKLN)

Default constraints for $0K bootstrap:

```typescript
{
  capital: 0,
  slaP99Ms: 90,           // Judge #6 non-negotiable
  roiMultiple: 3,         // ≥3× return
  roiMonths: 18,          // within 18 months
  ltvCacRatio: 4,         // ≥4:1 LTV:CAC
  ltvCacMonths: 12,       // within 12 months
  targetCompression: {
    from: '50KB',
    to: '487 bytes'       // Semantic compression
  }
}
```

## JR Engine Framework

**Purpose → Reasons → Brakes** decision model:

1. **Purpose**: Does it advance Pnkln/revenue?
2. **Reasons**: Is it defensible? Evidence-based? Scalable?
3. **Brakes**: Is it p99 survivable? Security maintained? ROI viable?

## Templates

### MCP Integration Analysis

```typescript
TransferPackageTemplates.mcpIntegrationAnalysis(
  threadId: string,
  repos: string[],
  strategy: 'BEST' | 'FAST' | 'CHEAP'
)
```

Pre-configured for:
- 7 target repos (Anthropic, MCP, DeepSeek, Qwen, Llama)
- Judge #6 p99≤90ms SLA
- 40-60% token reduction validation
- GKE-native deployment
- 5 namespace architecture

### Gemini Ingestion Layer

```typescript
TransferPackageTemplates.geminiIngestionLayer(
  threadId: string,
  sources: string[]
)
```

Pre-configured for:
- Multi-source intelligence collection
- Ethical compliance model
- Tier classification (1/2/3)
- ~45 min/night runtime
- ~$77/month operational cost

## Output Formats

### Markdown (default)

Full human-readable package with:
- Headers and sections
- Bullet points
- Validation results
- Usage instructions

### JSON

Machine-readable for:
- Programmatic processing
- Database storage
- API integration

### Compact

Quick restore format with:
- Single-line sections
- Minimal whitespace
- Fast scanning

## Validation

Automatic quality checks:

```typescript
const { package, validation } = builder.validate();

console.log(`Completeness: ${validation.completeness}%`);
console.log(`Errors: ${validation.errors.length}`);
console.log(`Warnings: ${validation.warnings.length}`);
```

**Validation Criteria**:
- Thread ID present (20% penalty if missing)
- Mission defined (15% penalty)
- Build artifacts documented (10% penalty)
- Next actions specified (10% penalty)
- Frameworks configured (20% penalty)
- Objectives set (15% penalty)
- Risk flags identified (10% penalty)
- Critique present (15% penalty)

## Examples

See `src/thread-transfer/examples/` for:
- **mcp-integration.ts**: MCP fork analysis examples
- Template usage
- From-scratch building
- JSON export
- Compact format

## Use Cases

1. **Session Handoff**: Transfer to new AI thread/instance
2. **Multi-Day Projects**: Resume complex work after breaks
3. **Team Collaboration**: Share context with other developers
4. **Audit Trail**: Document decision points and context
5. **Risk Documentation**: ATP 5-19 compliance tracking
6. **Milestone Checkpoints**: Save state at key project phases

## Integration

### With Claude Agent SDK

```typescript
import { Agent } from '@anthropic-ai/claude-agent-sdk';
import { TransferPackageBuilder } from './src/thread-transfer/index.js';

// Generate package during agent execution
const package = new TransferPackageBuilder()
  // ... build package
  .build();

// Export for next session
await agent.saveContext(package.toJSON());
```

### With GKE/GCP

```bash
# Export to Cloud Storage
gsutil cp transfer.json gs://pnkln-transfers/mcp-001.json

# Load in new instance
gsutil cp gs://pnkln-transfers/mcp-001.json ./context.json
```

## Best Practices

1. **Generate Early**: Create package at meaningful checkpoints, not just at end
2. **Auto-Critique**: Always use autoCritique() to surface blindspots
3. **Validate Before Export**: Check completeness score before sharing
4. **Version Thread IDs**: Use descriptive IDs (PROJECT-SCOPE-DATE)
5. **Document Blockers**: Always capture what's preventing progress
6. **Risk Assessment**: Apply ATP 5-19 to all non-trivial decisions
7. **Compact for Quick**: Use compact format for immediate restores
8. **JSON for Archive**: Use JSON for long-term storage/retrieval

## API Reference

See TypeScript definitions in:
- `types.ts`: Core interfaces and enums
- `state-summary.ts`: Part 1 builders
- `handoff-outline.ts`: Part 2 builders + risk assessment
- `restart-prompt.ts`: Part 3 builders
- `validation.ts`: Validation and critique
- `package.ts`: Main orchestrator + templates

## License

Part of PNKLN Core Stack™ - AiYou FastAPI Services

## Contributing

Contributions welcome. Follow:
- SOP-A: Upload Triage (2× speed, −90% errors)
- SOP-B: Change & Release (2× cadence, clearer audits)
- SOP-C: Decision Protocol (2× faster, +1.8× robustness)
- SOP-D: Code Review (+2× defect capture)

Bootstrap gates:
- ROI ≥3× (18mo)
- LTV:CAC ≥4:1 (12mo)
- p99 ≤90ms (Judge #6 SLA)
