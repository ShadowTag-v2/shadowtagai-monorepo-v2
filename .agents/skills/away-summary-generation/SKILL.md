# Away Summary Generation

## Overview
Harvested from `awaySummary.ts` and `AgentSummary/`. When the agent operates in `STATE A` (YOLO) or executes a long-running batch job, it must generate a concise summary for the operator upon their return.

## Implementation
1. Track the start state and end state of the workspace.
2. Aggregate all tool uses, files modified, and errors encountered.
3. Write the summary to `MERGE_STATUS.md` or output it directly to the chat interface.
4. Format:
   - **Time Elapsed:** [Time]
   - **Actions Taken:** [Bullet points]
   - **Anomalies:** [Any errors or warnings]
