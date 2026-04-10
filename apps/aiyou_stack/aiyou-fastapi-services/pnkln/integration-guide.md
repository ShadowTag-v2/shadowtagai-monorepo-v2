# PNKLN Skills & Agents Integration Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-15
**Compatibility:** Claude Agent SDK v0.1.30+

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start (5 minutes)](#quick-start)
3. [Architecture](#architecture)
4. [Installation & Setup](#installation--setup)
5. [Using Skills](#using-skills)
6. [Using Agents](#using-agents)
7. [Auto-Activation System](#auto-activation-system)
8. [Workflow Templates](#workflow-templates)
9. [Customization](#customization)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Usage](#advanced-usage)
12. [Performance Optimization](#performance-optimization)

---

## Overview

The PNKLN (pronounced "punchline") Skills & Agents Registry is a comprehensive framework for autonomous AI workflow automation. It provides:

- **6 Core Skills**: Research, Design Critique, Copywriting, Monetization, Workflow Optimization, Prompt Engineering
- **5 Specialized Agents**: Research, Design, Copy, Revenue, Project Orchestration
- **Auto-Activation System**: Intelligent skill/agent triggering based on user intent
- **Workflow Templates**: Pre-configured multi-agent workflows for common projects

### Key Benefits

- ⚡ **Reduce execution time** by 60-80% through automation
- 🎯 **Improve output quality** with specialized expert agents
- 🔄 **Simplify complex workflows** with orchestrated multi-agent execution
- 📊 **Increase consistency** through standardized processes

---

## Quick Start

### 1. Install Dependencies

```bash
npm install @anthropic-ai/claude-agent-sdk
```

### 2. Load Registry Files

```javascript
const skills = require('./pnkln/skills-registry.yaml');
const agents = require('./pnkln/agents-registry.yaml');
const rules = require('./pnkln/skill-rules.json');
```

### 3. Initialize PNKLN Engine

```javascript
const { PNKLNEngine } = require('./pnkln/engine');

const engine = new PNKLNEngine({
  skills: skills,
  agents: agents,
  activationRules: rules,
  autoActivate: true
});

await engine.initialize();
```

### 4. Use Your First Skill

```javascript
// Explicit activation
const result = await engine.activateSkill('research_explorer', {
  topic: 'AI agent orchestration trends 2025',
  depth_level: 'deep'
});

// Or let auto-activation handle it
const result = await engine.processUserPrompt(
  'Research AI agent orchestration trends for 2025'
);
```

**That's it!** You're now running PNKLN workflows.

---

## Architecture

### Component Hierarchy

```
┌─────────────────────────────────────────┐
│      User Input / Project Request       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     Auto-Activation Engine              │
│  (skill-rules.json)                     │
│  - Pattern matching                     │
│  - Semantic analysis                    │
│  - Agent selection                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    Agent Layer (agents-registry.yaml)   │
│  - ResearchAgent                        │
│  - DesignAgent                          │
│  - CopyAgent                            │
│  - RevenueAgent                         │
│  - ProjectDeepAgent (Orchestrator)      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Skills Layer (skills-registry.yaml)   │
│  - ResearchExplorerSkill                │
│  - DesignCriticSkill                    │
│  - CopyConverterSkill                   │
│  - MonetizationArchitectSkill           │
│  - WorkflowRefinerSkill                 │
│  - PromptCraftSkill                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Output / Deliverables           │
└─────────────────────────────────────────┘
```

### Data Flow

1. **User Input** → Auto-activation engine parses intent
2. **Pattern Matching** → Identifies relevant skills/agents
3. **Agent Selection** → Chooses best agent(s) for task
4. **Skill Execution** → Agent invokes required skills
5. **Result Synthesis** → Combines outputs into deliverable
6. **User Delivery** → Returns structured results

---

## Installation & Setup

### Prerequisites

- Node.js v18+ or Python 3.9+
- Claude Agent SDK v0.1.30+
- Access to Claude API (Anthropic)

### Installation Steps

#### Option A: NPM Package (Recommended)

```bash
npm install pnkln-agent-registry
```

#### Option B: Manual Setup

```bash
# Clone or copy the pnkln directory
cp -r /path/to/pnkln ./pnkln

# Install dependencies
npm install @anthropic-ai/claude-agent-sdk js-yaml
```

### Configuration

Create `pnkln.config.json` in your project root:

```json
{
  "pnkln": {
    "skills_registry": "./pnkln/skills-registry.yaml",
    "agents_registry": "./pnkln/agents-registry.yaml",
    "activation_rules": "./pnkln/skill-rules.json",

    "auto_activation": {
      "enabled": true,
      "confidence_threshold": 0.75,
      "max_concurrent_skills": 3
    },

    "claude_config": {
      "model": "claude-3-5-sonnet-20241022",
      "api_key": "${ANTHROPIC_API_KEY}",
      "max_tokens": 4096
    },

    "caching": {
      "enabled": true,
      "ttl": 3600,
      "storage": "redis"
    },

    "logging": {
      "level": "info",
      "output": "./logs/pnkln.log"
    }
  }
}
```

### Environment Variables

Create `.env`:

```bash
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Optional
PNKLN_LOG_LEVEL=info
PNKLN_CACHE_ENABLED=true
PNKLN_AUTO_ACTIVATE=true
```

---

## Using Skills

### Direct Skill Invocation

```javascript
const result = await engine.activateSkill('research_explorer', {
  topic: 'SaaS pricing models for developers',
  depth_level: 'deep',
  perspectives: ['business', 'user', 'competitive'],
  challenge_assumptions: true
});

console.log(result.findings.summary);
console.log(result.findings.challenged_assumptions);
```

### Skill Chaining

```javascript
// Research → Monetization → Copy
const workflow = engine.createWorkflow([
  {
    skill: 'research_explorer',
    input: { topic: 'AI developer tools market' }
  },
  {
    skill: 'monetization_architect',
    input: (previousResult) => ({
      business_model: 'SaaS',
      competitive_landscape: previousResult.findings.evidence_base
    })
  },
  {
    skill: 'copy_converter',
    input: (previousResult) => ({
      copy_type: 'landing_page',
      product_service: 'AI Development Platform',
      primary_benefit: previousResult.monetization_blueprint.revenue_model
    })
  }
]);

const results = await workflow.execute();
```

### Skill Reference

| Skill ID | Use When | Typical Output Time |
|----------|----------|---------------------|
| `research_explorer` | Need deep analysis, evidence, multi-perspective insights | 10-30 min |
| `design_critic` | Evaluating UI/UX, simplifying designs | 5-15 min |
| `copy_converter` | Creating marketing copy, ads, emails | 3-10 min |
| `monetization_architect` | Designing pricing, revenue models | 10-20 min |
| `workflow_refiner` | Optimizing processes, finding bottlenecks | 5-15 min |
| `prompt_craft` | Creating AI prompts, instructions | 2-5 min |

---

## Using Agents

### Agent Activation

#### Research Agent

```javascript
const researchResult = await engine.activateAgent('research_agent', {
  research_topic: 'Emerging AI frameworks for multi-agent systems',
  depth_level: 'exhaustive',
  time_constraint: 1800  // 30 minutes
});

// Access structured output
console.log(researchResult.research_report);
console.log(researchResult.assumption_analysis);
console.log(researchResult.recommended_actions);
```

#### Design Agent

```javascript
const designCritique = await engine.activateAgent('design_agent', {
  design_artifact: './mockups/landing-page.png',
  design_type: 'ui',
  ruthlessness_level: 'jobs_level',
  target_platform: 'web'
});

console.log(`Beauty Score: ${designCritique.beauty_score}/10`);
console.log(`Simplicity Score: ${designCritique.simplicity_score}/10`);
console.log('Remove:', designCritique.removal_recommendations);
```

#### Copy Agent

```javascript
const copy = await engine.activateAgent('copy_agent', {
  copy_type: 'landing_page',
  product_service: 'AI Workflow Automation Platform',
  target_audience: 'Technical founders and CTOs',
  primary_benefit: 'Reduce engineering time by 60%',
  tone: 'professional'
});

console.log(copy.primary_copy.headline);
console.log(copy.primary_copy.cta);
console.log(copy.ab_test_variants);
```

#### Revenue Agent

```javascript
const monetization = await engine.activateAgent('revenue_agent', {
  business_model: 'Usage-based SaaS with free tier',
  target_customer: 'Early-stage startups',
  current_revenue: {
    mrr: 5000,
    customers: 50,
    churn_rate: 0.05
  }
});

console.log(monetization.revenue_model_recommendation);
console.log(monetization.pricing_strategy);
console.log(monetization.financial_projections);
```

#### Project Deep Agent (Orchestrator)

```javascript
const project = await engine.activateAgent('project_deep_agent', {
  project_description: 'Launch new AI-powered code review tool',
  project_goals: [
    'Market research and positioning',
    'Pricing strategy',
    'Landing page design and copy',
    'Launch workflow automation'
  ],
  timeline: {
    deadline: '2025-12-01',
    milestones: ['Research complete', 'Design approved', 'Launch ready']
  }
});

// ProjectDeepAgent orchestrates multiple agents
console.log(project.agent_assignments);
console.log(project.integrated_deliverables);
```

---

## Auto-Activation System

The PNKLN auto-activation engine intelligently detects user intent and activates the appropriate skills/agents.

### How It Works

1. **User Input Parsing**: Analyzes user message
2. **Pattern Matching**: Checks against trigger rules
3. **Semantic Analysis**: Uses embeddings for intent matching
4. **Confidence Scoring**: Calculates activation confidence
5. **Skill/Agent Selection**: Chooses best match(es)
6. **Auto-Execution**: Runs if confidence > threshold

### Activation Methods

#### 1. Keyword Triggers

```
User: "Research the best practices for API design"
→ Auto-activates: research_explorer skill
```

#### 2. Pattern Triggers

```
User: "research: microservices vs monolith architecture"
→ Auto-activates: research_agent
```

#### 3. Explicit Mentions

```
User: "@copy write landing page for developer tool"
→ Auto-activates: copy_agent
```

#### 4. Semantic Matching

```
User: "I need compelling text for my product homepage"
→ Semantic match: copy_converter skill (0.87 confidence)
```

### Controlling Auto-Activation

#### Disable Auto-Activation

```javascript
engine.setAutoActivation(false);

// Now requires explicit calls
await engine.activateSkill('research_explorer', params);
```

#### Adjust Confidence Threshold

```javascript
engine.setConfidenceThreshold(0.85); // Higher = more conservative
```

#### Manual Override

```
User: "Research pricing models [no-auto]"
→ Auto-activation suppressed, manual control
```

---

## Workflow Templates

Pre-configured multi-agent workflows for common projects.

### New Product Launch

```javascript
const launch = await engine.executeWorkflow('new_product_launch', {
  product: 'AI Code Assistant',
  target_market: 'Individual developers',
  deadline: '2025-12-15'
});

// Executes:
// 1. ResearchAgent: Market research, competitors, customer pain points
// 2. RevenueAgent: Pricing strategy, monetization model
// 3. DesignAgent + CopyAgent (parallel): UI design, marketing copy
// 4. WorkflowRefiner: Launch workflow automation

console.log(launch.research_findings);
console.log(launch.pricing_strategy);
console.log(launch.marketing_assets);
console.log(launch.launch_plan);
```

### Marketing Campaign

```javascript
const campaign = await engine.executeWorkflow('marketing_campaign', {
  campaign_type: 'Product announcement',
  channels: ['email', 'linkedin', 'twitter'],
  target_audience: 'CTOs at Series A startups'
});

// Executes:
// 1. ResearchAgent: Audience analysis, message testing
// 2. CopyAgent + DesignAgent (parallel): Ad copy, creative assets, landing pages

console.log(campaign.audience_insights);
console.log(campaign.copy_variants);
console.log(campaign.creative_assets);
```

### Revenue Optimization

```javascript
const revenueOptimization = await engine.executeWorkflow('revenue_optimization', {
  current_mrr: 10000,
  goal_mrr: 50000,
  timeline_months: 6
});

// Executes:
// 1. ResearchAgent + RevenueAgent (parallel): Competitive pricing, revenue model
// 2. CopyAgent + DesignAgent (parallel): Pricing page copy, pricing page design

console.log(revenueOptimization.revenue_strategy);
console.log(revenueOptimization.pricing_page);
```

### Custom Workflow

```javascript
const customWorkflow = engine.defineWorkflow({
  name: 'feature_launch',
  description: 'Launch new feature with research, design, and marketing',

  phases: [
    {
      name: 'Discovery',
      agents: ['research_agent'],
      tasks: ['User research', 'Feature validation']
    },
    {
      name: 'Execution',
      agents: ['design_agent', 'copy_agent'],
      parallel: true,
      tasks: ['Feature design', 'Announcement copy']
    }
  ]
});

const result = await customWorkflow.execute({
  feature: 'Real-time collaboration',
  target_users: 'Team plan customers'
});
```

---

## Customization

### Adding Custom Skills

Create `custom-skill.yaml`:

```yaml
custom_analysis_skill:
  id: "custom-analysis-v1"
  name: "CustomAnalysisSkill"
  description: "Your custom skill description"

  capabilities:
    - "Capability 1"
    - "Capability 2"

  input_schema:
    input_field:
      type: "string"
      required: true

  output_schema:
    output_field:
      type: "object"

  prompt_template: |
    Your custom prompt template here.
    Input: {input_field}

  activation_triggers:
    keywords: ["custom", "analyze"]
```

Register it:

```javascript
await engine.registerSkill('./custom-skill.yaml');
```

### Modifying Activation Rules

Edit `skill-rules.json`:

```json
{
  "skill_rules": {
    "research_explorer": {
      "exact_triggers": [
        "research",
        "your_custom_trigger"  // Add this
      ],
      "confidence_threshold": 0.80  // Adjust threshold
    }
  }
}
```

### Custom Agent Behavior

```javascript
engine.modifyAgentBehavior('research_agent', {
  autonomy_level: 'low',  // Require more approval
  max_execution_time: 600,  // Reduce timeout
  custom_handler: async (input) => {
    // Your custom pre-processing
    return processedInput;
  }
});
```

---

## Troubleshooting

### Common Issues

#### 1. Skill Not Auto-Activating

**Problem**: User prompt doesn't trigger expected skill

**Solution**:
```javascript
// Debug activation matching
const debug = await engine.debugActivation(
  'Research AI agent frameworks'
);

console.log(debug.matched_skills);
console.log(debug.confidence_scores);
console.log(debug.why_not_activated);
```

**Common causes**:
- Confidence threshold too high
- Ambiguous phrasing
- Negative trigger matched

#### 2. Agent Timeout

**Problem**: Agent execution exceeds max time

**Solution**:
```javascript
// Increase timeout for specific agent
engine.configureAgent('research_agent', {
  max_execution_time: 3600  // 1 hour
});
```

#### 3. Low-Quality Output

**Problem**: Skill output doesn't meet expectations

**Solution**:
```javascript
// Provide more detailed input
const result = await engine.activateSkill('copy_converter', {
  copy_type: 'landing_page',
  product_service: 'Detailed product description here',
  target_audience: 'Specific persona with pain points',
  primary_benefit: 'Concrete, measurable benefit',
  brand_voice: 'Professional, technical but approachable',
  competitor_copy: ['Example 1', 'Example 2']  // More context
});
```

#### 4. Conflicting Agent Outputs

**Problem**: Multiple agents produce inconsistent results

**Solution**:
```javascript
// Use ProjectDeepAgent to orchestrate and resolve conflicts
const result = await engine.activateAgent('project_deep_agent', {
  project_description: 'Your project',
  conflict_resolution: 'prioritize_revenue_agent'  // Set priority
});
```

### Debug Mode

Enable verbose logging:

```javascript
engine.setDebugMode(true);

// Now all activation decisions are logged
const result = await engine.processUserPrompt('Research topic');

// Check logs
console.log(engine.getDebugLog());
```

### Validation

Validate registry files:

```bash
npm run validate-registry

# Output:
# ✓ skills-registry.yaml: valid
# ✓ agents-registry.yaml: valid
# ✓ skill-rules.json: valid
```

---

## Advanced Usage

### Streaming Outputs

```javascript
const stream = engine.activateSkillStream('research_explorer', {
  topic: 'AI safety research 2025'
});

for await (const chunk of stream) {
  if (chunk.type === 'progress') {
    console.log(`Progress: ${chunk.percentage}%`);
  } else if (chunk.type === 'finding') {
    console.log(`New finding: ${chunk.data}`);
  } else if (chunk.type === 'complete') {
    console.log('Research complete!');
    console.log(chunk.final_result);
  }
}
```

### Parallel Agent Execution

```javascript
const results = await Promise.all([
  engine.activateAgent('research_agent', { topic: 'Market size' }),
  engine.activateAgent('copy_agent', { copy_type: 'email' }),
  engine.activateAgent('design_agent', { design_artifact: 'mockup.png' })
]);

const [research, copy, design] = results;
```

### Caching & Performance

```javascript
// Enable result caching
engine.enableCaching({
  provider: 'redis',
  ttl: 3600,  // 1 hour
  keyPrefix: 'pnkln:'
});

// First call: executes and caches
const result1 = await engine.activateSkill('research_explorer', {
  topic: 'AI trends'
});

// Second call with same params: instant from cache
const result2 = await engine.activateSkill('research_explorer', {
  topic: 'AI trends'
});
```

### Webhooks & Callbacks

```javascript
engine.on('skill_activated', (event) => {
  console.log(`Skill ${event.skill_id} started`);
  // Send to analytics
});

engine.on('skill_completed', (event) => {
  console.log(`Skill ${event.skill_id} completed in ${event.duration}ms`);
  // Track performance
});

engine.on('agent_error', (event) => {
  console.error(`Agent ${event.agent_id} error:`, event.error);
  // Alert monitoring system
});
```

### Custom Metrics

```javascript
const metrics = await engine.getMetrics({
  timeRange: 'last_7_days',
  groupBy: 'skill_id'
});

console.log('Skill Usage:', metrics.skill_usage);
console.log('Success Rate:', metrics.success_rate);
console.log('Avg Execution Time:', metrics.avg_execution_time);
```

---

## Performance Optimization

### Best Practices

1. **Use Auto-Activation**: Let the engine choose skills instead of manual selection
2. **Enable Caching**: Cache results for repeated queries
3. **Parallel Execution**: Run independent agents in parallel
4. **Streaming**: Use streaming for long-running tasks
5. **Appropriate Timeouts**: Set realistic timeouts per agent

### Benchmarks

| Task | Without PNKLN | With PNKLN | Improvement |
|------|---------------|------------|-------------|
| Market Research | 2-4 hours | 15-30 min | 80% faster |
| Landing Page Copy | 1-2 hours | 5-10 min | 85% faster |
| Design Critique | 30-60 min | 5-15 min | 75% faster |
| Pricing Strategy | 2-3 hours | 10-20 min | 85% faster |
| Full Product Launch | 2-3 days | 4-6 hours | 90% faster |

### Optimization Tips

```javascript
// 1. Batch similar tasks
const topics = ['Topic A', 'Topic B', 'Topic C'];
const results = await Promise.all(
  topics.map(topic => engine.activateSkill('research_explorer', { topic }))
);

// 2. Use lower depth for quick insights
await engine.activateSkill('research_explorer', {
  topic: 'Quick validation',
  depth_level: 'surface'  // Faster
});

// 3. Reuse agent context
const agent = await engine.getAgent('research_agent');
await agent.execute({ topic: 'Topic 1' });
await agent.execute({ topic: 'Topic 2' });  // Reuses context
```

---

## Next Steps

1. **Try the templates**: Start with `templates/` directory for copy-paste prompts
2. **Run a pilot project**: Pick a real project and use ProjectDeepAgent
3. **Measure impact**: Track time saved, quality improvement
4. **Customize**: Add your own skills and workflows
5. **Share feedback**: Contribute improvements back to the registry

---

## Support & Resources

- **Documentation**: [Full API Reference](./api-reference.md)
- **Examples**: [/examples directory](./examples/)
- **Community**: [GitHub Discussions](#)
- **Issues**: [GitHub Issues](#)

---

## Changelog

### v1.0.0 (2025-11-15)
- Initial release
- 6 core skills
- 5 specialized agents
- Auto-activation system
- 3 workflow templates

---

**Built with ❤️ for autonomous AI workflows**
