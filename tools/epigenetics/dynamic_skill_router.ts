import { $ } from "bun";

async function routeSkill(intent: string, domain: "ui" | "backend") {
  console.log(`⚡ [Claude Opus 4.6] Engaging Epigenetic Meta-Discovery for: ${intent}`);
  const targetRepo = domain === "ui" ? "https://github.com/google-labs-code/stitch-skills.git" : "https://github.com/google-labs-code/jules-skills.git";

  const skillData = await $`bunx --bun skills --repo ${targetRepo} --skill find-skills "${intent}" --format=json`.text();
  const matchedSkill = JSON.parse(skillData)?.best_match?.skill_id;

  if (matchedSkill) {
      console.log(`⚡ [Bun] Capability acquired: ${matchedSkill}. Executing...`);
      await $`bunx --bun skills --repo ${targetRepo} --skill "${matchedSkill}" --auto-approve`;
  }
}
routeSkill(process.argv[2], process.argv[3] as "ui" | "backend");
