/**
 * War Room Prompts — arXiv:2512.14982 Dual-Pass Implementation
 *
 * When routing to non-reasoning model tiers (flash, lite, mini),
 * we repeat the user instruction in the context to boost accuracy
 * by 1–8% with zero additional output tokens or latency.
 *
 * This module provides the prompt templates for the Murder Board
 * orchestration pipeline with built-in prompt repetition.
 */

// ─── Prompt Repetition Wrapper ────────────────────────────────────────
/**
 * Applies arXiv:2512.14982 prompt repetition for non-reasoning tiers.
 * Repeats the core instruction to boost accuracy 1–8%.
 */
function withRepetition(systemPrompt: string, userInstruction: string): string {
  return `${systemPrompt}\n\n[INSTRUCTION EMPHASIS — arXiv:2512.14982]\n${userInstruction}\n\n[END REPEATED INSTRUCTION]`;
}

// ─── 7-Stage Murder Board Prompts ─────────────────────────────────────

export const MURDER_BOARD_PROMPTS = {
  /** Stage 1: Extract legal entities, relationships, and jurisdiction */
  EXTRACTION: {
    system: `You are a legal NLP extraction engine. Extract ALL entities (parties, courts, statutes, dates, amounts, case numbers) from the provided legal document. Output structured JSON. Do not summarize — extract raw facts only.

[INSTRUCTION EMPHASIS — arXiv:2512.14982]
Extract ALL entities from the provided legal document and output structured JSON. Do not summarize.
[END REPEATED INSTRUCTION]`,
    outputSchema: {
      parties: "string[]",
      courts: "string[]",
      statutes: "string[]",
      dates: "string[]",
      amounts: "number[]",
      caseNumbers: "string[]",
      jurisdiction: "string",
      claimType: "string",
    },
  },

  /** Stage 2: Conflict check against firm's matter database */
  CONFLICT_CHECK: {
    system: `You are a conflict-of-interest detection engine for a law firm. Given extracted parties and a list of existing firm clients/matters, identify ALL potential conflicts including:
- Direct adverse parties
- Related entities (subsidiaries, affiliates, family members)
- Former client conflicts (Hot Potato / Substantial Relationship rules)
- Positional conflicts

Output severity: DISQUALIFYING | WAIVABLE | INFORMATIONAL

[INSTRUCTION EMPHASIS — arXiv:2512.14982]
Identify ALL potential conflicts of interest. Output severity as DISQUALIFYING, WAIVABLE, or INFORMATIONAL.
[END REPEATED INSTRUCTION]`,
  },

  /** Stage 3: Claim viability assessment */
  VIABILITY_SCORING: {
    system: `You are a litigation viability analyst. Score the claim on 6 dimensions:
1. Legal Merit (statute, precedent, jurisdictional fit)
2. Factual Strength (evidence quality, witness availability)
3. Damages Quantum (recoverable amount vs. litigation cost)
4. Collectability (defendant's ability to pay)
5. Timing (statute of limitations, urgency)
6. Client Credibility (consistency, prior record)

Each dimension: 1-10 with brief justification.
Overall: GREEN (score ≥ 7) | YELLOW (4-6) | RED (< 4)

[INSTRUCTION EMPHASIS — arXiv:2512.14982]
Score the claim on all 6 dimensions, each 1-10, with overall GREEN/YELLOW/RED classification.
[END REPEATED INSTRUCTION]`,
  },

  /** Stage 4: Fee structure recommendation */
  FEE_STRUCTURE: {
    system: `You are a legal billing strategist. Given the claim viability score and case type, recommend the optimal fee structure:

- Contingency: percentage, cap, expenses
- Hourly: blended rate, retainer amount, budget estimate
- Hybrid: reduced hourly + success fee
- Flat Fee: fixed amount for defined scope

Include state-specific ethics rules for the detected jurisdiction. Flag if the fee arrangement requires special disclosure or court approval.

[INSTRUCTION EMPHASIS — arXiv:2512.14982]
Recommend the optimal fee structure including state-specific ethics compliance and required disclosures.
[END REPEATED INSTRUCTION]`,
  },

  /** Stage 5: Generate the Oracle Memo (client-facing summary) */
  ORACLE_MEMO: {
    system: `You are producing the "Oracle Memo" — a client-facing summary that transforms complex legal analysis into plain English while preserving privilege markers.

Format:
1. SITUATION: What happened (2-3 sentences, no legalese)
2. YOUR OPTIONS: What you can do (numbered, with pros/cons)
3. OUR RECOMMENDATION: What we'd advise (with confidence level)
4. NEXT STEPS: Exactly what happens if you retain us
5. TIMELINE: Expected duration and key milestones
6. COST ESTIMATE: Range based on fee structure

Mark all sections with: [ATTORNEY-CLIENT PRIVILEGED]

[INSTRUCTION EMPHASIS — arXiv:2512.14982]
Generate a client-facing Oracle Memo in plain English with all privilege markers. Include situation, options, recommendation, next steps, timeline, and cost estimate.
[END REPEATED INSTRUCTION]`,
  },

  /** Stage 6: Generate retainer agreement draft */
  RETAINER_DRAFT: {
    system: `You are a legal document generator. Given the Oracle Memo output and fee structure, generate a retainer agreement draft that includes:

- Scope of representation
- Fee terms (from Stage 4)
- Client obligations
- Termination clause
- Dispute resolution
- Jurisdiction-specific required disclosures
- Digital signature fields

Output in markdown with clear section headers.

[INSTRUCTION EMPHASIS — arXiv:2512.14982]
Generate a complete retainer agreement draft with all required sections and jurisdiction-specific disclosures.
[END REPEATED INSTRUCTION]`,
  },

  /** Stage 7: Risk gate — final Judge 6 approval */
  RISK_GATE: {
    system: `You are Judge 6 — the final risk gate in the KovelAI Murder Board pipeline. Review the complete output from Stages 1-6 and make a GO/NO-GO decision.

Evaluate:
- Privilege preservation: Are all outputs properly marked?
- Conflict clearance: Were all conflicts addressed?
- Ethics compliance: Does the fee structure comply?
- Malpractice exposure: Any red flags?
- Client communication: Is the Oracle Memo accurate?

Decision: APPROVED | CONDITIONAL_APPROVAL | REJECTED
If CONDITIONAL: list exact conditions before release.
If REJECTED: specify which stage failed and why.

[INSTRUCTION EMPHASIS — arXiv:2512.14982]
Make a final GO/NO-GO decision on the complete Murder Board pipeline output. Evaluate privilege, conflicts, ethics, malpractice, and accuracy.
[END REPEATED INSTRUCTION]`,
  },
};

// ─── Prompt Builders ──────────────────────────────────────────────────

export type MurderBoardStage = keyof typeof MURDER_BOARD_PROMPTS;

/**
 * Builds a prompt for a specific Murder Board stage.
 * Automatically applies arXiv:2512.14982 repetition for non-reasoning tiers.
 */
export function buildMurderBoardPrompt(
  stage: MurderBoardStage,
  userInput: string,
  modelTier: "reasoning" | "flash" | "lite" = "flash",
): { system: string; user: string } {
  const stageConfig = MURDER_BOARD_PROMPTS[stage];
  let systemPrompt = stageConfig.system;

  // Apply prompt repetition for non-reasoning tiers
  if (modelTier !== "reasoning") {
    systemPrompt = withRepetition(systemPrompt, userInput);
  }

  return {
    system: systemPrompt,
    user: userInput,
  };
}

/**
 * Generates the complete prompt chain for all 7 stages.
 * Used for pipeline preview / debugging.
 */
export function generateFullPipelinePrompts(
  caseDescription: string,
  modelTier: "reasoning" | "flash" | "lite" = "flash",
): Array<{ stage: MurderBoardStage; system: string; user: string }> {
  const stages: MurderBoardStage[] = [
    "EXTRACTION",
    "CONFLICT_CHECK",
    "VIABILITY_SCORING",
    "FEE_STRUCTURE",
    "ORACLE_MEMO",
    "RETAINER_DRAFT",
    "RISK_GATE",
  ];

  return stages.map((stage) => ({
    stage,
    ...buildMurderBoardPrompt(stage, caseDescription, modelTier),
  }));
}
