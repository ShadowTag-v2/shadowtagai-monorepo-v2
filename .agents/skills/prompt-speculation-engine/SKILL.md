# Prompt Speculation Engine

## Overview
Harvested from `PromptSuggestion/`. This governs the generation of the 5-22 nag prompts/suggestions at the end of the agent's turn.

## Protocol
1. Suggestions must be speculative and anticipate the user's next logical request.
2. If a test fails, suggest "View test logs" and "Attempt auto-fix".
3. If a deployment succeeds, suggest "Run Lighthouse audit" and "View live URL".
4. Never suggest redundant or purely rhetorical actions (e.g., "Should I continue?").
