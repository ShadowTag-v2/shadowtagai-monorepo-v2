# Production-Ready AI Agents Extraction Task

## Checklist
- [x] https://cloud.google.com/blog/products/ai-machine-learning/a-devs-guide-to-production-ready-ai-agents
- [ ] https://www.kaggle.com/whitepaper-introduction-to-agents
- [ ] https://www.kaggle.com/whitepaper-agent-tools-and-interoperability-with-mcp
- [ ] https://www.kaggle.com/whitepaper-context-engineering-sessions-and-memory
- [ ] https://www.kaggle.com/whitepaper-agent-quality
- [ ] https://www.kaggle.com/whitepaper-prototype-to-production

## Goals
- Architectural principles
- Code structures
- Routing logic
- Evaluation metrics
- Context-engineering rules
- Production-level constraints
- MCP interoperability methods
- Memory management mechanics

## Findings
### 1. A Dev’s Guide to Production-Ready AI Agents (Google Cloud Blog)
- **Agent Definition:** LLM (Cognitive Engine) + Orchestration Layer (Nervous System).
- **Core Loop:** Think -> Act -> Observe (Recursive).
- **Architecture:**
    - Session State (Short-term memory)
    - Memory Service/RAG (Long-term memory)
    - Tool Use (Execution modules)
    - Security Framework.
- **Interoperability:**
    - **MCP (Model Context Protocol):** Standard for connecting tools and data sources.
    - **A2A (Agent2Agent Protocol):** Standard for agent collaboration and negotiation.
- **Context Engineering:** Focuses on prompt design, retrieval, and conversation history.
- **Evaluation:** Metric shifts from "final answer" to "trajectories" (tool selection, reasoning, error recovery).
- **Production Deployment:** Scaling using GKE Inference Gateway and Vertex AI.
