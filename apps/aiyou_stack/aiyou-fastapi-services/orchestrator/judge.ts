export const prosecutor = {
  propose: async (caseFile: unknown) => ({ text: "Proposed change", confidence: 0.9 }),
  revise: async (proposal: unknown, guidance: unknown) => ({ ...proposal, text: "Revised change" }),
};

export const defense = {
  attack: async (proposal: unknown, caseFile: unknown) => ({ objections: [] }),
};

export const judge = {
  rule: async (context: unknown) => ({ status: "approved", score: 0.95 }),
};
