Apply the repo's vibe-coding guardrails without becoming mechanical.

Rules:
- split by concern, not line-count superstition
- prefer components under 150 lines
- if a file is 150-300 lines, scrutinize boundaries
- if a file exceeds 300 lines, propose refactor points explicitly
- keep UI separate from business logic when it reduces cognitive load
- never split an otherwise coherent file purely to satisfy a threshold
- prefer maintainability, clarity, and safe iteration over maximal fragmentation

Return:
- guardrail violations
- suggested restructures
- safe next moves
