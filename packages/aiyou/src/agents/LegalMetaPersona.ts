import { ArtifactId, TagSet } from "@shared/types";

/**
 * Defines the cognitive weight and strictness of an LLM Persona.
 */
export interface PersonaConstraint {
  id: string;
  name: string;
  systemPrompt: string;
  requiredEducationYears: number; // e.g., 27 for advanced legal logic
  cognitiveLoadMax: number; // Constraint metric to manage context window cost
}

export const LegalMetaLanguagePersona: PersonaConstraint = {
  id: "persona-law-meta-27",
  name: "Advanced Legal Logic & Meta-Language (27 YOE equivalent)",
  requiredEducationYears: 27,
  cognitiveLoadMax: 100000,
  systemPrompt: `
You are operating within the 'Law as a Meta-Language' cognitive layer.
This is a highly structured, un-ambiguous communications substrate functioning far above standard natural language.
Your outputs must reflect the exactitude, definitional strictness, and risk-managed logical deduction of an attorney with 19 years of formal schooling and 8+ years of dedicated empirical practice.
Never hallucinate precedent. Use extreme specificity in definitions and operational dependencies.
Every semantic output must minimize interpretive drift by anchoring to established, irrefutable definitions (Code, Physics, or Law).
`,
};

/**
 * The Persona Router modifies incoming prompts from the RagGraph
 * and wraps them in the Meta-Language syntax for precision extraction.
 */
export class CognitivePersonaRouter {

  constructor(private defaultPersona: PersonaConstraint = LegalMetaLanguagePersona) {}

  /**
   * Applies the high-fidelity meta-language strictures to a standard prompt.
   */
  injectMetaLanguage(userQuery: string, contextData: string): string {
    return \`
\${this.defaultPersona.systemPrompt}

## OPERATIONAL CONTEXT
\${contextData}

## EXPLICIT QUERY
\${userQuery}

## REQUIRED OUTPUT FORMAT
Respond ONLY via deductive logical blocks. Define variables upfront. State material facts. Execute logical synthesis.
\`;
  }

  getMetrics() {
    return {
      personaId: this.defaultPersona.id,
      cognitiveStrictnessLevel: this.defaultPersona.requiredEducationYears
    };
  }
}
