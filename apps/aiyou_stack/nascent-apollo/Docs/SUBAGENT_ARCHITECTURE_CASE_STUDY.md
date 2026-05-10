# Case Study: Sub-Agent Swarms (The Medium Protocol)

**Source:** "Data Analysis Pipeline with Claude Code" by Gombocz Márton
**Reference Repo:** `https://github.com/gomboczmarton/curated-medium-list-scraper`

## 🧠 Core Doctrine

**"Sub-Agents > Single Agent"**
Specialized agents working in concert outperform monolithic "do-everything" agents. This mirrors software teams where specialists collaborate.

## 🏗️ Architecture: The Triad

The "Medium Protocol" defines three distinct specialized agents for a complex data pipeline:

### 1. The Scraper (Ethical Data Miner)

- **Role:** Extract raw data from hostile/dynamic environments.
- **Tools:** Playwright (Browser Automation), Checkpoint System.
- **Key Features:**
  - **Ethical constraints:** Rate limiting, slow scrolling.
  - **Resilience:** `checkpoint.json` to resume interrupted jobs.
  - **Output:** Raw JSON/CSV.

### 2. The Analyst (Pattern Recognizer)

- **Role:** Derive insights from raw data.
- **Tools:** Python (Pandas), Statistical Analysis.
- **Key Features:**
  - **Parallel Execution:** Orchestrator runs multiple analysis scripts concurrently.
  - **Insight Generation:** Power Law distribution, Temporal Trends.

### 3. The Visualizer (Frontend Engineer)

- **Role:** Present data in an interactive format.
- **Tools:** Claude Artifacts, HTML/JS/CSS.
- **Output:** Interactive Web App (Mobile First).

## 🚀 Application to ShadowTag-Omega

This architecture validates the **ShadowTag V7 Topology**:

| Role             | Medium Protocol           | ShadowTag-Omega Equivalent         |
| :--------------- | :------------------------ | :--------------------------------- |
| **Orchestrator** | Main Agent (Claude Code)  | **Cortex (Gemini/Antigravity)**    |
| **Action**       | Web Scraper Subagent      | **Jetski (Browser Sidecar)**       |
| **Analysis**     | Dataset Insights Analyzer | **Kosmos (Deep Research/Analyst)** |
| **Governance**   | Ethical Constraints       | **Judge 6 (Sentinel)**             |

## 🛠️ Implementation Directives

1.  **Context is King:** Spend time building context (README, specs) before coding.
2.  **Define Subagents Explicitly:** specific prompts/personas for each role.
3.  **Parallel Execution:** Use the Orchestrator to run non-conflicting sub-tasks simultaneously.
