/**
 * Run3: Chain B (opposition) critiques Chain A's explanation
 */

import { load, save } from "./lib/io.mjs";
import { callLocalModelB } from "./lib/models.mjs";

const explain = await load("explain/A.run2.explain.md");

const OPP_PROMPT = `
You are Chain B (Opposition / Critic).

Review Chain A's explanation and identify:
1. Logic flaws or missing edge cases
2. Security vulnerabilities
3. Performance concerns
4. Alternative approaches

If you find critical issues, propose a small corrective patch (unified diff).
Otherwise, respond with "LGTM" (looks good to me).

---

Chain A's Explanation:

${explain}
`;

const { review, patch } = await callLocalModelB(OPP_PROMPT);

await save("review/B.run3.review.md", review || "LGTM");
if (patch && patch.trim()) {
  await save("patches/B.run3.patch", patch);
  console.log("✅ Wrote patches/B.run3.patch");
}
console.log("✅ Wrote review/B.run3.review.md");
