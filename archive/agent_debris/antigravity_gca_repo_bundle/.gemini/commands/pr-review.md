Review this change like a high-signal code reviewer.

Use REVIEW.md as the governing contract.

Review in this order:
1. correctness
2. security
3. performance
4. maintainability
5. style

Requirements:
- do not invent bugs
- only mark 🔴 when there is a concrete failure mode or deterministic proof path
- prefer a few high-value findings over many weak ones
- identify pre-existing issues separately as 🟣
- recommend the smallest sensible fix

Output format:
- Summary
- Findings
- Risks not fully verified
- Suggested follow-up tests
