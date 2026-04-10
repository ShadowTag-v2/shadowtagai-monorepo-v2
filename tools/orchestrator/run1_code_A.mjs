/**
 * Run1: Chain A generates code patch
 */

import { save } from "./lib/io.mjs";
import { callLocalModelA } from "./lib/models.mjs";

const GEN_PROMPT = `
You are Chain A (Code Generator).

Task: Produce a minimal, surgical unified diff patch to implement the requested feature.

Hard constraints:
- Minimal changes only
- Preserve existing API and style
- Include tests if applicable
- Output pure unified diff only (no explanations)

Feature request: ${process.env.FEATURE_REQUEST || "Add a health check endpoint to the API"}
`;

const { patch } = await callLocalModelA(GEN_PROMPT);
await save("patches/A.run1.patch", patch);
console.log("✅ Wrote patches/A.run1.patch");
