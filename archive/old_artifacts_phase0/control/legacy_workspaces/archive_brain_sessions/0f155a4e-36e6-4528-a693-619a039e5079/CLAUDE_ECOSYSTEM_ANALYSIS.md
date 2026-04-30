# CLAUDE ECOSYSTEM: TOOL UTILITY ANALYSIS
**CONTEXT**: Enhancing Kosmos with "Claude Code" capabilities.

## 1. Tool Analysis

| Repository | Utility & Relevance | Status |
| :--- | :--- | :--- |
| **Claude Skills Automation** | **Skill Injection**: Allows us to inject custom tools (like `browser-use`) directly into Claude Code. Essential for the "Chimera" architecture. | **Installed** |
| **Essentials Claude Code** | **Base Layer**: Likely contains core prompts or minimal setups for a Claude Code environment. Good for reference. | **Installed** |
| **Threadwork** | **Orchestration**: A framework for managing multi-turn agent threads. Useful for "SneakPeek" style long-running tasks. | **Cloning...** |
| **Claude Code System Prompt** | **Reverse Engineering**: The actual system prompt for Claude Code. **CRITICAL** for aligning our Gemini 3 Flash bridge to behave exactly like Claude. | **Cloning...** |
| **clauADA** | **ADA Compliance/Testing**: Specialized agent for accessibility testing. Niche, but useful for "Grandma-Simple" UI verification. | **Cloning...** |
| **Browser Use** | **Sovereign Browser**: The core engine for the "Unrestricted Browser" capability. We already have this. | **Installed** |
| **Claude Code Cheat Sheet** | **SOP/Documentation**: Reference for CLI commands. Good for training "Junior" agents or the user. | **Cloning...** |

## 2. Integration Strategy
1.  **System Prompt**: Ingest `claude-code-system-prompt` into `CCRouter` to make Gemini *feel* like Claude.
2.  **Threadwork**: Use patterns from here to improve `kosmos` memory management.
3.  **Skills**: Use `claude-skills-automation` to wrap `skyvern` as a native skill.
