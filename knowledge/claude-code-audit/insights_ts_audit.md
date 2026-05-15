# \`insights.ts\` Deep-Dive Audit

**File:** \`src/commands/insights.ts\`
**Complexity:** Highest single-file density (11 feature/env gates, 3000+ lines).

## Core Mechanisms
1. **Remote Host Telemetry (Ant-Only):**
   - Collects session metadata via SSH and \`coder\` CLI from remote homespaces.
   - Specifically routes \`USER_TYPE === 'ant'\` logic to execute remote gathering via \`scp\`.

2. **Session Facet Extraction:**
   - Evaluates conversational session logs, tokenizing user behavior into friction points, satisfaction curves, and project topologies.
   - Summarizes long transcripts by chunking at 25,000 characters and parallelizing summarization via Opus models.
   - Identifies whether users explicitly request help vs. Claude operating autonomously.

3. **Multi-Clauding Detection:**
   - A dedicated temporal function (\`detectMultiClauding\`) searches for interlocking session overlaps (Pattern: S1 -> S2 -> S1) within a 30-minute sliding window to detect when users spawn concurrent conversational agent instances.

4. **Categorization & NLP Analysis:**
   - Generates 6 distinct baseline insights in parallel: \`project_areas\`, \`interaction_style\`, \`what_works\`, \`friction_analysis\`, \`suggestions\`, and \`on_the_horizon\`.
   - **Ant-Only Insight Tiers:**
     - \`cc_team_improvements\`
     - \`model_behavior_improvements\`
   - Culminates in a unified HTML/Markdown report intended to drive behavioral changes in users or product improvements internally.
