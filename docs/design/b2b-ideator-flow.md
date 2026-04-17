# Bootstrapped B2B Ideator - Flow Mock

## Objective
To serve as a ruthless, lean SaaS brainstorming architecture constrained strictly by the HoldCo B2B pricing model ($20K/mo Enterprise minimum). 

## Component Flow
1. **Input Interface**: "What is the specific, high-friction pain point your target vertical is experiencing?"
2. **Analysis Node (`KovelAI.Ideate`)**:
   - Compares the problem against the 30-vertical matrix.
   - Triggers the `Asymmetric Compute` logic to ping Gemini-3.1-flash for basic structuring.
3. **Synthesis Engine**:
   - Outputs 3 MVP structures avoiding generic aesthetics.
   - Attaches direct pricing moats based on the "5-Slice commercial matrix".
4. **Validation**: Outputs the prompt sequence to NotebookLM for final executive "Dry Ground" sign-off.
