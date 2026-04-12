// Minimal Courtroom Loop

import { buildCase } from "./evidence";
import { prosecutor, defense, judge } from "./judge";
import { runWitnesses } from "./witnesses"; // Conceptual import

export async function courtroomLoop(inputs: unknown) {
  const caseFile = await buildCase(inputs); // clerk gathers exhibits
  const p = await prosecutor.propose(caseFile);
  const d = await defense.attack(p, caseFile); // targeted objections
  const evidence = await runWitnesses(p, d); // tests, stego/fft/policy
  const verdict = await judge.rule({ p, d, evidence });

  if (verdict.status === "revise") {
    const guidance = verdict.required_changes;
    const p2 = await prosecutor.revise(p, guidance);
    // In a real loop, this would recurse or loop back.
    // For minimal example:
    return { status: "revised", proposal: p2 };
  }
  return verdict;
}

async function rerun(inputs: unknown) {
  return courtroomLoop(inputs);
}
