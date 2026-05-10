# Vertex AI Agents for Workbench

A comprehensive collection of 44 specialized AI agents designed for Vertex AI Workbench. These agents help with software development, product strategy, data science, operations, and more.

## Overview

This repository contains a curated set of AI agents that can be used with Google Vertex AI Workbench to enhance your development workflow. Each agent is specialized for specific tasks and comes with:



- **Detailed system prompts** optimized for specific use cases


- **Capability definitions** outlining what each agent can do


- **Example prompts** to get started quickly


- **Tool configurations** for maximum effectiveness

## Quick Start

### Installation

```bash

# Clone the repository

git clone <repository-url>
cd vertex-ai-agents

# Install dependencies (Node.js)

npm install

# Or for Python

pip install -r requirements.txt

```

### Usage

#### JavaScript/TypeScript

```javascript
const { loadAgents, getAgent, searchAgents } = require('./index.js');

// Load all agents
await loadAgents();

// Get a specific agent
const agent = getAgent('system-architect');
console.log(agent.systemPrompt);

// Search for agents
const results = searchAgents('API');
console.log(results);

```

#### Python

```python
from agent_registry import get_agent, search_agents, get_agents_by_category

# Get a specific agent

agent = get_agent('system-architect')
print(agent.system_prompt)

# Search for agents

results = search_agents('API')
for agent in results:
    print(f"{agent.name}: {agent.description}")

# Get agents by category

dev_agents = get_agents_by_category('development')

```

## Agent Categories

### 💡 Product Strategy (5 agents)

Agents focused on product planning, growth, and market strategy.



- **Product Strategist** - Feature prioritization and roadmap planning


- **Growth Engineer** - Viral loops and growth mechanisms


- **User Researcher** - User flow analysis and UX improvements


- **Revenue Optimizer** - Pricing strategy and monetization


- **Market Analyst** - Competitive analysis and positioning

### 💻 Development (8 agents)

Agents for software development and engineering excellence.



- **System Architect** - System design and architecture


- **Code Refactorer** - Code quality and maintainability


- **API Builder** - REST/GraphQL API development


- **Database Expert** - Database design and optimization


- **Integration Master** - Third-party service integrations


- **Mobile Optimizer** - PWA and mobile web optimization


- **Performance Engineer** - Performance optimization and caching


- **Accessibility Pro** - WCAG compliance and accessibility

### 🎨 Design & UX (4 agents)

Agents for creating exceptional user experiences.



- **UX Optimizer** - User flow simplification


- **UI Polisher** - Visual design and animations


- **Content Writer** - UX writing and microcopy


- **Design System Builder** - Component libraries and design tokens

### ✅ Quality & Testing (4 agents)

Agents ensuring code quality and reliability.



- **Test Generator** - Automated test generation


- **Security Scanner** - Security audits and vulnerability fixes


- **Code Reviewer** - Code quality reviews


- **Load Tester** - Performance and load testing

### ⚙️ Operations (5 agents)

Agents for deployment, infrastructure, and operations.



- **Deployment Wizard** - CI/CD pipeline setup


- **Infrastructure Builder** - Cloud architecture and Terraform


- **Monitoring Expert** - Observability and alerting


- **Release Manager** - Feature flags and release management


- **Cost Optimizer** - Cloud cost optimization

### 📈 Business & Analytics (7 agents)

Agents for analytics, marketing, and business operations.



- **Analytics Engineer** - Product analytics and tracking


- **Email Automator** - Email marketing automation


- **Support Builder** - Help systems and chatbots


- **Compliance Expert** - GDPR/CCPA compliance


- **SEO Master** - Search engine optimization


- **Community Features** - Social features and forums


- **Landing Page Optimizer** - Conversion optimization

### 🚀 AI & Innovation (3 agents)

Agents for AI integration and cutting-edge technology.



- **AI Integration Expert** - LLM API integration and RAG systems


- **Automation Builder** - Workflow automation


- **Innovation Lab** - Emerging technology evaluation

### 📊 Data Science (3 agents)

Agents for machine learning and data analysis.



- **ML Engineer** - Machine learning model development


- **Data Analyst** - Data analysis and visualization


- **Data Engineer** - Data pipelines and warehouses

### 🛡️ DevOps & SRE (2 agents)

Agents for reliability engineering and container orchestration.



- **SRE Specialist** - Site reliability and incident management


- **Kubernetes Expert** - Container orchestration

### 👥 Collaboration (3 agents)

Agents for documentation, mentoring, and team collaboration.



- **Documentation Specialist** - Technical documentation


- **Code Mentor** - Teaching and mentoring


- **Localization Expert** - Internationalization and localization

## Agent Structure

Each agent is defined in a JSON file with the following structure:

```json
{
  "name": "Agent Name",
  "id": "agent-id",
  "category": "Category Name",
  "description": "Brief description",
  "icon": "🎯",
  "version": "1.0.0",
  "systemPrompt": "Detailed system prompt...",
  "capabilities": ["capability1", "capability2"],
  "useCases": ["use case 1", "use case 2"],
  "examplePrompts": ["example 1", "example 2"],
  "tools": ["tool1", "tool2"],
  "model": "gemini-pro",
  "temperature": 0.5,
  "maxTokens": 8192
}

```

## Configuration

Edit `config.yaml` to customize:



- Default model settings


- Tool configurations


- Category-specific settings


- Integration settings


- Security settings

## Using with Vertex AI Workbench

### 1. Setup Vertex AI Project

```python
from google.cloud import aiplatform

aiplatform.init(
    project='your-project-id',
    location='us-central1'
)

```

### 2. Load an Agent

```python
from agent_registry import get_agent

# Get the agent configuration

agent = get_agent('system-architect')

# Use the system prompt with Vertex AI

response = model.generate_content(
    contents=user_prompt,
    generation_config={
        'temperature': agent.temperature,
        'max_output_tokens': agent.max_tokens,
    },
    system_instruction=agent.system_prompt
)

```

### 3. Implement Agent Tools

Each agent specifies tools it can use. Implement these tools in your Vertex AI setup for full functionality.

## Best Practices



1. **Choose the Right Agent** - Use the search and recommendation functions to find the best agent for your task


2. **Customize System Prompts** - Adapt agent prompts to your specific needs


3. **Combine Agents** - Use multiple agents in sequence for complex tasks


4. **Monitor Performance** - Track agent effectiveness and iterate on prompts


5. **Respect Rate Limits** - Configure appropriate rate limiting in production

## Contributing

To add a new agent:



1. Create a JSON file in the appropriate category directory


2. Follow the agent structure template


3. Add the agent ID to `registry.json`


4. Update documentation

## Examples

See the `examples/` directory for:



- Integration examples


- Multi-agent workflows


- Custom tool implementations


- Vertex AI Workbench notebooks

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:


- GitHub Issues: [repository-url]/issues


- Documentation: [docs-url]

## Agent Count by Category

| Category | Agents |
|----------|--------|
| Product Strategy | 5 |
| Development | 8 |
| Design & UX | 4 |
| Quality & Testing | 4 |
| Operations | 5 |
| Business & Analytics | 7 |
| AI & Innovation | 3 |
| Data Science | 3 |
| DevOps & SRE | 2 |
| Collaboration | 3 |
| **Total** | **44** |

## Version History



- **1.0.0** (2025-11-15) - Initial release with 44 agents across 10 categories
