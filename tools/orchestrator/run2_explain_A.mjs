/**
 * Run2: Chain A reverse-engineers explanation using Cursor Plan Mode
 */

import { load, save } from "./lib/io.mjs";
import { cursorPlanExplain } from "./lib/models.mjs";

const patch = await load("patches/A.run1.patch");

const CONTEXT = `# Reverse-engineer this patch

Explain the rationale, edge cases handled, and test plan for this change.

\`\`\`diff
${patch}
\`\`\`
`;

const explain = await cursorPlanExplain(CONTEXT);
await save("explain/A.run2.explain.md", explain);
console.log("✅ Wrote explain/A.run2.explain.md");
